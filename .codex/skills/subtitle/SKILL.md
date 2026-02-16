---
name: subtitle
description: 从视频提取音频并生成同名 SRT 字幕。Use when user asks `/subtitle`, asks to transcribe video/audio, or upstream workflows (`smart-cut`, `video2doc`, `dub-en`) are blocked by missing subtitle files.
---

# Subtitle

## Inputs
- Required: video file path.
- Optional: language (default `zh`) and Whisper model (default `base`).

## Workflow
1. Validate that the input file exists.
2. Inspect media briefly:
   - `ffmpeg -i "$VIDEO" 2>&1 | head -20`
3. Extract temporary mono WAV audio:
   - `ffmpeg -i "$VIDEO" -ar 16000 -ac 1 -c:a pcm_s16le "$TMP_WAV" -y`
4. Run Whisper transcription and convert segments to SRT timestamps.
5. Save subtitle as `<video_basename>.srt` in the same directory as the video.
6. Delete temporary audio artifacts.

## Quality checks
- Ensure SRT index starts at 1 and increases monotonically.
- Ensure timestamp format is `HH:MM:SS,mmm` and every segment has non-empty text.
- If the output is sparse or empty, retry with another model (`tiny`, `base`, `small`) or language hint.

## Dependencies
- `ffmpeg`
- `python3`
- `openai-whisper` (install with `pip install openai-whisper` if missing)

## Detailed reference
- Open `.claude/commands/subtitle.md` for the original command-level specification.
