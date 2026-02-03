#!/usr/bin/env python3
"""渲染 4K 分辨率的转场动画（带原始音频）"""

import os
import subprocess
import shlex

TRANSITIONS = [
    {
        "name": "背景与需求",
        "text": "背景与需求",
        "audio_file": "audio/背景与需求.m4a",
        "style": "fade",
        "bg_color": "#1a1a2e",
        "text_color": "#ffffff",
    },
    {
        "name": "解决方案",
        "text": "解决方案",
        "audio_file": "audio/解决方案.m4a",
        "style": "scale",
        "bg_color": "#16213e",
        "text_color": "#4a9eff",
    },
    {
        "name": "任务处理流程",
        "text": "任务处理流程",
        "audio_file": "audio/任务处理流程.m4a",
        "style": "slide",
        "bg_color": "#0f3460",
        "text_color": "#e94560",
    },
]

WIDTH = 3840
HEIGHT = 2164
FPS = 30
FONT_FILE = "/System/Library/Fonts/STHeiti Medium.ttc"

def get_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 0

def render_transition(trans, output_dir):
    name = trans["name"]
    text = trans["text"]
    audio_file = trans["audio_file"]
    style = trans["style"]
    bg_color = trans["bg_color"][1:]
    text_color = trans["text_color"][1:]
    
    output_file = os.path.join(output_dir, f"{name}_4k.mp4")
    
    duration = get_duration(audio_file)
    print(f"\n🎬 {name}")
    print(f"   文字: {text}")
    print(f"   时长: {duration:.2f}s")
    
    font_size = 160
    
    # 构建滤镜表达式
    if style == "fade":
        alpha_expr = f"'if(lt(t,0.3),t/0.3,if(lt(t,{duration}-0.3),1,({duration}-t)/0.3))'"
        x_expr = "(w-text_w)/2"
    elif style == "scale":
        alpha_expr = f"'if(lt(t,0.3),t/0.3,if(lt(t,{duration}-0.3),1,({duration}-t)/0.3))'"
        x_expr = "(w-text_w)/2"
    elif style == "slide":
        alpha_expr = f"'if(lt(t,{duration}-0.3),1,({duration}-t)/0.3)'"
        x_expr = f"'if(lt(t,0.3),(w-text_w)/2-400+400*t/0.3,(w-text_w)/2)'"
    else:
        alpha_expr = "1"
        x_expr = "(w-text_w)/2"
    
    # 构建完整的滤镜字符串
    vf = f"drawtext=fontfile='{FONT_FILE}':text='{text}':fontcolor={text_color}:fontsize={font_size}:x={x_expr}:y=(h-text_h)/2:alpha={alpha_expr}"
    
    # 构建 FFmpeg 命令
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'lavfi', '-i', f'color=c={bg_color}:s={WIDTH}x{HEIGHT}:d={duration}',
        '-i', audio_file,
        '-vf', vf,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-profile:v', 'high',
        '-level:v', '5.2',
        '-crf', '18',
        '-preset', 'medium',
        '-r', str(FPS),
        '-g', '60',
        '-keyint_min', '60',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        out_dur = get_duration(output_file)
        file_size = os.path.getsize(output_file) / 1024
        print(f"   ✅ 完成: {output_file}")
        print(f"   📊 时长: {out_dur:.2f}s, 大小: {file_size:.1f}KB")
        return output_file
    else:
        print(f"   ❌ 失败: {result.stderr[:400]}")
        return None

def main():
    output_dir = "transitions_4k"
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*60)
    print("🎬 渲染 4K 转场动画")
    print("="*60)
    
    results = []
    for trans in TRANSITIONS:
        result = render_transition(trans, output_dir)
        if result:
            results.append(result)
    
    print(f"\n{'='*60}")
    print(f"✅ 完成! 共渲染 {len(results)} 个转场")
    print(f"{'='*60}")
    
    return results

if __name__ == "__main__":
    main()
