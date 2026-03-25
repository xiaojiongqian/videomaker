---
name: novel-continuity-auditor
description: 长篇小说连续性与一致性审计。用于审查章纲、场景草稿、章节草稿或状态文件是否与既有设定、时间线、角色动机、知识边界、开放回路、伏笔和主题约束一致；输出结构化风险清单、严重度、证据和修复建议；适合作为并行评估子 skill 使用。当用户提到连续性检查、设定打架、时间线矛盾、角色动机不通、伏笔遗失或跨章节一致性审查时触发。
---

# 连续性审计

## Overview

专注发现问题，不默认重写正文。
除了硬连续性，也要拦“事实没错但小说性明显不足”的草稿。

## Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

最少需要：

- `task_type`
- `objective`
- `scope`
- `context_bundle`
  - 至少包括待审文本、相关状态、章节摘要、关键设定
- `constraints`
- `expected_outputs`

## Audit Dimensions

默认检查三组问题：

1. 连续性
   - 世界规则
   - 时间线与空间顺序
   - 角色动机与知识边界
   - 开放回路、伏笔、主题偏移
2. 故事引擎
   - 是否有 `disturbance / pursuit / escalation / turn / residue`
   - 冲突是否真正落成事件、选择、代价和结果
3. 语言与表面
   - 是否写成总结、评论、资料改写或履历表
   - 是否缺少人物在场感、互动单元和主角声音
   - 是否桥接事实压倒硬场面
   - 是否作者直接替读者解释重点
   - 是否模板味、空心过桥句、顺读困难

## Workflow

1. 列出待审对象和证据范围
2. 逐维度比对相关 state / summary / canon
3. 对每个问题给严重度、置信度和证据
4. 给出最小修复建议
5. 如果问题来自上游规划或扩写，明确指出应回退到哪个 skill

## Output

至少返回：

- `status`
- `artifacts`
- `diagnostics`
  - 每条 finding 带 `analysis_dimension`、`severity`、`confidence`、`evidence_refs`
- `recommendations`
- `proposed_writebacks`

如果没有发现问题，也要说明残余风险来自哪里。

## Guardrails

- 不跳过证据直接凭感觉下判断
- 不把审计意见伪装成 canon
- 不把纯文风偏好和门禁缺陷混为一谈
- 如果输入不足，明确标记 `blocked` 或低置信度

## Shared References

- `references/novel-system/contracts.md`
- `references/novel-system/references/continuity-check.md`
- `references/novel-system/references/context-hygiene.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/references/language-surface.md`
