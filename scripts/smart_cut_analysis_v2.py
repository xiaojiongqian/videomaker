#!/usr/bin/env python3
"""智能视频剪辑分析脚本 V2 - 改进版
改进点：
1. 更智能的语气词识别和剪除
2. 全局扫描策略，避免剪辑不均衡
3. 优先使用加速播放（最多1.5倍），其次才剪除内容
"""
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
            'priority': 10,  # 默认优先级（数字越小越优先移除）
            'importance': 5,  # 内容重要性（1-10，越高越重要）
            'speed': 1.0  # 播放速度（1.0=正常，1.5=加速）
        })
    return segments

def similarity(text1, text2):
    """简单的文本相似度计算"""
    set1, set2 = set(text1), set(text2)
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

def is_filler_phrase(text):
    """判断是否为语气词短语"""
    # 扩展的语气词列表
    filler_words = {
        # 中文语气词
        '嗯', '啊', '呃', '哦', '喔', '唔', '額', '嗯哼', '嗯嗯', '啊啊', '呃呃',
        # 填充词
        '那个', '就是', '然后', '这个', '那么', '所以说', '对吧', '你知道',
        '怎么说呢', '就是说', '我觉得', '我认为', '应该说', '可以说',
        # 单字
        '那', '对', '就', '这', '是', '不', '可以', '好', '行', '嗯',
        # 英文
        'um', 'uh', 'er', 'ah', 'like', 'you know', 'I mean', 'OK', 'ok', 'yeah', 'well'
    }

    # 纯语气词
    if text in filler_words:
        return True

    # 只包含语气词的组合（如"嗯 那个 就是"）
    words = text.split()
    if all(w in filler_words for w in words):
        return True

    # 重复的语气词（如"那个那个那个"）
    if len(set(words)) == 1 and words[0] in filler_words:
        return True

    return False

def calculate_importance(seg, all_segments, index):
    """计算片段的内容重要性（1-10分）"""
    text = seg['text'].strip()
    importance = 5  # 基础分

    # 1. 长度因素（长文本通常更重要）
    text_len = len(text)
    if text_len > 30:
        importance += 3
    elif text_len > 15:
        importance += 2
    elif text_len > 8:
        importance += 1
    elif text_len <= 3:
        importance -= 2

    # 2. 关键词因素（包含重要概念的片段）
    important_keywords = [
        # 技术关键词
        '实现', '原理', '方法', '步骤', '流程', '架构', '设计', '算法', '优化',
        '问题', '解决', '关键', '重要', '核心', '本质', '总结', '结论',
        # 逻辑连接词
        '首先', '其次', '最后', '因此', '所以', '但是', '然而', '不过',
        '第一', '第二', '第三', '总之', '综上',
        # 英文关键词
        'implement', 'solution', 'key', 'important', 'core', 'main', 'first', 'second',
        'finally', 'therefore', 'however', 'but', 'so', 'because'
    ]

    if any(kw in text for kw in important_keywords):
        importance += 2

    # 3. 问句（通常引出重要内容）
    if '?' in text or '？' in text or text.startswith(('为什么', '怎么', '如何', 'why', 'how', 'what')):
        importance += 1

    # 4. 位置因素（开头和结尾的片段通常更重要）
    total_segments = len(all_segments)
    if index < total_segments * 0.1:  # 前10%
        importance += 1
    elif index > total_segments * 0.9:  # 后10%
        importance += 1

    # 5. 与前后文的连贯性
    if index > 0:
        prev_text = all_segments[index - 1]['text']
        if similarity(text, prev_text) < 0.3:  # 与前文差异大，可能是新话题
            importance += 1

    # 限制在1-10范围内
    return max(1, min(10, importance))

def analyze_segments(segments):
    """分析并标记冗余片段 - 分层策略
    第1层：裁剪没声音部分（空白片段）
    第2层：剪语气词和填充词
    第3层：剪重复语义内容
    """

    # 第一遍：计算所有片段的重要性
    for i, seg in enumerate(segments):
        seg['importance'] = calculate_importance(seg, segments, i)

    # 第1层：空白片段（没声音）
    print("  第1层：检测空白片段（无声音）")
    empty_count = 0
    for seg in segments:
        text = seg['text'].strip()
        if not text:
            seg['keep'] = False
            seg['reason'] = 'empty'
            seg['priority'] = 1
            seg['importance'] = 0
            empty_count += 1
    print(f"    找到 {empty_count} 个空白片段")

    # 第2层：语气词和填充词
    print("  第2层：检测语气词和填充词")
    filler_count = 0
    for seg in segments:
        if not seg['keep']:
            continue
        text = seg['text'].strip()

        # 纯语气词或填充词
        if is_filler_phrase(text):
            seg['keep'] = False
            seg['reason'] = 'filler'
            seg['priority'] = 1
            seg['importance'] = 0
            filler_count += 1
            continue

        # 重复的单字（如 "选择选择选择"）
        if len(set(text)) <= 3 and len(text) > 2:
            seg['keep'] = False
            seg['reason'] = 'repetitive'
            seg['priority'] = 1
            seg['importance'] = 0
            filler_count += 1
            continue

        # 非常短的片段（少于3个字符）
        if len(text) <= 2:
            seg['keep'] = False
            seg['reason'] = 'too_short'
            seg['priority'] = 1
            seg['importance'] = 0
            filler_count += 1
            continue
    print(f"    找到 {filler_count} 个语气词/填充词片段")

    # 第3层：重复语义内容
    print("  第3层：检测重复语义内容")
    duplicate_count = 0

    # 检测相邻重复内容（保留重要性更高的）
    for i in range(1, len(segments)):
        if not segments[i]['keep'] or not segments[i-1]['keep']:
            continue

        if similarity(segments[i]['text'], segments[i-1]['text']) > 0.8:
            # 比较重要性，移除较低的
            if segments[i]['importance'] <= segments[i-1]['importance']:
                segments[i]['keep'] = False
                segments[i]['reason'] = 'duplicate'
                segments[i]['priority'] = 2
                duplicate_count += 1
            else:
                segments[i-1]['keep'] = False
                segments[i-1]['reason'] = 'duplicate'
                segments[i-1]['priority'] = 2
                duplicate_count += 1

    # 检测口误/自我纠正（也属于重复/冗余）
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
                duplicate_count += 1

    print(f"    找到 {duplicate_count} 个重复/纠正片段")

    return segments

def adjust_to_target_v2(segments, original_duration, target_reduction):
    """改进的目标调整策略：
    1. 优先裁剪没声音部分（已在analyze_segments中处理）
    2. 然后剪语气词（已在analyze_segments中处理）
    3. 再剪重复语义内容（已在analyze_segments中处理）
    4. 然后使用加速播放（最多1.5倍）
    5. 最后还不够才剪除有价值内容
    """
    if target_reduction is None:
        return segments, 1.0  # 返回片段和全局速度

    target_duration = original_duration * (1 - target_reduction)

    # 计算当前保留时长
    current_duration = sum(
        seg['end_sec'] - seg['start_sec']
        for seg in segments if seg['keep']
    )

    print(f"\n目标调整策略（分层处理）：")
    print(f"  原始时长: {original_duration:.1f}秒")
    print(f"  目标时长: {target_duration:.1f}秒")
    print(f"  当前保留: {current_duration:.1f}秒 (已剪除空白/语气词/重复)")
    print(f"  需要减少: {current_duration - target_duration:.1f}秒")

    # 如果已经达到目标
    if current_duration <= target_duration:
        print(f"  ✓ 已达到目标，无需进一步调整")
        return segments, 1.0

    # 计算需要减少的比例
    reduction_needed = (current_duration - target_duration) / current_duration

    max_speed = 1.5
    max_speed_reduction = 1 - (1 / max_speed)  # 1.5倍速可以减少33%的时长

    # 策略4: 优先使用加速播放（最多1.5倍）
    if reduction_needed <= max_speed_reduction:
        # 计算需要的播放速度
        speed = 1 / (1 - reduction_needed)
        speed = min(speed, max_speed)  # 限制最大1.5倍

        print(f"  第4层策略: 使用 {speed:.2f}x 加速播放")
        print(f"  预计时长: {current_duration / speed:.1f}秒")

        # 标记所有保留片段使用加速
        for seg in segments:
            if seg['keep']:
                seg['speed'] = speed

        return segments, speed

    # 策略5: 如果加速还不够，先用1.5倍加速，再剪除低价值内容
    else:
        print(f"  第4层策略: 使用 1.5x 加速播放")

        # 先应用1.5倍加速
        for seg in segments:
            if seg['keep']:
                seg['speed'] = max_speed

        # 加速后的时长
        duration_after_speed = current_duration / max_speed
        print(f"  加速后时长: {duration_after_speed:.1f}秒")

        # 如果加速后还不够，需要剪除内容
        if duration_after_speed > target_duration:
            need_to_remove = duration_after_speed - target_duration
            print(f"\n  第5层策略: 剪除低价值内容")
            print(f"  还需剪除: {need_to_remove:.1f}秒")

            # 按重要性排序（低重要性优先移除）
            kept_segments = [s for s in segments if s['keep']]
            candidates = sorted(kept_segments, key=lambda x: (x['importance'], len(x['text'])))

            removed_duration = 0
            removed_count = 0

            for seg in candidates:
                if removed_duration >= need_to_remove:
                    break

                seg_duration = (seg['end_sec'] - seg['start_sec']) / max_speed

                # 避免移除高重要性内容（importance >= 7）
                if seg['importance'] >= 7:
                    print(f"    跳过高价值内容 (重要性{seg['importance']}): {seg['text'][:30]}...")
                    continue

                seg['keep'] = False
                seg['reason'] = 'target_reduction'
                removed_duration += seg_duration
                removed_count += 1

            print(f"  剪除片段: {removed_count} 个")
            print(f"  剪除时长: {removed_duration:.1f}秒")

            # 重新计算最终时长
            final_duration = sum(
                (seg['end_sec'] - seg['start_sec']) / seg['speed']
                for seg in segments if seg['keep']
            )
            print(f"  最终时长: {final_duration:.1f}秒")

        return segments, max_speed

def merge_adjacent_segments(segments, max_gap=0.5):
    """合并相邻的保留片段（间隔小于max_gap秒）"""
    kept = [s for s in segments if s['keep']]
    if not kept:
        return []

    merged = []
    current = {
        'start_sec': kept[0]['start_sec'],
        'end_sec': kept[0]['end_sec'],
        'text': kept[0]['text'],
        'speed': kept[0].get('speed', 1.0)
    }

    for seg in kept[1:]:
        gap = seg['start_sec'] - current['end_sec']
        # 考虑播放速度的影响
        effective_gap = gap / current['speed']

        if effective_gap <= max_gap and seg.get('speed', 1.0) == current['speed']:
            # 合并（相同速度）
            current['end_sec'] = seg['end_sec']
            current['text'] += ' ' + seg['text']
        else:
            merged.append(current)
            current = {
                'start_sec': seg['start_sec'],
                'end_sec': seg['end_sec'],
                'text': seg['text'],
                'speed': seg.get('speed', 1.0)
            }

    merged.append(current)
    return merged

def main():
    if len(sys.argv) < 2:
        print("用法: python smart_cut_analysis_v2.py <srt_path> [target_reduction]")
        print("例如: python smart_cut_analysis_v2.py video.srt 0.6")
        print("      python smart_cut_analysis_v2.py video.srt  # 智能分析，不指定压缩比")
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

    # 全局分析冗余内容
    print("\n=== 智能剪辑分层策略 ===")
    print("策略顺序：")
    print("  1. 裁剪没声音部分（空白片段）")
    print("  2. 剪语气词和填充词")
    print("  3. 剪重复语义内容")
    print("  4. 使用加速播放（最多1.5倍）")
    print("  5. 剪除低价值内容（最后手段）")
    print("\n执行第1-3层分析...")
    segments = analyze_segments(segments)

    # 统计初步分析结果
    removed_count = sum(1 for s in segments if not s['keep'])
    removed_reasons = {}
    for s in segments:
        if not s['keep']:
            reason = s['reason']
            removed_reasons[reason] = removed_reasons.get(reason, 0) + 1

    print(f"\n第1-3层处理结果：")
    print(f"  移除片段总数: {removed_count}")
    for reason, count in removed_reasons.items():
        reason_name = {
            'empty': '空白片段',
            'filler': '语气词/填充词',
            'repetitive': '重复字符',
            'too_short': '过短片段',
            'duplicate': '重复内容',
            'correction': '口误纠正'
        }.get(reason, reason)
        print(f"    - {reason_name}: {count}")

    # 计算初步保留时长
    kept_duration = sum(s['end_sec'] - s['start_sec'] for s in segments if s['keep'])
    print(f"  保留时长: {kept_duration:.2f}秒 ({kept_duration/60:.1f}分钟)")
    print(f"  压缩比: {(1 - kept_duration/original_duration)*100:.1f}%")

    # 根据目标调整（优先加速）
    if target_reduction:
        segments, global_speed = adjust_to_target_v2(segments, original_duration, target_reduction)
    else:
        global_speed = 1.0

    # 统计最终结果
    final_kept_count = sum(1 for s in segments if s['keep'])
    final_kept_duration = sum(
        (s['end_sec'] - s['start_sec']) / s.get('speed', 1.0)
        for s in segments if s['keep']
    )

    print(f"\n=== 最终结果 ===")
    print(f"保留片段: {final_kept_count} 个")
    print(f"最终时长: {final_kept_duration:.2f}秒 ({final_kept_duration/60:.1f}分钟)")
    print(f"最终压缩比: {(1 - final_kept_duration/original_duration)*100:.1f}%")
    if global_speed > 1.0:
        print(f"播放速度: {global_speed:.2f}x")

    # 合并相邻片段
    merged = merge_adjacent_segments(segments, max_gap=0.3)
    print(f"合并后片段数: {len(merged)}")

    # 输出保留的内容摘要（按重要性排序）
    print("\n=== 保留的主要内容（按重要性排序）===")
    kept_with_importance = [(s, s['importance']) for s in segments if s['keep'] and len(s['text']) > 5]
    kept_with_importance.sort(key=lambda x: x[1], reverse=True)

    for i, (seg, importance) in enumerate(kept_with_importance[:15]):
        speed_mark = f" [{seg['speed']:.1f}x]" if seg.get('speed', 1.0) > 1.0 else ""
        print(f"[重要性:{importance}]{speed_mark} [{seg['start']}] {seg['text']}")

    if len(kept_with_importance) > 15:
        print(f"... 还有 {len(kept_with_importance) - 15} 条")

    # 保存分析结果
    base_name = os.path.splitext(srt_path)[0]
    result_path = base_name + '_cut_result.json'

    result = {
        'original_duration': original_duration,
        'final_duration': final_kept_duration,
        'compression_ratio': (1 - final_kept_duration/original_duration),
        'global_speed': global_speed,
        'total_segments': len(segments),
        'kept_segments': final_kept_count,
        'merged_segments': len(merged),
        'merged': merged,
        'strategy': 'speed_first' if global_speed > 1.0 else 'cut_only'
    }

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n分析结果已保存到 {result_path}")

if __name__ == '__main__':
    main()
