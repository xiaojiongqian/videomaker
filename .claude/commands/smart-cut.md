---
description: 智能剪辑视频，去除冗余内容并提取主要观点
allowed-tools: Bash(ffmpeg:*), Bash(python3:*), Read, Write, Edit
argument-hint: <视频文件路径> [压缩百分比，如 50%]
---

# 智能视频剪辑 V2

分析视频内容，采用分层策略自动剪辑，保留主要观点内容。

## 分层剪辑策略

按以下优先级顺序处理：

1. **第1层：裁剪没声音部分** - 移除空白片段（无字幕内容）
2. **第2层：剪语气词** - 移除"嗯"、"啊"、"那个"等语气词和填充词
3. **第3层：剪重复内容** - 移除重复语义、口误纠正等冗余内容
4. **第4层：加速播放** - 使用1.0x-1.5x加速（保留所有内容但缩短时间）
5. **第5层：剪除低价值内容** - 最后手段，移除重要性较低的片段

这个策略确保：
- 优先使用无损或低损方法（剪空白、语气词）
- 在必要时使用加速播放保留内容
- 只在最后才剪除有价值的内容
- 全局扫描避免剪辑不均衡

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

### 3. 分析字幕内容（使用 V2 脚本）

使用改进的分析脚本 `scripts/smart_cut_analysis_v2.py`：

```bash
python3 scripts/smart_cut_analysis_v2.py "<字幕路径>" [target_reduction]
```

该脚本会：
1. 解析 SRT 字幕文件
2. 计算每个片段的内容重要性（1-10分）
3. 执行分层剪辑策略：
   - 第1层：标记空白片段
   - 第2层：标记语气词和填充词
   - 第3层：标记重复内容和口误
   - 第4层：如需进一步压缩，计算加速播放速度
   - 第5层：如仍不够，按重要性剪除低价值内容
4. 生成 `*_cut_result.json` 结果文件

### 4. 智能识别冗余内容

**已在 `smart_cut_analysis_v2.py` 中实现，分层处理：**

**第1层：空白片段（无声音）**
- 检测无字幕文本的片段
- 优先级最高，直接移除

**第2层：语气词和填充词**
- 扩展的语气词列表：嗯、啊、呃、那个、就是、然后等
- 英文：um, uh, er, like, you know 等
- 重复字符（如"选择选择选择"）
- 过短片段（少于3个字符）

**第3层：重复语义内容**
- 相邻片段文字相似度 > 80%
- 保留重要性更高的片段
- 口误/自我纠正（包含"不是"、"我是说"等）

**第4层：加速播放**
- 如需进一步压缩，计算所需播放速度
- 最多使用 1.5x 加速
- 使用 FFmpeg 的 `setpts` 和 `atempo` 滤镜

**第5层：剪除低价值内容**
- 最后手段，按内容重要性排序
- 优先移除重要性 < 7 的片段
- 避免移除高价值内容

### 5. 内容重要性评估

**已在 `smart_cut_analysis_v2.py` 中实现：**

```python
def calculate_importance(seg, all_segments, index):
    """计算片段的内容重要性（1-10分）"""
    # 考虑因素：
    # 1. 文本长度（长文本通常更重要）
    # 2. 关键词（技术术语、逻辑连接词）
    # 3. 问句（引出重要内容）
    # 4. 位置（开头和结尾更重要）
    # 5. 与前后文的连贯性（新话题更重要）
```

这确保在第5层剪除时，优先保留高价值内容。

### 6. 使用 AI 提取主要观点

在剪辑完成后，分析保留的字幕内容，提取视频主要观点：

```python
# 收集所有保留的文本（按重要性排序）
kept_texts = [(seg, seg['importance']) for seg in segments if seg['keep']]
kept_texts.sort(key=lambda x: x[1], reverse=True)

# 输出高重要性内容
for seg, importance in kept_texts[:20]:
    print(f"[重要性:{importance}] [{seg['start']}] {seg['text']}")
```

**请 Claude 分析上述内容，提取 3-5 个主要观点。**

### 4. 执行剪辑（使用 V2 脚本）

使用支持加速播放的执行脚本 `scripts/smart_cut_execute_v2.py`：

```bash
python3 scripts/smart_cut_execute_v2.py "<result_json>" "<input_video>"
```

该脚本会：
1. 读取分析结果 JSON
2. 根据每个片段的速度设置生成 FFmpeg filter
3. 对需要加速的片段应用 `setpts` 和 `atempo` 滤镜
4. 分批处理并合并所有片段
5. 生成同步字幕文件（考虑加速后的时间轴）

输出文件：
- `<原文件名>_cut.mp4` - 剪辑后的视频
- `<原文件名>_cut.srt` - 同步字幕文件

## 注意事项

- 如果视频没有字幕文件，会自动调用 `/subtitle` 先生成字幕
- 对于非中文视频，需要先确认字幕语言正确
- 剪辑过程可能较长，取决于视频长度和片段数量
- 建议先不指定百分比，查看智能剪辑结果后再决定是否需要进一步压缩
- 使用 V2 版本脚本支持加速播放和更智能的分层策略
- 加速播放最多 1.5 倍，音频使用 `atempo` 滤镜保持音调
- 分批处理避免 FFmpeg 命令过长

## 实现细节

使用以下脚本：
- `scripts/smart_cut_analysis_v2.py` - 分层分析脚本
- `scripts/smart_cut_execute_v2.py` - 支持加速播放的执行脚本

旧版本脚本（不支持加速）：
- `scripts/smart_cut_analysis.py` - 基础分析脚本
- `scripts/smart_cut_execute.py` - 基础执行脚本

## 使用示例

```bash
# 智能剪辑，自动移除冗余
/smart-cut video/example.mp4

# 指定压缩 30% 的时长
/smart-cut video/example.mp4 30%

# 压缩一半时长
/smart-cut video/example.mp4 50%
```
