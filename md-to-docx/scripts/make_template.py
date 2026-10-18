# -*- coding: utf-8 -*-
"""生成 md2docx 用的 reference.docx 模板（中文字体 / 标题层级 / 代码块 / 页边距）。
用法: python make_template.py [输出路径]
"""
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SANS = "Microsoft YaHei"
SERIF = "SimSun"
MONO = "Consolas"


def set_fonts(style, ascii_font, ea_font, size=None, bold=None, color=None):
    style.font.name = ascii_font
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), ea_font)
    if size is not None:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if color is not None:
        style.font.color.rgb = RGBColor(*color)


def shade(style_or_cell, hex_fill):
    el = style_or_cell._element
    pr = el.get_or_add_pPr() if hasattr(el, "get_or_add_pPr") else el
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    pr.append(shd)


def main(out="reference.docx"):
    doc = Document()
    from docx.enum.style import WD_STYLE_TYPE

    # 页面：A4，中文论文常规页边距
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin = s.bottom_margin = Cm(2.54)
        s.left_margin = s.right_margin = Cm(3.17)

    st = doc.styles
    set_fonts(st["Normal"], SANS, SANS, 11)
    st["Normal"].paragraph_format.line_spacing = 1.5
    st["Normal"].paragraph_format.space_after = Pt(6)

    set_fonts(st["Title"], SANS, SANS, 24, True, (0x11, 0x11, 0x11))
    set_fonts(st["Heading 1"], SANS, SANS, 20, True, (0x00, 0x00, 0x00))
    set_fonts(st["Heading 2"], SANS, SANS, 16, True, (0x11, 0x11, 0x11))
    set_fonts(st["Heading 3"], SANS, SANS, 13.5, True, (0x22, 0x22, 0x22))
    set_fonts(st["Heading 4"], SANS, SANS, 12, True, (0x33, 0x33, 0x33))
    for name in ("Heading 1", "Heading 2", "Heading 3", "Heading 4"):
        pf = st[name].paragraph_format
        pf.space_before = Pt(12)
        pf.space_after = Pt(6)
        pf.keep_with_next = True

    for name in ("Body Text", "First Paragraph", "Compact"):
        if name in [x.name for x in st]:
            set_fonts(st[name], SANS, SANS, 11)
            st[name].paragraph_format.line_spacing = 1.5
            st[name].paragraph_format.space_after = Pt(6)

    if "Source Code" in [x.name for x in st]:
        set_fonts(st["Source Code"], MONO, MONO, 9.5)
        st["Source Code"].paragraph_format.line_spacing = 1.2
    if "Verbatim Char" in [x.name for x in st]:
        set_fonts(st["Verbatim Char"], MONO, MONO, 10)

    for name, size, italic, color in (
        ("Block Text", 10.5, False, (0x44, 0x44, 0x44)),
        ("Caption", 9.5, False, (0x55, 0x55, 0x55)),
    ):
        if name in [x.name for x in st]:
            set_fonts(st[name], SANS, SANS, size, None, color)

    # pandoc 只在 reference.docx 里存在这些样式时才使用它们
    names = [x.name for x in st]
    if "Block Text" not in names:
        block = st.add_style("Block Text", WD_STYLE_TYPE.PARAGRAPH)
        block.base_style = st["Normal"]
        set_fonts(block, SANS, SANS, 10.5, None, (0x44, 0x44, 0x44))
        pf = block.paragraph_format
        pf.left_indent = Cm(0.8)
        pf.right_indent = Cm(0.4)
        pf.space_before = Pt(6)
        pf.space_after = Pt(6)
        ppr = block.element.get_or_add_pPr()
        pbdr = OxmlElement("w:pBdr")
        left = OxmlElement("w:left")
        left.set(qn("w:val"), "single")
        left.set(qn("w:sz"), "18")
        left.set(qn("w:space"), "8")
        left.set(qn("w:color"), "C8CDD4")
        pbdr.append(left)
        ppr.append(pbdr)

    if "Verbatim Char" not in names:
        verb = st.add_style("Verbatim Char", WD_STYLE_TYPE.CHARACTER)
        set_fonts(verb, MONO, MONO, 9.5)
        rpr = verb.element.get_or_add_rPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "EFF1F4")
        rpr.append(shd)

    doc.add_paragraph("参考模板", style="Title")
    p = doc.add_paragraph("此文件只用于 pandoc --reference-doc，内容不会被复制。", style="Normal")
    doc.add_heading("一级标题", level=1)
    doc.add_heading("二级标题", level=2)
    doc.add_heading("三级标题", level=3)
    doc.add_paragraph("正文段落示例，包含中文、English 与数字 123。", style="Normal")
    doc.save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "reference.docx")
