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

## Dispatch Scope

为保证独立审计稳定返回，默认限制如下：

- 完整 `quality_scorecard` 默认只审 `1 chapter`
- 如果一次给多章，先做 `triage pass`
  - 只返回排序、是否过线、最重 blocker
  - 不展开长篇逐章详评
- 如果输入已经超过这个粒度，优先返回 `blocked`
  - 并建议如何拆分

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
   - 前 20% 是否真的抓人
   - 是否存在不可删除的核心事件
   - 章末是否留下有效钩子
   - 是否写成总结、评论、资料改写或履历表
   - 是否缺少人物在场感、互动单元和主角声音
   - 是否桥接事实压倒硬场面
   - 是否作者直接替读者解释重点
   - 是否模板味、空心过桥句、顺读困难

## Excellent Scorecard

默认把章节质量拆成 8 个维度，每项 `0-10`：

1. `opening_hook`
2. `core_event`
3. `escalation`
4. `character_embodiment`
5. `scene_execution`
6. `ending_hook`
7. `continuity_causality`
8. `language_surface`

总分 `80`。

默认通过线：

- `score_total >= 72/80`
- 没有 `blockers`

默认 blocker 触发条件包括：

- 硬连续性冲突
- 前 20% 仍未进入扰动 / 压力
- 没有不可删除的核心事件
- 场面链塌成事实链或资料带
- 章末没有余波或钩子
- 主角长期不在压力线上且无叙事理由
- 模板味、总结味或解释句严重压过事件

如果任务运行在 `quality_council_loop` 中：

- 你的 canonical 维度只有：
  - `continuity_causality`
  - `language_surface`
- 对其余 6 个维度只给 `advisory_scores`
  - 不覆盖 owner seat 的 canonical 分
- 你仍保留对硬连续性冲突、证据不足和写回资格的最终 veto
- 首轮 gate 默认也走 `blind audit`
  - 优先只读 `seat_context_snapshot`
  - 不在交卷前偷看同轮 peer finding

## Quality Council Gate

当被 `novel-orchestrator-main` 作为 `canon_surface_gate` 调用时，优先做 gate，而不是通篇重评。

gate 职责：

- 检查 hard canon conflict、时间线断裂、知识边界错位
- 检查语言表面是否已严重伤害可读性
- 复核其他 seat 的修复是否引入新冲突
- 判断本轮产物是否具备写回资格

gate 输出至少要包含：

- `gate_decision`
  - `pass` / `continue_revision` / `blocked`
- `gate_veto`
  - 没有则显式写 `none`
- `owned_dimension_scores`
- `advisory_scores`
- `writeback_eligibility`

## Workflow

1. 列出待审对象和证据范围
2. 逐维度比对相关 state / summary / canon
3. 先给 `quality_scorecard`
4. 对每个问题给严重度、置信度和证据
5. 标出 `blockers`、`preferred_owner` 和最小修复范围
6. 给出 `pass / continue_revision / blocked` 决策
7. 如果问题来自上游规划或扩写，明确指出应回退到哪个 skill

如果当前任务是 `quality-council-gate`：

- 先给 `owned_dimension_scores`
- 再给 `gate_veto` 和 `writeback_eligibility`
- 非 owned dimension 只保留简短 advisory，不展开全面接管

如果当前 phase 是 `re-audit` 且 repair 刚完成：

- 额外检查 repair 是否引入了新的 canon 漂移、语言表面回退或 writeback 风险

如果 `constraints.output_contract` 要求紧凑模式：

- 先给结构化分数和 blocker
- 每项理由压到 `1 到 2` 句
- 不写长段散文式评论

## Output

至少返回：

- `status`
- `artifacts`
  - `quality_scorecard`
    - 每项维度分数、简短理由、`score_total`
  - `gate_seat_scorecard`
    - `continuity_causality`、`language_surface`、`gate_veto`
  - `advisory_scorecard`
    - 非 owned dimension 的观察，不覆盖 canonical score
  - `decision`
    - `pass` / `continue_revision` / `blocked`
- `diagnostics`
  - `blockers`
  - 每条 finding 带 `analysis_dimension`、`severity`、`confidence`、`evidence_refs`
- `recommendations`
  - `targeted_fix_list`
    - 每项至少包含 `failed_dimension`、`problem`、`minimal_fix`、`preferred_owner`、`rewrite_scope`
- `proposed_writebacks`

如果没有发现问题，也要说明残余风险来自哪里。

## Guardrails

- 不跳过证据直接凭感觉下判断
- 不把审计意见伪装成 canon
- 不把纯文风偏好和门禁缺陷混为一谈
- 如果输入不足，明确标记 `blocked` 或低置信度
- 不给“增强文采”这类空泛建议；修复建议必须能落到具体段落、场面或结构位点
- 如果多章任务无法在稳定预算里完成，先要求拆分，不要硬撑到超时
- 作为 gate 时，不用 advisory comment 偷偷覆盖其他 seat 的 canonical owner

## Shared References

- `references/novel-system/contracts.md`
- `references/novel-system/references/continuity-check.md`
- `references/novel-system/references/context-hygiene.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/references/language-surface.md`
