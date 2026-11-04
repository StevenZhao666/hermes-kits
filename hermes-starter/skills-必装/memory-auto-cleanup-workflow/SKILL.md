---
name: memory-auto-cleanup-workflow
description: 用定时任务每周自动检查+整理 memory——含 background_review 开关的 config 路径陷阱、定时任务静默停摆的排查。
version: 2.0.0
metadata:
  hermes:
    related_skills: [hermes-memory-strategy, memory-cleanup]
---

# 每周自动整理记忆（cron 定时任务）

> `<HERMES_HOME>`：Windows 是 `%LOCALAPPDATA%\hermes`，macOS / Linux 是 `~/.hermes`。

## 为什么要它

Hermes 的自动记忆（background review）会往 memory 里加东西；没人整理迟早顶到字符上限——**顶到之后写入会被静默拒绝**，机主以为记住了，其实没记。每周一次体检成本很低，而且失败是看得见的。

## 先确认自动记忆的开关

见 hermes-memory-strategy skill：生效的是**顶层** `memory.nudge_interval`（不是 `agent.memory.nudge_interval`，后者是死键）。

推荐配置（自动捕获 + 每周整理兜底）：

```yaml
memory:
  nudge_interval: 30          # 每 30 轮自动审查一次（默认 10）
skills:
  creation_nudge_interval: 0  # 不提醒建 skill
```

## 建任务

```
cronjob(
  action='create',
  name='memory-auto-cleanup',
  schedule='0 20 * * 0',          # 每周日 20:00（挑机主大概率在用电脑的时间）
  skills='hermes-memory-strategy', # 让任务会话带上策略 skill
  deliver='local',                 # 静默执行，不推送通知
  prompt=<下面那段>
)
```

- prompt 建议**自包含**——定时任务是独立会话，没有对话上下文，不知道"上周聊了什么"。
- `deliver='local'`：结果只留在本地。想收到通知可以改成对应平台。

## cron prompt 模板

```
你负责每周检查这台电脑上 Hermes 的记忆文件，超过阈值就整理。

规则见 hermes-memory-strategy skill：MEMORY.md / USER.md 只留身份 + 环境事实 +
项目→skill 指针，细节放 skill。

步骤：
1. 读 memories/MEMORY.md 和 memories/USER.md，算使用率（字符数 ÷ 上限 2200 / 1375）
2. 都没超过 60%：输出「无需清理」+ 实际数字，结束
3. 超过的：按 memory-cleanup skill 的流程做——项目细节迁到对应 skill、memory 缩成
   一行指针、全局偏好只精简不删、过时记录直接删
4. 报告格式：整理前 → 整理后字符数；迁移清单；删除清单；
   每条检查的**实际数字**（光写"检查通过"机主没法判断，不如给数字）

限制：只动 memories/ 下的两个文件和相关 skill；不改机主明确写下的规则；
改之前先在同目录留一份 <文件名>.bak-<日期> 备份。
```

## 验证（★ 建议做——跳过的话失败是看不见的）

1. `cronjob(action='run', job_id=...)` 手动跑一次，读它的输出
2. `hermes cron list` 确认 last run 状态和 next run 时间
3. 回读两个记忆文件，确认字符数真的变了（或确认确实无需清理）
4. 建议把上面三条的真实输出贴给机主看（她看不到后台在跑什么）

## 定时任务为什么静默停摆（通用）

- 任务跑在**本机**：电脑关机 / 睡眠时任务不执行，**错过的也不会补跑**（只等下一个周期）。所以时间要挑机主常用电脑的时候。
- 依赖 Hermes 后台服务（gateway）在运行；服务挂了任务就静默停摆，`hermes cron list` 可能还显示上次成功。
- 症状排查：看任务列表的 last run 时间是否远超预期；看后台进程在不在。
- Windows 上的完整排查方法 + 更稳的替代方案（Windows 任务计划程序）见 `windows-hermes-cron` skill。

## 告诉机主（★ 建议主动说，不然她不知道边界在哪）

1. 电脑关机/睡眠时任务不跑，也不补跑
2. 想立刻整理就说「**整理记忆**」，不用等周日
3. 每周任务是静默的，不会弹通知；想查状态可以让 agent 跑 `hermes cron list`

## 成本

每次任务消耗一次模型调用的 token，但每周 1 次，相比"每 10 轮自动审查"的量级可以忽略。
