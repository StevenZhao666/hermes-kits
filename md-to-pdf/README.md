# PDF 生成技能包

让 Hermes 会写 PDF：先写 Markdown，再一条命令转成 .pdf。
排版引擎是 Typst，中文、公式（原生排版，可选中复制）、表格、代码块、页码全部自动处理。

## 怎么装

把配套的那段提示词原样贴给 Hermes，它会自己判断要不要装、自己装、自己测。

## 装好之后怎么用

直接说：「帮我做一份 PDF，主题是 XXX」。

## 包里是什么

```
md-to-pdf/
├─ SKILL.md            Hermes 读的说明书
├─ README.md           本文件
├─ demo.md             演示输入
├─ install.bat         可选：双击安装（agent 装不上时的兜底）
└─ scripts/
   ├─ md2pdf.py        转换脚本（pandoc + typst）
   └─ style.typ        排版模板（字体/字号/行距/表格/代码块）
```

## 想改排版

改 `scripts/style.typ`：字体、字号、行距、表格边框、代码块底色都在里面，注释已标好位置。

## 边界

- 依赖 pandoc ≥ 3.1.3 与 typst（都是单个可执行文件，装起来 100 MB 以内）
- PDF 是印刷格式，不能像 Word 那样直接改字；要改就改 Markdown 重新生成
- 需要页眉/页脚自定义、目录域、批注的场景，这套做不好，另说
