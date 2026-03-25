---
name: novel-plot-architect
description: 长篇小说情节与结构规划。用于规划 master outline、arc、大纲、章纲、scene beats、冲突升级、信息揭示、伏笔布置和回收窗口；在主题、角色弧线和当前状态约束下提出可执行的结构方案；为 novel-scene-dramatizer 提供稳定输入。当用户提到卷纲、章纲、卡文求解、冲突升级、伏笔安排、结构优化或多方案构思时触发。
---

# 情节结构规划

## Overview

只规划结构，不直接承担正文。
目标是给下游一个够用、易写、不会把正文写僵的 plan。

## Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

最少需要：

- `task_type`
- `objective`
- `scope`
- `context_bundle`
  - 至少包括当前状态、相关摘要、角色动态、开放回路
- `constraints`
- `expected_outputs`

## Planning Rules

无论粒度大小，都尽量回答：

1. 谁在追求什么
2. 什么在阻拦
3. 哪个选择或事件推动转折
4. 代价落在哪
5. 结束时留下什么未完成感

章节规划时，再补：

- `disturbance`
- `pursuit`
- `escalation`
- `irreversible turn`
- `residue`

如果这些说不清，说明 plan 还不够可写。

## Plan Scenes, Not Essays

默认输出轻量章节 plan：

- 1 个 dominant scene
- 1 条压力线
- 3 到 5 个 beats
- 1 个章末余波

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

1. 确认规划层级
2. 读取当前义务
3. 搭建冲突链
4. 安排信息释放
5. 压缩成 scene-ready beats
6. 标出后续依赖和不可违背事实

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

## Guardrails

- 不要把 plan 写成章节评论
- 不要只给主题结论不给场面
- 不要靠巧合推动重大转折
- 如果某条 beat 稍微压缩就变成时间线条目，继续补足场面支点或互动单元

## Shared References

- `references/novel-system/references/plotting.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/scene-design.md`
- `references/novel-system/references/story-quality.md`
