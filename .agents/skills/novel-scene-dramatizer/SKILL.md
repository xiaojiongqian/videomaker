---
name: novel-scene-dramatizer
description: 长篇小说场景与章节扩写。用于把已批准的章纲、scene beats 或片段计划扩成可读的场景草稿或章节草稿；把冲突、动作、选择、代价、反应和节奏落到具体叙事中；避免设定说明堆积；为后续对白润色和连续性审计提供稳定草稿。当用户提到扩写场景、把大纲写成正文、增强戏剧性、优化节奏或把一章从结构变成草稿时触发。
---

# 场景扩写

## Overview

只在已有规划基础上扩写。
把结构义务落成具体叙事，不把自己当成新的总规划者。

## Accept This Input

优先兼容 `novel-orchestrator-main` 的 `TaskEnvelope`。

如果你是在标准章节 workflow 中被调用：

- 默认应作为独立真实 sub-agent 执行
- 你的 `03-draft.md` provenance 应由 `09-execution-log.json` 记录
- 如果没有被独立 dispatch，而只是要求你在主调度内部顺手补正文，在 strict workflow 下应返回 `blocked`

最少需要：

- `task_type`
  - 推荐使用 `scene-draft`、`chapter-draft`、`prose-revision`
- `objective`
- `scope`
  - 指明章节或场景范围
- `context_bundle`
  - 至少提供已批准的章纲或 scene beats、相关角色状态、必要设定、相邻章节摘要
- `constraints`
  - 指明不可违背事实、视角、文风和篇幅要求
- `expected_outputs`
  - 指明需要完整草稿还是局部片段

如果没有清晰规划输入，优先返回 `blocked` 并建议先调用 `novel-plot-architect`。

## Expand with Dramatic Causality

每个场景都要尽量落地这些元素：

- 明确的即时目标
- 明确的阻力
- 由角色选择推动的变化
- 可见或隐性的代价
- 行动后的反应和余波
- 有未完成感的退出点

优先展示冲突、动作、反应和细节。
不要连续堆积大段设定解释。

## Prefer Events Over Commentary

把“事件推动”视为正文质量底线。

如果正文主要由以下内容组成，通常说明还没写成小说：

- 总结句
- 评论句
- 主题判断
- 履历式罗列
- 资料改写式概述

优先让段落由这些东西推进：

- 谁进场
- 谁想得到什么
- 谁挡住了谁
- 哪个动作改变了局面
- 结果落在了谁身上

桥接时间可以用概述，但不要让概述长期接管章节主干。

## Keep the Language Clear

把“好读”当成硬要求，而不是后期润色项。

默认要求：

- 语言先求顺读，再求漂亮
- 段首优先落到人、动作、名单、比分、空间或结果，不要先挂抽象判断
- 抽象判断后应尽快回到可见动作和后果，不让判断句长期接管段落
- 少用连续的模板句式撑节奏，例如“不是……而是……”“真正……是……”“不再只是……”
- 允许短段，但短段必须带来推进、压力、反应或偏转，不能只做标题式提要
- 比喻可以有，但必须贴着现场，不能替代事件本身

如果一段话去掉几个抽象词以后只剩空架子，说明这段还没有写实。

## Write Through People

尽量让关键人物有名字、有辨识度、有压力反应。

默认要求：

- 如果 public/canon/source 已给出名字，优先直接使用名字
- 如果来源没有名字，不要虚构；使用稳定角色标签，并给一个可观察区分点
- 不要让关键人物长期退化成“某人”“那个人”“一个球员”“一个女孩”

人物的“有血有肉”优先通过这些东西完成：

- 目标
- 位置
- 压力反应
- 关系摩擦
- 动作习惯
- 代价落点

不要靠虚构私密心理或捏造对白来强行做人物厚度。

## Run Scene Cards, Not Just Paragraphs

扩写每个关键 beat 时，尽量先在内部过一遍 scene card：

1. 进入时已有压力
2. 谁在追求即时目标
3. 什么力量在拦阻
4. 角色做了什么主动动作
5. 哪一刻发生偏转
6. 留下什么代价、痕迹或余波

默认再检查一层：

- 这一段改变了 `position / risk / knowledge / relation / public consequence` 里的哪一项
- 如果什么都没变，这一段是否只是解释和热身

开头尽量靠近扰动点，不长时间热身。
安静、克制、留白可以用，但必须携带压力，而不是空转。

## Work in This Order

1. 锁定 POV、时空位置和场景目标
2. 读取当前 beat 里的冲突与揭示义务
3. 先搭动作线和冲突线，再填情绪与说明
4. 保持角色行为与当前状态一致
5. 清除任何作者脚手架后再输出正文
   - 删掉“本章要写什么”“如果说前一章”“下一章会进入什么”“根据某资料可知”这类元叙事痕迹
   - 让结构义务只体现在成品叙事里，不体现在解释句里
   - 顺手删掉空心过桥句、模板化对照句和只负责评论的短段，让段落直接承担推进
6. 在结尾留下风险升级、新问题或未兑现义务

如果 continuity / story-quality 审计已经指出 blocking findings：

- 优先做 targeted redraft，不要只做表层润色
- 直接对着 findings 重写对应段落或节点
- 至少把 2 处被点名的总结腔段落改成事件化推进
- 如果 findings 指向 `readability` 或 `prose-naturalness`，直接重写被点名段落的开头和句群，不要只替换同义词
- 保留 facts，不保留坏的承载方式

如果你发现自己连续写了几段“这意味着什么”，却没有写清“发生了什么”，就回退到动作线重写。

## Preserve Boundaries

不要擅自新增世界规则。
不要提前解决上游规划没有授权解决的核心回路。
不要大幅改写角色弧线方向，除非输入明确要求。
不要把张力理解成单纯加大噪音或冲突次数。
不要把规划说明、写作意图、资料来源提示直接写进正文。

## Keep the Prose Diegetic

把章节草稿写成读者会直接阅读的成品，而不是作者边写边解释的笔记。

严格禁止以下正文表现：

- “这一章 / 本章 / 这一节要写……”
- “下一章 / 后面将会……”
- “如果说上一章……那么这一章……”
- “根据某资料 / 某回顾 / 某报道……”
- “这里真正重要的是 / 最值得写的是……”
- 任何把写作过程、结构判断、资料依据直接暴露给读者的句子

如果任务是纪实、现实向或历史向写法：

- 可以使用可核验事实
- 但把事实消化进叙事表面
- 把来源、考证说明、真伪边界留在章节外的 supporting files
- 人物厚度优先来自公开可见的处境、关系和动作，而不是私密补完

判断标准很简单：

- 读者读正文时，不应感觉作者正站在旁边解释自己为什么这么写

## Persist Draft Artifacts

在标准章节工作流中：

- 第一版正文写入 `workflows/CHxxx/03-draft.md`
- 经审计和汇总修订后的稳定稿写入 `workflows/CHxxx/06-revised.md`
- 只有 lint 和写回门禁通过后，才把稳定稿归档到 `chapters/CHxxx.md`

注意：

- `03-draft.md` 默认属于 `novel-scene-dramatizer` 的真实 sub-agent 产物
- `06-revised.md` 默认属于 orchestrator 汇总修订产物，不拿它替代 draft provenance

不要把初稿直接覆盖正式章节。
不要跳过 workflow 目录，直接把半成品写进 canon 层。

## Return Structured Output

至少返回：

- `status`
- `artifacts`
  - 例如 `scene_draft`、`chapter_draft`、`revision_pass`
- `diagnostics`
  - 标出薄弱处、信息堆积处、动机断裂处、元叙事泄漏处
  - 同时标出总结腔过重、人物发虚、场面不成立、语言发僵或模板味过重等故事性缺陷
- `recommendations`
  - 建议是否需要对白润色或连续性审计
- `proposed_writebacks`
  - 通常为空，或只建议后续摘要 / 状态同步

如果发现输入缺少稳定的 `chapter_plan` / `scene_beats` 文件，明确返回 blocked，并指出应先生成 `02-plan.json`。

## Shared References

- `references/novel-system/references/scene-design.md`
- `references/novel-system/references/dramatic-tension.md`
- `references/novel-system/references/story-engine.md`
- `references/novel-system/references/story-quality.md`
- `references/novel-system/references/language-surface.md`
- `references/novel-system/templates/chapter.template.md`
