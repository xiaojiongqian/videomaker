# 视频英文配音（声音克隆版）

将中文讲解的视频转换为英文配音版本，**保留原说话人的音色特征**。

## 核心技术

使用 **声音克隆 (Voice Cloning)** 技术，从原视频中提取说话人的声音特征，然后用该声音朗读英文翻译内容。

**支持的声音克隆引擎：**
| 引擎 | 特点 | 费用 |
|------|------|------|
| **ElevenLabs** | 最佳质量，即时克隆 | 免费额度 10k 字符/月 |
| **Coqui XTTS** | 开源，本地运行 | 免费 |
| **OpenAI TTS** | 高质量但不支持克隆 | 备选方案 |

## 输入参数

```
$ARGUMENTS = 视频文件路径 [--engine 引擎] [--keep-original]
```

**参数说明：**
- `视频文件路径`：必需，要处理的视频文件
- `--engine` / `-e`：声音克隆引擎（elevenlabs / coqui / openai），默认 elevenlabs
- `--keep-original`：保留原始音轨作为背景音

## 工作流程

### 1. 解析输入参数

```python
import os

args = "$ARGUMENTS".strip().split()
video_path = None
engine = "elevenlabs"  # 默认使用 ElevenLabs
keep_original = False

i = 0
while i < len(args):
    part = args[i]
    if part in ['--engine', '-e'] and i + 1 < len(args):
        engine = args[i + 1].lower()
        i += 2
    elif part == '--keep-original':
        keep_original = True
        i += 1
    elif not part.startswith('-'):
        video_path = part
        i += 1
    else:
        i += 1

if not video_path or not os.path.exists(video_path):
    raise FileNotFoundError(f"视频文件不存在: {video_path}")
```

### 2. 提取原始音频样本

从视频中提取一段清晰的语音样本用于声音克隆：

```bash
# 提取完整音频
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 original_audio.wav

# 提取 30-60 秒的清晰语音片段作为克隆样本
ffmpeg -i original_audio.wav -ss 10 -t 30 voice_sample.wav
```

**样本选择策略：**
```python
def select_best_voice_sample(audio_path, subtitle_segments):
    """
    选择最佳的声音样本片段

    标准：
    1. 连续说话时间 > 5秒
    2. 无背景噪音
    3. 语速适中
    4. 音量稳定
    """
    best_segments = []

    for seg in subtitle_segments:
        duration = seg['end_sec'] - seg['start_sec']
        if duration >= 5:
            # 检查音频质量
            quality_score = analyze_audio_quality(audio_path, seg['start_sec'], seg['end_sec'])
            best_segments.append({
                'segment': seg,
                'score': quality_score
            })

    # 选择得分最高的片段
    best_segments.sort(key=lambda x: x['score'], reverse=True)

    # 合并前几个最佳片段，总时长约 30 秒
    selected = []
    total_duration = 0
    for item in best_segments:
        if total_duration >= 30:
            break
        selected.append(item['segment'])
        total_duration += item['segment']['end_sec'] - item['segment']['start_sec']

    return selected
```

### 3. 生成/获取中文字幕

检查是否已有字幕文件，如果没有则调用 `/subtitle` 生成。

### 4. 翻译字幕为英文

使用 Claude 进行高质量翻译：

```
翻译要求：
1. 保持原意，使用自然的英语口语表达
2. 技术术语准确（Git Worktree, MCP, Claude Code 等保持原样）
3. 考虑朗读节奏，翻译后的英文朗读时间应接近原中文
4. 适当简化过长的句子，便于配音
5. 保持说话人的语气和风格
```

### 5. 声音克隆 + 英文语音合成

#### 方案 A：ElevenLabs（推荐，最佳质量）

```python
import requests

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')

def clone_voice_elevenlabs(voice_sample_path, voice_name="cloned_voice"):
    """
    使用 ElevenLabs 创建克隆声音
    """
    url = "https://api.elevenlabs.io/v1/voices/add"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }

    with open(voice_sample_path, 'rb') as f:
        files = {
            'files': (voice_sample_path, f, 'audio/wav')
        }
        data = {
            'name': voice_name,
            'description': 'Cloned voice for video dubbing'
        }
        response = requests.post(url, headers=headers, files=files, data=data)

    return response.json()['voice_id']


def generate_speech_elevenlabs(text, voice_id, output_path):
    """
    使用克隆的声音生成英文语音
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # 支持跨语言
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, headers=headers, json=data)

    with open(output_path, 'wb') as f:
        f.write(response.content)
```

#### 方案 B：Coqui XTTS（开源免费）

```python
# 安装
# pip install TTS

from TTS.api import TTS

def clone_and_speak_coqui(text, voice_sample_path, output_path, language="en"):
    """
    使用 Coqui XTTS 进行声音克隆和语音合成
    """
    # 加载 XTTS 模型
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    # 使用声音样本克隆并生成英文语音
    tts.tts_to_file(
        text=text,
        file_path=output_path,
        speaker_wav=voice_sample_path,  # 用于克隆的声音样本
        language=language
    )
```

### 6. 音频时间对齐

```python
def align_dubbed_audio(segments, dubbed_files, original_duration):
    """
    对齐配音音频到原始时间轴

    策略：
    1. 计算每段配音的实际时长
    2. 如果配音比原时长短：添加静音填充
    3. 如果配音比原时长长：
       - 轻微加速（最多 1.2 倍，保持自然）
       - 如果仍然过长，调整翻译使其更简洁
    """
    aligned_audio = []

    for seg, dubbed_file in zip(segments, dubbed_files):
        target_duration = seg['end_sec'] - seg['start_sec']
        actual_duration = get_audio_duration(dubbed_file)

        if actual_duration <= target_duration:
            # 添加静音
            silence = target_duration - actual_duration
            aligned = pad_with_silence(dubbed_file, silence)
        elif actual_duration <= target_duration * 1.2:
            # 轻微加速
            speed = actual_duration / target_duration
            aligned = adjust_speed(dubbed_file, speed)
        else:
            # 需要重新翻译为更简洁的版本
            print(f"警告: 片段 {seg['index']} 过长，需要简化翻译")
            # 触发重新翻译
            aligned = handle_long_segment(seg, dubbed_file, target_duration)

        aligned_audio.append({
            'file': aligned,
            'start': seg['start_sec'],
            'duration': target_duration
        })

    return aligned_audio
```

### 7. 合成最终视频

```bash
# 合并所有配音片段
ffmpeg -f concat -safe 0 -i segments.txt -c copy dubbed_audio.wav

# 替换原视频音轨
ffmpeg -i original.mp4 -i dubbed_audio.wav \
    -c:v copy -map 0:v:0 -map 1:a:0 \
    output_en.mp4

# 如果 --keep-original：混合原音轨（降低音量作为背景）
ffmpeg -i original.mp4 -i dubbed_audio.wav \
    -filter_complex "[0:a]volume=0.15[bg];[1:a]volume=1.0[dub];[dub][bg]amix=inputs=2:duration=longest" \
    -c:v copy \
    output_en.mp4
```

### 8. 生成英文字幕

```python
def write_english_srt(segments, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(f"{seg['index']}\n")
            f.write(f"{seg['start']} --> {seg['end']}\n")
            f.write(f"{seg['translated']}\n\n")
```

## 输出文件

```
video.mp4              # 原视频
video_en.mp4           # 英文配音版本（克隆声音）
video_en.srt           # 英文字幕
video_translation.json # 中英对照翻译
```

## 使用示例

```bash
# 基本用法（使用 ElevenLabs）
/dub-en video/example.mp4

# 使用开源 Coqui XTTS（免费）
/dub-en video/example.mp4 --engine coqui

# 保留原音轨作为背景
/dub-en video/example.mp4 --keep-original
```

## 环境配置

### ElevenLabs（推荐）

```bash
# 注册获取 API Key: https://elevenlabs.io
export ELEVENLABS_API_KEY="your_api_key"

# 安装依赖
pip install requests
```

### Coqui XTTS（开源）

```bash
# 安装 Coqui TTS
pip install TTS

# 首次运行会自动下载模型（约 2GB）
```

### 通用依赖

```bash
# FFmpeg
brew install ffmpeg  # macOS

# Whisper（字幕生成）
pip install openai-whisper
```

## 注意事项

1. **声音样本质量**：克隆效果取决于原始声音样本的清晰度
2. **API 限制**：ElevenLabs 免费版每月 10,000 字符
3. **处理时间**：声音克隆 + 合成需要较长时间
4. **版权问题**：确保有权使用原视频进行配音
5. **效果预期**：克隆声音会有原说话人的特征，但不会完全相同

## 完整工作流程

```
1. 解析参数，验证视频文件
2. 提取原始音频
3. 选择最佳声音样本片段（约30秒清晰语音）
4. 检查/生成中文字幕
5. 使用 Claude 翻译为自然的英文
6. 创建克隆声音（ElevenLabs/Coqui）
7. 逐段生成英文配音
8. 对齐音频时间轴
9. 合成最终音频
10. 替换/混合原视频音轨
11. 输出英文字幕
12. 清理临时文件和克隆声音（可选保留）
```
