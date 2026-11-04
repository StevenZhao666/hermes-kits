---
name: hermes-memory-strategy
description: Hermes 记忆分层策略——MEMORY.md 只留指针、细节进 skill、到头就整理。整理记忆、memory 超限、新项目该写哪一层时加载。
version: 2.0.0
---

# Hermes 记忆策略（分层与体检）

> 下文用 `<HERMES_HOME>` 表示 Hermes 的配置目录：**Windows** 是 `%LOCALAPPDATA%\hermes`，**macOS / Linux** 是 `~/.hermes`。先确认你的实际路径再用。

## 四层结构

| 层 | 位置 | 什么时候加载 | 放什么 |
|---|---|---|---|
| MEMORY.md | `<HERMES_HOME>/memories/MEMORY.md` | **每轮对话都注入** | 身份、本机环境事实、项目→skill 指针 |
| USER.md | 同目录 | 每轮注入 | 机主画像、偏好、交流方式 |
| Skills | `<HERMES_HOME>/skills/**/SKILL.md` | 按需（靠 description 匹配） | 项目细节、流程、方法论 |
| state.db + 文件系统 | `<HERMES_HOME>/state.db`、磁盘 | 按需（session_search / 读文件） | 历史对话、原始资料 |

三条最重要的（越靠前越建议守）：

1. 两个 .md 文件**每轮对话都要付 token**（全量注入系统提示），skills 只在用到时付。所以：细节建议都进 skill，memory 只留一行指针。
2. 有字符上限（默认 MEMORY 2200 / USER 1375 字符）。顶到上限后**写入会被拒绝，而且是静默的**——你以为记下来了，其实没有。
3. 触发词建议只指向真实存在的 skill。指向不存在的 skill 比没有更糟：会浪费时间，还可能让 agent 怀疑自己记得的正确信息。

## 自动记忆机制 & 关闭方法（含 config 路径陷阱）

Hermes 默认每 N 轮对话 fork 一个后台子进程审查对话，自动往 memory / skill 里写东西。两个开关，写的时候注意位置：

```yaml
memory:
  nudge_interval: 30            # 每 30 轮自动审查一次；0 = 关
skills:
  creation_nudge_interval: 0    # 0 = 关掉"该建 skill 了吗"的提醒
```

- 生效的是**顶层 `memory:` / `skills:` 段**。写成 `agent.memory.nudge_interval` 会被静默保存但**永不生效**（`hermes config set` 不校验路径，回显还是 ✓）。
- 更干净的关闭方式（不跟数值纠缠、语义明确）：`auxiliary.background_review.enabled: false`——关掉自动审查 fork，手动 `/refine` 仍可用。
- 改完建议回读：`hermes config get memory.nudge_interval`，或 `grep -n nudge_interval config.yaml` 确认没写在 `agent:` 段下面。
- 判断某个 key 是否真的生效，最可靠的办法是找它的读取点：`grep -rn "<key名>" <Hermes 安装目录> --include=*.py`。
- 关掉的代价：**没有东西再从对话里"捞"新事实**，只剩人工整理和定时整理。保留它的代价：偶尔把 memory 弄乱——有每周整理兜底就无所谓。
- 想知道它到底在不在跑：日志里搜 `Background review complete`（`hermes logs`）。

## MEMORY.md / USER.md 格式

- 一条一件事，每条 ≤3 行。
- 项目细节超过 3 行 → 迁到对应 skill，memory 里只留一行：`项目名→加载 xxx skill`。
- 全局偏好（工作规则、交流习惯、环境事实）不受 3 行限制，但也只留必要信息。
- 建议不写密码、密钥，只写"凭据文件在哪个路径"（记忆文件是纯文本，谁都看得到）。
- 阈值：到上限的 **80%** 就该整理一次（2200 的 1760 / 1375 的 1100）。系统提示头部每轮都会显示使用率，如 `MEMORY [52% — 1,146/2,200 chars]`，这就是读数来源。

## 什么时候放哪一层

| 场景 | 放哪 |
|---|---|
| 新项目、细节多 | 建 skill，memory 留一行指针 |
| 简单偏好、没有项目上下文 | USER.md |
| 可复用的流程、排错步骤 | skill（编号步骤 + 坑） |
| 参考资料、API 文档、原始数据 | skill 的 references/ 目录 |
| 密码、密钥 | **哪层都不放**，只留文件路径 |

## 常见坑

1. 触发词指向已删除或改名的 skill。删 skill 前先删触发词。
2. MEMORY.md 越写越长——它每轮都付 token，还会稀释注意力。
3. skill 的 description 里没有机主真会说的词（机主说"整理记忆"，描述里只有 memory cleanup → 匹配不上，等于白写）。
4. 以为 skill 是唯一真相：磁盘上的文档往往更新，agent 应该会用文件搜索兜底。
5. 两个 Hermes 实例共用同一个 home 目录 → 记忆互相覆盖，各自记的东西对方不知道。要跑两个实例就给其中一个换 profile。

## 验证清单

- [ ] 每条 memory ≤3 行
- [ ] 每个触发词都指向存在的 skill
- [ ] 项目细节在 skill 里，不在 memory 里
- [ ] 任何一层都没有密码/密钥
- [ ] 每次改动都跟机主说过
