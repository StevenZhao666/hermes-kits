# 资源目录

> 一个索引入口：技能包 + 桌面小工具。给 agent 读，也给人看。
> 每条固定五项：**依赖 / 适合 / 获取 / 安装 / 限制**。
> 最后更新：2026-11-04

---

## 给接收方的 agent

把下面这段话连同目录链接一起交给它：

```
这是资源目录：https://raw.githubusercontent.com/StevenZhao666/hermes-kits/main/CATALOG.md
先读它，再按我的情况挑：<系统>、<身份>、<会不会技术>。
挑 1-2 个最相关的装好，不要一次装一堆。
装完告诉我：装了什么、怎么打开、有什么限制。
不要问我技术问题，能自己查的自己查。
```

判断规则：

- 先看「按场景选」，命中就直接跳到对应条目
- 只装能跑起来的：平台不匹配、依赖装不上，就跳过并说明原因
- 装完必须用真实动作验证（打开一次、跑一次），不要只复制文件就报成功
- 每个条目的「限制」要如实转告，不要美化

---

## 按场景选

| 我想要 | 拿这个 |
|---|---|
| 写带公式的笔记 / 作业 | MarkdownViewer |
| 电脑配置低、只要个轻量预览 | MarkdownViewer Lite |
| Markdown 交作业要 Word | md-to-docx |
| Markdown 交作业要 PDF | md-to-pdf |
| 读英文文档老查词 | Smart Dictionary |
| 想自己排健身计划 | SimpleTrainer |
| 分不清颜色但要做色号题 | ColorPicker |
| Wi-Fi 慢，想试试改网卡设置 | Network Optimizer |
| 玩一下 / 演示 | Piano、重构防线 |
| 学线代要精确分数解方程 | Gauss Elim |
| 写长文、小说 | Inkbloom |

---

## 技能包

### md-to-docx

- **类型**：Hermes 技能包（agent 用）
- **平台**：Windows / macOS / Linux
- **依赖**：pandoc、python-docx
- **适合**：要把 Markdown 转成 Word，要求公式原生、表格有边框、代码块有底色、带页码
- **获取**：https://github.com/StevenZhao666/hermes-kits/releases/download/packs/md-to-docx.zip
- **安装**：连同 `prompts/md-to-docx.txt` 一起交给 agent，它自己装依赖、自己跑 demo
- **限制**：复杂嵌套表格和自定义样式仍需手工调

### md-to-pdf

- **类型**：Hermes 技能包（agent 用）
- **平台**：Windows / macOS / Linux
- **依赖**：pandoc、Typst
- **适合**：Markdown → PDF，中文排版、公式、表格、页码都要像样
- **获取**：https://github.com/StevenZhao666/hermes-kits/releases/download/packs/md-to-pdf.zip
- **安装**：同 md-to-docx
- **限制**：字体要本机有；生僻字体需自己配

---

## 桌面工具

### MarkdownViewer

- **类型**：桌面工具（人用）
- **平台**：Windows / macOS / Linux（Chrome / Edge）
- **依赖**：无。单文件 HTML，KaTeX 全内联，离线可用
- **适合**：写带公式的笔记、作业、讲义；不想装任何东西
- **获取**：https://raw.githubusercontent.com/StevenZhao666/markdown-viewer/master/dist/MarkdownViewer.html
- **安装**：下载 → 双击 → 拖入 `.md` 或点「打开文件夹」→ `Ctrl+S` 保存
- **限制**：表格编辑不完整；保存依赖浏览器的 File System Access API（Chrome / Edge 支持）

功能：分屏编辑、KaTeX 实时预览、可视化公式编辑器（分式/根号/积分/矩阵/概率统计，可嵌套）、块编辑、多标签页、文件树、目录、主题色盘。

### MarkdownViewer Lite

- **类型**：桌面工具（人用）
- **平台**：任意现代浏览器
- **依赖**：无（KaTeX 走 CDN，首次打开需联网）
- **适合**：只要一个能写公式的轻量编辑器，64KB
- **获取**：https://raw.githubusercontent.com/StevenZhao666/markdown-viewer/master/MarkdownViewer-lite.html
- **安装**：下载 → 双击
- **限制**：保存走浏览器下载；功能比完整版少

### Smart Dictionary

- **类型**：桌面工具（人用）
- **平台**：Windows
- **依赖**：AutoHotkey v2 + DeepSeek API Key
- **适合**：经常读英文术语，想划词即查
- **获取**：https://github.com/StevenZhao666/smart-dictionary/archive/refs/heads/master.zip
- **安装**：装 AHK v2 → 双击 `smart-dict.ahk` → `Ctrl+Alt+Space` 填 API Key
- **限制**：本地词库 128 条起，未命中才调 API；需要自己的 key

### SimpleTrainer

- **类型**：桌面工具（人用）
- **平台**：任意现代浏览器
- **依赖**：无
- **适合**：想按自己的动作排训练计划、打卡
- **获取**：https://github.com/StevenZhao666/simple-trainer/archive/refs/heads/master.zip
- **安装**：打开 `开发/generator.html`，按三步生成 `trainer.html`
- **限制**：数据存浏览器 localStorage，换浏览器会丢

### ColorPicker

- **类型**：桌面工具（人用）
- **平台**：Windows
- **依赖**：AutoHotkey v2
- **适合**：不靠眼睛辨色、要对着 `#RRGGBB` 逐字符比对的人
- **获取**：https://raw.githubusercontent.com/StevenZhao666/hermes-kits/main/tools/color-picker/ColorPicker.ahk
- **安装**：装 AHK v2 → 双击脚本 → `Ctrl+Alt+C` 取色，左键复制
- **限制**：仅 Windows；改热键要编辑脚本

### Network Optimizer

- **类型**：桌面工具（人用）
- **平台**：Windows 10 / 11
- **依赖**：系统自带 PowerShell 5.1
- **适合**：Wi-Fi 慢，想试试把网卡锁 5GHz、关掉节能
- **获取**：https://raw.githubusercontent.com/StevenZhao666/hermes-kits/main/tools/network-optimizer/optimize-network.bat
- **安装**：双击（自动提权）→ 跑完看日志；还原用同目录 `restore-network.bat`
- **限制**：会断网十几秒；驱动不支持「首选频带」时该步跳过；不是万能提速

### Piano

- **类型**：桌面工具（人用）
- **平台**：任意现代浏览器
- **依赖**：无
- **适合**：玩
- **获取**：https://raw.githubusercontent.com/StevenZhao666/hermes-kits/main/tools/piano/piano.html
- **安装**：下载 → 双击
- **限制**：键盘映射固定

### Gauss Elim

- **类型**：桌面工具（人用）
- **平台**：Windows
- **依赖**：无（exe 静态编译）；源码需 g++
- **适合**：线代作业要精确分数解，不要浮点误差
- **获取**：https://raw.githubusercontent.com/StevenZhao666/hermes-kits/main/tools/gauss-elim/gauss.exe
- **安装**：下载 → 双击 → 按提示输入
- **限制**：控制台交互；只做消元，不做符号化简

### 重构防线

- **类型**：桌面工具（人用）
- **平台**：任意现代浏览器
- **依赖**：无
- **适合**：玩塔防；也可当「单文件能做成什么」的样例
- **获取**：https://github.com/StevenZhao666/reforging-defense-line
- **安装**：下载仓库 → 打开 `dist/index.html`
- **限制**：需要同目录 `app.js`

### Inkbloom

- **类型**：桌面应用（人用）
- **平台**：Windows / macOS
- **依赖**：安装包
- **适合**：写长文、小说，需要专注的写作环境
- **获取**：https://github.com/StevenZhao666/inkbloom
- **安装**：下载 Release 安装包
- **限制**：安装包较大（约 270MB）

### Canvas Lab

- **类型**：教学样例（人用）
- **平台**：任意现代浏览器
- **依赖**：无
- **适合**：学 Canvas，或想看「一个 HTML 能做出什么」
- **获取**：https://raw.githubusercontent.com/StevenZhao666/hermes-kits/main/tools/canvas-lab/canvas-lab.html
- **安装**：下载 → 双击
- **限制**：5 个固定任务，不是通用工具

---

## 维护

新增条目时照抄上面的五项格式，并同步更新 `catalog.json`。

- 单文件工具直接放 `tools/<名字>/`，链接用 `raw.githubusercontent.com/.../main/...`
- 有独立仓库的工具只登记链接，不复制源码
- 每次发布前跑一遍脱敏扫描：
  ```bash
  python scripts/scan_sensitive.py .
  ```
