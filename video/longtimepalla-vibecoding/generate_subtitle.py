#!/usr/bin/env python3
"""
高质量字幕生成
支持 FunASR (优先) 和 Whisper (备用)
使用上下文感知 LLM 优化
"""

import os
import subprocess
import json
import tempfile
import sys

# ==================== 配置 ====================

VIDEO_FILE = "video_final_4k.mp4"
OUTPUT_SRT = "video_final_4k.srt"

# 尝试使用虚拟环境的 Python
VENV_PYTHON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python3")
SYSTEM_PYTHON = "python3"

# 检查虚拟环境
if os.path.exists(VENV_PYTHON):
    PYTHON_CMD = VENV_PYTHON
    print(f"使用虚拟环境 Python: {PYTHON_CMD}")
else:
    PYTHON_CMD = SYSTEM_PYTHON
    print(f"使用系统 Python: {PYTHON_CMD}")

# ==================== 步骤 1: 提取音频 ====================

def extract_audio(video_path, audio_path):
    """提取音频"""
    print("🎵 提取音频...")
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
        '-ar', '16000', '-ac', '1', audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ 完成")
        return True
    return False

# ==================== 步骤 2: ASR 识别 ====================

def transcribe_with_funasr(audio_path, output_json):
    """使用 FunASR 识别"""
    print("\n🎤 尝试 FunASR 识别...")
    
    funasr_script = f'''
import json
import os
import sys

os.environ["MODELSCOPE_CACHE"] = "{os.path.dirname(audio_path)}"

try:
    from funasr import AutoModel
    
    print("加载 FunASR 模型...")
    model = AutoModel(
        model="paraformer-zh",
        vad_model="fsmn-vad",
        punc_model="ct-punc",
    )
    
    print("开始识别...")
    result = model.generate(input="{audio_path}")
    
    with open("{output_json}", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("✅ FunASR 识别完成")
    
except Exception as e:
    print(f"❌ FunASR 失败: {{e}}")
    sys.exit(1)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(funasr_script)
        script_path = f.name
    
    try:
        result = subprocess.run(
            [PYTHON_CMD, script_path],
            capture_output=True, text=True, timeout=300
        )
        os.unlink(script_path)
        
        if result.returncode == 0 and os.path.exists(output_json):
            print(f"   ✅ FunASR 成功")
            return True, "funasr"
        else:
            print(f"   ⚠️  FunASR 失败: {result.stderr[:200]}")
            return False, None
    except Exception as e:
        os.unlink(script_path)
        print(f"   ⚠️  FunASR 错误: {e}")
        return False, None

def transcribe_with_whisper(audio_path, output_json):
    """使用 Whisper 识别（备用）"""
    print("\n🎤 使用 Whisper 识别...")
    
    cmd = [
        'whisper', audio_path,
        '--model', 'base',
        '--language', 'zh',
        '--output_format', 'json',
        '--output_dir', os.path.dirname(output_json),
        '--fp16', 'False'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    if result.returncode == 0:
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        whisper_json = os.path.join(os.path.dirname(output_json), f"{base_name}.json")
        if os.path.exists(whisper_json):
            os.rename(whisper_json, output_json)
            print(f"   ✅ Whisper 成功")
            return True
    
    print(f"   ❌ Whisper 失败")
    return False

# ==================== 步骤 3: 加载结果 ====================

def load_asr_result(json_path, asr_type):
    """加载 ASR 结果"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    segments = []
    
    if asr_type == "funasr":
        # FunASR 格式
        if isinstance(data, list) and len(data) > 0:
            for item in data:
                if isinstance(item, dict):
                    text = item.get('text', '')
                    timestamp = item.get('timestamp', [])
                    if text and timestamp:
                        segments.append({
                            'start': timestamp[0][0] / 1000,
                            'end': timestamp[-1][1] / 1000,
                            'text': text
                        })
    else:
        # Whisper 格式
        segments = data.get('segments', [])
        segments = [{'start': s['start'], 'end': s['end'], 'text': s['text']} for s in segments]
    
    return segments

# ==================== 步骤 4: 合并短片段 ====================

def merge_segments(segments, min_duration=1.5, max_gap=0.3):
    """合并短片段"""
    if not segments:
        return []
    
    merged = []
    current = {
        'start': segments[0]['start'],
        'end': segments[0]['end'],
        'text': segments[0]['text'].strip()
    }
    
    for seg in segments[1:]:
        gap = seg['start'] - current['end']
        duration = current['end'] - current['start']
        
        if gap < max_gap and duration < min_duration:
            current['end'] = seg['end']
            current['text'] += ' ' + seg['text'].strip()
        else:
            merged.append(current)
            current = {
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text'].strip()
            }
    
    merged.append(current)
    return merged

# ==================== 步骤 5: 上下文感知 LLM 优化 ====================

def create_paragraphs(segments, max_duration=45, max_gap=2.0):
    """将片段组合成段落"""
    if not segments:
        return []
    
    paragraphs = []
    current = {
        'start': segments[0]['start'],
        'end': segments[0]['end'],
        'texts': [segments[0]['text']],
        'segments': [segments[0]]
    }
    
    for seg in segments[1:]:
        gap = seg['start'] - current['end']
        duration = current['end'] - current['start']
        
        if gap < max_gap and duration < max_duration:
            current['end'] = seg['end']
            current['texts'].append(seg['text'])
            current['segments'].append(seg)
        else:
            paragraphs.append(current)
            current = {
                'start': seg['start'],
                'end': seg['end'],
                'texts': [seg['text']],
                'segments': [seg]
            }
    
    paragraphs.append(current)
    return paragraphs

def optimize_paragraph_with_context(para, prev_para, next_para):
    """使用 LLM 基于上下文优化段落"""
    
    # 构建上下文
    prev_text = ' '.join(prev_para['texts'])[-80:] if prev_para else ""
    next_text = ' '.join(next_para['texts'])[:80] if next_para else ""
    current_text = ' '.join(para['texts'])
    
    prompt = f"""作为专业字幕校对专家，请基于上下文优化以下字幕文本。

【前文】{prev_text}

【当前文本】{current_text}

【后文】{next_text}

【优化要求】
1. 基于上下文理解修正识别错误（结合前后文语义）
2. 统一技术术语：
   - "Codex/CC/克劳德代码" → "Claude Code"
   - "Vibe Coding" → 保持原样
   - "Full Access Mode" → 保持原样
   - "Worktree/工作树" → "Git Worktree"
   - "MCP/mcp" → "MCP"
3. 保持句子在上下文中通顺连贯
4. 删除重复词、口头禅、语气词
5. 根据语气添加合适的标点符号
6. 不要改变原意，不要添加原文没有的内容

【重要】直接返回优化后的完整文本，不要添加解释。"""

    try:
        result = subprocess.run(
            ['kimi', '-c', prompt],
            capture_output=True, text=True, timeout=90
        )
        
        if result.returncode == 0:
            optimized = result.stdout.strip()
            # 清理可能的引号和说明
            optimized = optimized.strip('"').strip("'")
            # 去除 "优化后文本:" 等前缀
            if ':' in optimized[:20]:
                optimized = optimized.split(':', 1)[1].strip()
            return optimized
        
    except Exception as e:
        print(f"   LLM 错误: {e}")
    
    return None

def distribute_optimized_text(para, optimized_text):
    """将优化后的文本分配到各个片段"""
    segments = para['segments']
    original_texts = para['texts']
    
    if len(segments) == 1:
        return [{'start': segments[0]['start'], 'end': segments[0]['end'], 
                'text': optimized_text, 'original': segments[0]['text']}]
    
    # 按比例分配
    original_total = sum(len(t) for t in original_texts)
    result = []
    current_pos = 0
    
    for i, seg in enumerate(segments):
        if i == len(segments) - 1:
            # 最后一个片段取剩余所有
            seg_text = optimized_text[current_pos:]
        else:
            # 按比例计算
            ratio = len(original_texts[i]) / original_total
            seg_len = int(len(optimized_text) * ratio)
            seg_text = optimized_text[current_pos:current_pos + seg_len]
            current_pos += seg_len
        
        result.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': seg_text.strip(),
            'original': seg['text']
        })
    
    return result

def contextual_llm_optimize(segments):
    """上下文感知 LLM 优化"""
    print("\n🤖 上下文感知优化...")
    
    # 组合成段落
    paragraphs = create_paragraphs(segments)
    print(f"   组合成 {len(paragraphs)} 个段落")
    
    optimized_segments = []
    
    for i, para in enumerate(paragraphs):
        print(f"   段落 {i+1}/{len(paragraphs)}...", end=" ", flush=True)
        
        # 获取上下文
        prev_para = paragraphs[i-1] if i > 0 else None
        next_para = paragraphs[i+1] if i < len(paragraphs)-1 else None
        
        # LLM 优化
        optimized_text = optimize_paragraph_with_context(para, prev_para, next_para)
        
        if optimized_text:
            # 分配优化后的文本到各个片段
            segs = distribute_optimized_text(para, optimized_text)
            optimized_segments.extend(segs)
            print("✓")
        else:
            # 使用原文
            for seg in para['segments']:
                optimized_segments.append({
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'],
                    'original': seg['text']
                })
            print("○(原文)")
    
    print(f"   ✅ 优化完成: {len(optimized_segments)} 条")
    return optimized_segments

# ==================== 步骤 6: 生成 SRT ====================

def format_time(seconds):
    """格式化时间"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_srt(segments, output_path):
    """生成 SRT"""
    print(f"\n📝 生成 SRT...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        idx = 1
        for seg in segments:
            text = seg['text'].strip()
            if not text:
                continue
            
            start = format_time(seg['start'])
            end = format_time(seg['end'])
            
            # 长文本换行
            if len(text) > 30:
                mid = len(text) // 2
                for j in range(mid, min(mid+15, len(text))):
                    if text[j] in '，。、；：？！,':
                        text = text[:j+1] + '\n' + text[j+1:]
                        break
            
            f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
            idx += 1
    
    size = os.path.getsize(output_path) / 1024
    print(f"   ✅ 已生成: {output_path} ({size:.1f}KB)")

def show_comparison(segments):
    """显示对比"""
    print(f"\n📋 优化对比 (前5条):")
    print("-" * 70)
    for seg in segments[:5]:
        orig = seg.get('original', seg['text'])[:40]
        text = seg['text'][:40]
        print(f"原文: {orig}")
        print(f"优化: {text}")
        print()

# ==================== 主程序 ====================

def main():
    print("=" * 70)
    print("🎬 字幕生成: FunASR/Whisper + 上下文感知 LLM 优化")
    print("=" * 70)
    
    if not os.path.exists(VIDEO_FILE):
        print(f"❌ 视频不存在: {VIDEO_FILE}")
        return
    
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, "audio.wav")
        json_path = os.path.join(temp_dir, "asr_result.json")
        
        # 1. 提取音频
        if not extract_audio(VIDEO_FILE, audio_path):
            return
        
        # 2. ASR 识别 (优先 FunASR，备用 Whisper)
        asr_type = None
        if os.path.exists(VENV_PYTHON):
            success, asr_type = transcribe_with_funasr(audio_path, json_path)
        
        if not asr_type:
            if transcribe_with_whisper(audio_path, json_path):
                asr_type = "whisper"
        
        if not asr_type:
            print("❌ ASR 识别失败")
            return
        
        print(f"\n✅ 使用 {asr_type.upper()} 识别")
        
        # 3. 加载结果
        segments = load_asr_result(json_path, asr_type)
        print(f"📊 原始片段: {len(segments)}")
        
        # 4. 合并短片段
        segments = merge_segments(segments)
        print(f"📊 合并后: {len(segments)}")
        
        # 5. 上下文感知优化
        segments = contextual_llm_optimize(segments)
        
        # 6. 显示对比
        show_comparison(segments)
        
        # 7. 生成 SRT
        generate_srt(segments, OUTPUT_SRT)
    
    print(f"\n{'=' * 70}")
    print("✅ 字幕生成完成!")
    print(f"{'=' * 70}")
    print(f"输出: {OUTPUT_SRT}")

if __name__ == "__main__":
    main()
