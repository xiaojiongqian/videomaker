---
name: novel-orchestrator-main
description: 长篇小说工程主调度与共享真源宿主。用于把长篇小说项目当作有状态、可持续维护的创作工程来推进：识别当前任务属于规划、生成、审计还是状态同步；决定最小上下文加载；安排串行或并行步骤；协调 novel-bible-manager、novel-plot-architect、novel-scene-dramatizer、novel-dialogue-editor、novel-continuity-auditor、novel-chapter-summarizer 等子 skill；校验契约并统一写回 INDEX.md、CURRENT_STATE.md、OPEN_LOOPS.md、FORESHADOWS.md、CHARACTER_ARCS.md、RECENT_EVENTS.md 等文件。它还作为共享 novel-system 资料的唯一真源。当用户提到长篇小说策划、章节推进、设定维护、连续性检查、章节摘要、伏笔追踪或状态同步时触发。
---

# 长篇小说主调度

## Overview

把小说项目视为“正文 + 状态”的双轨系统。
你负责解释任务、裁剪上下文、选择子 skill、汇总结果、决定写回。

总优先级固定如下：

1. 先写出好读、像小说的正文
2. 再补流程工件和状态沉淀

不要为了 workflow 完整性牺牲成品阅读感。

## Core Principles

- `readability first`
  - 先让读者顺着读懂谁在场、卡在哪、发生了什么、局面怎么变
- `scene chain over fact chain`
  - 每章优先围绕 1 个 dominant scene 展开，必要时再加 1 个扩展场面
  - 其余同型节点优先压成 `bridge cluster`
- `minimum viable planning`
  - plan 只需要够写，不要过满到逼正文照施工图执行
- `state supports prose`
  - 状态文件帮助后续写作，不反过来统治正文
- `serial by default`
  - 生成新内容后再做审计和摘要；只有互不污染的分析任务才并行

## Read Context Progressively

默认按四层加载：

1. `INDEX.md`、`CURRENT_STATE.md`
2. `OPEN_LOOPS.md`、`CHARACTER_ARCS.md`、`RECENT_EVENTS.md`、`ARC_STATUS.md`
3. `WORLD.md`、`CHARACTERS.md`、`RULES.md` 等静态设定
4. 当前章节、相邻章节、相关摘要

只给子 skill 它真正需要的最小上下文。

## Route by Task

- `novel-bible-manager`
  - 维护静态设定和动态状态
- `novel-plot-architect`
  - 规划 arc、章纲、scene beats、信息释放
- `novel-scene-dramatizer`
  - 把已批准计划扩成场景或章节草稿
- `novel-dialogue-editor`
  - 修对白和互动声音
- `novel-continuity-auditor`
  - 做连续性、小说性和语言表面门禁
- `novel-chapter-summarizer`
  - 生成最小可传递记忆和状态写回草案

如果一个任务同时要求“生成”和“判断”，先生成，再审计。

## Set the Chapter Promise

章节起草前，先确认最小引擎：

- `disturbance`
- `pursuit`
- `escalation`
- `irreversible turn`
- `residue`

对纪实 / 传记 / 比赛线，再补四个问题：

- dominant scene 是哪个具体时刻、物件或比赛节点
- 压力线如何从开头压到章末
- 哪些内容只是 `bridge facts`
- 章末余波是什么，不要只剩主题总结

如果这些说不清，先回退给 `novel-plot-architect`。

## Standard Chapter Flow

默认章节流程：

1. 读最小状态
2. 立 chapter promise
3. 如需规划，调用 `novel-plot-architect`
4. 调用 `novel-scene-dramatizer` 生成或修正文稿
5. 如对白薄弱，再调用 `novel-dialogue-editor`
6. 调用 `novel-continuity-auditor` 做门禁
7. 通过后调用 `novel-chapter-summarizer`
8. 只在结果稳定后写回状态文件

## Quality Bar

默认拦截这些问题：

- 开头三段内仍未真正进入张力
- 一章塞太多同型节点，读感变成资料带
- 桥接事实压倒硬场面
- 主角长期只被旁白代言
- 章末只剩作者总结，没有余波
- 语言顺读但读者说不清“这一章到底往前走了哪一步”

如果用户要求“写厚”：

- 至少保证 2 个有效互动单元，或 1 条持续升级的互动链
- 主角应至少有一次明确回应
  - 开口、动作、短心理线都可以
- 加厚后的新增篇幅必须增加 `contact` 或 `shift`，不能只增加解释

## Write Back Conservatively

只写回已经被正文或用户明确确认的事实。
如果存在冲突、不确定解释或正文仍未稳定，先保留在 `diagnostics` 和 `recommendations`，不要抢先改 canon。

## Output

至少返回：

- `status`
- `routing_decision`
- `artifacts`
- `diagnostics`
- `recommendations`
- `proposed_writebacks`

## Shared References

- `references/novel-system/contracts.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/references/language-surface.md`
