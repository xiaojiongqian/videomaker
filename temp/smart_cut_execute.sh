#!/bin/bash

# 智能视频剪辑脚本

INPUT="/Users/vik.qian/study/videomaker/video/Codex-AGITest.mov"
OUTPUT="/Users/vik.qian/study/videomaker/video/Codex-AGITest_cut.mp4"
TEMP_DIR="/Users/vik.qian/study/videomaker/video/temp_segments"

mkdir -p "$TEMP_DIR"

echo "开始提取视频片段..."

# 片段 1/157: 我正在做一个开发...
ffmpeg -y -ss 0.000 -i "$INPUT" -t 4.560 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0000.mp4" 2>/dev/null
echo "  提取片段 1/157 完成"

# 片段 2/157: codex来解决一个问题 这个问题只是呢 昨天晚上做完这个功...
ffmpeg -y -ss 7.200 -i "$INPUT" -t 33.680 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0001.mp4" 2>/dev/null
echo "  提取片段 2/157 完成"

# 片段 3/157: 这问题是这样的就是...
ffmpeg -y -ss 44.079 -i "$INPUT" -t 4.160 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0002.mp4" 2>/dev/null
echo "  提取片段 3/157 完成"

# 片段 4/157: OtherField的功能 现在在会本做出来之后 能自动生成...
ffmpeg -y -ss 51.359 -i "$INPUT" -t 56.321 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0003.mp4" 2>/dev/null
echo "  提取片段 4/157 完成"

# 片段 5/157: 现在进入调步会走了 然后看下来这个数据还是没有 改了这个数据...
ffmpeg -y -ss 113.040 -i "$INPUT" -t 16.080 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0004.mp4" 2>/dev/null
echo "  提取片段 5/157 完成"

# 片段 6/157: 大概就是这本一个问题 这个问题解决方案就是...
ffmpeg -y -ss 131.759 -i "$INPUT" -t 7.361 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0005.mp4" 2>/dev/null
echo "  提取片段 6/157 完成"

# 片段 7/157: 如果是通常的大约模型来这个R6代码 这个是比较难解决的 因为...
ffmpeg -y -ss 141.759 -i "$INPUT" -t 17.760 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0006.mp4" 2>/dev/null
echo "  提取片段 7/157 完成"

# 片段 8/157: 我们可以氛围几个步骤 比如说我这边也给了一个题杀 分析线由的...
ffmpeg -y -ss 161.759 -i "$INPUT" -t 16.880 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0007.mp4" 2>/dev/null
echo "  提取片段 8/157 完成"

# 片段 9/157: 那就可以看数据库的制断也没有数据...
ffmpeg -y -ss 179.679 -i "$INPUT" -t 2.960 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0008.mp4" 2>/dev/null
echo "  提取片段 9/157 完成"

# 片段 10/157: 然后看能不能独取成功 另外关进度调不更新的问题 可以单独看就...
ffmpeg -y -ss 183.599 -i "$INPUT" -t 15.040 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0009.mp4" 2>/dev/null
echo "  提取片段 10/157 完成"

# 片段 11/157: 那今天这个方法跟 原来不一样的地方就是 我之前通过这个 另一...
ffmpeg -y -ss 201.839 -i "$INPUT" -t 19.721 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0010.mp4" 2>/dev/null
echo "  提取片段 11/157 完成"

# 片段 12/157: Retro的几个Skill 包括给它放开它的能力 访问法备是...
ffmpeg -y -ss 222.520 -i "$INPUT" -t 38.160 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0011.mp4" 2>/dev/null
echo "  提取片段 12/157 完成"

# 片段 13/157: 那我第一步就是...
ffmpeg -y -ss 262.759 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0012.mp4" 2>/dev/null
echo "  提取片段 13/157 完成"

# 片段 14/157: 告诉他有这个问题...
ffmpeg -y -ss 268.120 -i "$INPUT" -t 1.440 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0013.mp4" 2>/dev/null
echo "  提取片段 14/157 完成"

# 片段 15/157: 让他把这个工作的...
ffmpeg -y -ss 270.959 -i "$INPUT" -t 2.601 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0014.mp4" 2>/dev/null
echo "  提取片段 15/157 完成"

# 片段 16/157: 计划写在文档里面 然后他就把他把它写了 这个跟常规的是一样的...
ffmpeg -y -ss 274.560 -i "$INPUT" -t 9.399 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0015.mp4" 2>/dev/null
echo "  提取片段 16/157 完成"

# 片段 17/157: 要求自组调试了...
ffmpeg -y -ss 285.240 -i "$INPUT" -t 2.320 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0016.mp4" 2>/dev/null
echo "  提取片段 17/157 完成"

# 片段 18/157: 是通过它自动地来调 因为我是想 常试HDI这个编程 所谓编程...
ffmpeg -y -ss 289.560 -i "$INPUT" -t 11.639 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0017.mp4" 2>/dev/null
echo "  提取片段 18/157 完成"

# 片段 19/157: 那他这边也自动地 花了点时间 自动地安装各种Skill...
ffmpeg -y -ss 303.199 -i "$INPUT" -t 8.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0018.mp4" 2>/dev/null
echo "  提取片段 19/157 完成"

# 片段 20/157: 然后他这个Poss来的话...
ffmpeg -y -ss 312.199 -i "$INPUT" -t 2.601 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0019.mp4" 2>/dev/null
echo "  提取片段 20/157 完成"

# 片段 21/157: 但是一开始 他就按不就班了 先打开网页...
ffmpeg -y -ss 315.800 -i "$INPUT" -t 5.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0020.mp4" 2>/dev/null
echo "  提取片段 21/157 完成"

# 片段 22/157: 但登入我没告诉他...
ffmpeg -y -ss 322.199 -i "$INPUT" -t 1.601 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0021.mp4" 2>/dev/null
echo "  提取片段 22/157 完成"

# 片段 23/157: 那他就卡出来...
ffmpeg -y -ss 324.800 -i "$INPUT" -t 1.399 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0022.mp4" 2>/dev/null
echo "  提取片段 23/157 完成"

# 片段 24/157: 给他准备好的一个页名...
ffmpeg -y -ss 330.199 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0023.mp4" 2>/dev/null
echo "  提取片段 24/157 完成"

# 片段 25/157: 登入进来以后 然后这个页面...
ffmpeg -y -ss 335.199 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0024.mp4" 2>/dev/null
echo "  提取片段 25/157 完成"

# 片段 26/157: 也给他准备好...
ffmpeg -y -ss 340.199 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0025.mp4" 2>/dev/null
echo "  提取片段 26/157 完成"

# 片段 27/157: 然后到特定页名的地址 然后把这个地址...
ffmpeg -y -ss 344.199 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0026.mp4" 2>/dev/null
echo "  提取片段 27/157 完成"

# 片段 28/157: 后面就看他自组之情 至于这个支储他后面...
ffmpeg -y -ss 351.199 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0027.mp4" 2>/dev/null
echo "  提取片段 28/157 完成"

# 片段 29/157: 是執行的情况...
ffmpeg -y -ss 356.199 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0028.mp4" 2>/dev/null
echo "  提取片段 29/157 完成"

# 片段 30/157: 就是说已经登入好了 然后你在这个地址之情...
ffmpeg -y -ss 364.199 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0029.mp4" 2>/dev/null
echo "  提取片段 30/157 完成"

# 片段 31/157: 然后他就執行了...
ffmpeg -y -ss 369.199 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0030.mp4" 2>/dev/null
echo "  提取片段 31/157 完成"

# 片段 32/157: 还是有些进展 而且发现了这些问题...
ffmpeg -y -ss 374.199 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0031.mp4" 2>/dev/null
echo "  提取片段 32/157 完成"

# 片段 33/157: 工作的希望...
ffmpeg -y -ss 379.199 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0032.mp4" 2>/dev/null
echo "  提取片段 33/157 完成"

# 片段 34/157: 然后他就要求我...
ffmpeg -y -ss 382.199 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0033.mp4" 2>/dev/null
echo "  提取片段 34/157 完成"

# 片段 35/157: 或者通过这个本地 文化你的房子许策 那我就手动提交了 但实际...
ffmpeg -y -ss 387.199 -i "$INPUT" -t 11.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0034.mp4" 2>/dev/null
echo "  提取片段 35/157 完成"

# 片段 36/157: 把他手动提交了 但我告诉他 你可以自动安装 这个给他准备好...
ffmpeg -y -ss 399.199 -i "$INPUT" -t 9.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0035.mp4" 2>/dev/null
echo "  提取片段 36/157 完成"

# 片段 37/157: 需要帮助在找我 那后面的工作 就是比较科画...
ffmpeg -y -ss 413.199 -i "$INPUT" -t 7.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0036.mp4" 2>/dev/null
echo "  提取片段 37/157 完成"

# 片段 38/157: 完全要成他自组之情 那我告诉他 已经提交到代码...
ffmpeg -y -ss 421.199 -i "$INPUT" -t 5.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0037.mp4" 2>/dev/null
echo "  提取片段 38/157 完成"

# 片段 39/157: 触发这个不属优程...
ffmpeg -y -ss 428.199 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0038.mp4" 2>/dev/null
echo "  提取片段 39/157 完成"

# 片段 40/157: 给他安補这个优程 他真的是触发了...
ffmpeg -y -ss 437.199 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0039.mp4" 2>/dev/null
echo "  提取片段 40/157 完成"

# 片段 41/157: 也是他自动不属...
ffmpeg -y -ss 453.199 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0040.mp4" 2>/dev/null
echo "  提取片段 41/157 完成"

# 片段 42/157: 这是一块钱 我刚才讲的节点应该是在 在这个时候...
ffmpeg -y -ss 456.199 -i "$INPUT" -t 8.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0041.mp4" 2>/dev/null
echo "  提取片段 42/157 完成"

# 片段 43/157: 在这个时候 下午两点开始...
ffmpeg -y -ss 474.199 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0042.mp4" 2>/dev/null
echo "  提取片段 43/157 完成"

# 片段 44/157: 中间还有一些 直他的action和动作 我当晚在讲 那种子这...
ffmpeg -y -ss 479.199 -i "$INPUT" -t 9.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0043.mp4" 2>/dev/null
echo "  提取片段 44/157 完成"

# 片段 45/157: 个lex不属的...
ffmpeg -y -ss 490.199 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0044.mp4" 2>/dev/null
echo "  提取片段 45/157 完成"

# 片段 46/157: 然后他不属完以后...
ffmpeg -y -ss 494.199 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0045.mp4" 2>/dev/null
echo "  提取片段 46/157 完成"

# 片段 47/157: 自组进行这个 往前的车事...
ffmpeg -y -ss 499.199 -i "$INPUT" -t 5.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0046.mp4" 2>/dev/null
echo "  提取片段 47/157 完成"

# 片段 48/157: 就是体验不太好的地方 就运行时间...
ffmpeg -y -ss 506.199 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0047.mp4" 2>/dev/null
echo "  提取片段 48/157 完成"

# 片段 49/157: 提这个需求到 现在已经运行了 五个多小时了...
ffmpeg -y -ss 512.200 -i "$INPUT" -t 6.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0048.mp4" 2>/dev/null
echo "  提取片段 49/157 完成"

# 片段 50/157: 做了一些批准 批准主要就是...
ffmpeg -y -ss 523.200 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0049.mp4" 2>/dev/null
echo "  提取片段 50/157 完成"

# 片段 51/157: 主要就是这个 LC的这个 NodeMining...
ffmpeg -y -ss 527.200 -i "$INPUT" -t 6.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0050.mp4" 2>/dev/null
echo "  提取片段 51/157 完成"

# 片段 52/157: 脚本的命令...
ffmpeg -y -ss 534.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0051.mp4" 2>/dev/null
echo "  提取片段 52/157 完成"

# 片段 53/157: 是为了可以 统一的授权 它还是完全的这个...
ffmpeg -y -ss 540.200 -i "$INPUT" -t 5.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0052.mp4" 2>/dev/null
echo "  提取片段 53/157 完成"

# 片段 54/157: 那中间我这个...
ffmpeg -y -ss 548.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0053.mp4" 2>/dev/null
echo "  提取片段 54/157 完成"

# 片段 55/157: 太陆续续修复了一些东西...
ffmpeg -y -ss 553.200 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0054.mp4" 2>/dev/null
echo "  提取片段 55/157 完成"

# 片段 56/157: 就是talktag...
ffmpeg -y -ss 562.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0055.mp4" 2>/dev/null
echo "  提取片段 56/157 完成"

# 片段 57/157: 没法自动更新 它现在可以了 但是个lex还是不行 然后进度调...
ffmpeg -y -ss 564.200 -i "$INPUT" -t 7.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0056.mp4" 2>/dev/null
echo "  提取片段 57/157 完成"

# 片段 58/157: 结论就是 这个变成一支i4可行 但是现在速度还是很慢 就像正...
ffmpeg -y -ss 579.200 -i "$INPUT" -t 10.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0057.mp4" 2>/dev/null
echo "  提取片段 58/157 完成"

# 片段 59/157: 所以大家可能还是...
ffmpeg -y -ss 591.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0058.mp4" 2>/dev/null
echo "  提取片段 59/157 完成"

# 片段 60/157: 用没来烧 用传统的马车来跑...
ffmpeg -y -ss 594.200 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0059.mp4" 2>/dev/null
echo "  提取片段 60/157 完成"

# 片段 61/157: 那中间过程呢...
ffmpeg -y -ss 602.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0060.mp4" 2>/dev/null
echo "  提取片段 61/157 完成"

# 片段 62/157: 按时长还可以 做一些别的工作 我在这个 反面上呢...
ffmpeg -y -ss 608.200 -i "$INPUT" -t 7.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0061.mp4" 2>/dev/null
echo "  提取片段 62/157 完成"

# 片段 63/157: collects一直在 自动运行...
ffmpeg -y -ss 618.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0062.mp4" 2>/dev/null
echo "  提取片段 63/157 完成"

# 片段 64/157: 有一些这个 PR请求...
ffmpeg -y -ss 624.200 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0063.mp4" 2>/dev/null
echo "  提取片段 64/157 完成"

# 片段 65/157: 今天已经处理了这个 现在又进来一个...
ffmpeg -y -ss 630.200 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0064.mp4" 2>/dev/null
echo "  提取片段 65/157 完成"

# 片段 66/157: 按这个请求 那我可以通过...
ffmpeg -y -ss 636.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0065.mp4" 2>/dev/null
echo "  提取片段 66/157 完成"

# 片段 67/157: work3来...
ffmpeg -y -ss 639.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0066.mp4" 2>/dev/null
echo "  提取片段 67/157 完成"

# 片段 68/157: 互不干扰的...
ffmpeg -y -ss 643.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0067.mp4" 2>/dev/null
echo "  提取片段 68/157 完成"

# 片段 69/157: 来进行合并 因为我现在...
ffmpeg -y -ss 645.200 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0068.mp4" 2>/dev/null
echo "  提取片段 69/157 完成"

# 片段 70/157: 干嘛这工作在这个...
ffmpeg -y -ss 650.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0069.mp4" 2>/dev/null
echo "  提取片段 70/157 完成"

# 片段 71/157: arm invoke这个分支上...
ffmpeg -y -ss 653.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0070.mp4" 2>/dev/null
echo "  提取片段 71/157 完成"

# 片段 72/157: 对这个PR的一个...
ffmpeg -y -ss 657.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0071.mp4" 2>/dev/null
echo "  提取片段 72/157 完成"

# 片段 73/157: review和合并工作呢 我可以通过 work3来 工作具体...
ffmpeg -y -ss 660.200 -i "$INPUT" -t 9.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0072.mp4" 2>/dev/null
echo "  提取片段 73/157 完成"

# 片段 74/157: 右边这个 collect 然后这个...
ffmpeg -y -ss 672.200 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0073.mp4" 2>/dev/null
echo "  提取片段 74/157 完成"

# 片段 75/157: 我装一些谈...
ffmpeg -y -ss 677.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0074.mp4" 2>/dev/null
echo "  提取片段 75/157 完成"

# 片段 76/157: collects 也可以用collects 我做了一个 命令...
ffmpeg -y -ss 681.200 -i "$INPUT" -t 7.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0075.mp4" 2>/dev/null
echo "  提取片段 76/157 完成"

# 片段 77/157: 叫做PR...
ffmpeg -y -ss 690.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0076.mp4" 2>/dev/null
echo "  提取片段 77/157 完成"

# 片段 78/157: PR的这个...
ffmpeg -y -ss 694.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0077.mp4" 2>/dev/null
echo "  提取片段 78/157 完成"

# 片段 79/157: 就会自动的 review这个...
ffmpeg -y -ss 710.200 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0078.mp4" 2>/dev/null
echo "  提取片段 79/157 完成"

# 片段 80/157: review这个...
ffmpeg -y -ss 720.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0079.mp4" 2>/dev/null
echo "  提取片段 80/157 完成"

# 片段 81/157: 那我手段也可以 review...
ffmpeg -y -ss 726.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0080.mp4" 2>/dev/null
echo "  提取片段 81/157 完成"

# 片段 82/157: 这个提交然后...
ffmpeg -y -ss 729.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0081.mp4" 2>/dev/null
echo "  提取片段 82/157 完成"

# 片段 83/157: 当前的这个 collects工作 顾目干了...
ffmpeg -y -ss 738.200 -i "$INPUT" -t 5.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0082.mp4" 2>/dev/null
echo "  提取片段 83/157 完成"

# 片段 84/157: 那现在我们 我讲了这么多...
ffmpeg -y -ss 751.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0083.mp4" 2>/dev/null
echo "  提取片段 84/157 完成"

# 片段 85/157: 进展还是 非常慢的...
ffmpeg -y -ss 754.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0084.mp4" 2>/dev/null
echo "  提取片段 85/157 完成"

# 片段 86/157: playride...
ffmpeg -y -ss 759.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0085.mp4" 2>/dev/null
echo "  提取片段 86/157 完成"

# 片段 87/157: retest...
ffmpeg -y -ss 761.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0086.mp4" 2>/dev/null
echo "  提取片段 87/157 完成"

# 片段 88/157: retest 一边在修改这个问题...
ffmpeg -y -ss 763.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0087.mp4" 2>/dev/null
echo "  提取片段 88/157 完成"

# 片段 89/157: 改了一个 前段的一个问题...
ffmpeg -y -ss 767.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0088.mp4" 2>/dev/null
echo "  提取片段 89/157 完成"

# 片段 90/157: 真正改动的...
ffmpeg -y -ss 772.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0089.mp4" 2>/dev/null
echo "  提取片段 90/157 完成"

# 片段 91/157: 然后这边...
ffmpeg -y -ss 780.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0090.mp4" 2>/dev/null
echo "  提取片段 91/157 完成"

# 片段 92/157: 这就是所谓的 病型的工作 我嘗试过 最多也就 3-4个...
ffmpeg -y -ss 786.200 -i "$INPUT" -t 9.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0091.mp4" 2>/dev/null
echo "  提取片段 92/157 完成"

# 片段 93/157: 也不太有控制...
ffmpeg -y -ss 800.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0092.mp4" 2>/dev/null
echo "  提取片段 93/157 完成"

# 片段 94/157: command 呢...
ffmpeg -y -ss 813.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0093.mp4" 2>/dev/null
echo "  提取片段 94/157 完成"

# 片段 95/157: 也可以给大家看一下...
ffmpeg -y -ss 817.200 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0094.mp4" 2>/dev/null
echo "  提取片段 95/157 完成"

# 片段 96/157: 建了一个 cloud的一个 command 里面包含了一些 ...
ffmpeg -y -ss 822.200 -i "$INPUT" -t 7.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0095.mp4" 2>/dev/null
echo "  提取片段 96/157 完成"

# 片段 97/157: PR的这个动作 他会做一些...
ffmpeg -y -ss 839.200 -i "$INPUT" -t 5.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0096.mp4" 2>/dev/null
echo "  提取片段 97/157 完成"

# 片段 98/157: 先做验证 代码指南检查 便一个印象分析 真的报告 然后再做代...
ffmpeg -y -ss 846.200 -i "$INPUT" -t 14.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0097.mp4" 2>/dev/null
echo "  提取片段 98/157 完成"

# 片段 99/157: 这个是这样的 这个simplify Skill...
ffmpeg -y -ss 862.200 -i "$INPUT" -t 6.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0098.mp4" 2>/dev/null
echo "  提取片段 99/157 完成"

# 片段 100/157: 对分析进行检查 如果是目标分析 就是朝作 不认为分析...
ffmpeg -y -ss 878.200 -i "$INPUT" -t 8.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0099.mp4" 2>/dev/null
echo "  提取片段 100/157 完成"

# 片段 101/157: work3 然后还会解决冲突 这个就是冲突的侧面...
ffmpeg -y -ss 887.200 -i "$INPUT" -t 6.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0100.mp4" 2>/dev/null
echo "  提取片段 101/157 完成"

# 片段 102/157: 再做代码规判检查...
ffmpeg -y -ss 895.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0101.mp4" 2>/dev/null
echo "  提取片段 102/157 完成"

# 片段 103/157: TypeSquareF的这个检查...
ffmpeg -y -ss 899.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0102.mp4" 2>/dev/null
echo "  提取片段 103/157 完成"

# 片段 104/157: 代研测试...
ffmpeg -y -ss 902.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0103.mp4" 2>/dev/null
echo "  提取片段 104/157 完成"

# 片段 105/157: 合遍完以后 再提交报告...
ffmpeg -y -ss 909.200 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0104.mp4" 2>/dev/null
echo "  提取片段 105/157 完成"

# 片段 106/157: 那个检查...
ffmpeg -y -ss 917.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0105.mp4" 2>/dev/null
echo "  提取片段 106/157 完成"

# 片段 107/157: 可以提交一个 图的 command...
ffmpeg -y -ss 920.200 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0106.mp4" 2>/dev/null
echo "  提取片段 107/157 完成"

# 片段 108/157: 应该还是在...
ffmpeg -y -ss 936.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0107.mp4" 2>/dev/null
echo "  提取片段 108/157 完成"

# 片段 109/157: 我们可以回到当前...
ffmpeg -y -ss 941.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0108.mp4" 2>/dev/null
echo "  提取片段 109/157 完成"

# 片段 110/157: CodeX工作的一个情况...
ffmpeg -y -ss 945.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0109.mp4" 2>/dev/null
echo "  提取片段 110/157 完成"

# 片段 111/157: 现在还是很努力的在...
ffmpeg -y -ss 949.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0110.mp4" 2>/dev/null
echo "  提取片段 111/157 完成"

# 片段 112/157: 从这里来看...
ffmpeg -y -ss 964.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0111.mp4" 2>/dev/null
echo "  提取片段 112/157 完成"

# 片段 113/157: 直接跑这个...
ffmpeg -y -ss 972.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0112.mp4" 2>/dev/null
echo "  提取片段 113/157 完成"

# 片段 114/157: 扣不断的这个...
ffmpeg -y -ss 977.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0113.mp4" 2>/dev/null
echo "  提取片段 114/157 完成"

# 片段 115/157: 直接直接车户 断的代码...
ffmpeg -y -ss 980.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0114.mp4" 2>/dev/null
echo "  提取片段 115/157 完成"

# 片段 116/157: 它这边已经开始到 那个我手工测试的问题...
ffmpeg -y -ss 986.200 -i "$INPUT" -t 5.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0115.mp4" 2>/dev/null
echo "  提取片段 116/157 完成"

# 片段 117/157: 它也不做到这个问题了...
ffmpeg -y -ss 996.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0116.mp4" 2>/dev/null
echo "  提取片段 117/157 完成"

# 片段 118/157: 大家在场子解决 从这里来看它已经...
ffmpeg -y -ss 1001.200 -i "$INPUT" -t 5.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0117.mp4" 2>/dev/null
echo "  提取片段 118/157 完成"

# 片段 119/157: 通过手艺家的房子...
ffmpeg -y -ss 1008.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0118.mp4" 2>/dev/null
echo "  提取片段 119/157 完成"

# 片段 120/157: 测试和编码...
ffmpeg -y -ss 1011.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0119.mp4" 2>/dev/null
echo "  提取片段 120/157 完成"

# 片段 121/157: 它进入了这样一个循环...
ffmpeg -y -ss 1015.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0120.mp4" 2>/dev/null
echo "  提取片段 121/157 完成"

# 片段 122/157: 跑脚时间非常长...
ffmpeg -y -ss 1020.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0121.mp4" 2>/dev/null
echo "  提取片段 122/157 完成"

# 片段 123/157: 完成自动 review...
ffmpeg -y -ss 1035.200 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0122.mp4" 2>/dev/null
echo "  提取片段 123/157 完成"

# 片段 124/157: 现在提出来 要创建一个...
ffmpeg -y -ss 1046.200 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0123.mp4" 2>/dev/null
echo "  提取片段 124/157 完成"

# 片段 125/157: 它还是提醒我来做...
ffmpeg -y -ss 1053.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0124.mp4" 2>/dev/null
echo "  提取片段 125/157 完成"

# 片段 126/157: 我如果是直接 automatically 自动的话...
ffmpeg -y -ss 1057.200 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0125.mp4" 2>/dev/null
echo "  提取片段 126/157 完成"

# 片段 127/157: 就不用确认了...
ffmpeg -y -ss 1062.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0126.mp4" 2>/dev/null
echo "  提取片段 127/157 完成"

# 片段 128/157: 应该可以看我3 这个就是 现在在工作的...
ffmpeg -y -ss 1068.200 -i "$INPUT" -t 6.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0127.mp4" 2>/dev/null
echo "  提取片段 128/157 完成"

# 片段 129/157: I work3...
ffmpeg -y -ss 1076.200 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0128.mp4" 2>/dev/null
echo "  提取片段 129/157 完成"

# 片段 130/157: 单独间幕炉 刚剩下的...
ffmpeg -y -ss 1078.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0129.mp4" 2>/dev/null
echo "  提取片段 130/157 完成"

# 片段 131/157: 工作不冲突...
ffmpeg -y -ss 1082.200 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0130.mp4" 2>/dev/null
echo "  提取片段 131/157 完成"

# 片段 132/157: 看它這個代碼 修改都幫我自動提交了...
ffmpeg -y -ss 1124.200 -i "$INPUT" -t 5.119 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0131.mp4" 2>/dev/null
echo "  提取片段 132/157 完成"

# 片段 133/157: 看下這邊有沒有提交支路...
ffmpeg -y -ss 1130.600 -i "$INPUT" -t 2.040 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0132.mp4" 2>/dev/null
echo "  提取片段 133/157 完成"

# 片段 134/157: OK這邊 這裡來看一下...
ffmpeg -y -ss 1146.480 -i "$INPUT" -t 2.039 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0133.mp4" 2>/dev/null
echo "  提取片段 134/157 完成"

# 片段 135/157: OK這個是...
ffmpeg -y -ss 1154.200 -i "$INPUT" -t 2.559 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0134.mp4" 2>/dev/null
echo "  提取片段 135/157 完成"

# 片段 136/157: 26分鐘以前 坦幫我提交了...
ffmpeg -y -ss 1157.279 -i "$INPUT" -t 3.321 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0135.mp4" 2>/dev/null
echo "  提取片段 136/157 完成"

# 片段 137/157: 這些提交支路...
ffmpeg -y -ss 1164.440 -i "$INPUT" -t 1.800 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0136.mp4" 2>/dev/null
echo "  提取片段 137/157 完成"

# 片段 138/157: 26分鐘以前 坦幫我提交了...
ffmpeg -y -ss 1172.880 -i "$INPUT" -t 1.800 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0137.mp4" 2>/dev/null
echo "  提取片段 138/157 完成"

# 片段 139/157: 這些提交支路...
ffmpeg -y -ss 1178.519 -i "$INPUT" -t 1.800 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0138.mp4" 2>/dev/null
echo "  提取片段 139/157 完成"

# 片段 140/157: 從這裡來看...
ffmpeg -y -ss 1184.200 -i "$INPUT" -t 2.559 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0139.mp4" 2>/dev/null
echo "  提取片段 140/157 完成"

# 片段 141/157: 會非常好時...
ffmpeg -y -ss 1188.559 -i "$INPUT" -t 0.760 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0140.mp4" 2>/dev/null
echo "  提取片段 141/157 完成"

# 片段 142/157: 雖然是自動的但非常好時...
ffmpeg -y -ss 1190.600 -i "$INPUT" -t 3.840 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0141.mp4" 2>/dev/null
echo "  提取片段 142/157 完成"

# 片段 143/157: 現在在剋放...
ffmpeg -y -ss 1251.480 -i "$INPUT" -t 0.960 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0142.mp4" 2>/dev/null
echo "  提取片段 143/157 完成"

# 片段 144/157: WEativ的疫 mortar...
ffmpeg -y -ss 1255.599 -i "$INPUT" -t 1.920 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0143.mp4" 2>/dev/null
echo "  提取片段 144/157 完成"

# 片段 145/157: 然後這邊他在 完成最後的合併和經理...
ffmpeg -y -ss 1280.639 -i "$INPUT" -t 8.140 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0144.mp4" 2>/dev/null
echo "  提取片段 145/157 完成"

# 片段 146/157: 這邊再提交...
ffmpeg -y -ss 1343.779 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0145.mp4" 2>/dev/null
echo "  提取片段 146/157 完成"

# 片段 147/157: 它這邊的查看...
ffmpeg -y -ss 1360.779 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0146.mp4" 2>/dev/null
echo "  提取片段 147/157 完成"

# 片段 148/157: 高度的日子...
ffmpeg -y -ss 1364.779 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0147.mp4" 2>/dev/null
echo "  提取片段 148/157 完成"

# 片段 149/157: 這個地方是一道一道的困難...
ffmpeg -y -ss 1373.779 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0148.mp4" 2>/dev/null
echo "  提取片段 149/157 完成"

# 片段 150/157: 查看這個碰住...
ffmpeg -y -ss 1378.779 -i "$INPUT" -t 1.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0149.mp4" 2>/dev/null
echo "  提取片段 150/157 完成"

# 片段 151/157: 自己查碰住...
ffmpeg -y -ss 1380.779 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0150.mp4" 2>/dev/null
echo "  提取片段 151/157 完成"

# 片段 152/157: 這邊有個亂碼好奇怪...
ffmpeg -y -ss 1384.779 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0151.mp4" 2>/dev/null
echo "  提取片段 152/157 完成"

# 片段 153/157: 這個碰住...
ffmpeg -y -ss 1432.779 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0152.mp4" 2>/dev/null
echo "  提取片段 153/157 完成"

# 片段 154/157: 我不等了...
ffmpeg -y -ss 1452.779 -i "$INPUT" -t 2.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0153.mp4" 2>/dev/null
echo "  提取片段 154/157 完成"

# 片段 155/157: 還是比較廢時間...
ffmpeg -y -ss 1455.779 -i "$INPUT" -t 3.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0154.mp4" 2>/dev/null
echo "  提取片段 155/157 完成"

# 片段 156/157: 解論就是兩個第一個通過這個實驗 現在是可行的 但是現在還是速...
ffmpeg -y -ss 1462.779 -i "$INPUT" -t 11.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0155.mp4" 2>/dev/null
echo "  提取片段 156/157 完成"

# 片段 157/157: 現在很大程度上應該算是開始...
ffmpeg -y -ss 1475.779 -i "$INPUT" -t 4.000 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "$TEMP_DIR/seg_0156.mp4" 2>/dev/null
echo "  提取片段 157/157 完成"

# 生成合并列表
echo "生成合并列表..."
cat > "$TEMP_DIR/concat_list.txt" << EOF
file 'seg_0000.mp4'
file 'seg_0001.mp4'
file 'seg_0002.mp4'
file 'seg_0003.mp4'
file 'seg_0004.mp4'
file 'seg_0005.mp4'
file 'seg_0006.mp4'
file 'seg_0007.mp4'
file 'seg_0008.mp4'
file 'seg_0009.mp4'
file 'seg_0010.mp4'
file 'seg_0011.mp4'
file 'seg_0012.mp4'
file 'seg_0013.mp4'
file 'seg_0014.mp4'
file 'seg_0015.mp4'
file 'seg_0016.mp4'
file 'seg_0017.mp4'
file 'seg_0018.mp4'
file 'seg_0019.mp4'
file 'seg_0020.mp4'
file 'seg_0021.mp4'
file 'seg_0022.mp4'
file 'seg_0023.mp4'
file 'seg_0024.mp4'
file 'seg_0025.mp4'
file 'seg_0026.mp4'
file 'seg_0027.mp4'
file 'seg_0028.mp4'
file 'seg_0029.mp4'
file 'seg_0030.mp4'
file 'seg_0031.mp4'
file 'seg_0032.mp4'
file 'seg_0033.mp4'
file 'seg_0034.mp4'
file 'seg_0035.mp4'
file 'seg_0036.mp4'
file 'seg_0037.mp4'
file 'seg_0038.mp4'
file 'seg_0039.mp4'
file 'seg_0040.mp4'
file 'seg_0041.mp4'
file 'seg_0042.mp4'
file 'seg_0043.mp4'
file 'seg_0044.mp4'
file 'seg_0045.mp4'
file 'seg_0046.mp4'
file 'seg_0047.mp4'
file 'seg_0048.mp4'
file 'seg_0049.mp4'
file 'seg_0050.mp4'
file 'seg_0051.mp4'
file 'seg_0052.mp4'
file 'seg_0053.mp4'
file 'seg_0054.mp4'
file 'seg_0055.mp4'
file 'seg_0056.mp4'
file 'seg_0057.mp4'
file 'seg_0058.mp4'
file 'seg_0059.mp4'
file 'seg_0060.mp4'
file 'seg_0061.mp4'
file 'seg_0062.mp4'
file 'seg_0063.mp4'
file 'seg_0064.mp4'
file 'seg_0065.mp4'
file 'seg_0066.mp4'
file 'seg_0067.mp4'
file 'seg_0068.mp4'
file 'seg_0069.mp4'
file 'seg_0070.mp4'
file 'seg_0071.mp4'
file 'seg_0072.mp4'
file 'seg_0073.mp4'
file 'seg_0074.mp4'
file 'seg_0075.mp4'
file 'seg_0076.mp4'
file 'seg_0077.mp4'
file 'seg_0078.mp4'
file 'seg_0079.mp4'
file 'seg_0080.mp4'
file 'seg_0081.mp4'
file 'seg_0082.mp4'
file 'seg_0083.mp4'
file 'seg_0084.mp4'
file 'seg_0085.mp4'
file 'seg_0086.mp4'
file 'seg_0087.mp4'
file 'seg_0088.mp4'
file 'seg_0089.mp4'
file 'seg_0090.mp4'
file 'seg_0091.mp4'
file 'seg_0092.mp4'
file 'seg_0093.mp4'
file 'seg_0094.mp4'
file 'seg_0095.mp4'
file 'seg_0096.mp4'
file 'seg_0097.mp4'
file 'seg_0098.mp4'
file 'seg_0099.mp4'
file 'seg_0100.mp4'
file 'seg_0101.mp4'
file 'seg_0102.mp4'
file 'seg_0103.mp4'
file 'seg_0104.mp4'
file 'seg_0105.mp4'
file 'seg_0106.mp4'
file 'seg_0107.mp4'
file 'seg_0108.mp4'
file 'seg_0109.mp4'
file 'seg_0110.mp4'
file 'seg_0111.mp4'
file 'seg_0112.mp4'
file 'seg_0113.mp4'
file 'seg_0114.mp4'
file 'seg_0115.mp4'
file 'seg_0116.mp4'
file 'seg_0117.mp4'
file 'seg_0118.mp4'
file 'seg_0119.mp4'
file 'seg_0120.mp4'
file 'seg_0121.mp4'
file 'seg_0122.mp4'
file 'seg_0123.mp4'
file 'seg_0124.mp4'
file 'seg_0125.mp4'
file 'seg_0126.mp4'
file 'seg_0127.mp4'
file 'seg_0128.mp4'
file 'seg_0129.mp4'
file 'seg_0130.mp4'
file 'seg_0131.mp4'
file 'seg_0132.mp4'
file 'seg_0133.mp4'
file 'seg_0134.mp4'
file 'seg_0135.mp4'
file 'seg_0136.mp4'
file 'seg_0137.mp4'
file 'seg_0138.mp4'
file 'seg_0139.mp4'
file 'seg_0140.mp4'
file 'seg_0141.mp4'
file 'seg_0142.mp4'
file 'seg_0143.mp4'
file 'seg_0144.mp4'
file 'seg_0145.mp4'
file 'seg_0146.mp4'
file 'seg_0147.mp4'
file 'seg_0148.mp4'
file 'seg_0149.mp4'
file 'seg_0150.mp4'
file 'seg_0151.mp4'
file 'seg_0152.mp4'
file 'seg_0153.mp4'
file 'seg_0154.mp4'
file 'seg_0155.mp4'
file 'seg_0156.mp4'
EOF

echo "合并所有片段..."
ffmpeg -y -f concat -safe 0 -i "$TEMP_DIR/concat_list.txt" -c copy "$OUTPUT"

echo "清理临时文件..."
rm -rf "$TEMP_DIR"

echo "剪辑完成！"
echo "输出文件: $OUTPUT"