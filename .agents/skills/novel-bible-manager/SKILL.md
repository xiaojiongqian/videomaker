---
name: novel-bible-manager
description: 长篇小说设定与状态档案维护。用于维护和修订世界观、角色、势力、地点、规则、时间线、角色动态状态等结构化 canon；把零散创作笔记或章节事实沉淀到 WORLD.md、CHARACTERS.md、RULES.md、CHARACTER_ARCS.md、ARC_STATUS.md 等状态文件；区分静态设定与动态演进；处理设定冲突、档案压缩、条目规范化。当用户提到角色卡更新、设定整理、故事圣经维护、时间线条目、状态文件修订或 canon 冲突修复时触发。
---

# 设定档案维护

## Overview

只维护结构化 canon 和状态，不负责整章正文。
目标是把事实整理成后续写作可检索、可比对、可更新的条目。

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

## Workflow

1. 识别来源事实
   - 区分已写进正文的事实、用户刚确认的设定、仍属候选的想法
2. 做静态 / 动态分流
   - 静态进入 `WORLD.md`、`CHARACTERS.md`、`FACTIONS.md`、`LOCATIONS.md`、`RULES.md`
   - 动态进入 `CURRENT_STATE.md`、`RECENT_EVENTS.md`、`CHARACTER_ARCS.md`、`ARC_STATUS.md`
3. 做实体归一化
   - 统一名字、id、章节引用、关系指向
4. 做冲突检查
   - 检查是否与既有规则、时间线、角色背景、已知秘密冲突
5. 输出最小变更集
   - 优先条目 patch 和 change set，不整份覆盖大文件

## What To Preserve

除了结果事实，也尽量沉淀后续写作真正会用到的低成本记忆：

- 稳定姓名 / 角色标签
- 角色位置与关键关系
- 可观察特征
- 即时目标或长期追求
- 压力下常见反应
- 重要场面锚点
  - 例如名单、号码、楼梯、看台、面具、走廊、球衣
- 可反复调用的短 `voice pin`

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

## Guardrails

- 不直接写章节正文
- 不把未确认想法写成 canon
- 不在证据不足时补完隐含设定
- 如果多个来源冲突，先给冲突清单和候选修复

## Shared References

- `references/novel-system/conventions.md`
- `references/novel-system/schemas/character.schema.md`
- `references/novel-system/schemas/current-state.schema.md`
- `references/novel-system/references/context-hygiene.md`
