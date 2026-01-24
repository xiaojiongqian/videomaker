---
description: 从视频文件生成字幕
allowed-tools: Bash(ffmpeg:*), Bash(python3:*), Read, Write
argument-hint: <视频文件路径>
---

# 视频字幕生成

为指定的视频文件生成字幕。

## 输入

视频文件路径: $ARGUMENTS

## 执行步骤

请按以下步骤为视频生成字幕：

### 1. 验证视频文件
- 确认视频文件 `$ARGUMENTS` 存在
- 使用 ffmpeg 检查视频信息：`ffmpeg -i "$ARGUMENTS" 2>&1 | head -20`

### 2. 提取音频
- 从视频中提取音频文件（WAV 格式，16kHz 采样率，单声道）
- 命令：`ffmpeg -i "$ARGUMENTS" -ar 16000 -ac 1 -c:a pcm_s16le "<输出目录>/audio.wav" -y`
- 输出目录与视频文件同目录

### 3. 生成字幕
使用 Python 和 Whisper 进行语音识别：

```python
import whisper

model = whisper.load_model("base")  # 可选: tiny, base, small, medium, large
result = model.transcribe("audio.wav", language="zh")

# 生成 SRT 格式字幕
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

srt_content = ""
for i, segment in enumerate(result["segments"], 1):
    start = format_timestamp(segment["start"])
    end = format_timestamp(segment["end"])
    text = segment["text"].strip()
    srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"

# 保存字幕文件
with open("output.srt", "w", encoding="utf-8") as f:
    f.write(srt_content)
```

### 4. 输出结果
- 字幕文件保存为与视频同名的 .srt 文件
- 清理临时音频文件
- 告知用户字幕文件的位置

## 注意事项

- 如果 whisper 未安装，先执行：`pip install openai-whisper`
- 对于长视频，使用 `tiny` 或 `base` 模型以加快速度
- 默认识别中文，可根据视频内容调整 language 参数
