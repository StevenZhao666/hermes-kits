# Word 生成技能包

让 Hermes 会写 Word 文档：先写 Markdown，再一条命令转成 .docx。
公式是 Word 原生公式（能双击编辑），表格有边框，代码块有底色，页脚有页码。

## 怎么装

把配套的那段提示词原样贴给 Hermes，它会自己判断要不要装、自己装、自己测。不需要手动操作。

## 装好之后怎么用

直接说：「帮我写一份 Word 文档，主题是 XXX」。

如果它又开始写一大段 Python 代码，就说一句：「用 md-to-docx 技能」。

## 包里是什么

```
md-to-docx/
├─ SKILL.md            Hermes 读的说明书
├─ README.md           本文件
├─ demo.md             演示输入
├─ demo.docx           演示产物（可直接打开看效果）
├─ install.bat         可选：双击安装（agent 装不上时的兜底）
└─ scripts/
   ├─ md2docx.py       转换脚本（pandoc + python-docx）
   ├─ make_template.py 重建排版模板
   └─ reference.docx   排版模板（字体/字号/行距/页边距）
```

## 想改排版

不要改代码，改 `scripts/reference.docx`：用 Word 打开它，改「正文」「标题 1/2/3」「Body Text」「Block Text」样式，保存即可。以后所有文档自动套用。

改坏了就删掉它，重新跑 `python scripts/make_template.py scripts/reference.docx` 恢复默认。

## 边界

- 需要 Word / WPS 才能打开产物
- 合并单元格、跨页表头这类复杂表格做不好，需要单独处理
- 字体依赖系统里有微软雅黑和 Consolas（Windows 自带）
