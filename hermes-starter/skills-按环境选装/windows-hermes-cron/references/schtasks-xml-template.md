# Task Scheduler XML 模板（中文路径适用）

## 完整工作模板

取自 2026-07-21 的 DF 物价追踪迁移实践。此 XML 经实际验证可正确处理中文用户名 + 中文工作目录。

**关键点：**
- 编码需要是 **UTF-16**（XML header 声明 `encoding="UTF-16"`，Python 写入时用 `encoding='utf-16'`）
- `Principal/UserId` 直接写入中文用户名（如 `<主机名>\<用户名>`），不需要转义
- `LogonType` 用 `InteractiveToken` = 登录后才启动
- 任务名称（`/tn`）建议纯 ASCII，避免 schtasks 命令行处理
- `.bat` 文件路径即使用 `%LOCALAPPDATA%` 也可正常工作（此变量在运行时展开）

## 调试过程记录

### 失败的尝试
1. `schtasks /create /sc MINUTE /mo 1 /it` → 任务创建了但自动触发不工作（last_run 始终 1999/11/30）
2. `schtasks /create /sc ONLOGON /it` → 同样触发器不工作
3. PowerShell `Register-ScheduledTask` → `[TimeSpan]::MaxValue` 报错 `P99999999DT23H59M59S`
4. PowerShell `Register-ScheduledTask` → `whoami` 返回乱码用户名 → SID 映射失败
5. Python 写 UTF-8 `.bat` + schtasks → cmd.exe 读 UTF-8 为 GBK，中文路径乱码
6. GBK `.bat` + schtasks `/sc MINUTE /mo 1 /it` → 测试手动跑可以，但自动触发不行

### 成功方案
**XML 导入**：Python 写 UTF-16 XML → `schtasks /create /tn DailyTask /xml file.xml /f`

```python
import subprocess, os, xml.sax.saxutils

task_name = "DailyTask"
bat_path = r"C:\Users\<你的用户名>\AppData\Local\hermes\scripts\run_task.bat"
work_dir = r"D:\某个项目目录\某项目"

xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-07-21T11:00:00</Date>
    <Description>daily data collection</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT30M</Interval>
        <Duration>P365D</Duration>
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
      <UserId><主机名>\<用户名></UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <Enabled>true</Enabled>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT5M</ExecutionTimeLimit>
    <Priority>7</Priority>
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

subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], capture_output=True)
r = subprocess.run(['schtasks', '/create', '/tn', task_name, '/xml', xml_path, '/f'], capture_output=True)
assert r.returncode == 0
```
