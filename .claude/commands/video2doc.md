# 视频内容总结与配图生成

从视频/字幕素材中自动生成结构化总结文档，并智能提取、筛选配图。

## 触发命令

```
/video2doc <视频文件路径> [字数要求] [--author 署名] [--crop] [--annotate]
```

## 输入参数

- 视频文件路径: $ARGUMENTS 的第一个参数（支持 .mp4, .mov, .mkv 等格式）
- 字数要求（可选）: 如 `2000字` 表示生成约2000字的总结（默认2000字）
- 署名（可选）: `--author 作者名` 或 `-a 作者名`，在文档末尾添加署名
- 裁剪（可选）: `--crop` 或 `-c`，启用图片智能裁剪功能（默认不裁剪）
- 标注（可选）: `--annotate` 或 `-n`，启用图片智能标注功能（默认不标注）

> **注意**：裁剪和标注功能默认关闭，只有用户明确指定参数时才启用。

## 执行步骤

### 1. 解析参数

```python
import re
args = "$ARGUMENTS"
parts = args.strip().split()
video_path = parts[0] if parts else ""
word_count = 2000  # 默认字数
author = None  # 署名
enable_crop = False  # 默认不裁剪
enable_annotate = False  # 默认不标注

i = 1
while i < len(parts):
    part = parts[i]
    # 解析字数
    match = re.match(r'(\d+)字?', part)
    if match:
        word_count = int(match.group(1))
    # 解析署名
    elif part in ['--author', '-a'] and i + 1 < len(parts):
        author = parts[i + 1]
        i += 1
    # 解析裁剪参数
    elif part in ['--crop', '-c']:
        enable_crop = True
    # 解析标注参数
    elif part in ['--annotate', '-n']:
        enable_annotate = True
    i += 1
```

### 2. 检查前置条件

- 确认视频文件存在
- 检查是否已有同名 .srt 字幕文件
- 如果没有字幕，先调用 `/subtitle` 生成字幕
- 在视频同级目录创建 `doc/` 目录用于存放文档和配图
- 在 `doc/` 目录下创建 `images/` 子目录

**目录结构：**
```
video/
└── subjectX/
    ├── example.mp4
    ├── example.srt
    └── doc/
        ├── example_sum.md
        └── images/
            ├── 01_intro.jpg
            └── ...
```

### 3. 读取并分析字幕内容

读取 SRT 字幕文件，提取完整文本内容：

```python
import re

def parse_srt(srt_path):
    """解析 SRT 文件，返回时间戳和文本"""
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
            'text': text.strip()
        })
    return segments
```

### 4. 使用 AI 生成结构化总结

基于字幕内容，让 Claude 生成结构化的 Markdown 总结文档：

**写作风格要求（重要）：**
1. **大白话**：用通俗易懂的语言，避免晦涩的专业术语
2. **深入浅出**：把复杂概念用简单的方式解释清楚
3. **易懂**：像给朋友讲故事一样，让读者轻松理解
4. **接地气**：多用生活化的比喻和例子
5. **有温度**：保持亲切自然的语气，不要太正式

**内容要求：**
1. 提取视频的核心主题和主要观点
2. 按逻辑结构组织内容（背景、问题、解决方案、实践经验、总结）
3. 使用清晰的标题层级（一级、二级、三级标题）
4. 包含代码示例（如果视频中有涉及）
5. 使用表格、列表等格式增强可读性
6. 字数控制在目标字数左右

**输出格式：**
```markdown
# 视频标题

> 一句话概述（用大白话说清楚这个视频讲了啥）

## 一、背景与问题
（用通俗的语言描述问题背景，让读者快速理解）
...

## 二、解决方案
### 2.1 方案一
（深入浅出地解释方案，多用例子）
...

## 三、实践经验
（分享实用的经验和技巧）
...

## 四、总结
（用简洁的语言总结要点）
...

---
*作者：xxx*（如果指定了署名）
```

### 5. 智能提取关键帧截图（基于内容分析）

**核心原则：基于字幕内容预测最佳截图时间点，而非均匀分布**

#### 5.1 分析字幕内容，识别关键主题时间点

首先分析字幕文本，识别以下类型的关键时间点：

```
关键时间点类型：
1. **主题切换点**：当讲述内容从一个主题切换到另一个主题时
2. **演示开始点**：当开始展示代码、界面、操作时（关键词：看一下、这里、这个、演示）
3. **重要概念点**：当解释核心概念时（关键词：关键、重要、核心、第一、第二）
4. **工具/界面展示点**：当展示特定工具或界面时（关键词：窗口、界面、配置、设置）
5. **总结点**：当进行阶段性总结时（关键词：总结、所以、因此）
```

#### 5.2 字幕分析流程

```
分析步骤：
1. 读取完整字幕文件，解析每条字幕的时间戳和文本
2. 识别主题段落：
   - 根据内容相似度将连续字幕分组
   - 识别主题切换的边界点
3. 为每个主题段落评估重要性（1-5分）：
   - 核心概念讲解：5分
   - 工具/界面演示：5分
   - 实践操作展示：4分
   - 背景介绍：3分
   - 过渡性内容：2分
4. 选择截图时间点：
   - 优先选择重要性高的段落
   - 在每个选中段落内，选择最可能出现有价值画面的时间点
   - 总数控制在约10张
```

#### 5.3 预测最佳截图时间点

```
时间点选择策略：
1. 对于"演示类"内容：选择演示开始后3-5秒（画面已稳定）
2. 对于"界面展示"内容：选择提到界面名称后2-3秒
3. 对于"代码讲解"内容：选择开始讲解后5-10秒（代码已显示完整）
4. 对于"操作演示"内容：选择操作中间点（避免开始和结束的过渡画面）
5. 避免选择：
   - 主题切换的过渡时刻
   - 鼠标移动、页面滚动的时刻
   - 字幕中出现"等一下"、"稍等"等词的时刻
```

#### 5.4 输出格式

分析完成后，输出预测的截图时间点列表：

```json
{
  "predicted_timestamps": [
    {
      "time_sec": 45,
      "topic": "多窗口并行工作环境",
      "reason": "演示开始，展示桌面布局",
      "importance": 5,
      "expected_content": "多个终端窗口并排显示"
    },
    {
      "time_sec": 95,
      "topic": "Full Access 模式",
      "reason": "展示 Claude Code 设置界面",
      "importance": 5,
      "expected_content": "Claude Code 权限设置"
    },
    ...
  ]
}
```

#### 5.5 提取截图

根据预测的时间点提取截图：

```bash
# 对于每个预测的时间点
ffmpeg -ss {time_sec} -i video.mp4 -vframes 1 -q:v 2 {output_file} -y
```

**注意**：提取后仍需通过视觉分析验证截图实际内容是否与预期匹配。如果不匹配，可能需要微调时间点（±5秒）重新提取。

### 6. 智能分析和筛选截图（关键步骤）

使用 Claude 的视觉能力分析每张截图，判断其是否适合作为文档配图：

**分析标准：**
1. **内容相关性**：截图内容是否与文档主题相关
2. **信息量**：截图是否包含有价值的信息（代码、界面、图表等）
3. **清晰度**：截图是否清晰可辨
4. **重复性**：是否与其他截图内容重复

**⚠️ 关键原则：基于实际内容匹配，而非预期匹配**

> **重要**：图片与章节的匹配必须基于图片**实际显示的内容**，而不是基于时间戳或预期。
>
> 错误示例：因为截图时间点在"MCP配置"章节对应的时间段，就假设图片显示的是MCP配置
> 正确做法：仔细分析图片实际内容，只有当图片确实显示了MCP配置界面时，才将其匹配到该章节

**分析流程：**
```
对于每张截图：
1. 使用 Read 工具读取图片
2. **【核心】客观描述图片实际内容**：
   - 图片中显示了什么界面/窗口？
   - 有哪些可识别的文字、代码、UI元素？
   - 图片的主要信息是什么？
3. **【核心】基于实际内容判断适用章节**：
   - 根据图片实际显示的内容，判断它适合哪个章节
   - 如果图片内容与任何章节都不匹配，标记为"无匹配章节"
   - **禁止**：不要因为"需要一张XX图"就强行匹配不相关的图片
4. 给出评分（1-5分）和建议用途
5. 删除评分低于3分的截图或无匹配章节的截图
6. 为保留的截图生成描述性文件名（基于实际内容）
7. 识别兴趣区域（ROI）并决定是否需要裁剪或标注
```

**内容匹配验证检查清单：**
- [ ] 图片描述是否基于实际可见内容？
- [ ] 章节匹配是否有图片内容支撑？
- [ ] 标注文字是否与图片实际显示的内容一致？
- [ ] 如果图片显示的是A内容，是否错误地标注为B？

**筛选后的截图应该：**
- 每张都有明确的用途（对应文档某个章节）
- **图片实际内容与章节描述一致**
- 内容不重复
- 清晰且信息量大
- 数量适中（通常5-10张）

### 6.1 兴趣区域识别与裁剪（新增功能）

在分析截图时，同时识别图片中的**兴趣区域（ROI, Region of Interest）**，判断是否需要裁剪以突出重点内容。

**ROI 识别标准：**
1. **代码区域**：终端窗口、代码编辑器中的关键代码片段
2. **UI 元素**：按钮、菜单、对话框等交互元素
3. **配置界面**：设置面板、配置文件内容
4. **关键信息**：错误提示、成功消息、重要数据

**分析时输出 ROI 信息：**
```json
{
  "filename": "03_frame.jpg",
  "original_size": {"width": 1920, "height": 1080},
  "roi": {
    "need_crop": true,
    "crop_region": {"x": 100, "y": 200, "width": 800, "height": 600},
    "reason": "聚焦于终端窗口中的命令输出"
  }
}
```

**裁剪执行（使用 ffmpeg）：**
```bash
# 裁剪图片到指定区域
ffmpeg -i input.jpg -vf "crop=800:600:100:200" -y output_cropped.jpg
```

### 6.2 智能标注功能（新增功能）

对于需要强调特定区域的截图，使用 ffmpeg 添加可视化标注：

**⚠️ 标注原则：只标注图片中实际存在的内容**

> **重要**：标注必须基于图片中**实际可见的元素**，而不是基于预期或假设。
>
> 错误示例：图片显示的是代码编辑器，却标注为"MCP配置界面"
> 正确做法：只标注图片中实际可见的元素，如"代码编辑器"、"终端窗口"等

**标注类型：**

| 标注类型 | 用途 | ffmpeg 实现 |
|---------|------|-------------|
| 红色圆角矩形 | 框选重要区域 | drawbox + 圆角处理 |
| 红色圆圈 | 标记关键点 | drawtext 配合特殊字符或 overlay |
| 红色箭头/线条 | 指示方向或连接 | drawline |
| 文本标注 | 添加说明文字 | drawtext |

**标注前的验证步骤：**
```
1. 确认要标注的区域在图片中实际存在
2. 确认标注文字与该区域的实际内容一致
3. 如果图片内容与预期不符，应该：
   a) 寻找更合适的截图
   b) 或者根据实际内容调整标注文字
   c) 或者放弃使用该图片
```

**标注分析输出：**
```json
{
  "filename": "03_frame.jpg",
  "annotations": [
    {
      "type": "rectangle",
      "region": {"x": 150, "y": 300, "width": 400, "height": 200},
      "color": "red",
      "thickness": 3,
      "label": "Full Access 模式设置"
    },
    {
      "type": "text",
      "position": {"x": 150, "y": 280},
      "content": "① 开启此选项",
      "font_size": 24,
      "color": "red"
    },
    {
      "type": "circle",
      "center": {"x": 500, "y": 400},
      "radius": 30,
      "color": "red",
      "thickness": 3
    }
  ]
}
```

**ffmpeg 标注命令示例：**

> **注意**：建议优先使用英文标注，避免中文字体兼容性问题。如需中文标注，需确保系统有支持中文的字体文件。

```bash
# 1. 添加红色矩形框
ffmpeg -i input.jpg -vf "drawbox=x=150:y=300:w=400:h=200:color=red@0.8:t=3" -y output.jpg

# 2. 添加英文文本标注（推荐，无需指定字体）
ffmpeg -i input.jpg -vf "drawtext=text='1. Main Window':x=150:y=280:fontsize=24:fontcolor=red" -y output.jpg

# 3. 组合多个标注（使用滤镜链）- 英文版
ffmpeg -i input.jpg -vf "\
  drawbox=x=150:y=300:w=400:h=200:color=red@0.8:t=3,\
  drawtext=text='1. Full Access Mode':x=150:y=280:fontsize=24:fontcolor=red,\
  drawbox=x=600:y=100:w=300:h=150:color=red@0.8:t=3,\
  drawtext=text='2. Worktree List':x=600:y=80:fontsize=24:fontcolor=red\
" -y output_annotated.jpg

# 4. 先裁剪再标注
ffmpeg -i input.jpg -vf "\
  crop=800:600:100:200,\
  drawbox=x=50:y=100:w=300:h=150:color=red@0.8:t=3,\
  drawtext=text='Key Code':x=50:y=80:fontsize=20:fontcolor=red\
" -y output_final.jpg

# 5. 如需中文标注，指定支持中文的字体（macOS）
ffmpeg -i input.jpg -vf "drawtext=text='中文标注':x=150:y=280:fontsize=24:fontcolor=red:fontfile=/System/Library/Fonts/STHeiti\ Light.ttc" -y output.jpg
```

**圆圈标注实现（使用 overlay 方式）：**
```bash
# 方法1：使用 geq 滤镜绘制圆圈
ffmpeg -i input.jpg -vf "\
  geq=r='if(between(sqrt((X-500)^2+(Y-400)^2),27,33),255,r(X,Y))':\
      g='if(between(sqrt((X-500)^2+(Y-400)^2),27,33),0,g(X,Y))':\
      b='if(between(sqrt((X-500)^2+(Y-400)^2),27,33),0,b(X,Y))'\
" -y output_circle.jpg

# 方法2：使用预制的圆圈 PNG 叠加
ffmpeg -i input.jpg -i circle_red.png -filter_complex "overlay=470:370" -y output.jpg
```

### 6.3 标注决策流程

在视觉分析阶段，对每张截图判断：

```
1. 读取截图，分析内容
2. 判断是否需要处理：
   a) 全图清晰且重点突出 → 保持原图，无需处理
   b) 图片过大，重点区域较小 → 裁剪到 ROI
   c) 需要强调多个区域 → 添加标注
   d) 裁剪后仍需强调 → 先裁剪再标注
3. 输出处理方案（JSON 格式）
4. 执行 ffmpeg 命令
5. 保存处理后的图片
```

**完整分析输出示例：**
```json
{
  "filename": "intro_multiwindow.jpg",
  "score": 5,
  "keep": true,
  "section": "解决方案",
  "caption": "多窗口并行工作界面",
  "processing": {
    "crop": {
      "enabled": false
    },
    "annotations": {
      "enabled": true,
      "items": [
        {
          "type": "rectangle",
          "region": {"x": 50, "y": 100, "width": 400, "height": 300},
          "label": "① 主控窗口"
        },
        {
          "type": "rectangle",
          "region": {"x": 500, "y": 100, "width": 400, "height": 300},
          "label": "② 功能开发窗口"
        },
        {
          "type": "rectangle",
          "region": {"x": 50, "y": 450, "width": 400, "height": 300},
          "label": "③ Worktree 列表"
        }
      ]
    }
  },
  "ffmpeg_command": "ffmpeg -i intro_multiwindow.jpg -vf \"drawbox=x=50:y=100:w=400:h=300:color=red@0.8:t=3,drawtext=text='① 主控窗口':x=50:y=80:fontsize=20:fontcolor=red:fontfile=/System/Library/Fonts/PingFang.ttc,drawbox=x=500:y=100:w=400:h=300:color=red@0.8:t=3,drawtext=text='② 功能开发窗口':x=500:y=80:fontsize=20:fontcolor=red:fontfile=/System/Library/Fonts/PingFang.ttc\" -y intro_multiwindow_annotated.jpg"
}

### 7. 重命名和组织截图

根据分析结果，重命名截图文件：

```python
def rename_screenshots(screenshots, analysis_results, doc_images_dir):
    """根据分析结果重命名截图"""
    import os
    import shutil

    for shot, result in zip(screenshots, analysis_results):
        if result['keep']:
            # 生成描述性文件名
            new_name = f"{result['section']}_{result['description']}.jpg"
            new_path = os.path.join(doc_images_dir, new_name)
            shutil.move(shot['path'], new_path)
            shot['new_path'] = new_path
            shot['caption'] = result['caption']
        else:
            # 删除不合适的截图
            os.remove(shot['path'])
```

### 8. 将配图插入 Markdown 文档

根据截图的用途，将其插入到文档的相应位置：

```python
def insert_images_to_markdown(markdown_content, screenshots):
    """将截图插入到 Markdown 文档中"""

    # 图片插入规则：
    # 1. 文档开头放一张概览图
    # 2. 每个主要章节后放相关截图
    # 3. 使用相对路径引用图片（images/filename.jpg）

    # 示例插入格式：
    # ![图片描述](images/filename.jpg)

    return updated_markdown
```

### 9. 添加署名（如果指定）

如果用户通过 `--author` 参数指定了署名，在文档末尾添加：

```markdown
---
*作者：{author}*
```

### 10. 输出最终文档

1. 保存 Markdown 文件到 `doc/<视频名>_sum.md`
2. 保存配图到 `doc/images/` 目录
3. 显示生成报告：
   - 文档字数
   - 配图数量
   - 各章节概要
   - 署名信息（如果有）

## 输出文件

```
video/
└── subjectX/
    ├── example.mp4
    ├── example.srt
    └── doc/
        ├── example_sum.md      # 图文并茂的总结文档
        └── images/             # 筛选后的配图目录
            ├── intro.jpg
            ├── solution_cli.jpg
            └── ...
```

## 图片筛选标准详解

### 应该保留的截图类型：
1. **代码/配置界面**：显示关键代码或配置的截图
2. **操作演示**：展示具体操作步骤的截图
3. **结果展示**：显示运行结果或效果的截图
4. **架构/流程图**：展示系统架构或流程的截图
5. **关键界面**：展示重要功能界面的截图

### 应该删除的截图类型：
1. **模糊/不清晰**：内容无法辨认
2. **过渡画面**：鼠标移动、加载中等过渡状态
3. **重复内容**：与其他截图内容高度相似
4. **无关内容**：与文档主题无关的画面
5. **隐私信息**：包含敏感信息的截图

## 使用示例

```bash
# 基本用法（不裁剪、不标注）
/video2doc video/example.mp4

# 指定字数
/video2doc video/example.mp4 3000字

# 添加署名
/video2doc video/example.mp4 --author 张三

# 指定字数并添加署名
/video2doc video/example.mp4 2000字 --author 张三

# 简写署名参数
/video2doc video/example.mp4 -a 李四

# 启用智能裁剪
/video2doc video/example.mp4 --crop

# 启用智能标注
/video2doc video/example.mp4 --annotate

# 同时启用裁剪和标注
/video2doc video/example.mp4 --crop --annotate

# 完整参数示例
/video2doc video/example.mp4 2000字 --author 张三 --crop --annotate
```

## 注意事项

- 如果视频没有字幕文件，会自动调用 `/subtitle` 先生成字幕
- 截图分析使用 Claude 的视觉能力，需要逐张读取图片
- 建议视频时长在 30 分钟以内，过长的视频可能需要分段处理
- 生成的文档可能需要人工微调，特别是图片位置和描述
- 文档和配图统一存放在视频同级的 `doc/` 目录下

## 完整工作流程

### 第一阶段：准备工作
1. 解析输入参数（视频路径、字数要求、署名、裁剪开关、标注开关）
2. 检查视频文件是否存在
3. 检查/生成字幕文件
4. 创建 `doc/` 和 `doc/images/` 目录

### 第二阶段：内容分析
1. 读取字幕文件，提取完整文本
2. 分析视频主题和结构
3. 生成结构化的 Markdown 总结文档（大白话、深入浅出、易懂）

### 第三阶段：智能截图提取（基于内容分析）

**核心：根据字幕内容预测最佳截图时间点，而非均匀分布**

1. **分析字幕内容，识别关键主题**：
   - 将字幕按内容分组，识别主题切换点
   - 标记演示、界面展示、代码讲解等关键时刻
   - 为每个主题段落评估重要性（1-5分）

2. **预测最佳截图时间点**：
   - 优先选择重要性高的段落
   - 演示类内容：选择演示开始后3-5秒
   - 界面展示：选择提到界面名称后2-3秒
   - 代码讲解：选择开始讲解后5-10秒
   - 避免过渡时刻、鼠标移动、页面滚动

3. **输出预测时间点列表**（约10个）：
   ```json
   {"time_sec": 45, "topic": "主题名", "reason": "选择原因", "importance": 5}
   ```

4. **使用 ffmpeg 提取截图**：
   ```bash
   ffmpeg -ss {time_sec} -i video.mp4 -vframes 1 -q:v 2 output.jpg -y
   ```

5. 保存截图到 `doc/images/` 目录

### 第四阶段：图片智能筛选与增强（关键）

**⚠️ 核心原则：基于实际内容匹配，禁止强行匹配**

对于每张截图，执行以下分析：

```
1. 使用 Read 工具读取图片文件
2. 【核心】客观分析图片实际内容：
   - 详细描述图片中实际显示的内容（界面、文字、代码等）
   - 判断是否清晰可辨
   - 判断是否包含有价值的信息
3. 【核心】基于实际内容匹配章节：
   - 根据图片实际显示的内容，判断它适合哪个章节
   - 如果图片内容与所有章节都不匹配，标记为"无匹配"并删除
   - **禁止**：不要因为"需要一张XX图"就强行匹配
4. 给出评分（1-5分）：
   - 5分：非常适合，内容清晰、信息量大、与章节高度匹配
   - 4分：适合，内容清晰、与章节匹配
   - 3分：一般，可用
   - 2分：不太适合或匹配度低
   - 1分：不适合，应删除
5. 决定保留或删除：
   - 评分 >= 3分 且 有匹配章节：保留
   - 评分 < 3分 或 无匹配章节：删除
6. 如果保留：
   - 生成描述性文件名（基于实际内容，英文）
   - 生成图片说明文字（基于实际内容，中文）
   - 指定适用的文档章节
7. **【仅当 --crop 参数启用时】** 识别兴趣区域（ROI）：
   - 判断是否需要裁剪（图片过大、重点区域较小）
   - 输出裁剪坐标：{"x": 100, "y": 200, "width": 800, "height": 600}
   - 如果未启用 --crop，跳过此步骤
8. **【仅当 --annotate 参数启用时】** 判断是否需要标注：
   - 只标注图片中实际存在的元素
   - 标注文字必须与图片实际内容一致
   - 输出标注信息：矩形框坐标、标注文字、位置
   - 如果未启用 --annotate，跳过此步骤
9. 如果启用了裁剪或标注，生成 ffmpeg 处理命令并执行
```

**内容匹配验证（必须执行）：**
```
在确定图片用途前，回答以下问题：
Q1: 图片中实际显示了什么？（客观描述）
Q2: 这个内容与哪个章节相关？（基于Q1的答案判断）
Q3: 如果要标注，标注的内容在图片中是否真实存在？

如果Q3的答案是"否"，则：
- 要么调整标注内容以匹配实际图片
- 要么放弃使用该图片
- 要么寻找更合适的截图
```

### 第五阶段：文档整合
1. 删除评分低的截图文件
2. 重命名保留的截图（使用描述性文件名）
3. 将截图引用插入到 Markdown 文档的相应位置
4. 添加署名（如果指定）
5. 保存最终文档到 `doc/` 目录

## 图片分析示例

当读取一张截图后，输出分析结果：

```json
{
  "filename": "03_frame_180s.jpg",
  "description": "显示了终端窗口中运行 Claude Code 的界面，左侧是代码编辑器，右侧是 AI 对话区",
  "score": 5,
  "keep": true,
  "section": "解决方案",
  "new_filename": "cli_interface.jpg",
  "caption": "Claude Code 命令行界面"
}
```

如果不适合保留：
```json
{
  "filename": "05_frame_300s.jpg",
  "description": "模糊的过渡画面，鼠标正在移动中",
  "score": 1,
  "keep": false,
  "reason": "画面模糊，为过渡状态，无实际信息"
}
```

### 带裁剪和标注的分析示例（新增）

**需要裁剪的截图：**
```json
{
  "filename": "04_frame.jpg",
  "description": "全屏截图，但重点是右下角的终端窗口显示的命令输出",
  "score": 4,
  "keep": true,
  "section": "解决方案",
  "new_filename": "terminal_output.jpg",
  "caption": "终端命令输出",
  "processing": {
    "crop": {
      "enabled": true,
      "region": {"x": 960, "y": 540, "width": 900, "height": 500},
      "reason": "裁剪聚焦于终端窗口区域"
    },
    "annotations": {
      "enabled": false
    }
  },
  "ffmpeg_command": "ffmpeg -i 04_frame.jpg -vf 'crop=900:500:960:540' -y terminal_output.jpg"
}
```

**需要标注的截图：**
```json
{
  "filename": "06_frame.jpg",
  "description": "显示了多窗口开发环境，包含多个重要区域需要说明",
  "score": 5,
  "keep": true,
  "section": "实战演示",
  "new_filename": "multiwindow_annotated.jpg",
  "caption": "多窗口并行开发环境",
  "processing": {
    "crop": {
      "enabled": false
    },
    "annotations": {
      "enabled": true,
      "items": [
        {
          "type": "rectangle",
          "region": {"x": 50, "y": 80, "width": 450, "height": 350},
          "label": "① 主控窗口",
          "label_position": {"x": 50, "y": 60}
        },
        {
          "type": "rectangle",
          "region": {"x": 520, "y": 80, "width": 450, "height": 350},
          "label": "② 功能开发",
          "label_position": {"x": 520, "y": 60}
        },
        {
          "type": "rectangle",
          "region": {"x": 50, "y": 450, "width": 300, "height": 200},
          "label": "③ Worktree",
          "label_position": {"x": 50, "y": 430}
        }
      ]
    }
  },
  "ffmpeg_command": "ffmpeg -i 06_frame.jpg -vf \"drawbox=x=50:y=80:w=450:h=350:color=red@0.8:t=3,drawtext=text='① 主控窗口':x=50:y=60:fontsize=22:fontcolor=red:fontfile=/System/Library/Fonts/PingFang.ttc,drawbox=x=520:y=80:w=450:h=350:color=red@0.8:t=3,drawtext=text='② 功能开发':x=520:y=60:fontsize=22:fontcolor=red:fontfile=/System/Library/Fonts/PingFang.ttc,drawbox=x=50:y=450:w=300:h=200:color=red@0.8:t=3,drawtext=text='③ Worktree':x=50:y=430:fontsize=22:fontcolor=red:fontfile=/System/Library/Fonts/PingFang.ttc\" -y multiwindow_annotated.jpg"
}
```

**先裁剪再标注的截图：**
```json
{
  "filename": "08_frame.jpg",
  "description": "配置文件界面，需要裁剪到配置区域并标注关键配置项",
  "score": 5,
  "keep": true,
  "section": "解决方案",
  "new_filename": "config_annotated.jpg",
  "caption": "MCP 配置文件",
  "processing": {
    "crop": {
      "enabled": true,
      "region": {"x": 200, "y": 150, "width": 800, "height": 500}
    },
    "annotations": {
      "enabled": true,
      "items": [
        {
          "type": "rectangle",
          "region": {"x": 50, "y": 100, "width": 300, "height": 80},
          "label": "Playwright MCP"
        }
      ]
    }
  },
  "ffmpeg_command": "ffmpeg -i 08_frame.jpg -vf \"crop=800:500:200:150,drawbox=x=50:y=100:w=300:h=80:color=red@0.8:t=3,drawtext=text='Playwright MCP':x=50:y=80:fontsize=20:fontcolor=red:fontfile=/System/Library/Fonts/PingFang.ttc\" -y config_annotated.jpg"
}
```
```

## 配套脚本

以下脚本位于 `scripts/` 目录：

- `extract_frames.py` - 视频关键帧提取
- `generate_summary.py` - 总结文档生成辅助
- `analyze_screenshots.py` - 截图分析标准参考

## 常见错误与避免方法

### ❌ 错误1：基于时间戳假设图片内容

**错误做法**：
```
截图时间点在视频的 5:30，而字幕显示此时在讲"MCP配置"，
所以假设这张图片显示的是MCP配置界面。
```

**正确做法**：
```
1. 先读取图片，客观描述实际内容
2. 发现图片实际显示的是"代码编辑器和PR合并信息"
3. 将图片匹配到"代码审查"章节，而非"MCP配置"章节
```

### ❌ 错误2：强行匹配不相关的图片

**错误做法**：
```
文档需要一张"Playwright测试"的配图，但没有合适的截图，
于是将一张显示"代码编辑器"的图片标注为"Playwright测试界面"。
```

**正确做法**：
```
1. 如果没有合适的截图，宁可不放图片
2. 或者在文档中说明"此处无配图"
3. 或者尝试从视频的其他时间点提取更合适的截图
```

### ❌ 错误3：标注与图片实际内容不符

**错误做法**：
```
图片显示的是多窗口开发环境，但标注为：
- "① MCP配置面板"（实际是代码编辑器）
- "② Playwright测试"（实际是终端窗口）
```

**正确做法**：
```
1. 仔细观察图片中每个区域的实际内容
2. 标注应该反映实际内容：
   - "① 代码编辑器"
   - "② 终端窗口"
3. 如果需要MCP配置的图片，应该寻找真正显示MCP配置的截图
```

### ✅ 正确的图片分析流程

```
1. 读取图片
2. 客观描述：这张图片显示了什么？
   - 左侧：VSCode编辑器，打开了 config.toml 文件
   - 右侧：终端窗口，显示 git status 输出
   - 底部：文件浏览器
3. 判断匹配：这个内容适合哪个章节？
   - 适合"开发环境配置"或"Git工作流"章节
   - 不适合"MCP配置"章节（因为没有显示MCP相关内容）
4. 决定标注：如果要标注，标注什么？
   - "① 配置文件编辑器"
   - "② Git状态输出"
   - 不要标注图片中不存在的内容
```
