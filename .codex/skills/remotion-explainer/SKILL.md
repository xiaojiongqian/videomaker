---
name: remotion-explainer
description: 基于 Remotion 生成“左侧原视频 + 右侧解释动画”的分屏讲解视频。Use when the user wants to turn an existing video, SRT, script.md, and optional SVG/PNG images into a synchronized explainer render with animated text and vector graphics.
---

# Remotion Explainer

## Inputs
- Required: source video path.
- Required: subtitle path (`.srt`).
- Required: content script path (`script.md` or another Markdown outline).
- Optional: image directory containing SVG/PNG/JPG assets.
- Optional: output path, fps, width, height, video panel ratio.

## Workflow
1. Validate the video, SRT, and script paths.
2. If the subtitle is missing, run the `subtitle` skill first.
3. Use the Remotion project under `video/remotion-explainer/`.
4. For interactive timing checks, run:
   - `cd video/remotion-explainer && npm run studio`
5. For final rendering, run:
   - `cd video/remotion-explainer && node render/render.mjs --video "<video>" --srt "<srt>" --script "<script>" --out "<out>" [--images-dir "<images-dir>"]`

## Script Contract
- Prefer one Markdown section per explanation segment.
- Supported headings: `#` and `##`.
- Supported bullets: lines starting with `- `.
- Optional explicit timing:
  - `@range 00:01:05-00:01:30`
- Optional per-scene asset:
  - `![diagram](./doc/images/example.svg)`
- If no `@range` is provided, the renderer distributes sections across the full video duration.
- If no scene asset is provided, files from `--images-dir` are assigned in order.

## Output
- A split-screen MP4 where:
  - left panel shows the original video,
  - right panel shows synchronized title, bullets, optional SVG/image, and live subtitle excerpt.
- A render manifest JSON is written into `video/remotion-explainer/public/jobs/<job-id>/input-props.json`.

## Validation
- Confirm the rendered output exists.
- Confirm the number of scenes is sensible relative to the script sections.
- Spot-check that scene timing and subtitle timing line up.

## Notes
- The current scaffold focuses on deterministic timing and reusable structure.
- If the user wants richer motion design, extend `src/SplitExplainer.tsx` rather than rewriting the pipeline.
