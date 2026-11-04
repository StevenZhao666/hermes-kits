---
name: hermes-known-issues
description: Hermes 常见坑与绕过方法——.env 不能读、终端输出打码、config 路径、闪退、定时任务停摆。工具行为异常时先查这里。
version: 1.0.0
---

# Hermes 已知问题与绕过（通用版）

> 这是"最常撞的坑"清单，不是配置教程。遇到新坑、自己解决之后，可以往这里补一条：**症状 + 根因 + 绕过方法**。建议别往 MEMORY.md 里塞这些细节（那边只留指针）。
>
> `<HERMES_HOME>`：Windows 是 `%LOCALAPPDATA%\hermes`，macOS / Linux 是 `~/.hermes`。

## 一、文件与凭据

### `.env` 和含密钥的文件不能直接读

- `read_file` 会**拒绝**读 `.env`（安全设计，报 "Access denied"）。
- `terminal cat` 能把内容打出来，但疑似密钥的值会被**打码**（如 `sk-abcd…1234`）。
- ⚠️ **最危险的操作**：拿打码后的值去做替换/patch——会把真凭据写成截断版，永久损坏。
- 正确做法：用 Python 直接读写文件（`open(path, encoding="utf-8")`），或 `sed -i` 在终端原地替换；核对内容先 `od -A x -t x1z -v <文件>`。

### 终端输出层会把 `""` 显示成 `***`

- `terminal` / `execute_code` 的输出里，空字符串、疑似令牌会显示成 `***`。文件本身没变，但**用打码后的输出当字符串去匹配，一定匹配不上**。
- 规则：读文件用 `read_file`（不打码），不要拿 `cat` 的输出去构造 patch 内容。

### patch 工具的两个坑

- 编辑 HTML / JS 时反斜杠会被再加一层转义（`\s` → `\\s`），导致语法错误 → 含正则的代码改用 `write_file` 整体重写。
- 同一个锚点反复 patch（尤其被打断后重试），会重复插入同一段 → 接续修改前先看行数是否异常膨胀（有 git 就 `git diff --stat`）。

## 二、Windows 环境（非 Windows 可跳过）

### 中文用户名可能踩的坑

- **装完没有桌面快捷方式**：安装器在某些中文用户名下创建快捷方式会失败（不影响安装本身）。手动建：右键桌面 → 新建快捷方式 → 目标填 `%LOCALAPPDATA%\hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe`。
- **.bat 里写中文路径会乱码**（cmd.exe 用 GBK，写文件默认 UTF-8）→ bat 里不要写死中文路径，用 `%LOCALAPPDATA%` 环境变量。
- **终端里搜中文文件名搜不到**（cmd.exe 编码问题）→ 让 agent 去搜的文件名尽量用纯 ASCII（文件内容可以是中文）。

### 两个 config 路径，只有一个生效

| 路径 | 状态 |
|---|---|
| `%LOCALAPPDATA%\hermes\config.yaml` | ✅ Windows 版真正读的那个 |
| `C:\Users\<你>\.hermes\config.yaml` | ❌ 旧版残留 / WSL 版 |

改配置前先确认路径（`echo %LOCALAPPDATA%\hermes`）。改错了不会报错，只是永远不生效。

### 强制关机后打开就闪退

- 原因：`state.db` 的 WAL 日志文件残留，启动时恢复失败。
- 修：删掉 `%LOCALAPPDATA%\hermes\state.db-shm` 和 `state.db-wal`（**别删 state.db 本身**），再启动。
- 预防：正常退出 Hermes，别直接关电源或强杀进程。

## 三、网络

### 不要设全局 HTTP_PROXY / HTTPS_PROXY

- 一旦写进环境变量，**所有**请求都走代理；代理一挂，Hermes 连模型都连不上，看起来像"Hermes 坏了"。
- 需要代理的服务单独配，别污染全局。

### 下载 / 安装超时（GitHub、npm、pip 慢或断）

- 在中国大陆网络环境：见 `china-network-setup` skill（镜像源、断点续传、代理的正确用法）。

## 三·五、默认模型和 key 不匹配 → 无人值守的运行静默失败（新装机器最常见）

- **现象**：能聊天的会话正常（你手动选了模型），但定时任务（cron）、后台记忆审查、`hermes chat -q` 这类**没人手动选模型**的运行全部失败或毫无动静。
- **原因**：`config.yaml` 的 `model.default` 是**装 Hermes 时设置向导写进去的推荐模型**（免费/未登录档位常推荐门户上的模型，形如 `anthropic/claude-opus-4.6`）；后来只往 `.env` 加了某家的 key，provider 被自动识别成那家，但 `model.default` 还是旧的门户模型名 → 直连 API 报"模型不存在/401"。
- **定位**：`hermes config get model.default`，跟 `.env` 里的 key 对一下厂商；一致才算配对。
- **修**：把 `model.default` 改成该 key 能用的模型（例：只有 DeepSeek key → `deepseek-flash`，必要时同时设 `model.provider`）。
- **为什么交互会话看不出来**：手动选模型是**会话级**覆盖，只影响那一次会话，配置文件里的默认值没变。
- **修完之后**：重跑一次出问题的定时任务确认 last run 正常（`hermes cron list`），别只看"配置改了"。

## 四、行为与习惯

### 定时任务会静默停摆

- 电脑关机 / 睡眠时任务不执行，**且不补跑**；Hermes 后台服务挂了也一样。
- 症状：任务列表看着正常，但数据/输出一直不更新。
- 完整排查见 `memory-auto-cleanup-workflow`（通用排查）与 `windows-hermes-cron`（Windows 专属）。

### 聊天里半角 `~` 会渲染成删除线

- 回复里写数字区间（`300~500`）会被渲染成删除线，读不出来。区间用 `-`、`–` 或全角 `～`。

### 别让两个 Hermes 实例共用同一个 home 目录

- 记忆和技能是各自维护的，两个实例同时写会互相覆盖。要跑两个就用 profile 隔开。

### 桌面版设置里找不到某个模型供应商？

- 设置向导的"激活列表"只列**还没配置的**供应商。已经配过的去 Settings → Providers / Keys 里看和管理。

## 五、改了配置没生效？

- 有些配置要**重开会话**才生效（一段对话里的系统提示是固定的，中途不会重载）。
- 先回读确认值写进去了：`hermes config get <key>`；再确认路径对不对。
- `hermes config set` 对不认识的 key 也会显示 ✓ 并保存，只多一行提示——**回显成功 ≠ 真的生效**。判断某个 key 是否有效，最可靠的是找它的读取点（`grep -rn "<key名>" <Hermes 安装目录> --include=*.py`）。
