#!/bin/bash
# 分段处理方案 - 只有叠加图片的部分重新编码，其他部分直接复制

cd "/Users/vik.qian/study/videomaker/video/longtimepalla-vibecoding/doc"

VIDEO="/Users/vik.qian/study/videomaker/video/longtimepalla-vibecoding/并行长时间使用codex_cut.mp4"
OUTPUT="/Users/vik.qian/study/videomaker/video/longtimepalla-vibecoding/并行长时间使用codex_cut_cn_segmented.mp4"
TEMP_DIR="images/temp_mix"
SEGMENTS_DIR="segments"

mkdir -p "$SEGMENTS_DIR"

echo "=== 分段处理方案 ==="
echo "输入: $VIDEO"
echo "输出: $OUTPUT"
echo ""

# 定义时间点
T1_START=0;    T1_END=8      # 片头 - 复制
T2_START=8;    T2_END=33     # 架构图 - 重新编码
T3_START=33;   T3_END=70     # 间隔1 - 复制
T4_START=70;   T4_END=98     # 对比图 - 重新编码
T5_START=98;   T5_END=200    # 间隔2 - 复制
T6_START=200;  T6_END=225    # 流程图 - 重新编码
T7_START=225;  T7_END=800    # 片尾 - 复制

echo "📦 步骤1/7: 提取片头 (0-8秒) - 直接复制..."
ffmpeg -i "$VIDEO" -ss $T1_START -t $(($T1_END - $T1_START)) -c copy -y "$SEGMENTS_DIR/seg1_head.mp4" 2>&1 | tail -1

echo "📦 步骤2/7: 处理架构图片段 (8-33秒) - 重新编码..."
ffmpeg -ss $T2_START -t $(($T2_END - $T2_START)) -i "$VIDEO" \
  -loop 1 -t 30 -i "$TEMP_DIR/architecture.png" \
  -filter_complex "
    [1:v]format=rgba,fade=t=in:st=0:d=0.8:alpha=1,fade=t=out:st=24:d=0.8:alpha=1[img];
    [0:v][img]overlay=x=800:y=150:enable='between(t,0,25)':format=auto[out]
  " -map "[out]" -map 0:a -c:v libx264 -preset fast -crf 26 -c:a aac -b:a 128k -y "$SEGMENTS_DIR/seg2_arch.mp4" 2>&1 | tail -3

echo "📦 步骤3/7: 提取间隔1 (33-70秒) - 直接复制..."
ffmpeg -i "$VIDEO" -ss $T3_START -t $(($T3_END - $T3_START)) -c copy -y "$SEGMENTS_DIR/seg3_gap1.mp4" 2>&1 | tail -1

echo "📦 步骤4/7: 处理对比图片段 (70-98秒) - 重新编码..."
ffmpeg -ss $T4_START -t $(($T4_END - $T4_START)) -i "$VIDEO" \
  -loop 1 -t 30 -i "$TEMP_DIR/comparison.png" \
  -filter_complex "
    [1:v]format=rgba,fade=t=in:st=0:d=0.8:alpha=1,fade=t=out:st=27:d=0.8:alpha=1[img];
    [0:v][img]overlay=x=800:y=350:enable='between(t,0,28)':format=auto[out]
  " -map "[out]" -map 0:a -c:v libx264 -preset fast -crf 26 -c:a aac -b:a 128k -y "$SEGMENTS_DIR/seg4_comp.mp4" 2>&1 | tail -3

echo "📦 步骤5/7: 提取间隔2 (98-200秒) - 直接复制..."
ffmpeg -i "$VIDEO" -ss $T5_START -t $(($T5_END - $T5_START)) -c copy -y "$SEGMENTS_DIR/seg5_gap2.mp4" 2>&1 | tail -1

echo "📦 步骤6/7: 处理流程图片段 (200-225秒) - 重新编码..."
ffmpeg -ss $T6_START -t $(($T6_END - $T6_START)) -i "$VIDEO" \
  -loop 1 -t 30 -i "$TEMP_DIR/flow.png" \
  -filter_complex "
    [1:v]format=rgba,fade=t=in:st=0:d=0.8:alpha=1,fade=t=out:st=24:d=0.8:alpha=1[img];
    [0:v][img]overlay=x=800:y=50:enable='between(t,0,25)':format=auto[out]
  " -map "[out]" -map 0:a -c:v libx264 -preset fast -crf 26 -c:a aac -b:a 128k -y "$SEGMENTS_DIR/seg6_flow.mp4" 2>&1 | tail -3

echo "📦 步骤7/7: 提取片尾 (225-800秒) - 直接复制..."
ffmpeg -i "$VIDEO" -ss $T7_START -t $(($T7_END - $T7_START)) -c copy -y "$SEGMENTS_DIR/seg7_tail.mp4" 2>&1 | tail -1

echo ""
echo "🔗 拼接所有片段..."

# 创建拼接列表
cat > "$SEGMENTS_DIR/concat_list.txt" << EOF
file 'seg1_head.mp4'
file 'seg2_arch.mp4'
file 'seg3_gap1.mp4'
file 'seg4_comp.mp4'
file 'seg5_gap2.mp4'
file 'seg6_flow.mp4'
file 'seg7_tail.mp4'
EOF

# 拼接
ffmpeg -f concat -safe 0 -i "$SEGMENTS_DIR/concat_list.txt" -c copy -y "$OUTPUT" 2>&1 | tail -3

echo ""
echo "=== ✅ 处理完成 ==="
ls -lh "$OUTPUT"

# 清理临时文件
# rm -rf "$SEGMENTS_DIR"
