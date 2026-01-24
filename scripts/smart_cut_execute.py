#!/usr/bin/env python3
"""高效 FFmpeg 剪辑 - 使用 trim/concat 滤镜，保留原分辨率"""
import json
import subprocess
import os
import sys

def seconds_to_timestamp(seconds):
    """将秒数转换为 SRT 时间戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_new_srt(segments, output_srt_path):
    """为剪辑后的视频生成新字幕"""
    new_srt = ""
    current_time = 0.0

    for i, seg in enumerate(segments, 1):
        duration = seg['end_sec'] - seg['start_sec']
        start = seconds_to_timestamp(current_time)
        end = seconds_to_timestamp(current_time + duration)

        new_srt += f"{i}\n{start} --> {end}\n{seg['text']}\n\n"
        current_time += duration

    with open(output_srt_path, 'w', encoding='utf-8') as f:
        f.write(new_srt)

    return output_srt_path

def main():
    if len(sys.argv) < 3:
        print("用法: python smart_cut_execute.py <result_json> <input_video>")
        sys.exit(1)

    result_path = sys.argv[1]
    input_path = sys.argv[2]

    # 读取分析结果
    with open(result_path, 'r', encoding='utf-8') as f:
        result = json.load(f)

    segments = result['merged']

    # 生成输出路径
    base_name = os.path.splitext(input_path)[0]
    output_path = base_name + '_cut.mp4'
    output_srt = base_name + '_cut.srt'
    temp_dir = os.path.dirname(input_path) + '/temp_batch'

    os.makedirs(temp_dir, exist_ok=True)

    # 由于片段较多，分批处理
    batch_size = 20
    batch_files = []

    total_batches = (len(segments) + batch_size - 1) // batch_size

    for batch_idx in range(0, len(segments), batch_size):
        batch_num = batch_idx // batch_size + 1
        batch_segments = segments[batch_idx:batch_idx + batch_size]
        batch_file = f'{temp_dir}/batch_{batch_idx:04d}.mp4'
        batch_files.append(batch_file)

        # 构建 filter_complex
        filter_parts = []
        concat_v = []
        concat_a = []

        for i, seg in enumerate(batch_segments):
            start = seg['start_sec']
            end = seg['end_sec']
            # 使用 trim 和 atrim 精确裁剪
            filter_parts.append(
                f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{i}]"
            )
            filter_parts.append(
                f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[a{i}]"
            )
            concat_v.append(f"[v{i}]")
            concat_a.append(f"[a{i}]")

        n = len(batch_segments)
        filter_complex = ";".join(filter_parts)
        filter_complex += f";{''.join(concat_v)}concat=n={n}:v=1:a=0[outv]"
        filter_complex += f";{''.join(concat_a)}concat=n={n}:v=0:a=1[outa]"

        # 执行 FFmpeg 命令 - 保留原分辨率，使用高质量编码
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-filter_complex', filter_complex,
            '-map', '[outv]', '-map', '[outa]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',  # 高质量
            '-c:a', 'aac', '-b:a', '192k',
            batch_file
        ]

        print(f"处理批次 {batch_num}/{total_batches}...")
        subprocess.run(cmd, capture_output=True)
        print(f"  批次 {batch_num} 完成")

    # 合并所有批次
    if len(batch_files) == 1:
        # 只有一个批次，直接重命名
        os.rename(batch_files[0], output_path)
    else:
        # 多个批次，使用 concat demuxer 合并
        concat_list = f'{temp_dir}/concat_list.txt'
        with open(concat_list, 'w') as f:
            for bf in batch_files:
                f.write(f"file '{bf}'\n")

        print("合并所有批次...")
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_list, '-c', 'copy', output_path
        ]
        subprocess.run(cmd, capture_output=True)

    # 生成同步字幕
    print("生成同步字幕...")
    generate_new_srt(segments, output_srt)

    # 清理临时文件
    print("清理临时文件...")
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"\n剪辑完成！")
    print(f"输出视频: {output_path}")
    print(f"输出字幕: {output_srt}")

    # 验证输出文件
    if os.path.exists(output_path):
        # 获取输出文件时长
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', output_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.stdout.strip():
            duration = float(result.stdout.strip())
            print(f"输出文件时长: {duration:.1f}秒 ({duration/60:.1f}分钟)")

        # 获取文件大小
        size = os.path.getsize(output_path)
        print(f"输出文件大小: {size / 1024 / 1024:.1f} MB")

if __name__ == '__main__':
    main()
