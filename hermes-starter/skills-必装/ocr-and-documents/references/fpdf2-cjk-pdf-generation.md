# fpdf2 CJK PDF Generation (WSL)

Generate PDFs with Chinese/Japanese/Korean text using fpdf2 + Windows fonts via WSL.

## Quick Start

```bash
pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple fpdf2 Pillow
```

## Font Registration (WSL → Windows Fonts)

```python
from fpdf import FPDF
import os

fd = "/mnt/c/Windows/Fonts"
pdf = FPDF('P', 'pt', (1010, 1468))  # custom page size in points
pdf.add_font("Hei", "", os.path.join(fd, "msyh.ttc"))      # 微软雅黑
pdf.add_font("Hei", "B", os.path.join(fd, "msyhbd.ttc"))   # 微软雅黑 粗体
pdf.add_font("Song", "", os.path.join(fd, "STSONG.TTF"))   # 宋体
pdf.add_font("Kai", "", os.path.join(fd, "STKAITI.TTF"))   # 楷体
pdf.add_font("FS", "", os.path.join(fd, "STFANGSO.TTF"))   # 仿宋
```

## Chinese Text in Python Source

**PITFALL**: Chinese quotation marks `"` `"` (U+201C, U+201D) look like ASCII `"` to Python. Implicit string concatenation breaks:

```python
# BROKEN - " and " confuse Python's string parser
text = (
    "他说"你好"世界"    # SyntaxError!
)
```

**FIX**: Use JSON intermediate files for CJK-heavy content:

```python
import json
# Write content to JSON (handles Unicode natively)
with open("content.json", "w", encoding="utf-8") as f:
    json.dump({"text": '他说"你好"世界'}, f, ensure_ascii=False)

# Read back in PDF generator
with open("content.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

Or use Unicode escapes: `"\u201c\u4f60\u597d\u201d"` → `"你好"`

## Multi-Column Layout

```python
# 3-column newspaper layout on 1010pt wide page
x1, x2, x3 = 28, 350, 672    # column left edges
cw = 305                       # column width
gutter = 17                    # gap between columns

# Draw article
pdf.set_font("Hei", "B", 16)  # headline
pdf.set_xy(x, y)
pdf.multi_cell(cw, 22, title)

pdf.set_font("Song", "", 11)  # body
pdf.set_text_color(40, 40, 40)
pdf.set_xy(x, y + title_h + 18)
pdf.multi_cell(cw, 17, body)  # 17pt line height
```

## Image Placement

```python
from PIL import Image
im = Image.open(path)
iw, ih = im.size
ratio = iw / ih

# Fit image into box (w x h) preserving aspect ratio
if w / h > ratio:
    draw_h = h - 20   # height-constrained
    draw_w = draw_h * ratio
else:
    draw_w = w - 10   # width-constrained
    draw_h = draw_w / ratio

pdf.image(path, x=box_x + (w - draw_w)/2, y=box_y + 5, w=draw_w, h=draw_h)
```

## JPEG Dimensions Without PIL

```python
import struct
with open(path, 'rb') as f:
    f.seek(163)
    w, h = struct.unpack('>HH', f.read(4))
```

## Design Patterns

- **Divider lines**: `pdf.line(x1, y, x2, y)` with `pdf.set_draw_color(r, g, b)`
- **Filled rectangles**: `pdf.rect(x, y, w, h, 'F')` after `pdf.set_fill_color(r, g, b)`
- **Circles**: `pdf.circle(cx, cy, r, 'F')` or `pdf.ellipse(cx-r, cy-r, 2*r, 2*r, 'DF')`
- **Stars**: `pdf.polygon([(x1,y1), ...], 'F')` — compute 10 points for 5-pointed star
- **Page size**: `FPDF('P', 'pt', (width, height))` — points = mm × 2.835

## Common Page Sizes (points)

| Format | mm | points |
|--------|-----|--------|
| A4 | 210×297 | 595×842 |
| A3 | 297×420 | 842×1190 |
| Broadsheet | ~356×518 | 1010×1468 |
