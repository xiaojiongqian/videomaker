---
name: dub-en
description: 将中文讲解视频生成英文配音版本，并尽量保留原说话人音色（voice cloning）。Use when user asks `/dub-en`, asks for Chinese-to-English dubbing, bilingual tracks/subtitles, or voice-clone style English narration.
---

# Dub En

## Inputs
- Required: video path.
- Optional: `--engine` (`elevenlabs`, `coqui`, `openai`), `--keep-original`.

## Workflow
1. Parse arguments and validate input video exists.
2. Extract source audio and a clean 30-60s voice sample for cloning.
3. Ensure Chinese subtitle exists; if missing, run `subtitle` skill.
4. Merge short subtitle chunks into longer semantic units to improve translation/TTS continuity.
5. Translate subtitle to natural spoken English with full-context coherence (not line-by-line literal translation).
6. Generate English speech with selected engine:
   - `elevenlabs`: best quality, needs API key
   - `coqui`: local open-source option
   - `openai`/edge fallback: no cloning or weaker cloning
7. Align generated segments to timeline and normalize volume against original audio.
8. Mux final outputs:
   - bilingual MP4 (CN+EN audio tracks, CN+EN subtitles)
   - optional EN-only MP4
   - English subtitle and translation mapping file

## Output
- `<video_basename>_multilang.mp4`
- `<video_basename>_en.mp4` (optional)
- `<video_basename>_en.srt`
- `<video_basename>_translation.json`

## Quality checks
- Keep terminology consistent for technical words.
- Keep speaking rhythm close to original pacing.
- Check output loudness and clip-free audio.
- Warn about API quotas/cost and voice-clone legal constraints.

## Dependencies
- `ffmpeg`
- `openai-whisper`
- TTS engine dependencies (`requests` for ElevenLabs, `TTS` for Coqui)

## Detailed reference
- Open `.claude/commands/dub-en.md` for engine-specific implementation and muxing details.
