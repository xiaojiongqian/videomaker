# 视频英文配音（声音克隆版）

将中文讲解的视频转换为英文配音版本，**保留原说话人的音色特征**。

## 核心技术

使用 **声音克隆 (Voice Cloning)** 技术，从原视频中提取说话人的声音特征，然后用该声音朗读英文翻译内容。

**支持的声音克隆引擎：**
| 引擎 | 特点 | 费用 |
|------|------|------|
| **Edge TTS** | 微软免费TTS，质量好 | 免费（推荐） |
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

### 4. 字幕预处理与合并（关键优化步骤）

**问题**：原始字幕通常按短句分段，直接翻译会导致：
- 句子不连贯，缺乏上下文
- TTS 输出断断续续，不自然
- 语法不完整

**解决方案**：智能合并相邻字幕段落

```python
def merge_subtitle_segments(segments, max_duration=8.0, max_gap=1.0):
    """
    智能合并字幕段落，生成更自然的句子单元

    参数：
    - max_duration: 合并后最大时长（秒），建议 6-10 秒
    - max_gap: 允许合并的最大间隔（秒），超过则不合并

    合并策略：
    1. 相邻段落间隔 < max_gap 秒时考虑合并
    2. 合并后总时长 < max_duration
    3. 检测句子边界（句号、问号、感叹号）
    4. 保持语义完整性
    """
    merged = []
    current_group = []
    current_start = None
    current_text = []

    for i, seg in enumerate(segments):
        if not current_group:
            # 开始新组
            current_group = [seg]
            current_start = seg['start_sec']
            current_text = [seg['text']]
        else:
            # 检查是否可以合并
            gap = seg['start_sec'] - current_group[-1]['end_sec']
            total_duration = seg['end_sec'] - current_start

            # 检查上一段是否以句子结束符结尾
            last_text = current_text[-1].strip()
            ends_sentence = last_text.endswith(('。', '！', '？', '.', '!', '?'))

            if gap <= max_gap and total_duration <= max_duration and not ends_sentence:
                # 合并
                current_group.append(seg)
                current_text.append(seg['text'])
            else:
                # 保存当前组，开始新组
                merged.append({
                    'index': len(merged) + 1,
                    'start_sec': current_start,
                    'end_sec': current_group[-1]['end_sec'],
                    'duration': current_group[-1]['end_sec'] - current_start,
                    'text': ' '.join(current_text),
                    'original_segments': current_group
                })
                current_group = [seg]
                current_start = seg['start_sec']
                current_text = [seg['text']]

    # 处理最后一组
    if current_group:
        merged.append({
            'index': len(merged) + 1,
            'start_sec': current_start,
            'end_sec': current_group[-1]['end_sec'],
            'duration': current_group[-1]['end_sec'] - current_start,
            'text': ' '.join(current_text),
            'original_segments': current_group
        })

    return merged
```

### 5. 翻译字幕为英文

使用 Claude 进行高质量翻译，**必须整体翻译以保持连贯性**：

```
翻译要求（重要）：

【连贯性要求】
1. 将所有字幕作为一个整体来理解，而非逐句翻译
2. 保持上下文连贯，前后句子要有逻辑衔接
3. 使用适当的连接词（however, therefore, so, then 等）
4. 避免重复的句式开头

【语言质量】
5. 使用自然的英语口语表达，避免翻译腔
6. 修正原文中的语病和口误（口语中常见）
7. 简化冗长或重复的表达
8. 确保语法正确、句子完整

【技术准确性】
9. 技术术语保持准确：
   - Git Worktree → Git Worktree
   - MCP → MCP
   - Claude Code → Claude Code
   - Playwright → Playwright
   - PR → PR (Pull Request)
   - Full Access Mode → Full Access Mode

【TTS 优化】
10. 考虑朗读节奏，翻译后的英文朗读时间应接近原中文
11. 避免过长的句子（建议每句 < 20 词）
12. 适当断句，在自然停顿处分割
13. 避免难以发音的词汇组合

【输出格式】
- 每个合并后的段落对应一条翻译
- 保持段落编号对应
- 如果一个段落翻译后过长，可以在输出中用 | 分隔建议的断句点
```

**翻译示例**：

原文（合并后）：
```
今天要躺一個問題 當大家用Cloud Code或者 Collects等工具 做Web Code的時候 如何提高效率
```

翻译：
```
Today I want to discuss a topic. When using Claude Code or Codex and similar tools for Vibe Coding, how can we improve efficiency?
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

#### 7.1 音量检测与标准化（关键步骤）

**问题**：TTS 生成的音频通常音量偏低，需要标准化到与原视频一致的音量。

```bash
# 检测原视频音量
ffmpeg -i original.mp4 -af "volumedetect" -vn -f null - 2>&1 | grep mean_volume
# 输出示例: mean_volume: -28.0 dB

# 检测配音音量
ffmpeg -i dubbed_audio.wav -af "volumedetect" -vn -f null - 2>&1 | grep mean_volume
# 输出示例: mean_volume: -47.6 dB

# 计算需要增加的音量
# volume_boost = original_mean - dubbed_mean = -28.0 - (-47.6) = 19.6 dB
```

```python
def normalize_audio_volume(input_path, output_path, target_db=-25.0):
    """
    标准化音频音量到目标分贝

    参数：
    - target_db: 目标平均音量，建议 -25 到 -20 dB（正常说话音量）
    """
    import subprocess
    import re

    # 检测当前音量
    cmd = ['ffmpeg', '-i', input_path, '-af', 'volumedetect', '-vn', '-f', 'null', '-']
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 解析平均音量
    match = re.search(r'mean_volume: ([-\d.]+) dB', result.stderr)
    if match:
        current_db = float(match.group(1))
        boost_db = target_db - current_db

        # 应用音量调整
        cmd = [
            'ffmpeg', '-i', input_path,
            '-af', f'volume={boost_db}dB',
            '-y', output_path
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"音量调整: {current_db:.1f} dB → {target_db:.1f} dB (增加 {boost_db:.1f} dB)")
    else:
        # 无法检测，使用默认增益
        cmd = ['ffmpeg', '-i', input_path, '-af', 'volume=15dB', '-y', output_path]
        subprocess.run(cmd, capture_output=True)
        print("使用默认音量增益: +15 dB")

    return output_path


def match_original_volume(original_video, dubbed_audio, output_path):
    """
    将配音音量匹配到原视频音量
    """
    import subprocess
    import re

    def get_mean_volume(file_path):
        cmd = ['ffmpeg', '-i', file_path, '-af', 'volumedetect', '-vn', '-f', 'null', '-']
        result = subprocess.run(cmd, capture_output=True, text=True)
        match = re.search(r'mean_volume: ([-\d.]+) dB', result.stderr)
        return float(match.group(1)) if match else -30.0

    original_vol = get_mean_volume(original_video)
    dubbed_vol = get_mean_volume(dubbed_audio)

    boost_db = original_vol - dubbed_vol
    # 限制最大增益，避免失真
    boost_db = min(boost_db, 25.0)

    print(f"原视频音量: {original_vol:.1f} dB")
    print(f"配音音量: {dubbed_vol:.1f} dB")
    print(f"应用增益: {boost_db:.1f} dB")

    cmd = [
        'ffmpeg', '-i', dubbed_audio,
        '-af', f'volume={boost_db}dB',
        '-y', output_path
    ]
    subprocess.run(cmd, capture_output=True)

    return output_path
```

#### 7.2 合并音频片段

```bash
# 合并所有配音片段
ffmpeg -f concat -safe 0 -i segments.txt -c copy dubbed_audio.wav
```

#### 7.3 生成多语言 MP4（推荐输出格式）

将中英文音轨和字幕整合到一个 MP4 文件中，播放时可自由切换：

```bash
# 生成多语言版本（中英双音轨 + 中英双字幕）
ffmpeg -i original.mp4 \
  -i dubbed_audio_normalized.wav \
  -i chinese_subtitles.srt \
  -i english_subtitles.srt \
  -map 0:v -map 0:a -map 1:a -map 2 -map 3 \
  -c:v copy -c:a aac -c:s mov_text \
  -metadata:s:a:0 language=chi -metadata:s:a:0 title="中文 (原声)" \
  -metadata:s:a:1 language=eng -metadata:s:a:1 title="English (Dubbed)" \
  -metadata:s:s:0 language=chi -metadata:s:s:0 title="中文字幕" \
  -metadata:s:s:1 language=eng -metadata:s:s:1 title="English Subtitles" \
  -y output_multilang.mp4
```

```python
def create_multilang_video(original_video, dubbed_audio, chinese_srt, english_srt, output_path):
    """
    创建多语言视频文件

    包含：
    - 原视频画面
    - 中文原声音轨
    - 英文配音音轨
    - 中文字幕
    - 英文字幕
    """
    import subprocess

    cmd = [
        'ffmpeg',
        '-i', original_video,
        '-i', dubbed_audio,
        '-i', chinese_srt,
        '-i', english_srt,
        '-map', '0:v',      # 视频轨道
        '-map', '0:a',      # 中文音轨
        '-map', '1:a',      # 英文音轨
        '-map', '2',        # 中文字幕
        '-map', '3',        # 英文字幕
        '-c:v', 'copy',     # 视频直接复制
        '-c:a', 'aac',      # 音频转 AAC
        '-c:s', 'mov_text', # 字幕格式
        # 中文音轨元数据
        '-metadata:s:a:0', 'language=chi',
        '-metadata:s:a:0', 'title=中文 (原声)',
        # 英文音轨元数据
        '-metadata:s:a:1', 'language=eng',
        '-metadata:s:a:1', 'title=English (Dubbed)',
        # 中文字幕元数据
        '-metadata:s:s:0', 'language=chi',
        '-metadata:s:s:0', 'title=中文字幕',
        # 英文字幕元数据
        '-metadata:s:s:1', 'language=eng',
        '-metadata:s:s:1', 'title=English Subtitles',
        '-y', output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"多语言视频已生成: {output_path}")
        print("包含: 中英双音轨 + 中英双字幕")
    else:
        print(f"生成失败: {result.stderr}")

    return result.returncode == 0
```

**播放器支持**：
- VLC：菜单 → 音频/字幕 → 选择轨道
- IINA：右键 → 音轨/字幕
- QuickTime：播放时可切换
- 大多数现代播放器都支持多轨道切换

#### 7.4 生成纯英文版本（可选）

```bash
# 仅替换音轨为英文
ffmpeg -i original.mp4 -i dubbed_audio_normalized.wav \
    -c:v copy -map 0:v:0 -map 1:a:0 \
    output_en.mp4

# 如果 --keep-original：混合原音轨（降低音量作为背景）
ffmpeg -i original.mp4 -i dubbed_audio_normalized.wav \
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

**主输出（多语言整合版）**：
```
video_multilang.mp4    # 多语言版本（包含所有内容）
```

**多语言 MP4 包含**：
| 轨道 | 类型 | 语言 | 说明 |
|------|------|------|------|
| 0 | 视频 | - | 原视频画面 |
| 1 | 音频 | 中文 | 原始中文讲解 |
| 2 | 音频 | 英文 | 英文配音 |
| 3 | 字幕 | 中文 | 中文字幕 |
| 4 | 字幕 | 英文 | 英文字幕 |

**辅助输出**：
```
video_en.mp4           # 纯英文配音版本（可选）
video_en.srt           # 英文字幕文件
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
5. **【新增】智能合并字幕段落**（相邻短句合并为完整句子）
6. **【优化】使用 Claude 整体翻译为自然的英文**（保持连贯性，修正语病）
7. 创建克隆声音（ElevenLabs/Coqui）或使用 Edge TTS
8. 逐段生成英文配音
9. 对齐音频时间轴
10. 合成最终音频
11. **【新增】音量标准化**（匹配原视频音量）
12. **【新增】生成多语言 MP4**（中英双音轨 + 中英双字幕）
13. 输出英文字幕文件
14. 清理临时文件和克隆声音（可选保留）
```

## 优化要点总结

### 连贯性优化
- 合并短字幕段落为完整句子（6-10秒为宜）
- 整体翻译而非逐句翻译
- 使用连接词保持上下文衔接

### 翻译质量优化
- 修正原文口误和语病
- 使用自然的英语口语表达
- 技术术语保持准确

### TTS 输出优化
- 合理断句，避免过长句子
- 考虑朗读节奏
- 选择合适的 TTS 声音

### 音量优化
- 检测原视频音量作为基准
- 自动计算并应用音量增益
- 确保输出音量与原视频一致

### 多语言整合
- 输出单一 MP4 文件包含所有内容
- 中英双音轨可切换
- 中英双字幕可切换
- 兼容主流播放器（VLC、IINA、QuickTime 等）
