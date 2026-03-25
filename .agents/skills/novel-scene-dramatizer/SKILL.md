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
- `constraints`
- `expected_outputs`

如果没有清楚的场面支点或压力线，返回 `blocked`，建议先补 plan。

## Expansion Rules

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

1. 把计划压成场面链
2. 先写 dominant scene
3. 用最短的 bridge 搬运必要结果
4. 只在需要处补互动和主观线
5. 检查章末余波是否仍挂在具体场面上

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

## Guardrails

- 不机械照抄 plan
- 不靠评论、总结、履历式罗列支撑正文
- 不虚构会改变理解的私密细节和对白
- 如果读者需要自己重排时间线或因果链，视为失败，应重写

## Shared References

- `references/novel-system/references/scene-design.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/language-surface.md`
- `references/novel-system/references/story-quality.md`
