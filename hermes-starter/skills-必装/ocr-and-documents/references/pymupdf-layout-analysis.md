# pymupdf Layout Analysis

Analyze existing PDF layouts to replicate or understand their structure.

## Extract Block Structure

```python
import pymupdf
doc = pymupdf.open("reference.pdf")
for i in range(doc.page_count):
    p = doc[i]
    print(f"Page {i+1}: {p.rect.width:.0f} x {p.rect.height:.0f}")
    blocks = p.get_text('dict')['blocks']
    for b in blocks:
        x0, y0, x1, y1 = b['bbox']
        t = b.get('type', '?')  # 0=text, 1=image
        if t == 0:
            txt = ''.join([s['text'] for s in b.get('lines',[{}])[0].get('spans',[])])[:60]
        elif t == 1:
            txt = '[IMAGE]'
        print(f'  [{t}] x={x0:.0f} y={y0:.0f} w={x1-x0:.0f} h={y1-y0:.0f} {txt}')
```

This reveals:
- Page dimensions (for matching target size)
- Column widths and positions (from text block x-coordinates)
- Image positions and sizes
- Text flow order and line breaks
- Header/footer zones (y near 0 or near page bottom)

## Use Cases

- Replicating newspaper/magazine column layouts
- Understanding multi-column text flow
- Extracting image placement patterns for template matching
- Measuring margins and gutters from an existing design

## Common Patterns

- Newspaper columns typically 170-350pt wide with 15-20pt gutters
- Headers at y=0-100, footers at bottom 30pt
- Body text in 9-11pt range, headlines 16-38pt
- Images often span 1-3 column widths
