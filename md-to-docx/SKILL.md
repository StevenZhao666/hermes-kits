---
name: md-to-docx
description: Use when generating Word .docx (Word 文档/报告/作业) — write Markdown then convert with the bundled md2docx script; never hand-write python-docx layout code per task.
---

# Markdown → Word (.docx)

**核心原则：正文永远用 Markdown 写，转换用本目录里现成的脚本。不要为每个文档重新手写 python-docx 排版代码**——那会让每次生成多花 1–3k token 外加 2–3 轮调 bug 的往返。

## 一条命令

```bash
python scripts/md2docx.py 输入.md 输出.docx
```

- 公式（`$...$` / `$$...$$`）→ **Word 原生公式对象**（OMML），可在 Word 里点开编辑，不是图片
- 表格自动加边框、表头加粗+浅灰底
- 代码块浅灰底 + 等宽字体 + 语法高亮
- 引用块左侧竖线
- 页脚自动加居中页码
- 中文字体已固化在 `scripts/reference.docx` 模板里（正文微软雅黑 11pt / 1.5 倍行距 / A4 / 标题黑体层级）

## 参数

| 参数 | 作用 |
|---|---|
| `--open` | 生成后立刻用默认程序打开（用户要「生成后立即打开」时加） |
| `--no-page-number` | 不要页脚页码（如做封面/一页纸） |
| `--template=路径` | 换自定义 reference.docx（换字号/字体/页边距时改模板，不改代码） |

## 前置依赖（一次性）

```bash
pandoc --version                      # 需要 ≥ 2.11
python -c "import docx"               # python-docx
```

缺的话：`winget install JohnMacFarlane.Pandoc` / `pip install python-docx`。
模板丢了就重建：`python scripts/make_template.py scripts/reference.docx`。

## 何时仍然需要手写 python-docx

只有这几种情况值得绕过脚本：

1. 需要**精确控制单元格合并、复杂跨页表格**、目录域、批注
2. 需要**读写已有 docx**（改别人的文档、填表模板）→ 用 python-docx 直接改，不要 pandoc
3. 需要 Word 里没有对应 md 语法的版式（多栏、文本框、水印）

其余一切（报告、作业、笔记、说明书、简历、会议纪要）都走 md2docx。

## Markdown 写法注意

- 图片用相对路径，脚本会带上 `--resource-path`；跨目录就用绝对路径
- 表格不要塞太长内容，Word 会挤；超宽表格考虑改成列表
- 公式不要用 `\(...\)`，用 `$...$`；多行公式用 `$$\begin{aligned}...\end{aligned}$$`
- 需要强制分页：`\newpage` 不行，改用 HTML 技巧或转换后用 python-docx 插分页符

## 验证（交付前必做）

```bash
python -c "from docx import Document; d=Document('out.docx'); print(len(d.paragraphs), len(d.tables))"
```
再打开看一遍。有条件就用 Word COM 转 PDF 渲首页图检查排版，别只凭「命令返回 0」交付。
