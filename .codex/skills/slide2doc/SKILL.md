---
name: slide2doc
description: 从 PPT/PPTX/PDF 自动生成图文并茂的 Markdown 文章。Use when user asks `/slide2doc`, asks to turn slides into an article, or needs long-form notes with selected slide images and optional author signature.
---

# Slide2Doc

## Inputs
- Required: source file path (`.ppt`, `.pptx`, `.pdf`).
- Optional: target word count (default `2000`), author (`--author`/`-a`).

## Workflow
1. Parse input arguments and validate file exists.
2. Create output folders beside source file:
   - `doc/`
   - `doc/images/`
3. Convert slides/pages to images.
   - For PPT/PPTX: `soffice --headless --convert-to pdf ...` then `magick -density 200 ...`
   - For PDF: `magick -density 200 ...`
4. Analyze each slide image for role (title/content/summary/transition) and key message.
5. Draft Markdown article with clear narrative flow, not bullet-dump translation of slides.
6. Keep only high-value images (cover, charts, frameworks, key summaries) and reference as `images/slide_XX.png`.
7. Append author footer when provided and save final document.

## Output
- `doc/<source_basename>_sum.md`
- `doc/images/slide_*.png`

## Writing constraints
- Use plain, natural Chinese; avoid rigid template language.
- Make title and opening hook stronger than original slide wording.
- Prefer readability and explanation depth over slide-by-slide restatement.

## Dependencies
- `soffice` (LibreOffice)
- `magick` (ImageMagick)
- `gs` (Ghostscript)

## Detailed reference
- Open `.claude/commands/slide2doc.md` for full style constraints and examples.
