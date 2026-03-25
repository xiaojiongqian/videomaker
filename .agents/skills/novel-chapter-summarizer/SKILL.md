---
name: novel-chapter-summarizer
description: 长篇小说章节摘要与状态沉淀。用于把章节草稿或定稿压缩成最小可传递上下文，生成章节摘要、最近事件条目、当前状态补丁、开放回路变化和伏笔变化草案；帮助主 skill 在不灌输全文的前提下向后续章节传递记忆。当用户提到章节摘要、最近事件提取、上下文压缩、状态同步草案或归档后摘要时触发。
---

# 章节摘要沉淀

## Overview

只做压缩、提取和状态整理，不创造新剧情。
摘要的目标是给后续章节留下最小但够用的故事记忆。

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

## Workflow

1. 提取可确认事实
2. 先列事件账本
   - 谁在场
   - 谁做了什么
   - 哪个动作改变了局面
   - 后果落在谁身上
3. 区分“发生了什么”和“这意味着什么”
4. 压缩成摘要与状态变化
5. 标出不确定项和应回退重写的问题

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

## Shared References

- `references/novel-system/context-model.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/schemas/chapter-summary.schema.md`
- `references/novel-system/templates/chapter-summary.template.md`
