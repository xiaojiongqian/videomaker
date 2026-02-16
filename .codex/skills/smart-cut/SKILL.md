---
name: smart-cut
description: 智能剪辑视频并提取主要观点，优先移除空白/语气词/重复内容，再按需加速到 1.5x。Use when user asks `/smart-cut`, asks to shorten a talking-head video, or requests percentage-based duration compression with subtitle sync.
---

# Smart Cut

## Inputs
- Required: video file path.
- Optional: target reduction percentage (for example `30%`, `50%`).

## Workflow
1. Validate the video path and parse reduction target to `0.0-1.0` ratio.
2. Ensure subtitle exists (`<video_basename>.srt`); if missing, run the `subtitle` skill first.
3. Analyze subtitle with layered strategy:
   - `python3 scripts/smart_cut_analysis_v2.py "$SRT" [target_reduction_ratio]`
4. Execute FFmpeg cut plan:
   - `python3 scripts/smart_cut_execute_v2.py "${BASE}_cut_result.json" "$VIDEO"`
5. Produce key-point summary from kept high-importance segments printed by analysis.
6. For strict sync requirements, regenerate subtitle on final cut video and replace adjusted subtitle.

## Output
- `<video_basename>_cut.mp4`
- `<video_basename>_cut.srt`
- `<video_basename>_cut_result.json`

## Validation
- Check output file exists and duration is reasonable.
- Verify A/V sync with `ffprobe`; keep audio/video duration difference under ~0.5 seconds.
- If target compression is aggressive, explain trade-off between content loss and speed-up.

## Implementation files
- `scripts/smart_cut_analysis_v2.py`
- `scripts/smart_cut_execute_v2.py`

## Detailed reference
- Open `.claude/commands/smart-cut.md` when full heuristics or hard-subtitle details are needed.
