#!/usr/bin/env python3
"""
视频总结文档生成脚本
从字幕内容生成结构化的 Markdown 总结文档
"""
import re
import os
import sys
import json

def parse_srt(srt_path):
    """解析 SRT 文件"""
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

def extract_full_text(segments):
    """提取完整文本"""
    texts = []
    for seg in segments:
        if seg['text']:
            texts.append(f"[{seg['start'][:8]}] {seg['text']}")
    return '\n'.join(texts)

def generate_summary_prompt(full_text, word_count=2000):
    """生成总结提示词"""
    prompt = f"""请根据以下视频字幕内容，生成一份结构化的 Markdown 总结文档。

## 要求：
1. 字数约 {word_count} 字
2. 使用清晰的标题层级（一级、二级、三级标题）
3. 提取核心主题和主要观点
4. 按逻辑结构组织：背景/问题 → 解决方案 → 实践经验 → 总结
5. 包含代码示例（如果视频中有涉及）
6. 使用表格、列表等格式增强可读性
7. 在适当位置预留图片占位符，格式为：`![图片描述](images/placeholder.jpg)`

## 输出格式：
```markdown
# 视频标题

> 一句话概述

![概览图](images/01_overview.jpg)

## 一、背景与问题
...

## 二、解决方案
### 2.1 方案一
...
![方案示意图](images/02_solution.jpg)

## 三、实践经验
...

## 四、总结
| 序号 | 要点 | 说明 |
|------|------|------|
| 1 | ... | ... |
```

## 字幕内容：
{full_text}
"""
    return prompt

def main():
    if len(sys.argv) < 2:
        print("用法: python generate_summary.py <srt_path> [word_count]")
        print("例如: python generate_summary.py video.srt 2000")
        sys.exit(1)

    srt_path = sys.argv[1]
    word_count = int(sys.argv[2]) if len(sys.argv) > 2 else 2000

    # 检查字幕文件
    if not os.path.exists(srt_path):
        print(f"错误: 字幕文件不存在: {srt_path}")
        sys.exit(1)

    # 解析字幕
    segments = parse_srt(srt_path)
    print(f"字幕片段数: {len(segments)}")

    # 提取完整文本
    full_text = extract_full_text(segments)

    # 生成提示词
    prompt = generate_summary_prompt(full_text, word_count)

    # 输出提示词（供 Claude 使用）
    output_path = srt_path.replace('.srt', '_summary_prompt.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

    print(f"提示词已保存到: {output_path}")
    print(f"\n请将此提示词发送给 Claude 生成总结文档")

    # 同时输出字幕全文
    text_path = srt_path.replace('.srt', '_full_text.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f"字幕全文已保存到: {text_path}")

if __name__ == '__main__':
    main()
