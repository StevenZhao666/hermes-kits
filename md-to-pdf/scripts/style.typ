// pandoc + typst 模板：A4、中文字体、表格边框、代码块底色、页码
#set page(
  paper: "a4",
  margin: (x: 3.0cm, y: 2.4cm),
  numbering: "1",
)
#set text(
  font: ("Microsoft YaHei", "Noto Sans CJK SC", "New Computer Modern"),
  size: 11pt,
  lang: "zh",
)
#set par(leading: 0.95em, justify: true, spacing: 1.1em)
#show heading: set text(font: ("Microsoft YaHei", "New Computer Modern"))
#show heading.where(level: 1): set text(size: 19pt, weight: "bold")
#show heading.where(level: 2): set text(size: 15pt, weight: "bold")
#show heading.where(level: 3): set text(size: 12.5pt, weight: "bold")
#show heading: set block(above: 1.4em, below: 0.8em)

// 表格：全边框 + 表头浅灰底
#show table: set table(
  stroke: 0.5pt + luma(150),
  inset: 6pt,
  fill: (_, y) => if y == 0 { luma(238) } else { white },
)
#show table.cell.where(y: 0): set text(weight: "bold")

// 代码：优先等宽字体，中文字符回落到微软雅黑（否则会掉到奇怪的中文字体）
#show raw: set text(font: ("Consolas", "JetBrains Mono", "Microsoft YaHei", "DejaVu Sans Mono"))
#show raw.where(block: true): it => block(
  fill: luma(246),
  inset: 9pt,
  radius: 3pt,
  width: 100%,
  it,
)
#show raw.where(block: false): set text(fill: rgb("#b03060"))

// 图片：单张图片宽度由脚本预处理（超宽自动加 width=100%），此处只保证不被裁切
#show figure: set block(breakable: false)

// 引用块
#show quote.where(block: true): it => block(
  inset: (left: 12pt),
  stroke: (left: 2pt + luma(190)),
  text(fill: luma(80), it.body),
)

$if(title)$
#align(center)[
  #text(size: 22pt, weight: "bold")[$title$]
]
$endif$
$if(author)$
#align(center)[#text(size: 11pt)[$author$]]
$endif$
$if(date)$
#align(center)[#text(size: 10pt, fill: luma(110))[$date$]]
$endif$
$if(title)$
#v(1.2em)
$endif$

$body$
