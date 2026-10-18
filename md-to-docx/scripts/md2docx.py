# -*- coding: utf-8 -*-
"""md2docx: Markdown -> Word(.docx)，公式转 Word 原生公式，表格加边框，页脚页码。

用法:
    python md2docx.py 输入.md [输出.docx] [--open] [--no-page-number]
                           [--template 自定义reference.docx]

依赖: pandoc (>=2.11) + python-docx
"""
import os
import subprocess
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, "reference.docx")

PANDOC_FROM = (
    "markdown"
    "+pipe_tables+footnotes+task_lists+tex_math_dollars+strikeout"
    "+autolink_bare_uris+backtick_code_blocks+fenced_code_blocks"
    "+implicit_figures+definition_lists"
)


def run_pandoc(md_path, out_path, template):
    cmd = [
        "pandoc", md_path,
        "-f", PANDOC_FROM,
        "-t", "docx",
        "--reference-doc", template,
        "--resource-path", os.path.dirname(os.path.abspath(md_path)) or ".",
        "-o", out_path,
    ]
    proc = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(md_path)) or ".",
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit("pandoc 失败:\n" + (proc.stderr or proc.stdout))


def _border(el, edges=("top", "left", "bottom", "right", "insideH", "insideV"),
            sz=4, color="999999"):
    tblpr = el.find(qn("w:tblPr"))
    if tblpr is None:
        tblpr = OxmlElement("w:tblPr")
        el.insert(0, tblpr)
    borders = OxmlElement("w:tblBorders")
    for edge in edges:
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), color)
        borders.append(e)
    tblpr.append(borders)


def _shade_cell(cell, fill="F2F4F7"):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def style_tables(doc):
    for table in doc.tables:
        _border(table._tbl)
        table.autofit = True
        if table.rows:
            for cell in table.rows[0].cells:
                _shade_cell(cell)
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.bold = True
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_page_number(doc):
    for section in doc.sections:
        p = section.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        for instr, kind in (("begin", None), (None, "PAGE"), ("end", None)):
            if kind:
                fld = OxmlElement("w:instrText")
                fld.set(qn("xml:space"), "preserve")
                fld.text = f" {kind} "
                run._r.append(fld)
            else:
                fld = OxmlElement("w:fldChar")
                fld.set(qn("w:fldCharType"), instr)
                run._r.append(fld)
        run.font.size = Pt(9)


def _para_shade(p, fill="F4F5F7"):
    ppr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def _para_left_border(p, color="C8CDD4", sz=18):
    ppr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), str(sz))
    left.set(qn("w:space"), "8")
    left.set(qn("w:color"), color)
    pbdr.append(left)
    ppr.append(pbdr)


def ensure_code_block_look(doc):
    for p in doc.paragraphs:
        name = p.style.name if p.style is not None else ""
        if name == "Source Code":
            pf = p.paragraph_format
            pf.left_indent = Cm(0.5)
            pf.right_indent = Cm(0.3)
            pf.space_before = Pt(0)
            pf.space_after = Pt(0)
            _para_shade(p)
        elif name == "Block Text":
            pf = p.paragraph_format
            pf.left_indent = Cm(0.8)
            pf.right_indent = Cm(0.4)
            _para_left_border(p)
            _para_shade(p, "FAFAFA")

    # 行内代码：给 Verbatim Char 加浅底纹
    for style in doc.styles:
        if style.name == "Verbatim Char":
            rpr = style.element.get_or_add_rPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "EFF1F4")
            rpr.append(shd)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 2
    md = os.path.abspath(args[0])
    if not os.path.isfile(md):
        raise SystemExit(f"找不到文件: {md}")
    out = os.path.abspath(args[1]) if len(args) > 1 else os.path.splitext(md)[0] + ".docx"
    template = DEFAULT_TEMPLATE
    for f in flags:
        if f.startswith("--template="):
            template = os.path.abspath(f.split("=", 1)[1])
    if not os.path.isfile(template):
        raise SystemExit(f"缺少模板 {template}，先跑 make_template.py")

    run_pandoc(md, out, template)
    doc = Document(out)
    style_tables(doc)
    ensure_code_block_look(doc)
    if "--no-page-number" not in flags:
        add_page_number(doc)
    doc.save(out)
    print(out)
    if "--open" in flags:
        os.startfile(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
