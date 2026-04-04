---
name: novel-chapter-summarizer
description: 长篇小说章节摘要与状态沉淀。用于把章节草稿或定稿压缩成最小可传递上下文，生成章节摘要、最近事件条目、当前状态补丁、开放回路变化和伏笔变化草案；帮助主 skill 在不灌输全文的前提下向后续章节传递记忆；并以 `mainline / explorer / critic` 三角张力避免把余波和义务压扁成平面摘要。当用户提到章节摘要、最近事件提取、上下文压缩、状态同步草案或归档后摘要时触发。
---

# 章节摘要沉淀

## Overview

只做压缩、提取和状态整理，不创造新剧情。
摘要的目标是给后续章节留下最小但够用的故事记忆。

你默认同时承担三个 stance：

- `mainline`
  - 提取稳定事实并完成最小摘要
- `explorer`
  - 找出真正值得带进后文的余波、压差、未完成义务和可回收锚点
- `critic`
  - 拦截把核心事件写成主题判断、漏掉后果或把猜测偷塞进摘要

## Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

最少需要：

- `task_type`
- `objective`
- `scope`
- `context_bundle`
  - 至少包括目标章节或稳定草稿、相关状态、相邻章节摘要
- `constraints`
- `expected_outputs`

如果 `context_bundle.quality_loop_report` 明确显示本章仍未 `pass`，且用户没有显式要求“先总结未稳定草稿”，默认返回 `blocked` 或 `needs_review`。
摘要沉淀默认只服务于已过线或已被用户明确确认的文本版本。

`explorer` 默认追问：

- 本章最该继续发热的余波是什么
- 哪个关系变化、物件、短话语或门槛最值得后文记住
- 哪个 `open loop` 虽未解决，但已经被明显推进

`critic` 默认追问：

- 摘要有没有把事件压成空泛结论
- 有没有漏掉真正改变局面的动作
- 有没有把解释、推测或主题评论写得比事件更重

## Workflow

1. 提取可确认事实
   - 先确认本章是否已经通过 `quality_council_loop` 或得到用户明确确认
2. 先做 `mainline` 事件账本
   - 谁在场
   - 谁做了什么
   - 哪个动作改变了局面
   - 后果落在谁身上
3. 跑 `explorer` pass
   - 标出真正需要 carry forward 的 tension residue 和记忆锚点
4. 跑 `critic` pass
   - 检查是否压扁核心事件、漏掉后果或夹带推测
5. 区分“发生了什么”和“这意味着什么”
6. 压缩成摘要与状态变化
7. 标出不确定项和应回退重写的问题

## What To Preserve

默认保留这些内容：

- `one_line_summary`
  - 写明本章真正跨过的门槛或局面变化
- `major_beats`
  - 具名人物、关键动作、场面锚点
- `actor_refs`
- `state_changes`
- `open_loops`
  - `opened`
  - `advanced`
  - `resolved`
- `carry_forward`
  - 下一章必须承接的余波、义务和风险

优先保留场面记忆，而不是主题评论：

- 物件、号码、空间、名单、比分
- 关键互动单元
- 主角回应节点
- 关键短话语或 later quote

如果原章本身过于概述，导致无法提炼清晰事件锚点，要在 `diagnostics` 里明确指出，不要替正文发明细节。

## Output

至少返回：

- `status`
- `artifacts`
- `diagnostics`
- `recommendations`
- `proposed_writebacks`
- `change_set`
- `carry_forward_tension_list`
- `summary_loss_report`

推荐 `chapter_summary` 使用稳定结构：

- `one_line_summary`
- `major_beats`
- `actor_refs`
- `state_changes`
- `open_loops`
- `carry_forward`

## Guardrails

- 不补写新桥段
- 不把推测当成既成事实
- 不输出比原章更长的“摘要”
- 不借摘要夹带主题结论和作者解释
- `explorer` 只能强化保留，不能发明新伏笔或新剧情
- `critic` 要分清“文本有意保留空白”和“摘要把关键义务漏掉了”这两件事
- 对未过线草稿，不默认产出可直接写回状态文件的摘要

## Shared References

- `references/novel-system/context-model.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/schemas/chapter-summary.schema.md`
- `references/novel-system/templates/chapter-summary.template.md`
