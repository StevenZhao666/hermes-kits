# -*- coding: utf-8 -*-
"""md2pdf: Markdown -> PDF（pandoc 转 Typst，Typst 排版）。

排版由 Typst 完成：中文、数学公式（原生排版，可选中）、表格、代码块、页码。
用法:
    python md2pdf.py 输入.md [输出.pdf] [--open] [--template=自定义.typ]

依赖: pandoc(>=3.1.3) + typst
"""
import glob
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, "style.typ")

# A4 去掉左右页边距后的正文宽约 15cm ≈ 566px(96dpi)
MAX_IMG_PX = 560

IMG_RE = re.compile(r"(!\[([^\]]*)\]\(([^)\s]+)([^)]*)\)(\{[^}]*\})?)")

PANDOC_FROM = (
    "markdown"
    "+pipe_tables+footnotes+task_lists+tex_math_dollars+strikeout"
    "+autolink_bare_uris+backtick_code_blocks+fenced_code_blocks"
    "+implicit_figures+definition_lists"
)


def find_typst():
    exe = shutil.which("typst")
    if exe:
        return exe
    local = os.environ.get("LOCALAPPDATA", "")
    patterns = [
        os.path.join(local, "Microsoft", "WinGet", "Links", "typst.exe"),
        os.path.join(local, "Microsoft", "WinGet", "Packages", "Typst.Typst*", "typst-*", "typst.exe"),
        os.path.join(local, "Microsoft", "WinGet", "Packages", "Typst.Typst*", "typst.exe"),
    ]
    for pat in patterns:
        hits = glob.glob(pat)
        if hits:
            return hits[0]
    return None


def _img_width(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size[0]
    except Exception:
        return None


def prepare_md(md):
    """超过正文宽度的图片自动补 width=100%，避免溢出页面。返回可用路径 + 临时文件。"""
    text = open(md, encoding="utf-8").read()
    base = os.path.dirname(md) or "."
    changed = [False]

    def repl(m):
        whole, alt, src, title, attrs = m.groups()
        if attrs and "width=" in attrs:
            return whole
        if src.startswith(("http://", "https://")):
            return whole
        p = src if os.path.isabs(src) else os.path.join(base, src)
        w = _img_width(p)
        if w and w > MAX_IMG_PX:
            changed[0] = True
            return whole + "{width=100%}"
        return whole

    new = IMG_RE.sub(repl, text)
    if not changed[0]:
        return md, None
    tmp = os.path.join(base, ".md2pdf_" + os.path.basename(md))
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(new)
    return tmp, tmp


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 2

    md = os.path.abspath(args[0])
    if not os.path.isfile(md):
        raise SystemExit(f"找不到文件: {md}")
    out = os.path.abspath(args[1]) if len(args) > 1 else os.path.splitext(md)[0] + ".pdf"

    template = DEFAULT_TEMPLATE
    for f in flags:
        if f.startswith("--template="):
            template = os.path.abspath(f.split("=", 1)[1])

    typst = find_typst()
    if not typst:
        raise SystemExit(
            "缺少 typst。Windows: winget install Typst.Typst；"
            "macOS: brew install typst；其它见 https://typst.app"
        )
    if not shutil.which("pandoc"):
        raise SystemExit("缺少 pandoc。Windows: winget install JohnMacFarlane.Pandoc")

    env = os.environ.copy()
    env["PATH"] = os.path.dirname(typst) + os.pathsep + env.get("PATH", "")

    src, tmp = prepare_md(md)
    cmd = [
        "pandoc", src,
        "-f", PANDOC_FROM,
        "-o", out,
        "--pdf-engine=typst",
        "--template", template,
        "--resource-path", os.path.dirname(md) or ".",
    ]
    proc = subprocess.run(cmd, cwd=os.path.dirname(md) or ".", env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if tmp and os.path.exists(tmp):
        os.remove(tmp)
    if proc.returncode != 0:
        raise SystemExit("转换失败:\n" + (proc.stderr or proc.stdout))

    size = os.path.getsize(out)
    print(f"{out}  ({size/1024:.0f} KB)")
    if "--open" in flags:
        os.startfile(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
