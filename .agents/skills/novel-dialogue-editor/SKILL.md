---
name: novel-dialogue-editor
description: 长篇小说对白与角色声音修订。用于打磨对白、区分角色口吻、增强潜台词、压缩直白解释、修正对白中的角色串音，并在不破坏剧情事实的前提下以 `mainline / explorer / critic` 三角张力提升谈话场景的压差和辨识度。当用户提到对白打磨、角色说话太像、潜台词不足、台词太直白、对话场景发虚或需要对白审校时触发。
---

# 对白声音修订

## Overview

只修对白和对白附近的互动，不接管整章结构。
目标是让角色通过目标、节奏、回避方式和用词显出区别。

你默认同时承担三个 stance：

- `mainline`
  - 给出最小可落地的对白修订
- `explorer`
  - 试出更有压差、潜台词和互动反弹的 line / interaction option
- `critic`
  - 拆穿串音、直白解释、装饰性机锋和“看似有火花其实没推进”的台词

## Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

最少需要：

- `task_type`
- `objective`
- `scope`
- `context_bundle`
  - 至少包括原对白、说话者、角色状态、场景压力
  - 若来自质量闭环，还应包括 `quality_scorecard`、`blockers`、`targeted_fix_list`
- `constraints`
- `expected_outputs`

## Targeted Voice Fix

如果任务来自审计闭环，只修对白和互动类 blocker。

默认做法：

- 锁住既有事实和 beats，不改剧情骨架
- 优先修 `character_embodiment`、潜台词、串音、解释性台词
- 能用 1 到 3 处局部替换解决，就不要整场重写
- 如果根因是场景太薄，明确回退 `novel-scene-dramatizer`

`explorer` 默认找：

- 哪句台词可以少说半句，但让关系更紧
- 哪个打断、停顿、转移话题或动作比直接解释更有力
- 哪个角色其实应该更会回避、顶回去、装傻或借物说话

`critic` 默认拦：

- 所有人都说得一样聪明或一样克制
- 角色把潜台词直接解释出来
- 只有好听句子，没有局面变化
- 为了“有张力”硬塞不符合身份的信息或表白

## Workflow

1. 识别说话者此刻想要什么、怕什么、如何回避
2. 先做 `mainline` 修订草案
3. 跑 `explorer` pass
   - 产出 `1 到 3` 个更强 line / interaction option
4. 跑 `critic` pass
   - 拆穿串音、直白解释、无推进感
5. 在不改变事实的前提下选最小强升级
6. 如果根因是场景太薄，明确回退给上游

## Editing Priorities

优先检查：

- 不同角色是否说得太像
- 台词是否把潜台词直接说穿
- 对话是否真的推动冲突或关系变化
- 主角是否真正到场，而不是只靠旁白代言
- 是否有来源支撑的短话语、转述或互动动作可用

如果任务是纪实骨架写法：

- 不要用对白改写关键事实
- 如果没有可靠引语，优先做 `interaction pass`
  - 用提醒、照看、起身、停顿、热身、摘面具等人际动作补现场感
- 如果连互动单元都薄，明确建议回退 `novel-scene-dramatizer`

## Output

至少返回：

- `status`
- `artifacts`
- `diagnostics`
- `recommendations`
- `proposed_writebacks`

常见 artifact：

- `dialogue_revision`
- `line_alternatives`
- `voice_notes`
- `subtext_option_set`
- `dialogue_break_report`

## Guardrails

- 不无授权改写核心情节
- 不为了文采抹掉角色差异
- 不用几句修辞掩盖场景结构问题
- 如果直接开口会破坏真实感，优先用动作或短心理线，不要硬加引号
- `explorer` 不得虚构会改写事实的新秘密或关键告白
- `critic` 不得把所有锋利感都削成安全中性口吻

## Shared References

- `references/novel-system/references/dialogue.md`
- `references/novel-system/references/dramatic-tension.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/language-surface.md`
