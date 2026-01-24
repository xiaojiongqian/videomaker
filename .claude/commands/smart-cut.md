---
description: 智能剪辑视频，去除冗余内容并提取主要观点
allowed-tools: Bash(ffmpeg:*), Bash(python3:*), Read, Write, Edit
argument-hint: <视频文件路径> [压缩百分比，如 50%]
---

# 智能视频剪辑

分析视频内容，自动识别并剪除沉默、重复、口误等冗余片段，保留主要观点内容。

## 输入参数

- 视频文件路径: $ARGUMENTS 的第一个参数
- 压缩百分比（可选）: $ARGUMENTS 的第二个参数，如 `50%` 表示将视频时长压缩 50%

## 执行步骤

### 1. 解析参数

从 `$ARGUMENTS` 中解析：
- 视频文件路径（必需）
- 目标压缩百分比（可选，默认为智能判断）

```python
import re
args = "$ARGUMENTS"
# 解析视频路径和百分比参数
parts = args.strip().split()
video_path = parts[0] if parts else ""
target_reduction = None
for part in parts[1:]:
    match = re.match(r'(\d+)%', part)
    if match:
        target_reduction = int(match.group(1)) / 100.0
```

### 2. 检查前置条件

- 确认视频文件存在
- 检查是否已有同名 .srt 字幕文件
- 如果没有字幕，先调用 `/subtitle` 生成字幕
- 获取视频时长：`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "<视频路径>"`

### 3. 分析字幕内容

读取 SRT 字幕文件，使用 Python 解析每个片段：

```python
import re

def parse_srt(srt_path):
    """解析 SRT 文件，返回片段列表"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
    segments = []
    for match in re.finditer(pattern, content, re.DOTALL):
        idx, start, end, text = match.groups()
        segments.append({
            'index': int(idx),
            'start': start,
            'end': end,
            'start_sec': timestamp_to_seconds(start),
            'end_sec': timestamp_to_seconds(end),
            'text': text.strip(),
            'keep': True,  # 默认保留
            'reason': None  # 移除原因
        })
    return segments

def timestamp_to_seconds(ts):
    """将时间戳转换为秒数"""
    h, m, s = ts.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)
```

### 4. 智能识别冗余内容

分析每个字幕片段，标记以下类型的冗余内容：

```python
def analyze_segments(segments):
    """分析并标记冗余片段"""

    # 4.1 检测沉默/空白片段（无文字或只有语气词）
    filler_words = {'嗯', '啊', '呃', '那个', '就是', '然后', '这个', '那么', '所以说', '对吧'}

    for seg in segments:
        text = seg['text'].strip()
        # 空白或纯语气词
        if not text or all(w in filler_words for w in text):
            seg['keep'] = False
            seg['reason'] = 'filler'
            seg['priority'] = 1  # 最优先移除

    # 4.2 检测重复内容（相邻片段文字相似度高）
    for i in range(1, len(segments)):
        if similarity(segments[i]['text'], segments[i-1]['text']) > 0.8:
            segments[i]['keep'] = False
            segments[i]['reason'] = 'duplicate'
            segments[i]['priority'] = 2

    # 4.3 检测口误/自我纠正（包含"不是"、"我是说"等纠正词）
    correction_patterns = ['不是', '我是说', '不对', '应该是', '错了', '重来']
    for seg in segments:
        if any(p in seg['text'] for p in correction_patterns):
            seg['keep'] = False
            seg['reason'] = 'correction'
            seg['priority'] = 3

    # 4.4 检测过长的停顿（片段间隔超过2秒）
    for i in range(1, len(segments)):
        gap = segments[i]['start_sec'] - segments[i-1]['end_sec']
        if gap > 2.0:
            # 标记这个间隔需要被压缩
            segments[i]['gap_before'] = gap

    return segments

def similarity(text1, text2):
    """简单的文本相似度计算"""
    set1, set2 = set(text1), set(text2)
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)
```

### 5. 根据目标百分比调整

如果指定了目标压缩百分比，按优先级逐步移除片段直到达到目标：

```python
def adjust_to_target(segments, original_duration, target_reduction):
    """调整移除片段以达到目标压缩率"""
    if target_reduction is None:
        return segments

    target_duration = original_duration * (1 - target_reduction)

    # 计算当前保留时长
    current_duration = sum(
        seg['end_sec'] - seg['start_sec']
        for seg in segments if seg['keep']
    )

    if current_duration <= target_duration:
        return segments  # 已达到目标

    # 按优先级排序待移除片段（优先级低的片段）
    # 优先级: 1=语气词, 2=重复, 3=纠正, 4=内容较少的片段
    candidates = sorted(
        [s for s in segments if s['keep']],
        key=lambda x: (len(x['text']), -x.get('priority', 10))
    )

    for seg in candidates:
        if current_duration <= target_duration:
            break
        seg_duration = seg['end_sec'] - seg['start_sec']
        seg['keep'] = False
        seg['reason'] = 'target_reduction'
        current_duration -= seg_duration

    return segments
```

### 6. 使用 AI 提取主要观点

调用 Claude 分析保留的字幕内容，提取视频主要观点：

```python
# 收集所有保留的文本
kept_text = "\n".join([
    f"[{seg['start']}] {seg['text']}"
    for seg in segments if seg['keep']
])

# 输出分析提示，让 Claude 总结主要观点
print("=== 视频主要观点 ===")
print(kept_text)
```

**请 Claude 分析上述内容，提取 3-5 个主要观点，格式如下：**
1. 主要观点一
2. 主要观点二
...

### 7. 生成 FFmpeg 剪辑命令

根据保留的片段生成 FFmpeg 剪辑脚本：

```python
def generate_ffmpeg_script(segments, input_path, output_path):
    """生成 FFmpeg 剪辑命令"""
    kept_segments = [s for s in segments if s['keep']]

    if not kept_segments:
        return None

    # 生成 filter_complex 片段选择
    filter_parts = []
    concat_v = []
    concat_a = []

    for i, seg in enumerate(kept_segments):
        start = seg['start_sec']
        end = seg['end_sec']
        # 视频和音频裁剪
        filter_parts.append(
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}];"
        )
        filter_parts.append(
            f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}];"
        )
        concat_v.append(f"[v{i}]")
        concat_a.append(f"[a{i}]")

    # 拼接所有片段
    n = len(kept_segments)
    filter_complex = "".join(filter_parts)
    filter_complex += f"{''.join(concat_v)}concat=n={n}:v=1:a=0[outv];"
    filter_complex += f"{''.join(concat_a)}concat=n={n}:v=0:a=1[outa]"

    cmd = f'''ffmpeg -i "{input_path}" -filter_complex "{filter_complex}" -map "[outv]" -map "[outa]" "{output_path}" -y'''

    return cmd
```

### 8. 生成同步字幕

为剪辑后的视频生成新的同步字幕文件：

```python
def generate_new_srt(segments, output_srt_path):
    """为剪辑后的视频生成新字幕"""
    kept_segments = [s for s in segments if s['keep']]

    new_srt = ""
    current_time = 0.0

    for i, seg in enumerate(kept_segments, 1):
        duration = seg['end_sec'] - seg['start_sec']
        start = seconds_to_timestamp(current_time)
        end = seconds_to_timestamp(current_time + duration)

        new_srt += f"{i}\n{start} --> {end}\n{seg['text']}\n\n"
        current_time += duration

    with open(output_srt_path, 'w', encoding='utf-8') as f:
        f.write(new_srt)

    return output_srt_path

def seconds_to_timestamp(seconds):
    """将秒数转换为 SRT 时间戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
```

### 9. 执行剪辑并输出结果

1. 执行 FFmpeg 命令进行视频剪辑
2. 输出文件命名：`原文件名_cut.mp4` 和 `原文件名_cut.srt`
3. 显示剪辑统计信息：
   - 原始时长 vs 剪辑后时长
   - 压缩比例
   - 移除的片段数量及原因分类
   - 视频主要观点摘要

## 输出文件

- `<原文件名>_cut.mp4` - 剪辑后的视频
- `<原文件名>_cut.srt` - 同步字幕文件
- 控制台输出剪辑报告和主要观点摘要

## 注意事项

- 如果视频没有字幕文件，会自动调用 `/subtitle` 先生成字幕
- 对于非中文视频，需要先确认字幕语言正确
- 剪辑过程可能较长，取决于视频长度和片段数量
- 建议先不指定百分比，查看智能剪辑结果后再决定是否需要进一步压缩
- 对于片段较多的视频，FFmpeg 命令可能会很长，会自动使用 concat demuxer 方式处理

## 使用示例

```bash
# 智能剪辑，自动移除冗余
/smart-cut video/example.mp4

# 指定压缩 30% 的时长
/smart-cut video/example.mp4 30%

# 压缩一半时长
/smart-cut video/example.mp4 50%
```
