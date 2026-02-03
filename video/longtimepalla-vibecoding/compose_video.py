#!/usr/bin/env python3
"""
4K 视频合成 - 调整转场时间点
"""

import os
import subprocess

def get_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 0

def format_time(seconds):
    """将秒数转换为分:秒格式"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}分{s}秒"

def main():
    main_video = "并行长时间使用codex_cut_cn_final.mp4"
    transitions_dir = "transitions_4k"
    
    # 调整后的转场时间点
    # 任务处理流程移到第4分钟 (240秒)
    transitions = [
        (0, f"{transitions_dir}/背景与需求_4k.mp4", "背景与需求"),
        (45, f"{transitions_dir}/解决方案_4k.mp4", "解决方案"),
        (240, f"{transitions_dir}/任务处理流程_4k.mp4", "任务处理流程"),  # 调整到4分钟
    ]
    
    main_dur = get_duration(main_video)
    print(f"主视频时长: {main_dur:.2f}s ({format_time(main_dur)})\n")
    
    # 计算预期输出时长
    trans_total = sum(get_duration(t[1]) for t in transitions)
    print(f"转场总时长: {trans_total:.2f}s")
    print(f"预计输出时长: {main_dur + trans_total:.2f}s\n")
    
    print("转场插入位置:")
    for i, (insert_at, trans_file, name) in enumerate(transitions):
        trans_dur = get_duration(trans_file)
        print(f"  {i+1}. {name} - {insert_at}s ({format_time(insert_at)}) - 时长{trans_dur:.2f}s")
    
    temp_dir = "temp_4k_compose_v2"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 准备输入文件列表
    input_files = []
    filter_parts = []
    input_idx = 0
    
    last_end = 0
    segment_count = 0
    
    for i, (insert_at, trans_file, name) in enumerate(transitions):
        trans_dur = get_duration(trans_file)
        print(f"\n转场 {i+1}: {name}")
        print(f"  插入位置: {insert_at}s ({format_time(insert_at)})")
        print(f"  转场时长: {trans_dur:.2f}s")
        
        # 1. 切分主视频段（插入点之前）
        if insert_at > last_end:
            main_segment = f"{temp_dir}/main_seg_{i:02d}.mp4"
            seg_dur = insert_at - last_end
            print(f"  切分主视频: {last_end:.1f}s - {insert_at:.1f}s ({seg_dur:.1f}s)")
            
            cmd = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-i', main_video,
                '-ss', str(last_end),
                '-t', str(seg_dur),
                '-c', 'copy',
                '-avoid_negative_ts', 'make_zero',
                main_segment
            ]
            subprocess.run(cmd)
            
            if os.path.exists(main_segment) and os.path.getsize(main_segment) > 10000:
                input_files.append(main_segment)
                filter_parts.append(f"[{input_idx}:v:0][{input_idx}:a:0]")
                input_idx += 1
                segment_count += 1
        
        # 2. 添加转场视频
        print(f"  添加转场: {name}")
        input_files.append(trans_file)
        filter_parts.append(f"[{input_idx}:v:0][{input_idx}:a:0]")
        input_idx += 1
        segment_count += 1
        
        last_end = insert_at
    
    # 3. 添加最后的主视频段
    if last_end < main_dur:
        final_segment = f"{temp_dir}/main_seg_final.mp4"
        final_dur = main_dur - last_end
        print(f"\n结尾段: {last_end:.1f}s - {main_dur:.1f}s ({final_dur:.1f}s)")
        
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', main_video,
            '-ss', str(last_end),
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            final_segment
        ]
        subprocess.run(cmd)
        
        if os.path.exists(final_segment) and os.path.getsize(final_segment) > 10000:
            input_files.append(final_segment)
            filter_parts.append(f"[{input_idx}:v:0][{input_idx}:a:0]")
            segment_count += 1
    
    # 构建 concat filter
    filter_complex = ''.join(filter_parts) + f"concat=n={segment_count}:v=1:a=1[outv][outa]"
    
    print(f"\n{'='*60}")
    print(f"合成视频...")
    print(f"输入片段: {segment_count}")
    print(f"{'='*60}\n")
    
    # 构建 FFmpeg 命令
    inputs = []
    for f in input_files:
        inputs.extend(['-i', f])
    
    output = "video_final_4k_adjusted.mp4"
    
    cmd = [
        'ffmpeg', '-y', '-hide_banner',
    ] + inputs + [
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', '[outa]',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-profile:v', 'high',
        '-level:v', '5.2',
        '-crf', '18',
        '-preset', 'slow',
        '-r', '30',
        '-g', '60',
        '-c:a', 'aac',
        '-b:a', '192k',
        output
    ]
    
    print("开始渲染（这可能需要几分钟）...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        out_dur = get_duration(output)
        file_size = os.path.getsize(output) / 1024 / 1024
        
        print(f"\n{'='*60}")
        print(f"✅ 合成完成!")
        print(f"{'='*60}")
        print(f"输出文件: {output}")
        print(f"视频时长: {out_dur:.2f}s ({format_time(out_dur)})")
        print(f"文件大小: {file_size:.1f}MB")
        
        # 验证分辨率
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
               '-show_entries', 'stream=width,height',
               '-of', 'default=noprint_wrappers=1', output]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(f"分辨率: {r.stdout.strip()}")
        
    else:
        print(f"\n❌ 合成失败!")
        print(f"错误: {result.stderr[:500]}")

if __name__ == "__main__":
    main()
