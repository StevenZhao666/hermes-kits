# hermes-kits

Hermes Agent 的技能包与桌面工具目录。

## 技能包

| 包 | 作用 | 下载 |
|---|---|---|
| `hermes-starter` | 新手底座：记忆整理 + 避坑 + 文档处理（8 个技能） | [zip](https://github.com/StevenZhao666/hermes-kits/releases/download/packs/hermes-starter.zip) |
| `md-to-docx` | Markdown → Word（公式原生、表格边框、代码块底色、页码） | [zip](https://github.com/StevenZhao666/hermes-kits/releases/download/packs/md-to-docx.zip) |
| `md-to-pdf` | Markdown → PDF（pandoc + Typst：原生公式、中文排版、表格、代码块、页码） | [zip](https://github.com/StevenZhao666/hermes-kits/releases/download/packs/md-to-pdf.zip) |

安装：解压后把包目录放进 Hermes 的 `skills/`，或按包内 `README.md` 操作。

## 桌面工具

MarkdownViewer、Smart Dictionary、ColorPicker、Network Optimizer 等，共 11 个。

- [CATALOG.md](CATALOG.md) —— 全部条目，每条五项：依赖 / 适合 / 获取 / 安装 / 限制
- [catalog.json](catalog.json) —— 结构化版本，字段同构
- [docs/intro.md](docs/intro.md) —— 一页简介

单文件工具直接放在 `tools/` 下，独立仓库的工具只登记链接。

## 目录结构

```
CATALOG.md              全部条目
catalog.json            结构化目录
docs/intro.md           简介
md-to-docx/             技能包：Markdown → Word
md-to-pdf/              技能包：Markdown → PDF
prompts/                每个包对应的提示词
tools/                  单文件桌面工具
  color-picker/
  network-optimizer/
  piano/
  gauss-elim/
  canvas-lab/
```

## 加新包

```
<包名>/                 # 包本体：SKILL.md + README.md + scripts/ + demo
prompts/<包名>.txt      # 提示词（文件版）
prompts/<包名>-链接.txt # 提示词（链接版）
```

发版：

```bash
git add -A && git commit -m "update <包名>" && git push
# 打成 zip（根目录必须是 <包名>/ 文件夹），资产名等于 <包名>.zip
# 上传到固定的 packs 发行版（替换同名资产），不要每包建一个 release
```

所有 zip 都挂在 tag 为 `packs` 的发行版下，链接形如
`https://github.com/StevenZhao666/hermes-kits/releases/download/packs/<包名>.zip`。

不要用 `releases/latest/download/<包名>.zip`：`latest` 是全局最新发行版，
一旦为别的包发版，旧链接就会 404。

## 约定

- 包里不带个人路径、项目名、密钥
- 单文件工具进 `tools/`，大项目只登记链接
- 目录条目保持五项格式，`CATALOG.md` 与 `catalog.json` 同步
