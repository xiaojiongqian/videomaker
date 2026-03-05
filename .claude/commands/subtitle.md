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

**根据语言选择 ASR 引擎**：
- **中文视频** → 使用 FunASR（阿里达摩院，中文识别更准确）
- **其他语言** → 使用 Whisper（OpenAI，多语言支持）

#### 3a. 中文视频：使用 FunASR

```python
from funasr import AutoModel

model = AutoModel(
    model="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    vad_model="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
    punc_model="iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
)

res = model.generate(input="<视频文件路径>", batch_size_s=300)

item = res[0]
full_text = item["text"]
timestamps = item["timestamp"]  # 每个非标点字符的 [start_ms, end_ms]

# 注意：标点符号由 punc_model 后加，没有对应时间戳
# 需要跳过标点来对齐 timestamps
punc_chars = set("。！？；，、：""''（）《》【】…—·!?,;:\"'()[]{}.-")

ts_idx = 0
char_ts = []
for ch in full_text:
    if ch in punc_chars:
        char_ts.append(None)
    else:
        if ts_idx < len(timestamps):
            char_ts.append(timestamps[ts_idx])
            ts_idx += 1
        else:
            char_ts.append(None)

# 按标点断句生成 SRT 段落
# 句号/问号/感叹号处断句，逗号处超过 18 字也断句
```

#### 3b. 其他语言：使用 Whisper

```python
import whisper

model = whisper.load_model("medium")  # 可选: tiny, base, small, medium, large
result = model.transcribe("audio.wav", language="<语言代码>")

# 生成 SRT 格式字幕
for i, segment in enumerate(result["segments"], 1):
    # segment 自带 start/end 时间戳（秒）
    pass
```

### 4. 输出结果
- 字幕文件保存为与视频同名的 .srt 文件
- 清理临时音频文件
- 告知用户字幕文件的位置

## 注意事项

- 中文视频必须使用 FunASR，识别准确率显著高于 Whisper
- FunASR 的 timestamp 是词级别的，标点符号没有时间戳，需要用标点感知对齐
- 其他语言使用 Whisper，如未安装先执行：`pip install openai-whisper`
- 对于长视频，Whisper 使用 `base` 或 `small` 模型以加快速度
