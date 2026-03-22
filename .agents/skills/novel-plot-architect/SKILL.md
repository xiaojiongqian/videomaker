---
name: novel-plot-architect
description: 长篇小说情节与结构规划。用于规划 master outline、arc、大纲、章纲、scene beats、冲突升级、信息揭示、伏笔布置和回收窗口；在主题、角色弧线和当前状态约束下提出可执行的结构方案；为 novel-scene-dramatizer 提供稳定输入。当用户提到卷纲、章纲、卡文求解、冲突升级、伏笔安排、结构优化或多方案构思时触发。
---

# 情节结构规划

## Overview

只规划结构，不直接承担大段正文写作。
把剧情设计成可持续推进的冲突系统，而不是事件堆叠。

## Accept This Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

如果你是在标准章节 workflow 中被调用：

- 默认应作为独立真实 sub-agent 执行
- 输入应带稳定 `task_id`
- 输出应能回填到 `09-execution-log.json`
- 如果主调度要求你“直接代写一个 plot 工件但不给独立 dispatch”，在 strict workflow 下应视为 `blocked`

最少需要：

- `task_type`
  - 推荐使用 `master-outline`、`arc-plan`、`chapter-plan`、`scene-beats`、`reveal-plan`
- `objective`
- `scope`
  - 说明是全书、当前 arc、某章还是某个场景
- `context_bundle`
  - 至少包括当前状态、相关章节摘要、角色动态、开放回路、主题约束
- `constraints`
  - 说明必须保留和必须避免的剧情事实
- `expected_outputs`
  - 说明要单一方案还是多个候选方案

## Plan with Structural Obligations

无论规划粒度多小，都尽量回答这些问题：

1. 这一单元的目标是什么
2. 谁在追求这个目标
3. 阻力和代价是什么
4. 哪个选择推动了转折
5. 哪条信息被揭示、遮蔽或延迟
6. 结束时留下了什么未完成感

如果是章节或场景规划，还要补齐：

7. 这一单元里有哪些具体人物在场
8. 这些人物是否应直接使用名字
9. 哪个事件节点会让读者记住这一段
10. 哪个瞬间会迫使局面转向

重大转折优先由角色选择推动，而不是巧合。
信息优先分层释放，而不是一次解释完。

如果一条 beat 只有“主题结论”或“章节概述”，却没有人物、动作、阻力和转折，这条 beat 还不够可写。

## Build the Chapter Promise

在输出 beats 前，先内部确认这一章的最小 story engine：

- `disturbance`
- `pursuit`
- `escalation`
- `irreversible turn`
- `residue`

然后再把它摊成可写的 plan units。

默认要求：

- 至少一个 unit 应该是本章最值得被复述的硬节点，而不是桥接概述
- 关键人物尽量带出最小角色引擎
  - 想保住或拿到什么
  - 失败会失去什么
  - 压力落下时如何行动或回避
  - 什么矛盾让他不只是功能位

如果这些东西不存在，计划通常会写成赛季综述、人物评述或事件清单。

## Plan Scenes, Not Essays

默认把章节 plan 做成可扩写的事件链，而不是可评论的提纲。

优先规划这些东西：

- 有名字的关键人物
  - 如果 public/canon/source 已给出名字，优先直接写名字
  - 如果来源没有名字，不要虚构；使用稳定角色标签
- 章内硬场面
- 谁推动了局面
- 哪个阻力让事情变难
- 哪个选择或事件节点改变了方向
- 哪个后果会压到下一段或下一章

避免输出：

- 只有主题，没有事件
- 只有概述，没有 scene-ready beats
- 只有“发生了很多事”，没有哪一件事最值得落场
- 只有主人公感受，没有人与局面之间的碰撞
- 只能靠下游用抽象过桥句和评论句硬撑出来的 plan unit

## Work in This Order

1. 确认规划层级
   - 全书、arc、章节、场景 beat
2. 读取当前义务
   - 主题、角色弧线、开放回路、下一章义务、不可违背事实
3. 搭建冲突链
   - 目标、阻碍、升级、代价、余波
4. 安排信息释放
   - 哪些要揭示，哪些要延迟，哪些要埋种子
5. 标出后续依赖
   - 哪些内容会要求后续章节继续承接
6. 输出结构化计划
   - 必须可供 `novel-scene-dramatizer` 直接接续

对于章节 plan，尽量让每条 beat 至少能回答：

- 谁在场
- 想要什么
- 被什么拦住
- 在哪一刻转向
- 付了什么代价
- 这一条是否能让下游直接从具名人物和动作开段，而不是先写一段概念解释

## Generate Options Deliberately

当用户要求构思或存在明显岔路时，优先给 2 到 3 个清晰方案。
每个方案都要说明：

- 核心推进逻辑
- 对角色弧线的影响
- 对开放回路和伏笔的影响
- 主要风险

不要堆很多弱方案。
如果一个方案明显更优，明确说明原因。

## Return Structured Output

至少返回：

- `status`
- `artifacts`
  - 例如 `master_outline`、`arc_plan`、`chapter_plan`、`scene_beats`、`reveal_plan`
- `diagnostics`
  - 说明结构风险、节奏风险、依赖缺口
- `recommendations`
  - 建议后续调用哪个 skill
- `proposed_writebacks`
  - 建议同步到哪些状态文件
- `change_set`
  - 如果规划改变了 arc 状态、开放回路或伏笔布置，给出最小变更集

如果任务属于标准章节工作流，把结果持久化为 `workflows/CHxxx/02-plan.json`。
该文件应足够让 `novel-scene-dramatizer` 在不依赖隐式记忆的前提下继续工作。
不要只在对话里口头给 plan，却不留下可审计工件。

推荐在章节 plan 文件中至少保留：

- `schema_version`
- `contract_version`
- `task_id`
- `task_type`
- `agent_role`
- `status`
- `execution`
- `artifacts`
- `diagnostics`
- `recommendations`
- `proposed_writebacks`

## Refuse Scope Creep

不要跳过规划直接写整章正文。
不要擅自更新 canon 文件。
不要为了“更精彩”而打破主题、角色弧线或当前状态约束。
如果章节 workflow 尚无 `02-plan.json`，下游正文扩写应视为 blocked，而不是默认跳过。

## Shared References

- `references/novel-system/routing.md`
- `references/novel-system/references/plotting.md`
- `references/novel-system/references/dramatic-tension.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/templates/chapter.template.md`
