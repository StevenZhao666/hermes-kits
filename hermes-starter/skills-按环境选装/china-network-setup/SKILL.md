---
name: china-network-setup
description: Install CLI tools and download files from behind GFW — GitHub/npm mirrors, aria2 torrent client, curl resume patterns. Use when a tool install or download fails with timeout/connection-reset.
---

# China Network Setup

Installing tools and downloading files when GitHub, npm, and other foreign services are blocked or slow.

## Quick Reference

| Source | Problem | Solution |
|--------|---------|----------|
| GitHub releases | `Connection was reset` | `ghproxy.net` proxy: `https://ghproxy.net/<original-url>` |
| GitHub raw/files | Timeout | Try `ghproxy.net` first; for code files, use jsDelivr CDN |
| GitHub raw code | Timeout (ghproxy down) | jsDelivr CDN: `https://cdn.jsdelivr.net/gh/OWNER/REPO@main/PATH` |
| npm registry | Slow / timeout | `npm config set registry https://registry.npmmirror.com` |
| GitHub API | Timeout | API may work while raw content doesn't — try `api.github.com` directly |
| pip/uv | Slow | Use `-i https://pypi.tuna.tsinghua.edu.cn/simple`（2026-07 实测：tuna 索引 0.8s、aliyun 4.5s、官方 files.pythonhosted.org 直接超时——tuna 为默认首选，aliyun 作备胎） |

## PowerShell 脚本走本地代理（irm | iex 类安装）

PowerShell 的 Invoke-WebRequest 不读 HTTP_PROXY 环境变量，但可注入 DefaultWebProxy。实测（2026-08-05，cua-driver 安装）：

```bash
powershell -NoProfile -ExecutionPolicy Bypass -Command '
$env:HTTP_PROXY="http://127.0.0.1:<你的代理端口>"
$env:HTTPS_PROXY="http://127.0.0.1:<你的代理端口>"
[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy("http://127.0.0.1:<你的代理端口>")
irm https://xxx/install.ps1 | iex
'
```

配合技巧：
- 先 `curl -s -x http://127.0.0.1:<你的代理端口> -o out.ps1 -w "%{http_code}" <url>` 下载脚本到本地审查，再本地执行（`& "C:\...\install.ps1"`），避免盲跑远程脚本。
- 若安装脚本内部还调 `cua-driver update` 之类直连 GitHub 的子命令，装完后把 bin 目录加进当前 shell PATH 再跑：`export PATH="$PATH:/c/Users/<user>/AppData/Local/Programs/Cua/cua-driver/bin"`。
- 检查 User PATH 是否已写入：`powershell -NoProfile -Command '[Environment]::GetEnvironmentVariable("Path","User")'`。
- **Windows 原生 curl.exe 不认 MSYS 的 `/tmp`**——`-o /tmp/x` 会落到当前盘符的 `D:\tmp\`。用 `C:/Users/<user>/AppData/Local/Temp/...` 或先 `cygpath -w`。

## Hermes computer-use 安装

`hermes computer-use install` 封装了 cua-driver 官方安装器，GitHub 被墙时同样失败，会提示手动重跑 `irm ... | iex`。用上面的 PowerShell 代理注入跑通后：
- `hermes computer-use status` / `doctor` 验证（doctor 需 PATH 含 cua-driver，当前 shell 记得 export）。
- 装完 `cua-driver autostart kick` 立即启动 daemon（计划任务已注册但等下次登录才触发）。
- **当前已开的 Hermes 会话不会自动获得 computer_use 工具**——工具集在会话启动时加载，需新开会话/重启 Hermes。config.yaml 的 `platform_toolsets.cli` 已含 `computer_use` 的话无需再配。

## GitHub Downloads via ghproxy

When curl/wget to github.com times out:
```
curl -L -o output.zip "https://ghproxy.net/https://github.com/OWNER/REPO/releases/download/TAG/FILE.zip"
```

ghproxy.net 本身可能失效（2026-08-05 实测超时）——此时优先走本地代理（本地代理 等）：`curl -x http://127.0.0.1:<你的代理端口> -L -o output.zip <原始github url>`，或 jsDelivr 拉 raw 代码文件。

## npm via Chinese Mirror

```
npm config set registry https://registry.npmmirror.com
```

To revert: `npm config delete registry`

## aria2c Torrent Downloader

### Install on Windows
1. Download from GitHub via ghproxy:
   ```
   curl -L -o D:/aria2.zip "https://ghproxy.net/https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip"
   ```
2. Extract: `unzip -o D:/aria2.zip -d D:/aria2`
3. Binary at: `D:/aria2/aria2-1.37.0-win-64bit-build1/aria2c.exe`

### Add to PATH (git-bash)
```bash
echo 'export PATH="$PATH:/d/aria2/aria2-1.37.0-win-64bit-build1"' >> ~/.bashrc
source ~/.bashrc
```

### Download a torrent with DHT + extra trackers
```bash
aria2c --seed-time=0 --dir="D:/output" \
  --bt-tracker="udp://tracker.opentrackr.org:1337/announce,udp://tracker.torrent.eu.org:451/announce" \
  "path/to/file.torrent"
```

### aria2 status line decoding
```
[#5bbb50 0B/165MiB(0%) CN:4 SD:0 DL:0B]
```
- CN = Connections (peers connected)
- SD = Seeds (peers with complete file)
- DL = Download speed
- **If SD:0 after 2+ minutes, the torrent has no active seeds — no tool will help.**

## Pitfalls

- **私有 tracker 的种子**（很多资源站的种子属于这类）常因 NAT 后做种人数少而下不动。 Even with DHT + public trackers added, if no one is seeding the exact content, it won't download.
- **aria2 DHT error on first run** (`Failed to load DHT routing table from .../dht.dat`) is harmless — it creates a fresh table.
- **`File exists but .aria2 control file does not`** — delete the existing file or add `--allow-overwrite=true`.
- **npm packages with native modules** (webtorrent, node-datachannel) may fail on Windows without build tools. Prefer aria2 for torrents.
- **Online torrent download services** (seedr.cc, zbigz.com) may be blocked from the terminal even if the main website loads in a browser with VPN.

## Hermes 接 Telegram 机器人时的代理问题（不用 Telegram 可跳过）

Telegram 的 API（`api.telegram.org`）在国内被墙，接机器人的话 gateway 会报
`httpx.ConnectTimeout → telegram.error.TimedOut`。

**关键点：代理要写进 `.env`，不是 config.yaml。** 机器人库用的 httpx 只读环境变量；
用 `hermes config set HTTPS_PROXY` 会写进 config.yaml，程序读不到，照样连不上。

```bash
# Windows Hermes 的 .env 在 %LOCALAPPDATA%\hermes\.env
echo "HTTPS_PROXY=http://127.0.0.1:<你的代理端口>" >> "$LOCALAPPDATA/hermes/.env"
echo "HTTP_PROXY=http://127.0.0.1:<你的代理端口>"  >> "$LOCALAPPDATA/hermes/.env"
# 不知道端口：netstat -an | grep LISTEN | grep 127.0.0.1
# 常见：Clash 7890 / V2Ray 10809 / Shadowsocks 1080
```

验证代理能不能通：`curl -x http://127.0.0.1:<端口> -s --connect-timeout 5 https://api.telegram.org/bot<TOKEN>/getMe`
→ 返回 `{"ok":true,...}` 就对了。

其它坑：
- 机器人只在「电脑开着 + gateway 在跑」时在线（服务在本机，不是云上）。
- 默认拒绝陌生用户：日志提示 `No env user allowlists configured`，需要设 `TELEGRAM_ALLOWED_USERS`。
- 建机器人得去 Telegram 客户端找 @BotFather，命令行建不了。

## See Also
- `references/torrent-debugging.md` — 诊断死种子的分步流程和症状对照表
