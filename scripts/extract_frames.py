#!/usr/bin/env python3
"""
视频关键帧提取脚本
从视频中提取关键帧截图，用于文档配图
"""
import subprocess
import os
import sys
import json
import re

def timestamp_to_seconds(ts):
    """将时间戳转换为秒数"""
    if ',' in ts:
        ts = ts.replace(',', '.')
    parts = ts.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    else:
        return float(ts)

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
            'start_sec': timestamp_to_seconds(start),
            'end_sec': timestamp_to_seconds(end),
            'text': text.strip()
        })
    return segments

def get_video_duration(video_path):
    """获取视频时长"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout.strip():
        return float(result.stdout.strip())
    return None

def extract_frames(video_path, output_dir, timestamps):
    """提取指定时间点的帧"""
    os.makedirs(output_dir, exist_ok=True)
    screenshots = []

    for i, ts in enumerate(timestamps):
        output_file = os.path.join(output_dir, f"{i+1:02d}_frame_{int(ts)}s.jpg")
        cmd = [
            'ffmpeg', '-ss', str(ts), '-i', video_path,
            '-vframes', '1', '-q:v', '2', output_file, '-y'
        ]
        subprocess.run(cmd, capture_output=True)

        if os.path.exists(output_file):
            screenshots.append({
                'path': output_file,
                'filename': os.path.basename(output_file),
                'timestamp': ts,
                'timestamp_str': f"{int(ts//60):02d}:{int(ts%60):02d}"
            })
            print(f"  提取截图 {i+1}: {output_file} (时间: {int(ts//60):02d}:{int(ts%60):02d})")

    return screenshots

def calculate_timestamps(duration, srt_segments=None, max_frames=12, min_interval=60):
    """计算截图时间点"""
    timestamps = []

    if duration <= 0:
        return timestamps

    # 方法1：基于字幕内容的关键点（如果有字幕）
    if srt_segments and len(srt_segments) > 0:
        # 找到内容变化的关键点
        # 简单策略：在长停顿后的位置截图（可能是新话题开始）
        for i in range(1, len(srt_segments)):
            gap = srt_segments[i]['start_sec'] - srt_segments[i-1]['end_sec']
            if gap > 2.0:  # 超过2秒的停顿
                ts = srt_segments[i]['start_sec']
                if ts > 30 and ts < duration - 30:
                    timestamps.append(ts)

    # 方法2：均匀分布补充
    interval = max(min_interval, duration / max_frames)
    t = 30  # 从30秒开始
    while t < duration - 30 and len(timestamps) < max_frames:
        # 避免与已有时间点太近
        if not any(abs(t - ts) < min_interval/2 for ts in timestamps):
            timestamps.append(t)
        t += interval

    # 排序并限制数量
    timestamps = sorted(set(timestamps))[:max_frames]

    return timestamps

def main():
    if len(sys.argv) < 3:
        print("用法: python extract_frames.py <video_path> <output_dir> [srt_path]")
        print("例如: python extract_frames.py video.mp4 ./images video.srt")
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    srt_path = sys.argv[3] if len(sys.argv) > 3 else None

    # 检查视频文件
    if not os.path.exists(video_path):
        print(f"错误: 视频文件不存在: {video_path}")
        sys.exit(1)

    # 获取视频时长
    duration = get_video_duration(video_path)
    if not duration:
        print("错误: 无法获取视频时长")
        sys.exit(1)

    print(f"视频时长: {duration:.1f}秒 ({duration/60:.1f}分钟)")

    # 解析字幕（如果有）
    srt_segments = None
    if srt_path and os.path.exists(srt_path):
        srt_segments = parse_srt(srt_path)
        print(f"字幕片段数: {len(srt_segments)}")

    # 计算截图时间点
    timestamps = calculate_timestamps(duration, srt_segments)
    print(f"计划提取 {len(timestamps)} 张截图")

    # 提取截图
    screenshots = extract_frames(video_path, output_dir, timestamps)

    # 保存结果
    result = {
        'video_path': video_path,
        'duration': duration,
        'screenshots': screenshots
    }

    result_path = os.path.join(output_dir, 'screenshots_info.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n提取完成！共 {len(screenshots)} 张截图")
    print(f"截图信息保存到: {result_path}")

if __name__ == '__main__':
    main()
