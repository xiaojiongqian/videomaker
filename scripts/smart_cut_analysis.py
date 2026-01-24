#!/usr/bin/env python3
"""智能视频剪辑分析脚本 - 通用版本"""
import re
import json
import sys
import os

def timestamp_to_seconds(ts):
    """将时间戳转换为秒数"""
    h, m, s = ts.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def seconds_to_timestamp(seconds):
    """将秒数转换为 SRT 时间戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

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
            'keep': True,
            'reason': None,
            'priority': 10
        })
    return segments

def similarity(text1, text2):
    """简单的文本相似度计算"""
    set1, set2 = set(text1), set(text2)
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

def analyze_segments(segments):
    """分析并标记冗余片段"""

    # 语气词和填充词
    filler_words = {'嗯', '啊', '呃', '那个', '就是', '然后', '这个', '那么', '所以说', '对吧',
                    '那', '对', '就', '这', '是', '不', '可以', 'OK', 'ok', '好', '嗯嗯',
                    '啊啊', '呃呃', '哦', '喔', '唔', '額', '嗯哼'}

    # 单字或双字的无意义片段
    single_fillers = {'那', '对', '就', '这', '是', '不', '然后', '这个', '那个', '就是',
                      '所以', '因为', '但是', '而且', '还有', '可以', '能', '会', '要',
                      'OK', 'ok', '好', '對', '這個', '那個', '嗯', '啊', '呃', '哦',
                      '選擇', '自測', '那', '嗯', '啊'}

    for seg in segments:
        text = seg['text'].strip()

        # 1. 空白片段
        if not text:
            seg['keep'] = False
            seg['reason'] = 'empty'
            seg['priority'] = 1
            continue

        # 2. 纯语气词或单字填充
        if text in single_fillers or (len(text) <= 2 and any(w in text for w in filler_words)):
            seg['keep'] = False
            seg['reason'] = 'filler'
            seg['priority'] = 1
            continue

        # 3. 重复的单字（如 "选择选择选择"）
        if len(set(text)) <= 3 and len(text) > 2:
            seg['keep'] = False
            seg['reason'] = 'repetitive'
            seg['priority'] = 1
            continue

        # 4. 非常短的片段（少于3个字符且不是有意义的词）
        if len(text) <= 2:
            seg['keep'] = False
            seg['reason'] = 'too_short'
            seg['priority'] = 1
            continue

    # 5. 检测相邻重复内容
    for i in range(1, len(segments)):
        if not segments[i]['keep']:
            continue
        if similarity(segments[i]['text'], segments[i-1]['text']) > 0.8:
            seg_len = len(segments[i]['text'])
            prev_len = len(segments[i-1]['text'])
            # 保留较长的那个
            if seg_len <= prev_len:
                segments[i]['keep'] = False
                segments[i]['reason'] = 'duplicate'
                segments[i]['priority'] = 2
            else:
                segments[i-1]['keep'] = False
                segments[i-1]['reason'] = 'duplicate'
                segments[i-1]['priority'] = 2

    # 6. 检测口误/自我纠正
    correction_patterns = ['不是', '我是说', '不对', '应该是', '错了', '重来', '不是不是']
    for seg in segments:
        if not seg['keep']:
            continue
        if any(p in seg['text'] for p in correction_patterns):
            # 只标记短的纠正片段
            if len(seg['text']) < 10:
                seg['keep'] = False
                seg['reason'] = 'correction'
                seg['priority'] = 3

    return segments

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
        return segments

    # 按内容价值排序（短文本、低优先级先移除）
    kept_segments = [s for s in segments if s['keep']]

    # 评估每个片段的价值
    for seg in kept_segments:
        text_len = len(seg['text'])
        # 短片段价值低
        if text_len < 5:
            seg['value'] = 1
        elif text_len < 10:
            seg['value'] = 2
        elif text_len < 15:
            seg['value'] = 3
        else:
            seg['value'] = 4

    # 按价值排序（低价值先移除）
    candidates = sorted(kept_segments, key=lambda x: (x['value'], len(x['text'])))

    for seg in candidates:
        if current_duration <= target_duration:
            break
        seg_duration = seg['end_sec'] - seg['start_sec']
        seg['keep'] = False
        seg['reason'] = 'target_reduction'
        current_duration -= seg_duration

    return segments

def merge_adjacent_segments(segments, max_gap=0.5):
    """合并相邻的保留片段（间隔小于max_gap秒）"""
    kept = [s for s in segments if s['keep']]
    if not kept:
        return []

    merged = []
    current = {
        'start_sec': kept[0]['start_sec'],
        'end_sec': kept[0]['end_sec'],
        'text': kept[0]['text']
    }

    for seg in kept[1:]:
        gap = seg['start_sec'] - current['end_sec']
        if gap <= max_gap:
            # 合并
            current['end_sec'] = seg['end_sec']
            current['text'] += ' ' + seg['text']
        else:
            merged.append(current)
            current = {
                'start_sec': seg['start_sec'],
                'end_sec': seg['end_sec'],
                'text': seg['text']
            }

    merged.append(current)
    return merged

def main():
    if len(sys.argv) < 2:
        print("用法: python smart_cut_analysis.py <srt_path> [target_reduction]")
        print("例如: python smart_cut_analysis.py video.srt 0.6")
        print("      python smart_cut_analysis.py video.srt  # 智能分析，不指定压缩比")
        sys.exit(1)

    srt_path = sys.argv[1]
    target_reduction = float(sys.argv[2]) if len(sys.argv) > 2 else None

    # 解析字幕
    segments = parse_srt(srt_path)
    print(f"总片段数: {len(segments)}")

    # 计算原始时长
    if segments:
        original_duration = segments[-1]['end_sec']
        print(f"原始时长: {original_duration:.2f}秒 ({original_duration/60:.1f}分钟)")
    else:
        print("没有找到字幕片段")
        return

    # 分析冗余内容
    segments = analyze_segments(segments)

    # 统计初步分析结果
    removed_count = sum(1 for s in segments if not s['keep'])
    removed_reasons = {}
    for s in segments:
        if not s['keep']:
            reason = s['reason']
            removed_reasons[reason] = removed_reasons.get(reason, 0) + 1

    print(f"\n初步分析移除: {removed_count} 个片段")
    for reason, count in removed_reasons.items():
        print(f"  - {reason}: {count}")

    # 计算初步保留时长
    kept_duration = sum(s['end_sec'] - s['start_sec'] for s in segments if s['keep'])
    print(f"初步保留时长: {kept_duration:.2f}秒 ({kept_duration/60:.1f}分钟)")
    print(f"初步压缩比: {(1 - kept_duration/original_duration)*100:.1f}%")

    # 根据目标调整
    if target_reduction:
        segments = adjust_to_target(segments, original_duration, target_reduction)

        # 统计调整后结果
        final_kept_duration = sum(s['end_sec'] - s['start_sec'] for s in segments if s['keep'])
        final_kept_count = sum(1 for s in segments if s['keep'])

        print(f"\n调整后保留: {final_kept_count} 个片段")
        print(f"调整后时长: {final_kept_duration:.2f}秒 ({final_kept_duration/60:.1f}分钟)")
        print(f"最终压缩比: {(1 - final_kept_duration/original_duration)*100:.1f}%")
    else:
        final_kept_duration = kept_duration

    # 合并相邻片段
    merged = merge_adjacent_segments(segments, max_gap=0.3)
    print(f"\n合并后片段数: {len(merged)}")

    # 输出保留的内容摘要
    print("\n=== 保留的主要内容 ===")
    kept_texts = []
    for seg in segments:
        if seg['keep'] and len(seg['text']) > 5:
            kept_texts.append(f"[{seg['start']}] {seg['text']}")

    # 只显示部分
    for i, text in enumerate(kept_texts[:20]):
        print(text)
    if len(kept_texts) > 20:
        print(f"... 还有 {len(kept_texts) - 20} 条")

    # 保存分析结果
    base_name = os.path.splitext(srt_path)[0]
    result_path = base_name + '_cut_result.json'

    result = {
        'original_duration': original_duration,
        'final_duration': final_kept_duration,
        'compression_ratio': (1 - final_kept_duration/original_duration),
        'total_segments': len(segments),
        'kept_segments': sum(1 for s in segments if s['keep']),
        'merged_segments': len(merged),
        'merged': merged
    }

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n分析结果已保存到 {result_path}")

if __name__ == '__main__':
    main()
