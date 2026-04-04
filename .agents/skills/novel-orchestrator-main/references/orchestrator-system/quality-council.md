# Quality Council

`quality_council_loop` 是 `novel-orchestrator-main` 的默认高质量章节闭环。

它解决两个问题：

- 生成 agent 容易对自己的草稿过宽
- 单一审计器容易把“结构、场面、对白、连续性”混成一张大意见单

它还坚持两个工程原则：

- 互相校验必须建立在独立上下文上
- 质量来自不同力量的拉扯，而不是快速求和

## Minimum Complete Unit

最小完整单元不是“一个人写完再自己改”，而是一轮完整的：

1. 生成可审草稿
2. 多席位独立评分
3. 汇总 failed dimensions
4. 最小修复
5. 复审

只要这五步能闭环，系统就能递归扩展到单章、单场面和跨章分诊。

## Seat Ownership

- `story_engine_seat`
  - skill: `novel-plot-architect`
  - task_type: `quality-seat-story-engine`
  - owns: `opening_hook`, `core_event`, `escalation`
- `scene_heat_seat`
  - skill: `novel-scene-dramatizer`
  - task_type: `quality-seat-scene-heat`
  - owns: `scene_execution`, `ending_hook`
- `voice_embodiment_seat`
  - skill: `novel-dialogue-editor`
  - task_type: `quality-seat-voice-embodiment`
  - owns: `character_embodiment`
- `canon_surface_gate`
  - skill: `novel-continuity-auditor`
  - task_type: `quality-council-gate`
  - owns: `continuity_causality`, `language_surface`
  - veto: hard blocker, writeback eligibility

非 owner seat 可以评论，但不能覆盖 canonical score。

## Independent Context Protocol

`quality_council_loop` 的首轮评分默认是 `blind audit`：

- 每个 seat 收到独立的 `seat_context_snapshot`
- 不共享同轮 `peer_findings`
- 不共享同轮 `peer_scorecards`
- 不把 author self-justification 当首轮评分依据

主调度只有在所有 seat 独立交卷后，才做聚合。
如果一开始就共享解释，系统会更快达成表面一致，也更快失去真正的互相校验。

## Pass Rule

默认通过线：

- `score_total >= 72/80`
- 无 `blockers`
- 无 canonical 维度低于 `7/10`
- `canon_surface_gate` 没有 veto

## Ratchet Rule

为了避免闭环抖动，主调度默认维护 `locked_dimensions`：

- `>= 8/10` 且无 blocker 的维度进入锁定
- 后续轮次除非有新证据证明回归，否则不再改
- repair owner 必须声明是否尊重了锁定维度

## Repair Routing

默认一次只修最小 cluster：

- 结构根因：`novel-plot-architect`
- 场面热度 / 章末余波：`novel-scene-dramatizer`
- 角色在场感 / 对白压差：`novel-dialogue-editor`
- `language_surface`
  - 默认：`novel-scene-dramatizer`
  - 若问题局部集中在对白：`novel-dialogue-editor`
- canon / 时间线 / 状态冲突：`novel-bible-manager`

每轮默认最多 `2` 个 repair owner，避免多头改稿互相污染。

## Counterforce Protocol

repair 不以 owner 自报“修好了”为准。
默认再派一个 `counterforce seat` 从相反方向复核：

- `novel-plot-architect` repair
  - counterforce: `scene_heat_seat`
  - 主要防“结构更稳，但场面变冷”
- `novel-scene-dramatizer` repair
  - counterforce: `story_engine_seat`
  - 主要防“更热闹，但推进更空”
- `novel-dialogue-editor` repair
  - counterforce: `scene_heat_seat`
  - 主要防“台词更好听，但压力不落地”
- `novel-bible-manager` repair
  - counterforce: `story_engine_seat`
  - 主要防“canon 更干净，但章节推进被写扁”

`canon_surface_gate` 不替代 counterforce，它只负责最终门禁和 veto。

## Convergence Guard

默认停止条件：

- 达到通过线
- 已做 `3` 轮
- 总分提升小于 `3/80`
- 没有任何 failed dimension 至少提升 `1`
- 同一 blocker 连续两轮重复
- 修复开始破坏已锁定维度

这是一套收敛机制，不是永动机。
