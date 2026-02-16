---
description: 从PPT/PPTX/PDF生成图文并茂的Markdown文章
allowed-tools: Bash(soffice:*), Bash(magick:*), Bash(python3:*), Bash(gs:*), Bash(ls:*), Bash(mkdir:*), Bash(cp:*), Bash(rm:*), Read, Write, Edit
argument-hint: <PPT/PDF文件路径> [字数要求，如 2000字] [--author 署名]
---

# PPT/PDF 转 Markdown 文章

从 PPT/PPTX/PDF 文件生成图文并茂、深入浅出的 Markdown 文章。

## 核心原则

**写作风格（重要）：**
1. **大白话**：通俗易懂，避免晦涩术语
2. **深入浅出**：复杂概念用简单方式讲清楚
3. **有吸引力**：像给朋友讲故事，有节奏感
4. **无 AI 味**：不要"首先/其次/总之"的八股文结构，不要"在当今时代"之类的套话
5. **有温度**：亲切自然，不端着

**禁止出现的表达：**
- "在当今XXX时代"、"随着XXX的发展"
- "首先...其次...最后..."、"综上所述"
- "不可否认"、"毋庸置疑"、"众所周知"
- 过度使用"赋能"、"抓手"、"闭环"等词

## 输入参数

- 文件路径: $ARGUMENTS 的第一个参数（支持 .ppt, .pptx, .pdf）
- 字数要求（可选）: 如 `2000字`，默认 2000 字
- 署名（可选）: `--author 作者名` 或 `-a 作者名`

## 执行步骤

### 1. 解析参数

```python
import re
args = "$ARGUMENTS"
parts = args.strip().split()
file_path = parts[0] if parts else ""
word_count = 2000
author = None

i = 1
while i < len(parts):
    part = parts[i]
    match = re.match(r'(\d+)字?', part)
    if match:
        word_count = int(match.group(1))
    elif part in ['--author', '-a'] and i + 1 < len(parts):
        author = parts[i + 1]
        i += 1
    i += 1
```

### 2. 检查前置条件

- 确认文件存在，识别格式（.ppt/.pptx/.pdf）
- 在文件同级目录创建 `doc/` 和 `doc/images/` 目录
- 检查依赖工具：`soffice`（LibreOffice）、`magick`（ImageMagick）、`gs`（Ghostscript）

**目录结构：**
```
source_dir/
├── presentation.pptx
└── doc/
    ├── presentation_sum.md
    └── images/
        ├── slide_00.png
        └── ...
```

### 3. 导出每页为图片

**PPT/PPTX 文件：**
```bash
# 先转 PDF
soffice --headless --convert-to pdf --outdir <输出目录> "<文件路径>"

# 再用 ImageMagick 把 PDF 每页转 PNG（density=200 保证清晰）
magick -density 200 "<PDF路径>" -quality 95 "<输出目录>/slide_%02d.png"
```

**PDF 文件：**
```bash
# 直接用 ImageMagick 转 PNG
magick -density 200 "<文件路径>" -quality 95 "<输出目录>/slide_%02d.png"
```

### 4. 分析每页内容

使用 Read 工具逐页读取图片，分析每页 PPT 的内容：

```
对于每张幻灯片：
1. 读取图片，识别文字和图表内容
2. 提炼该页的核心信息
3. 判断该页在整体叙事中的角色（标题页/内容页/总结页/过渡页）
4. 记录关键数据、图表、对比关系
```

**输出分析结构：**
```json
{
  "slides": [
    {
      "index": 0,
      "role": "title",
      "key_content": "主标题和副标题",
      "use_image": true,
      "image_caption": "图片说明"
    }
  ]
}
```

### 5. 生成 Markdown 文章

**基于幻灯片分析结果，生成结构化文章：**

**文章结构模板：**
```markdown
# 文章标题（从PPT标题提炼，可以更吸引人）

> 一句话概述（大白话说清楚核心观点，要有吸引力）

![标题图](images/slide_00.png)

## 一、[第一个主题]

[正文内容，深入浅出地展开]

![图片说明](images/slide_XX.png)

[继续展开...]

## 二、[第二个主题]
...

## N、总结/思考

[收尾，可以留一个问题引发思考]

---
*作者：xxx*（如果指定了署名）
```

**写作要求：**

1. **标题要吸引人**：不要照搬 PPT 标题，要提炼出更有吸引力的表达
2. **开头要抓人**：用一个问题、一个场景或一个反常识的观点开头
3. **内容要有层次**：不是简单罗列 PPT 要点，而是用叙事逻辑串起来
4. **图片要精选**：不是每页都放图，选择信息量大、有助于理解的页面
5. **结尾要有力**：留一个思考题或行动建议，不要烂尾

**图片使用原则：**
- 标题页：通常保留，作为文章封面
- 内容页：选择有图表、对比、框架的页面，纯文字页面可以不放图
- 总结页：如果有精炼的总结图，保留
- 过渡页：通常不需要放图
- 每张图只用一次，不重复
- 图片说明要基于图片实际内容

### 6. 图片筛选与组织

```
筛选标准：
- 保留：包含图表、框架、对比、数据的页面
- 保留：标题页（作为封面）
- 保留：有精炼总结的页面
- 可选：纯文字但排版精美的页面
- 删除：纯过渡页、空白页、重复内容页

命名规则：
- slide_00.png → 按原始顺序保留
- 在 Markdown 中用相对路径引用：images/slide_XX.png
```

### 7. 添加署名（如果指定）

```markdown
---
*作者：{author}*
```

### 8. 输出结果

1. 保存 Markdown 文件到 `doc/<文件名>_sum.md`
2. 图片保存在 `doc/images/` 目录
3. 显示生成报告：文档字数、配图数量

## 使用示例

```bash
# 基本用法
/slide2doc presentation.pptx

# 指定字数
/slide2doc presentation.pptx 3000字

# 添加署名
/slide2doc presentation.pptx --author 张三

# PDF 文件
/slide2doc report.pdf 2000字 -a 李四
```

## 注意事项

- 需要安装 LibreOffice（`brew install --cask libreoffice`）
- 需要安装 ImageMagick 和 Ghostscript（`brew install imagemagick ghostscript`）
- PPT 中的动画效果不会体现，只导出静态页面
- 如果 PPT 有备注（Notes），也可以作为写作参考
- 生成的文章需要人工微调，特别是专业术语和上下文逻辑
