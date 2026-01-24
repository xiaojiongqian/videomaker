#!/usr/bin/env python3
"""使用 Whisper 生成字幕"""
import whisper
import sys

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def main():
    audio_path = "/Users/vik.qian/study/videomaker/video/temp_audio.wav"
    output_path = "/Users/vik.qian/study/videomaker/video/并行长时间使用codex.srt"

    print("加载 Whisper 模型 (base)...")
    model = whisper.load_model("base")

    print("开始语音识别...")
    result = model.transcribe(audio_path, language="zh", verbose=True)

    print(f"\n识别完成，共 {len(result['segments'])} 个片段")

    # 生成 SRT 格式字幕
    srt_content = ""
    for i, segment in enumerate(result["segments"], 1):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = segment["text"].strip()
        srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"

    # 保存字幕文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"\n字幕已保存到: {output_path}")

if __name__ == "__main__":
    main()
