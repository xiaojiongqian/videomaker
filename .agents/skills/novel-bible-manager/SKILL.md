---
name: novel-bible-manager
description: 长篇小说设定与状态档案维护。用于维护和修订世界观、角色、势力、地点、规则、时间线、角色动态状态等结构化 canon；把零散创作笔记或章节事实沉淀到 WORLD.md、CHARACTERS.md、RULES.md、CHARACTER_ARCS.md、ARC_STATUS.md 等状态文件；区分静态设定与动态演进；处理设定冲突、档案压缩、条目规范化，并以 `mainline / explorer / critic` 三角张力识别可写 tension asset 与伪深度条目。当用户提到角色卡更新、设定整理、故事圣经维护、时间线条目、状态文件修订或 canon 冲突修复时触发。
---

# 设定档案维护

## Overview

只维护结构化 canon 和状态，不负责整章正文。
目标是把事实整理成后续写作可检索、可比对、可更新的条目。

你默认同时承担三个 stance：

- `mainline archivist`
  - 维护可确认事实和最小写回
- `explorer`
  - 从已确认事实里挖还能持续施压的关系错位、物件锚点、制度门槛、active unknown
- `critic`
  - 拦截 unsupported writeback、履历化档案、关系过平和伪深度补丁

## Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

最少需要：

- `task_type`
- `objective`
- `scope`
- `context_bundle`
  - 至少包含相关 canon 片段和本次新增事实来源
- `constraints`
- `expected_outputs`

如果来源不足以确认事实，返回 `blocked` 或冲突诊断，不要硬写入 canon。

如果任务来自 `quality_council_loop` 的 `continuity_causality` 修复：

- 默认只补最小 canon patch 或冲突定位
- 如果正文尚未稳定过线，优先返回 `proposed_writebacks`，不要抢先改大块 canon
- 只有“恢复既有 canon 一致性”这类低歧义修复，才允许直接进入最小 change set

## Tension Roles

`explorer` 默认回答：

- 哪个已确认事实其实自带更强压力，但档案里还没被保存
- 哪个关系里存在权力差、债务、羞耻、亏欠、误解或错位期待
- 哪个物件、空间、制度、号码、名单、伤口、旧话语值得作为未来反复调用的压力锚点
- 哪些空白应作为 `active unknown` 保留，而不是被过早补死

`critic` 默认追问：

- 这条档案是不是像履历表，而不像后续场面的燃料
- 这条关系是不是只有标签，没有真正会咬人的约束
- 有没有把推论、作者解释或候选想法偷写成既成 canon
- 有没有遗漏会决定后文张力的知识边界、时间约束、空间门槛或秘密线

## Workflow

1. 识别来源事实
   - 区分已写进正文的事实、用户刚确认的设定、仍属候选的想法
2. 先做 `mainline` 事实底稿
   - 只保留已经被文本或用户确认的部分
3. 跑 `explorer` pass
   - 产出 tension asset 候选、active unknown 候选、可回收场面锚点
   - 这些内容默认进入 `artifacts` 或 `recommendations`，不直接写回 canon
4. 做静态 / 动态分流
   - 静态进入 `WORLD.md`、`CHARACTERS.md`、`FACTIONS.md`、`LOCATIONS.md`、`RULES.md`
   - 动态进入 `CURRENT_STATE.md`、`RECENT_EVENTS.md`、`CHARACTER_ARCS.md`、`ARC_STATUS.md`
5. 做实体归一化
   - 统一名字、id、章节引用、关系指向
6. 做冲突检查
   - 检查是否与既有规则、时间线、角色背景、已知秘密冲突
7. 跑 `critic` gate
   - 拦 unsupported writeback、过度抽象条目、履历化角色卡、误把候选当事实
8. 输出最小变更集
   - 优先条目 patch 和 change set，不整份覆盖大文件

如果当前任务是质量闭环里的 canon repair，再额外返回：

- `touched_dimensions`
- `touched_entities`
- `expected_score_gain`
- `locked_dimensions_respected`
- `writeback_mode`
  - `proposal_only` / `minimal_patch`

## What To Preserve

除了结果事实，也尽量沉淀后续写作真正会用到的低成本记忆：

- 稳定姓名 / 角色标签
- 角色位置与关键关系
- 关系中的权力差、亏欠、互相误判和可利用裂缝
- 可观察特征
- 即时目标或长期追求
- 压力下常见反应
- 知识边界与秘密线
- 重要场面锚点
  - 例如名单、号码、楼梯、看台、面具、走廊、球衣
- 可反复调用的短 `voice pin`
- 会在未来继续施压的制度门槛或物件记忆

不要把角色档案做成只有年份、功能位和抽象标签的履历表。

## Output

至少返回：

- `status`
- `artifacts`
- `diagnostics`
- `recommendations`
- `proposed_writebacks`
- `change_set`

适合的 artifact 类型：

- `character_entry`
- `character_state_entry`
- `world_rule_entry`
- `timeline_entry`
- `arc_state_entry`
- `current_state_patch`
- `tension_asset_candidate`
- `active_unknown_candidate`
- `canon_risk_report`
- `pressure_memory_entry`

## Guardrails

- 不直接写章节正文
- 不把未确认想法写成 canon
- 不在证据不足时补完隐含设定
- 如果多个来源冲突，先给冲突清单和候选修复
- `explorer` 产物必须显式标成 `candidate`、`unknown` 或 `recommendation`
- `critic` 要区分“硬冲突”和“值得保留的未知”，不要把所有空白都当 bug 修掉
- 不为了显得深刻就把条目写成抽象评论；优先保存后续真会被场景调用的低成本记忆
- 在质量闭环里，不用扩大 canon 改写范围来掩盖正文局部问题

## Shared References

- `references/novel-system/conventions.md`
- `references/novel-system/schemas/character.schema.md`
- `references/novel-system/schemas/current-state.schema.md`
- `references/novel-system/references/context-hygiene.md`
