---
name: windows-hermes-cron
description: Manage scheduled cron jobs under Windows Hermes — dealing with gateway crashes, cron scheduler downtime, and more stable alternatives like Windows Task Scheduler. For when cron jobs silently stop firing.
version: 1.2.0
---

# Windows Hermes Cron/Gateway 管理

## 基本预防：不让电脑休眠

Hermes cron 跑在用户本地 Windows PC 上。电脑一休眠，Gateway → 调度器 → 采集全部停摆。**最便宜的解决方式就是关掉休眠：**

```bash
powercfg /change standby-timeout-ac 0   # 插电状态下永不睡眠
powercfg /change standby-timeout-dc 0   # 电池状态下永不睡眠
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0
powercfg /change monitor-timeout-ac 30  # 显示器30分钟关（省电）
powercfg /change monitor-timeout-dc 15
```

这些命令**不需要管理员权限**，普通终端即可执行。如果用户问"把休眠改了"，他指的是这个。

要彻底关掉休眠文件（省十几G磁盘空间）需要管理员权限跑 `powercfg /h off`。

## 背景

Windows 上 Hermes 的 cron 调度依赖 Gateway 后台进程。Gateway 是一个 Python 进程（`pythonw.exe`），它随时可能崩溃（原因不明：内存、异常、Windows 休眠等）。VBS 开机自启脚本只启动一次，中途崩了没人拉。

**症状**：
- 数据采集停了几小时甚至整天，但 Cron 列表里 `last_status` 仍是 `ok`
- `hermes gateway status` 超时不返回（该命令在 Windows 上已知有 bug）
- `ps aux | grep python` 看不到 Gateway 进程

## 诊断 Gateway 是否活着

```bash
# 方法1（最可靠）：用 tasklist 查 Windows Python 进程（推荐）
tasklist | grep -i python

# 方法2：查 cron 列表
hermes cron list

# 方法3：看最新数据时间（最实锤）
tail -1 "D:/path/to/data.csv" | cut -d',' -f1
```
如果最新数据跟当前时间差很远（如 10 小时），Gateway 肯定挂了。

⚠ **关于 `ps aux`**：MSYS/git-bash 的 `ps aux` **不会可靠显示 Windows 原生进程**。即使 Gateway 正在运行（python.exe），`ps aux | grep python` 也可能返回空结果，给出假阴性。**始终用 `tasklist | grep -i python` 替代。**

**不要依赖 `hermes gateway status`** 来判断——它在 Windows 上经常超时，但不是 Gateway 本身的问题。

## 心跳验证法（★推荐）

最快确认 cron 是否在跑的方法——临时改到每分钟：

1. 改 1 分钟：`cronjob(action='update', job_id='...', schedule='* * * * *')`
2. 等 1-2 分钟
3. 检查新数据是否写入
4. 改回原计划：`cronjob(action='update', job_id='...', schedule='*/30 * * * *')`

比等 30 分钟的下一次采集快 30 倍。

## 启动/重启 Gateway

```bash
# 方式1：后台启动（推荐——Hermes CLI 后台模式）
hermes gateway run     # 在 Hermes 中设为 background=true

# 方式2：通过 VBS 启动（开机自启的方式）
wscript.exe "C:\\Users\\<你的用户名>\\AppData\\Local\\hermes\\gateway-service\\Hermes_Gateway.vbs"

# 方式3：先 kill 再重启
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
hermes gateway run
```

⚠ **不要用 `ps aux` 判断 Gateway 是否启动** — 见诊断章节。启动后若收到 "Another gateway instance is already running" 错误，这是**好现象**：说明 Gateway 本身已经跑着（用 `tasklist | grep python` 确认 PID）。不要强行 kill。

Gateway 跑起来后，cron 调度器自动恢复，不需要额外操作。

## 根本解决方案：Windows 任务计划程序

Windows Task Scheduler 比 Hermes Gateway + cron 稳定得多：
- ✅ Windows 原生服务，系统自己管自己，不会挂
- ✅ 重启后自动恢复
- ✅ 不依赖 Hermes Gateway 进程

### 创建任务

#### 方案 A：纯 ASCII 路径（推荐，无编码问题）

```cmd
schtasks /create /sc MINUTE /mo 30 /tn "DailyTask" /tr "python D:\某个项目\collect.py" /f /ru SYSTEM
```

用 `/ru SYSTEM` 可以避免中文用户名问题。

#### 方案 B：中文路径 → GBK 批处理包装

中文用户目录和中文路径（如 `C:\\Users\\<你的用户名>\\`）在 Task Scheduler 中有严重编码问题。**一种方法是：用 Python 写 GBK 编码的批处理文件，然后用 `schtasks` 指向它。**

```python
"""创建定时任务：Python 写 GBK bat + schtasks（最可靠的中文路径方案）"""
import subprocess, os

task_name = "DailyTask"
python_exe = r"完整路径\to\python.exe"  # 或 sys.executable
script_path = r"完整路径\to\script.py"
work_dir   = r"D:\中文路径\to\project"
bat_path   = r"C:\path\to\run_collect.bat"

# ★ 关键：得用 GBK 编码，cmd.exe 不认识 UTF-8 下的中文
bat_content = f'''@echo off
cd /d "{work_dir}"
"{python_exe}" "{script_path}"
'''
with open(bat_path, 'w', encoding='gbk') as f:
    f.write(bat_content)

# 先测试批处理本身能否跑通
proc = subprocess.run([bat_path], capture_output=True, timeout=30)
if proc.returncode != 0:
    print(f"批处理测试失败: {proc.stderr.decode('utf-8','replace')}")
    exit(1)

# 创建定时任务
subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'],
               capture_output=True)
subprocess.run([
    'schtasks', '/create',
    '/sc', 'MINUTE', '/mo', interval,  # 如 30
    '/tn', task_name,
    '/tr', bat_path,
    '/ru', f'<主机名>\\<用户名>',   # 需要正确格式的主机名\用户名
    '/it', '/f'
])
```

> **为什么不能直接用 schtasks 指定命令？** 中文路径传给 schtasks 的 `/tr` 参数时，MSYS 和 cmd.exe 之间的编码转换会导致乱码，批处理文件路径本身不能正确传递。打包成 .bat 让 schtasks 只看到文件路径（而非命令行中的中文）可以避免这个问题。

#### 方案 C：PowerShell（注意两个常见失败模式）

```powershell
$taskName = "DailyTask"
$pythonExe = "$env:LOCALAPPDATA\hermes\script.py"
$workDir = "D:\某个项目目录\某项目"

$action = New-ScheduledTaskAction -Execute "python" -Argument $pythonExe -WorkingDirectory $workDir
# ★ 不要用 [TimeSpan]::MaxValue — Task Scheduler 不接受 P99999999D
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 30) `
    -RepetitionDuration (New-TimeSpan -Days 365)
# ★ 不要用 -UserId (whoami) — 用户名含中文时 whoami 返回乱码导致 SID 映射失败
$principal = New-ScheduledTaskPrincipal -UserId "<主机名>\<用户名>" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Force
```

**PowerShell 方式的两个常见失败模式：**
- `[TimeSpan]::MaxValue` → 报错 `Duration:P99999999DT23H59M59S` → 改用 `New-TimeSpan -Days 365`
- `-UserId (whoami)` → 报错 `用户帐户安全标识与任何映射都不对应` → 改用 `"主机名\用户名"` 硬编码

#### 方案 D：XML 导入（中文路径下最可靠 ★）

`schtasks` 和 PowerShell 在处理中文路径时都有编码坑。**XML 导入是最可靠的方法**——用 Python 生成 UTF-16 编码的 XML 定义文件，然后用 `schtasks /xml` 导入，完全绕过编码问题。

```python
"""XML 导入法创建定时任务（中文路径首选）"""
import subprocess, os, xml.sax.saxutils

task_name = "DailyTask"
bat_path = r"C:\path\to\run_collect.bat"        # 已存在的 GBK 批处理
work_dir = r"D:\中文路径\to\project"

# 构建 XML（UTF-16 编码，原生支持中文）
xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-07-21T11:00:00</Date>
    <Description>Task description</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT30M</Interval>        # 重复间隔
        <Duration>P365D</Duration>        # 持续 1 年
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2026-07-21T11:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId><主机名>\\<用户名></UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <Enabled>true</Enabled>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT5M</ExecutionTimeLimit>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{xml.sax.saxutils.escape(bat_path)}</Command>
      <WorkingDirectory>{work_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

xml_path = os.path.join(os.environ['LOCALAPPDATA'], 'hermes', 'scripts', 'task.xml')
with open(xml_path, 'w', encoding='utf-16') as f:
    f.write(xml)

# 删除旧任务
subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], capture_output=True)

# XML 导入
subprocess.run(['schtasks', '/create', '/tn', task_name, '/xml', xml_path, '/f'])
```

**为什么 XML 导入最可靠：**
- UTF-16 编码天然支持中文路径和中文用户名
- 不经过 MSYS → cmd.exe 的编码转换
- 完整定义所有触发器、设置、电源选项
- 稳定触发，已验证过自动循环触发正常

#### 启动后验证（无论哪种方案都必需）

创建任务后，**建议等一次自动触发确认**——只手动 `/run` 测过不算数：

```bash
# 1. 先设 1 分钟测试
schtasks /change /tn "DailyTask" /ri 1

# 2. 等 1-2 分钟后检查数据是否更新
tail -1 "D:\path\to\data.csv"

# 3. 验证通过后改回
schtasks /change /tn "DailyTask" /ri 30
```

## 常见陷阱

### Gateway 启动后 cron 还显示"expired"

Gateway 停止期间错过的采集不会补跑，cron 从下一个周期才开始。可以手动触发一次：
```bash
cronjob(action='run', job_id='...')
```

### `hermes gateway status` 超时但 cron 能跑

这是 Windows 下该命令的 bug——status 命令向 Gateway 进程发信号时 hang 住，但调度功能本身没问题。不要因 status 超时就认为挂了，用心跳验证法确认。

### 数据采集正常但 crontab 里 `last_status` 显示旧时间

`no_agent=True` 模式的脚本采集后，cron 的 `last_run_at` 字段通常会更新。如果没更新，检查脚本是否有非零退出码。

### 中文路径 + MSYS/CMD 编码不匹配 ★

MSYS（git-bash）用 UTF-8，cmd.exe 用系统 ANSI 编码（中文 Windows 为 GBK/CP936）。涉及中文路径时：

- **`write_file` 写到 `.bat` 文件是 UTF-8 → cmd.exe 读出乱码** → 报错 `系统找不到指定路径`
- **MSYS 终端传给 cmd.exe 的中文参数会乱码** → 命令行中的 `C:\Users\<你的用户名>\...` 变成 `C:\Users\...`
- **解决方案**：用 Python `subprocess.run()` + `encoding='gbk'` 写 .bat 文件，再用 `schtasks` 指向该 .bat（让 schtasks 只处理文件路径，不处理命令行中文）
- **`%LOCALAPPDATA%` 在 MSYS 终端中传参**：如果直接用 `%LOCALAPPDATA%` 作为 schtasks `/tr` 参数的一部分，MSYS 不会展开它，但 cmd.exe 可能也无法正确展开嵌套在引号中的变量

### PowerShell New-ScheduledTaskPrincipal -UserId (whoami) 失败

当 Windows 用户名含中文时（如 `<用户名>`），`whoami` 返回 `主机名\<用户名>`，其中文部分在 PowerShell 输出中编码成乱码，导致 SID 映射失败：
```
用户帐户安全标识与任何映射都不对应。(23,8):UserId:
```
**解决方案**：硬编码 `-UserId "<主机名>\<用户名>"` 或用 `-LogonType ServiceAccount`。

### New-ScheduledTaskTrigger -RepetitionDuration [TimeSpan]::MaxValue 失败

`[TimeSpan]::MaxValue` 产生的 ISO 8601 周期字符串 `P99999999DT23H59M59S` 超出 Windows Task Scheduler 限制：
```
Duration:P99999999DT23H59M59S
```
**解决方案**：改用 `-RepetitionDuration (New-TimeSpan -Days 365)`。

### `ps aux | grep python` 返回空，但 Gateway 实际在跑

MSYS/git-bash 的 `ps` 命令只看到 MSYS 子进程，看不到 Windows 原生进程（如 python.exe）。这是 MSYS 的限制，**不是 Gateway 挂了**。改用 `tasklist | grep -i python` 确认。

### "Another gateway instance is already running" 不是错误

这是好迹象——表示 Gateway 已经在后台跑着了。先 `tasklist | grep python` 确认 PID，不需要 kill 重启。如果确实要重启，先 `taskkill /F /IM python.exe` 再重试。
