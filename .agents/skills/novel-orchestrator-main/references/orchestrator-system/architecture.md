# Architecture

## Main Skill

`novel-orchestrator-main` 是唯一全局状态协调者。

它负责：

- 理解用户意图
- 识别任务类型
- 决定上下文加载范围
- 判断步骤该串行还是可并行
- 选择要调用的子 skill
- 校验子 skill 结果
- 决定最终写回哪些文件

子 skill 不应自行决定全局状态写回。
子 skill 不应自行解释整个项目状态。

## Quality Council Layer

当任务目标是“写到可发布”而不是“先出一稿”时，主调度默认加一层 `quality_council_loop`。

这一层的职责划分如下：

- orchestrator
  - 生成 round id
  - fan-out 多个独立评分席位
  - 汇总 canonical scorecard
  - 决定修复 owner、修复顺序和停止条件
- `novel-plot-architect`
  - `story_engine_seat`
  - 拥有 `opening_hook`、`core_event`、`escalation`
- `novel-scene-dramatizer`
  - `scene_heat_seat`
  - 拥有 `scene_execution`、`ending_hook`
- `novel-dialogue-editor`
  - `voice_embodiment_seat`
  - 拥有 `character_embodiment`
- `novel-continuity-auditor`
  - `canon_surface_gate`
  - 拥有 `continuity_causality`、`language_surface`
  - 对 hard blocker 和 writeback eligibility 拥有 veto

质量闭环的本质不是“更多意见”，而是“把评分权拆成稳定契约”。
这样每个 sub-agent 只负责自己最擅长、最可复查的维度。

## Sub-Skills

- `novel-bible-manager`
  - 维护静态设定与动态状态条目
- `novel-plot-architect`
  - 规划主线、arc、章纲、scene beats、揭示与伏笔
- `novel-scene-dramatizer`
  - 把规划扩写为场景或章节草稿
- `novel-dialogue-editor`
  - 打磨对白与角色声音
- `novel-continuity-auditor`
  - 审计连续性、动机、时间线、知识边界和回路延续
- `novel-chapter-summarizer`
  - 沉淀章节摘要和状态同步草案

## State Model

项目状态分三类：

- 正文产物
  - `chapters/`
- 结构化工作记忆
  - `CURRENT_STATE.md`、`OPEN_LOOPS.md`、`FORESHADOWS.md`、`CHARACTER_ARCS.md`
- 稳定基础设定
  - `WORLD.md`、`CHARACTERS.md`、`RULES.md` 等

静态设定与动态演进必须分离。
正文与状态文件必须分离。

## Coordination Rule

所有跨 skill 协作都通过版本化契约完成。
所有影响全局状态的结果都优先以 change set 形式返回。
