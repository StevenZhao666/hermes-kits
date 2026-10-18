---
name: md-to-pdf
description: Use when generating PDF (PDF 文件/报告/讲义) — write Markdown then convert with the bundled md2pdf script; pandoc + Typst does the typesetting, don't hand-write a PDF renderer.
---

# Markdown → PDF

**核心原则：正文用 Markdown 写，转换交给本目录的脚本。** 排版引擎是 Typst（pandoc 负责 md→Typst），不要自己拼 HTML/CSS 或调浏览器打印。

## 一条命令

```bash
python scripts/md2pdf.py 输入.md 输出.pdf
```

产物特性：

- 中文字体微软雅黑（缺失时回落 Noto Sans CJK / New Computer Modern），自动子集嵌入
- 数学公式 $...$ / $$...$$ → **Typst 原生数学排版**，可选中、可复制，不是图片
- 表格全边框 + 表头浅灰底加粗
- 代码块浅灰圆角底 + 语法高亮，行内代码标红
- 引用块左侧竖线
- 页脚居中页码（`numbering: "1"`）
- 超过正文宽度的图片自动 `width=100%`，不会溢出页面
- 生成 20 页文档约 1.5 秒

## 参数

| 参数 | 作用 |
|---|---|
| `--open` | 生成后打开 |
| `--template=路径` | 换自定义 `.typ` 模板（改字号/字体/页边距时改模板，不改脚本） |

## 前置依赖（一次性）

```bash
pandoc --version          # 需要 ≥ 3.1.3（才有 typst 引擎）
typst --version           # 需要 typst 本体
```

Windows：`winget install JohnMacFarlane.Pandoc` / `winget install Typst.Typst`
macOS：`brew install pandoc typst`

可选但建议装 `pillow`（检测图片宽度用；没装则超宽图片不自动缩放）。

## 改样式

改 `scripts/style.typ`，不要改 md2pdf.py：

- 字体/字号/行距 → `#set text(...)`、`#set par(...)`
- 标题层级 → `#show heading.where(level: n)`
- 表格边框/底纹 → `#show table: set table(...)`
- 代码块底色 → `#show raw.where(block: true)`

改坏了重新从仓库下发即可。

## 什么时候该用 Word 而不是 PDF

- 对方要**编辑** → md-to-docx
- 要**正式排版/打印/提交作业** → 本技能
- 需要页眉页脚自定义、目录域、批注 → 两者都不擅长，单独处理

## 验证（交付前必做）

```bash
python -c "import pymupdf; d=pymupdf.open('out.pdf'); print(d.page_count, len(d[0].get_text()))"
```
页码、页数、正文是否有内容都能这么查。再打开看一眼，别只凭命令返回 0 交付。

## 坑

1. `pandoc --pdf-engine=typst` 要求 pandoc ≥ 3.1.3，旧版本会报 unknown engine。
2. 图片路径相对 markdown 所在目录；脚本已设置 `--resource-path`，跨目录就用绝对路径。
3. 表格单元格里别塞超长段落，Typst 会自动换行但列宽会挤。
4. `$...$` 里不要写中文。
5. 中文字体按 `Microsoft YaHei` → `Noto Sans CJK SC` → `New Computer Modern` 顺序回落；Linux 上记得装 Noto CJK，否则出现方框。
