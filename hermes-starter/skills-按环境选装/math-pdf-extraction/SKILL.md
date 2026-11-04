---
name: math-pdf-extraction
description: "Accurately read math content from exam/worksheet PDFs (esp. Chinese 试卷 from jyeoo/菁优网) — text extraction garbles formulas, so render pages to images and read with vision before solving."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Math, OCR, Vision, Exam, Chinese]
    related_skills: [ocr-and-documents]
---

# Math PDF Extraction (formula-safe)

Use when asked to solve, transcribe, or analyze math problems from a PDF worksheet/exam.

## Core rule

**Never trust raw text extraction for math formulas.** Chinese exam PDFs (jyeoo.com, 菁优网, school 期中/期末 papers) mangle fractions, sub/superscripts, and exponents into `�` or reordered glyphs (e.g. `求 3 2 −�的最大值` was actually `求 (3/2)b − c 的最大值`). Solving from mangled text = solving the wrong problem.

## Workflow

1. Extract text with pymupdf first to locate the target problems (see `ocr-and-documents` for install; on this host use the ASCII-path venv, `C:/pdfenv/venv/Scripts/python.exe`):
   ```python
   import pymupdf
   doc = pymupdf.open(path)
   for i, page in enumerate(doc):
       print(f"===== PAGE {i+1} ====="); print(page.get_text())
   ```
2. For every problem containing formulas (fractions, powers, subscripts, √, ∑), render that page at 2.5x and read it with `vision_analyze`:
   ```python
   pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5))
   pix.save("page.png")
   ```
   Ask vision to transcribe the exact expression verbatim (上下标、分数、指数).
3. Only then solve. Show the verification step (代回验证) for each answer — exam answers should be checkable.

## Solving conventions for 九年级代数综合 (quadratic functions)

- x-axis intersections → use Vieta (x₁+x₂=−b, x₁·x₂=c) rather than solving roots explicitly.
- Max/min on a variable interval [a, t] → split cases on whether the vertex lies inside the interval; check each case for feasibility, don't assume t lands right of the vertex.
- "最大值与最小值的差" → |max − min|, verify with the three candidate points f(a), f(vertex), f(t).
- Vertical distance between parabola and line at x=t → simplifies to absolute-value equation in t; keep both roots unless the domain excludes them.

## Pitfalls

- Text extraction often *looks* complete for the problem stem but garbles only the key formula — scan for `�` or suspicious spacing/number runs as the signal to render the page.
- One render per page is enough; don't render all 20+ pages, just the pages with the requested problems.
- On Chinese-locale Windows, `uv run --with pymupdf` may crash with a GBK UnicodeDecodeError — pre-built ASCII-path venv at `C:/pdfenv/venv` already has pymupdf.
