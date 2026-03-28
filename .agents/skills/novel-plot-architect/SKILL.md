---
name: novel-plot-architect
description: 长篇小说情节与结构规划。用于规划 master outline、arc、大纲、章纲、scene beats、冲突升级、信息揭示、伏笔布置和回收窗口；在主题、角色弧线和当前状态约束下提出可执行的结构方案；以 `mainline / explorer / critic` 三角张力找出更强 disturbance 与更稳因果；为 novel-scene-dramatizer 提供稳定输入。当用户提到卷纲、章纲、卡文求解、冲突升级、伏笔安排、结构优化或多方案构思时触发。
---

# 情节结构规划

## Overview

只规划结构，不直接承担正文。
目标是给下游一个够用、易写、不会把正文写僵的 plan。

你默认同时承担三个 stance：

- `mainline planner`
  - 给出当前最可执行的计划
- `explorer`
  - 找更强 disturbance、更高代价、更具体场面支点、更热 residue 的候选方案
- `critic`
  - 压测因果、可写性、假升级和“看起来更猛其实更空”的 beat

## Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

最少需要：

- `task_type`
- `objective`
- `scope`
- `context_bundle`
  - 至少包括当前状态、相关摘要、角色动态、开放回路
  - 若来自质量闭环，还应包括现稿、`quality_scorecard`、`blockers`、`targeted_fix_list`
- `constraints`
- `expected_outputs`

## Tension Roles

`explorer` 默认找：

- 更能立刻压住读者的 `opening hook`
- 更具体的阻力来源
  - 人、制度、时间、空间、公开后果、关系错位、信息差
- 更可见的代价载体
  - 名单、比分、席位、伤势、证词、迟到、被看见、错过窗口
- 更难被删掉的 `core event`
- 更会发热的 `residue`

`critic` 默认拦：

- 只有主题判断、没有动作和后果的 beat
- 靠巧合、误会模板或纯黑化硬推的转折
- “ stakes 更大了” 但没有具体承载物的假升级
- 可轻易压缩成时间线条目的段落
- 平均用力、没有 dominant scene 的 plan

## Planning Rules

无论粒度大小，都尽量回答：

1. 谁在追求什么
2. 什么在阻拦
3. 哪个选择或事件推动转折
4. 代价落在哪
5. 结束时留下什么未完成感

章节规划时，再补：

- `opening hook`
- `disturbance`
- `pursuit`
- `escalation`
- `irreversible turn`
- `core event`
- `residue`

其中：

- `opening hook` 负责前 20% 抓人
- `core event` 必须是这一章删不掉的硬节点
- `residue` 必须能直接勾住下一章，而不是只给主题判断

如果这些说不清，说明 plan 还不够可写。

每条关键 beat 最好还能回答：

- 这一步的 `desire` 是什么
- 当前 `resistance` 来自哪里
- `visible cost` 落在什么人或物上

## Targeted Repair Mode

如果任务来自审计闭环，不默认重做全章规划。

默认做法：

- 只读取失败维度和受影响段落 / 场面
- 先产出 `repair_plan`，再补 `chapter_promise` 或 `scene_beats`
- 每个修复项都说明：
  - `failed_dimension`
  - `repair_goal`
  - `affected_beats`
  - `new_pressure_or_turn`
  - `expected_score_gain`

常见归属：

- `opening_hook`、`core_event`、`escalation` 失效：优先由你修
- 如果只是局部语言或对白问题，不要抢走 `novel-scene-dramatizer` / `novel-dialogue-editor` 的工作

修复时也默认走三角协议：

- `mainline` 先给最低可修方案
- `explorer` 只对失败维度补更强替代
- `critic` 检查修复是否只是加码，而没有新因果或新压力

## Dispatch Scope

默认 `1 chapter / dispatch`。
如果用户一次要求多章详细规划：

- 先给跨章 route plan
- 不要在一次 dispatch 里展开多章完整 beats
- 真正下放到 sub-agent 时，逐章拆开

## Plan Scenes, Not Essays

默认输出轻量章节 plan：

- 1 个 dominant scene
- 1 条压力线
- 2 到 4 个 beats
- 1 个章末余波

每个 beat 尽量带最少三件事：

- 谁在主动追求
- 哪个阻力具体到场
- 哪个选择、代价或结果把下一拍逼出来

其余同型节点优先压成 `bridge cluster`，不要平均展开。

对纪实 / 传记章节，尽量再标出：

- `primary scene object`
  - 名单、号码、比分、空间、物件、比赛节点
- `interaction units`
  - 提醒、照看、打断、热身、短话语、即时反应
- `voice pin`
  - 可安全使用的短话语、later quote 或最低限度主观线

如果用户要求“写厚”：

- 默认安排至少 2 个互动单元
- 至少 1 个由主角亲自回应
- 明确哪些内容只是桥接，不能吃掉正文主干

## Workflow

1. 确认规划层级或 `targeted_repair` 模式
2. 读取当前义务或 blocker 列表
3. 先做 `mainline` 基础方案
4. 跑 `explorer` pass
   - 只给 `2 到 3` 个高杠杆升级或变体
5. 跑 `critic` pass
   - 压测基础方案和候选方案
6. 综合出最强但仍可写的单条方案
7. 安排信息释放
8. 压缩成 scene-ready beats
9. 标出后续依赖和不可违背事实

## Output

至少返回：

- `status`
- `artifacts`
- `diagnostics`
- `recommendations`
- `proposed_writebacks`

常见 artifact：

- `chapter_promise`
- `chapter_plan`
- `scene_beats`
- `reveal_plan`
- `repair_plan`
- `patched_scene_beats`
- `pressure_upgrade_options`
- `plan_break_report`
- `tension_synthesis`

## Guardrails

- 不要把 plan 写成章节评论
- 不要只给主题结论不给场面
- 不要靠巧合推动重大转折
- 如果某条 beat 稍微压缩就变成时间线条目，继续补足场面支点或互动单元
- 如果只存在 1 到 2 个局部 blocker，不要借机重设计整个 arc
- `explorer` 不靠无来由的极端事件抬高张力；升级必须仍受 canon 和人物选择约束
- `critic` 不要求“更大更惨”本身；必须指出哪条因果、代价或场面支点失效
- 如果多个候选都成立，不平均混搭；交付 1 条主方案，再把其余强备选放进 `recommendations`

## Shared References

- `references/novel-system/references/plotting.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/scene-design.md`
- `references/novel-system/references/story-quality.md`
