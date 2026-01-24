#!/usr/bin/env python3
"""
截图分析和筛选脚本
分析截图内容，筛选适合作为文档配图的图片
"""
import os
import sys
import json
import shutil

# 图片分析标准
ANALYSIS_CRITERIA = """
## 截图分析标准

### 应该保留的截图（评分 4-5 分）：
1. **代码/配置界面**：显示关键代码、配置文件、命令行操作
2. **操作演示**：展示具体操作步骤、界面交互
3. **结果展示**：显示运行结果、效果对比
4. **架构/流程图**：展示系统架构、流程图、示意图
5. **关键界面**：展示重要功能界面、工具界面

### 应该删除的截图（评分 1-2 分）：
1. **模糊/不清晰**：内容无法辨认
2. **过渡画面**：鼠标移动中、加载中、切换中
3. **重复内容**：与其他截图内容高度相似
4. **无关内容**：与文档主题无关的画面
5. **空白/黑屏**：无实际内容的画面

### 评分标准：
- 5分：非常适合，内容清晰、信息量大、与主题高度相关
- 4分：适合，内容清晰、有一定信息量
- 3分：一般，可用但不是最佳选择
- 2分：不太适合，内容模糊或相关性低
- 1分：不适合，应删除
"""

def generate_analysis_prompt(screenshot_info, doc_outline=None):
    """生成图片分析提示词"""
    prompt = f"""请分析以下截图，判断其是否适合作为文档配图。

## 截图信息：
- 文件名: {screenshot_info['filename']}
- 时间点: {screenshot_info.get('timestamp_str', 'N/A')}

{ANALYSIS_CRITERIA}

## 请回答以下问题：

1. **内容描述**：这张截图显示了什么内容？（简要描述）

2. **评分**：根据上述标准，给这张截图打分（1-5分）

3. **适用章节**：如果保留，这张截图适合放在文档的哪个章节？
   - 概览/引言
   - 背景/问题
   - 解决方案
   - 实践经验
   - 总结
   - 不适用

4. **建议文件名**：如果保留，建议的描述性文件名（英文，如 cli_interface.jpg）

5. **图片说明**：如果保留，建议的图片说明文字（中文）

6. **是否保留**：是/否

请以 JSON 格式输出：
```json
{{
  "description": "内容描述",
  "score": 4,
  "section": "解决方案",
  "suggested_filename": "cli_interface.jpg",
  "caption": "命令行界面示例",
  "keep": true
}}
```
"""
    return prompt

def process_analysis_result(screenshot, analysis_result, output_dir):
    """处理分析结果，重命名或删除截图"""
    if analysis_result.get('keep', False) and analysis_result.get('score', 0) >= 3:
        # 保留并重命名
        new_filename = analysis_result.get('suggested_filename', screenshot['filename'])
        new_path = os.path.join(output_dir, new_filename)

        # 避免文件名冲突
        if os.path.exists(new_path) and new_path != screenshot['path']:
            base, ext = os.path.splitext(new_filename)
            i = 1
            while os.path.exists(new_path):
                new_filename = f"{base}_{i}{ext}"
                new_path = os.path.join(output_dir, new_filename)
                i += 1

        if screenshot['path'] != new_path:
            shutil.move(screenshot['path'], new_path)

        return {
            'kept': True,
            'old_path': screenshot['path'],
            'new_path': new_path,
            'filename': new_filename,
            'section': analysis_result.get('section', ''),
            'caption': analysis_result.get('caption', ''),
            'score': analysis_result.get('score', 0)
        }
    else:
        # 删除
        if os.path.exists(screenshot['path']):
            os.remove(screenshot['path'])
        return {
            'kept': False,
            'old_path': screenshot['path'],
            'reason': f"评分 {analysis_result.get('score', 0)} 分，不符合保留标准"
        }

def generate_markdown_images(kept_screenshots):
    """生成 Markdown 图片引用"""
    sections = {
        '概览/引言': [],
        '背景/问题': [],
        '解决方案': [],
        '实践经验': [],
        '总结': []
    }

    for shot in kept_screenshots:
        section = shot.get('section', '其他')
        if section in sections:
            sections[section].append(shot)
        else:
            sections['实践经验'].append(shot)

    markdown_snippets = {}
    for section, shots in sections.items():
        if shots:
            snippets = []
            for shot in shots:
                caption = shot.get('caption', '截图')
                filename = shot.get('filename', 'image.jpg')
                snippets.append(f"![{caption}](images/{filename})")
            markdown_snippets[section] = '\n\n'.join(snippets)

    return markdown_snippets

def main():
    print("截图分析和筛选工具")
    print("=" * 50)
    print(ANALYSIS_CRITERIA)
    print("\n使用方法：")
    print("1. 运行 extract_frames.py 提取截图")
    print("2. 使用 Claude 的 Read 工具逐张分析截图")
    print("3. 根据分析结果筛选和重命名截图")
    print("4. 将保留的截图插入到 Markdown 文档中")

if __name__ == '__main__':
    main()
