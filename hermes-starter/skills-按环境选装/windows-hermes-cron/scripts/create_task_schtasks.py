"""
Windows Task Scheduler 创建定时任务 — Python + GBK bat + schtasks 方案
用此方案处理中文用户名/路径的编码问题。

注意：如果 GBK bat 方案创建的任务自动触发不工作，改用 XML 导入方案：
  参见 references/schtasks-xml-template.md（UTF-16 XML，最可靠）

用法:
  python create_task_schtasks.py

会创建:
  - 批处理文件 (run_task.bat) — GBK 编码，cmd.exe 可正确读取中文路径
  - Windows 定时任务，开机启动 + 每 N 分钟重复
"""

import subprocess, os, time, sys


def create_scheduled_task(
    task_name: str,
    python_exe: str,
    script_path: str,
    work_dir: str,
    interval_minutes: int = 30,
    bat_path: str = None,
    user_domain: str = None,
    user_name: str = None,
):
    """
    创建 Windows 定时任务。

    参数:
        task_name: 任务名（ASCII，如 "DailyTask"）
        python_exe: Python 可执行文件完整路径
        script_path: 要定时运行的 Python 脚本完整路径
        work_dir: 工作目录（可含中文）
        interval_minutes: 重复间隔（分钟），默认 30
        bat_path: 批处理文件路径（默认 auto）
        user_domain: 主机名（如 "<主机名>"）
        user_name: 用户名（如 "<用户名>"）
    """
    if bat_path is None:
        bat_path = os.path.join(os.path.dirname(script_path), "run_task.bat")
    if user_domain is None or user_name is None:
        import getpass
        user_name = user_name or getpass.getuser()
        user_domain = user_domain or os.environ.get("COMPUTERNAME", "")

    # ── 1. 写 GBK 编码的批处理文件 ──
    bat_content = f"""@echo off
cd /d "{work_dir}"
"{python_exe}" "{script_path}"
"""
    with open(bat_path, "w", encoding="gbk") as f:
        f.write(bat_content)
    print(f"[OK] 批处理文件已写入: {bat_path} ({os.path.getsize(bat_path)} bytes)")

    # ── 2. 测试批处理 ──
    print("[*] 测试批处理...")
    proc = subprocess.run([bat_path], capture_output=True, timeout=30)
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace")
        stdout = proc.stdout.decode("utf-8", errors="replace")
        print(f"[FAIL] 批处理测试失败 (rc={proc.returncode})")
        print(f"  stdout: {stdout[:200]}")
        print(f"  stderr: {stderr[:200]}")
        return False
    print("[OK] 批处理测试通过")

    # ── 3. 删除旧任务（如果有） ──
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"],
                   capture_output=True)

    # ── 4. 创建新任务 ──
    full_user = f"{user_domain}\\{user_name}"
    print(f"[*] 创建任务: {task_name}, 用户={full_user}, 间隔={interval_minutes}分钟")
    result = subprocess.run([
        "schtasks", "/create",
        "/sc", "MINUTE",
        "/mo", str(interval_minutes),
        "/tn", task_name,
        "/tr", bat_path,
        "/ru", full_user,
        "/it", "/f"
    ], capture_output=True)

    out = result.stdout.decode("gbk", errors="replace")
    err = result.stderr.decode("gbk", errors="replace")
    if result.returncode != 0:
        print(f"[FAIL] 创建任务失败: {err}")
        return False
    print(f"[OK] 任务创建成功: {out.strip()}")

    # ── 5. 手动触发一次验证 ──
    time.sleep(2)
    subprocess.run(["schtasks", "/run", "/tn", task_name], capture_output=True)
    print("[*] 已手动触发任务, 等待 10 秒检查结果...")
    time.sleep(10)

    # 查状态
    qr = subprocess.run(
        ["schtasks", "/query", "/tn", task_name, "/v", "/fo", "CSV"],
        capture_output=True
    )
    query_out = qr.stdout.decode("gbk", errors="replace")
    # 取 CSV 第 6 列（上次运行时间）和第 7 列（上次结果）
    fields = query_out.strip().split("\n")
    if len(fields) >= 2:
        data = fields[-1].split(",")
        last_run = data[5] if len(data) > 5 else "?"
        last_rc = data[6] if len(data) > 6 else "?"
        print(f"[OK] 状态: 上次运行={last_run}, 返回码={last_rc}")

    print(f"\n[OK] 完成! 任务 '{task_name}' 每 {interval_minutes} 分钟运行一次")
    print(f"     开机自动启动 + 按间隔重复")
    return True


# ── 使用示例 ──
if __name__ == "__main__":
    create_scheduled_task(
        task_name="DailyTask",
        python_exe=os.path.join(os.environ["LOCALAPPDATA"],
                                "hermes", "hermes-agent", "venv", "Scripts", "python.exe"),
        script_path=os.path.join(os.environ["LOCALAPPDATA"],
                                 "hermes", "scripts", "df_price_collect.py"),
        work_dir=r"D:\某个项目目录\某项目",
        interval_minutes=1,  # 测试用 1 分钟，通过后改回 30
        user_domain="<主机名>",
        user_name="<用户名>",
    )
