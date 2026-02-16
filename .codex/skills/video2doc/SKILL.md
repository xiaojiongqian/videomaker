---
name: video2doc
description: 从视频和字幕生成图文并茂的 Markdown 总结文档，并智能提取/筛选配图。Use when user asks `/video2doc`, asks to convert a video into structured article notes, or needs optional `--crop` / `--annotate` image enhancement.
---

# Video2Doc

## Inputs
- Required: video path.
- Optional: word count (default `2000`), author (`--author`/`-a`), `--crop`, `--annotate`.

## Workflow
1. Parse arguments and create `doc/` and `doc/images/` beside the source video.
2. Ensure subtitle exists; if missing, run the `subtitle` skill.
3. Parse subtitle and extract full text context.
4. Generate summary draft prompt with:
   - `python3 scripts/generate_summary.py "$SRT" "$WORD_COUNT"`
5. Write Markdown article in plain-language style (clear, story-like, no boilerplate phrasing).
6. Extract candidate keyframes:
   - `python3 scripts/extract_frames.py "$VIDEO" "$DOC_DIR/images" "$SRT"`
7. Review each image by actual visual content (not by timestamp guess), then keep/rename only useful images.
8. Insert selected images into matching sections and append author footer when provided.
9. Apply crop/annotation only when user explicitly enables those flags.

## Output
- `doc/<video_basename>_sum.md`
- `doc/images/*` (filtered screenshots)

## Quality rules
- Prefer relevance over quantity; do not force images into unrelated sections.
- Remove blurry, transition, duplicate, or privacy-sensitive screenshots.
- Keep document structure coherent: background -> solution -> practice -> summary.

## Implementation files
- `scripts/generate_summary.py`
- `scripts/extract_frames.py`
- `scripts/analyze_screenshots.py` (analysis criteria helper)

## Detailed reference
- Open `.claude/commands/video2doc.md` for complete decision rules and crop/annotate examples.
