# Workflow Workspace

本目录保存单章工作流工件。

## Conventions

- 每章一个目录，例如 `CH005/`
- `_template/` 提供空模板
- `init_chapter_workflow.py` 用于从模板初始化新章节目录
- 正式章节推进时，优先走固定的多 agent 协作流程，而不是临时拼接步骤

## Why Only CH001-CH006 Exists Now

- `CH001` 到 `CH006` 是早期已经完整留痕的章节工作流。
- `CH007` 之后的正文和摘要虽然已经完成，但没有继续把同等粒度的 workflow 工件归档到本目录。
- 这不表示后续章节没有写完，只表示“workflow 台账”没有继续同步。

## Fixed Sub-Agent Protocol

从当前模板版本开始，推荐把每个新章节都当成一次显式的多席位协作，而不是单次串行草稿。

### Mainline Dispatches

1. `novel-plot-architect`
   - 产出 `02-plan.json`
2. `novel-scene-dramatizer`
   - 产出 `03-draft.md`
3. `novel-continuity-auditor`
   - 产出 `04-continuity-audit.json`
4. `novel-dialogue-editor`
   - 按需产出 `05-dialogue-audit.json`
5. `novel-scene-dramatizer`
   - 产出 `06-revised.md`
6. `novel-chapter-summarizer`
   - 产出 `07-summary.json`

### Quality Council Dispatches

当章节进入过线检查时，默认再跑一轮 `quality_council`：

- `novel-plot-architect` -> `11-story-engine-seat.json`
- `novel-scene-dramatizer` -> `12-scene-heat-seat.json`
- `novel-dialogue-editor` -> `13-voice-seat.json`
- `novel-continuity-auditor` -> `14-canon-surface-gate.json`
- 主调度汇总 -> `15-quality-council-report.json`

`10-seat-context-snapshots.json` 用于保存四个席位的独立上下文快照，避免同轮席位互相污染。

## Visibility Note

- 你在聊天界面里只能看到“当前这次线程里实时触发”的 sub-agent 消息。
- 历史章节的 sub-agent 协作不会自动回放成聊天消息。
- 这套机制的长期真源是：
  - `09-execution-log.json`
  - `10-seat-context-snapshots.json`
  - `11-15` 的席位与 council 报告

也就是说，UI 不一定会 replay，但 workflow 工件会把协作过程固定下来。

## Standard Use

1. 初始化目录：
   - `python3 stories/messi-series/workflows/init_chapter_workflow.py CH021 "章节标题"`
2. 填写 `01-context.md`
3. 跑 mainline dispatches
4. 如需修订，更新 `06-revised.md`
5. 跑 `quality_council`
6. 通过后更新 `07-summary.json` 和 `08-writeback.md`
7. 在 `09-execution-log.json` 中补齐所有 dispatch 记录与异常

## Artifact Map

- `00-manifest.json`: 本章工作流契约、是否强制 sub-agent、quality council 配置
- `01-context.md`: 章节最小上下文包
- `02-plan.json`: 结构计划
- `03-draft.md`: 首轮场景稿
- `04-continuity-audit.json`: 连续性/语言表面审计
- `05-dialogue-audit.json`: 对白与角色声音审计
- `06-revised.md`: 定向修订后的稳定稿
- `07-summary.json`: 最小可传递记忆
- `08-writeback.md`: 状态写回建议
- `09-execution-log.json`: 所有 sub-agent dispatch 的持久留痕
- `10-seat-context-snapshots.json`: 四个 council 席位的独立上下文快照
- `11-story-engine-seat.json`: 结构席位评分
- `12-scene-heat-seat.json`: 场面热度席位评分
- `13-voice-seat.json`: 角色在场感席位评分
- `14-canon-surface-gate.json`: gate 席位与最终 veto
- `15-quality-council-report.json`: 主调度汇总报告

## Guardrails

- 不要只留正文，不留 trace。
- 不要把多个席位的判断都塞进一个 audit 文件里。
- 如果当前轮没有真的使用 sub-agent，就在 `09-execution-log.json` 里明确写明例外和原因。
- 如果 UI 中没有看到 sub-agent 消息，不代表协作没有发生；以 execution log 和 council artifacts 为准。
