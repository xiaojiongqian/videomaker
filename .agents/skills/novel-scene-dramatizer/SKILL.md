---
name: novel-scene-dramatizer
description: 长篇小说场景与章节扩写。用于把已批准的章纲、scene beats 或片段计划扩成可读的场景草稿或章节草稿；把冲突、动作、选择、代价、反应和节奏落到具体叙事中；避免设定说明堆积；为后续对白润色和连续性审计提供稳定草稿。当用户提到扩写场景、把大纲写成正文、增强戏剧性、优化节奏或把一章从结构变成草稿时触发。
---

# 场景扩写

## Overview

只在已有计划基础上扩写。
如果上游 plan 过满、过碎、过像摘要，先压回可写的场面链，再下笔。

优先级固定如下：

1. 清楚
2. 现场感
3. 文气和结构花样

## Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

最少需要：

- `task_type`
- `objective`
- `scope`
- `context_bundle`
  - 至少包括已批准的章纲或 scene beats、必要设定、相关状态
  - 若来自质量闭环，还应包括现稿、`quality_scorecard`、`blockers`、`targeted_fix_list`
- `constraints`
- `expected_outputs`

如果没有清楚的场面支点或压力线，返回 `blocked`，建议先补 plan。

## Expansion Rules

开头前 20% 默认先做这件事：

- 把读者直接推到冲突、等待、门槛、结果快要落下的瞬间

每个关键段落尽量具备：

- `anchor`
  - 可见时刻、物件、空间、名单、比分
- `contact`
  - 人对人 / 人对物 / 人对门槛的实际作用
- `shift`
  - 局面、风险、位置、结果发生偏转
- `residue`
  - 留下余波，把下一段逼出来

如果一个段落没有 `contact` 和 `shift`，它大概率只是摘要。

每章至少要让 1 个核心事件慢下来写，不能所有节点都按同样速度划过去。

## Targeted Revision Mode

如果任务来自审计闭环，默认从现稿出发做局部修复，而不是整章重写。

优先顺序：

1. 开头抓力不足
2. 核心事件不够硬
3. dominant scene 被桥接段吃掉
4. 章末没有发热余波

执行要求：

- 先冻结已通过的段落和 beats
- 只改受影响的段落、场面链或章末落点
- 每次修复优先处理 `2 到 3` 个 blocker cluster
- 新增段落必须增加 `contact` 或 `shift`
- 如果根因其实是上游结构错误，返回给 `novel-plot-architect`
- 修复回执至少带：
  - `touched_dimensions`
  - `expected_score_gain`
  - `locked_dimensions_respected`

## Quality Council Seat

当被 `novel-orchestrator-main` 作为 `scene_heat_seat` 调用时，你优先做“场面热度评审”，不直接重写。

你拥有的 canonical 维度：

- `scene_execution`
- `ending_hook`

执行要求：

- 默认只读取 `seat_context_snapshot`
  - 不读取同轮 `peer_findings`、`peer_scorecards`、作者自述修复理由
- 只给 owned dimension 打 canonical 分
- 明确指出哪一段只是 `bridge facts`，哪一段真正承担 dominant scene
- 章末必须判断余波是否仍挂在具体动作、物件或结果上
- 如果当前轮文本是由 `novel-scene-dramatizer` 写出来的，也必须用新的评审 session 来打分

## Dispatch Scope

默认 `1 chapter` 或 `1 dominant scene chain / dispatch`。

- 不在一次 sub-agent 调用里重写多章正文
- 如果用户要批量优化，先分诊，再逐章下发
- 如果 scope 已经过大，返回 `blocked` 并要求拆分

## Prefer Events Over Commentary

优先让段落由这些东西推进：

- 谁进场
- 谁想拿到什么
- 什么在拦他
- 哪个动作改变局面
- 代价落到谁身上

桥接段只能搬运必要事实，不能长期接管章节主干。

默认要求：

- 每章优先 1 个 dominant scene，必要时再加 1 个扩展场面
- 其余同型节点压成 `bridge cluster`
- bridge 段不连续超过两段
- 单段尽量只搬 1 到 2 个新事实

## Keep the Language Clear

- 先让读者一遍读懂时间、层级、门槛和结果
- 段首优先落到人、动作、物件、比分、空间
- 少用总结句、评论句、主题句开路
- 抽象判断后应尽快回到动作和后果
- 少用连续模板句式撑节奏
- 章末直接写清推进和余波，不拿隐喻代替结论

对比赛 / 成长线章节，前 1 到 2 段内尽快说清：

- 当前年份 / 赛季 / 层级
- 本章相对上一阶段新增了什么门槛
- 如果是两回合或淘汰赛，现在的形势和结果意味着什么

## Write Through People

尽量让关键人物通过动作和反应到场：

- 提醒
- 劝说
- 照看
- 打断
- 热身
- 顶回去
- 短心理线
- later quote

对纪实骨架写法，优先顺序如下：

1. 来源明确的短对白或转述
2. 来源明确的人际动作
3. 低风险细节层
4. bounded interiority

如果用户要求“写厚”：

- 默认补到 2 个有效互动单元，或 1 条持续升级的互动链
- 主角至少有一次明确回应
  - 开口、动作、短心理线都可以
- 新增篇幅必须增加 `contact` 或 `shift`

## Workflow

1. 判断是全新扩写还是 `targeted_revision`
2. 把计划或 blocker 列表压成场面链
3. 先写或重写 dominant scene
4. 用最短的 bridge 搬运必要结果
5. 只在需要处补互动和主观线
6. 检查章末余波是否仍挂在具体场面上

## Quality Council Review Workflow

当 `task_type` 是 `quality-seat-scene-heat` 或目标明确要求评分时，默认执行：

1. 只检查 `scene_execution` 和 `ending_hook`
2. 判断 dominant scene 是否真的承担不可删除的推进
3. 找出最伤热度的 `bridge leak`、`scene blur` 或 `cold ending`
4. 对每个问题给：
   - `minimal_fix`
   - `rewrite_scope`
   - `expected_score_gain`
   - 是否会影响 `locked_dimensions`
5. 如果根因明显属于上游结构或对白，不自己吞掉，而是标注正确 owner
6. 如果当前 phase 是 `re-audit` 且你被标为 `counterforce seat`
   - 重点检查修复是否把文本改成“解释更顺了，但场面热度死了”或“结构更稳了，但现场感消失了”

## Output

至少返回：

- `status`
- `artifacts`
- `diagnostics`
- `recommendations`
- `proposed_writebacks`

常见 artifact：

- `scene_draft`
- `chapter_draft`
- `prose_revision`
- `targeted_prose_revision`
- `revision_scope`
- `scene_heat_seat_scorecard`
- `scene_heat_report`
- `ending_residue_report`

## Guardrails

- 不机械照抄 plan
- 不靠评论、总结、履历式罗列支撑正文
- 不虚构会改变理解的私密细节和对白
- 如果读者需要自己重排时间线或因果链，视为失败，应重写
- 不因修 1 个局部问题就重刷整章文风；先保住已通过的场面和节奏
- 作为评审席位时，不用“我可以重写得更好”代替证据化评分

## Shared References

- `references/novel-system/references/scene-design.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/language-surface.md`
- `references/novel-system/references/story-quality.md`
