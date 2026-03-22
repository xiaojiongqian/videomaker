---
name: novel-continuity-auditor
description: 长篇小说连续性与一致性审计。用于审查章纲、场景草稿、章节草稿或状态文件是否与既有设定、时间线、角色动机、知识边界、开放回路、伏笔和主题约束一致；输出结构化风险清单、严重度、证据和修复建议；适合作为并行评估子 skill 使用。当用户提到连续性检查、设定打架、时间线矛盾、角色动机不通、伏笔遗失或跨章节一致性审查时触发。
---

# 连续性审计

## Overview

专注发现问题，不默认重写正文。
把判断压缩成可排序、可证据追溯、可修复的结构化审计结果。

## Accept This Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

如果你是在标准章节 workflow 中被调用：

- 默认应作为独立真实 sub-agent 执行
- 输入至少应固定到某个 `task_id` 和 `input_snapshot`
- 如果主调度没有给独立 dispatch，却要求你伪造 `04-continuity-audit.json`，在 strict workflow 下应返回 `blocked`

最少需要：

- `task_type`
  - 推荐使用 `continuity-audit`、`character-consistency-audit`、`timeline-audit`
- `objective`
- `scope`
  - 明确待审对象
- `context_bundle`
  - 至少包括待审文本或大纲、当前状态、相关章节摘要、关键设定和角色状态
- `constraints`
  - 说明审计重点和允许忽略的维度
- `expected_outputs`
  - 要求 findings、severity、evidence 和 fix 建议

## Audit by Dimension

默认检查这些维度：

- 世界规则
- 时间线与空间连续性
- 角色动机与成长阶段
- 知识边界
- 开放回路延续
- 伏笔使用与回收窗口
- 主题与风格偏移
- `narrative-surface`
  - 是否写成评论、总结、资料改写或履历表
- `character-embodiment`
  - 关键人物是否有名字、辨识度和可见压力
- `tension`
  - 冲突是否真正落成事件、选择、代价和结果
- `readability`
  - 句子和段落是否顺读，是否长期先下判断、后补动作
- `prose-naturalness`
  - 是否频繁依赖模板句、空心短段、抽象比喻或生成腔支撑节奏

如果输入不足以判断某一维度，明确标成 `blocked` 或低置信度，不要装作确定。

## Audit the Story Engine

除了事实和连续性，也要检查章节是否具备最小可读引擎。

优先追问：

- 是否存在清楚的 `disturbance`
- 是否有人在明确 `pursuit`
- 压力是否真正 `escalation`
- 是否出现了可见的 `turn`
- 章末留下的是 `residue`，还是作者总结

如果角色名字都对、事实也没错，但 chapter promise 仍然发平，同样应报问题。

## Work in This Order

1. 列出待审对象和证据范围
2. 逐维度比对相关 state / summary / canon
3. 对每个问题给严重度、置信度和证据
4. 提出最小修复建议
5. 如果问题来自上游规划缺口，明确指出应回退到哪个 skill

把以下问题默认视为重要质量缺陷，而不是纯文风差异：

- 章节主要由总结句、评论句和抽象判断组成
- 角色长期只有功能标签，没有稳定名字和辨识度
- 读完整章记不住发生了哪几件事
- 冲突只停留在旁白判断，没有落到事件节点
- 语言频繁用空泛总括句挂段，真正的动作总在下一句或下一段才出现
- prose 听起来像模板拼接，而不是被这一章的具体事件逼出来

## Return Structured Output

至少返回：

- `status`
- `artifacts`
  - 通常为 `audit_report`
- `diagnostics`
  - 每条 findings 都应带 `analysis_dimension`、`severity`、`confidence`、`evidence_refs`
- `recommendations`
  - 建议重写正文、回退到规划、更新状态文件，或仅做轻微修补
- `proposed_writebacks`
  - 通常为空，或只建议更新审计记录

如果没有发现问题，明确返回空 findings，并说明残余风险来自哪里。

如果发现草稿“事实没错，但小说性明显不足”，也要照样报问题；不要因为它不属于硬事实错误就放过。

如果发现草稿“事实没错，但语言僵硬、难读、模板味重”，也要照样报问题；这同样属于应被门禁拦下的质量问题。

在标准章节工作流中，把结果持久化为 `workflows/CHxxx/04-continuity-audit.json`。
即使 findings 为空，也保留一份空问题审计结果，供 orchestrator 和 lint 门禁消费。

推荐至少保留：

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

不要在未被要求时重写整章。
不要把审计意见伪装成 canon。
不要跳过证据，直接说“感觉不对”。

## Shared References

- `references/novel-system/contracts.md`
- `references/novel-system/references/continuity-check.md`
- `references/novel-system/references/context-hygiene.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/references/language-surface.md`
