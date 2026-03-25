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
- `excellent chapter gate`
  - 前 20% 内必须有即时张力、重大事件或情感冲击
  - 每章至少有 1 个不可删除的核心事件
  - 章末必须留下仍在发热的钩子，不用主题总结收口
- `scene chain over fact chain`
  - 每章优先围绕 1 个 dominant scene 展开，必要时再加 1 个扩展场面
  - 其余同型节点优先压成 `bridge cluster`
- `bounded quality loop`
  - 先拿到可审草稿，再做独立审计
  - 只修 `blockers` 和最低分维度，不整章反复推倒
  - 默认最多 3 轮；提升不足 `3/80` 或修复开始外溢时停止
- `small dispatches beat heroic dispatches`
  - sub-agent 默认吃小任务，不吃“十章一起审”这类大包
  - 先做轻量分诊，再把真正需要处理的章节拆开
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

对 sub-agent 默认再加三条限制：

- 全量质量审计默认 `1 chapter / dispatch`
- 定向修订默认 `1 chapter` 或 `1 dominant scene chain / dispatch`
- 多章节请求先做 `triage pass`，不要直接把详细 scorecard 压给一个 agent

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
  - 输出 `quality_scorecard`、`blockers`、`targeted_fix_list`
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
6. 进入 `quality_loop`
7. 通过后调用 `novel-chapter-summarizer`
8. 只在结果稳定后写回状态文件

## Keep Sub-Agent Runs Small

默认粒度：

- `novel-continuity-auditor`
  - 1 章完整 scorecard
  - 最多 2 章轻量分诊，不输出长篇逐章细评
- `novel-plot-architect`
  - 1 章 plan 或 1 组 repair cluster
- `novel-scene-dramatizer`
  - 1 章正文或 1 条 dominant scene chain
- `novel-dialogue-editor`
  - 1 个对话场景或 1 章的对白修订

如果用户一次点名 `CH001-CH010`：

1. 先本地或轻量 sub-agent 做分诊
2. 只把低分章拆出去单独审
3. 修复后只复审动过的章节

## Run the Quality Loop

当目标是“写到优秀 / 达标 / 可发布”时，默认执行有界闭环：

1. `pass_0`
   - 基于现有 plan 或现稿，先拿到一版可审文本
2. `independent audit`
   - 调用 `novel-continuity-auditor`
   - 如果运行环境支持 sub-agent，优先独立 dispatch，避免生成方自评
   - 如果只能串行 fallback，在 `diagnostics` 标明
   - 默认 1 章 1 个 audit dispatch；多章只做 triage
3. `stop on pass`
   - 若 `score_total >= 72/80` 且无 `blockers`，视为达到优秀线
4. `route only failed dimensions`
   - 把每个 blocker 转成 1 个最小修复任务
   - 优先修最低分维度和会卡住整章读感的硬伤
5. `owner mapping`
   - 结构缺口、核心事件缺失、压力线失效：`novel-plot-architect`
   - 开头不抓人、场面发虚、桥接过量、章末不热：`novel-scene-dramatizer`
   - 角色串音、潜台词太直白、对白无压：`novel-dialogue-editor`
   - 设定 / 时间线 / canon 冲突：`novel-bible-manager`
6. `re-audit`
   - 修完后必须再次调用 `novel-continuity-auditor`
7. `stop conditions`
   - 达到通过线
   - 已做 3 轮
   - 本轮提升小于 `3/80`
   - 为修 1 个局部问题开始引发大面积结构漂移

不要把它实现成无限“重写直到满意”。
闭环目标是稳定抬高成品，不是制造永动机。

## Timeout Recovery Ladder

sub-agent 超时不是“多等一会儿”就算处理了。
默认按下面顺序恢复：

1. `single wait`
   - 只做一次正常等待，不忙轮询
2. `shrink and respawn`
   - 如果超时，先减半 scope，再收紧输出格式
   - 默认只重派 1 次
3. `approved fallback`
   - 第二次仍超时，只有分析 / 摘要 / 轻量定向修订允许 fallback
   - 必须在 `execution` 和 trace 里登记 `subagent-timeout` 或 `subagent-no-response`
4. `quality guard`
   - timeout fallback 产物不能单独作为 canon 写回依据
   - 遇到 blocker、设定冲突或大结构改动，宁可停在 `needs_review`
5. `close stale agents`
   - 超时的旧 agent 不要长期挂着，避免后续结果互相污染

稳定性来自缩 scope、收格式、记退化，不来自无限等待。

## Quality Bar

默认拦截这些问题：

- 开头三段内仍未真正进入张力
- 第一场景可以整段删除而不伤主线
- 一章塞太多同型节点，读感变成资料带
- 桥接事实压倒硬场面
- 主角长期只被旁白代言
- 章末只剩作者总结，没有余波
- 关键情绪主要靠解释句，而不是动作、反应和物件落地
- 语言顺读但读者说不清“这一章到底往前走了哪一步”

默认通过线：

- `score_total >= 72/80`
- 无 `blockers`
- 读者能复述本章核心事件、压力升级和章末余波

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
  - 如运行 `quality_loop`，补 `quality_loop_report`
- `diagnostics`
- `recommendations`
- `proposed_writebacks`
- `execution`
  - 如发生 timeout recovery，补 `degraded_execution`、`recovery_actions`、`fallback_reason_codes`

## Shared References

- `references/novel-system/contracts.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/references/language-surface.md`
