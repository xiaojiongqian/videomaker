# Messi Series Workflow

## Goal

把小说章节生产从“主代理临时包办”改成“有工件、有门禁、可回溯”的稳定流程。

本项目从 CH005 起默认使用 workflow 目录驱动章节推进。
如果存在 `scripts/novel_workflow.py`，优先通过 runner 操作流程，而不是手工维护状态。

## Directory Layout

- `chapters/`
  - 正式归档章节正文，只放通过门禁的稳定稿
- `summaries/`
  - 正式归档章节摘要
- `workflows/CHxxx/`
  - 单章工作流工件

## Required Workflow Files

每个章节默认使用以下文件：

- `00-manifest.json`
  - 章节 id、标题、当前流程状态、是否要求连续性审计 / 对白审计
- `01-context.md`
  - 当前入口状态、相关开放回路、必须保留事实、来源边界
- `02-plan.json`
  - `novel-plot-architect` 产物
- `03-draft.md`
  - `novel-scene-dramatizer` 初稿
- `04-continuity-audit.json`
  - `novel-continuity-auditor` 审计报告
- `05-dialogue-audit.json`
  - `novel-dialogue-editor` 报告；仅在 manifest 要求时必需
- `06-revised.md`
  - 主调度整合后的稳定稿
- `07-summary.json`
  - `novel-chapter-summarizer` 结构化摘要结果
- `08-writeback.md`
  - 本次 canon admission、状态写回和来源同步说明

## Workflow Status

`00-manifest.json` 里的 `status` 使用以下阶段：

- `initialized`
  - 已建立章目录和上下文
- `planned`
  - 章纲已完成
- `drafted`
  - 初稿已完成
- `audited`
  - 审计已完成
- `revised`
  - 稳定稿已完成
- `summarized`
  - 结构化摘要和写回草案已完成
- `archived`
  - 正式章节、summary 和状态文件已归档

## Default Chapter Pipeline

1. 主调度读取 `INDEX.md`、`CURRENT_STATE.md`、`OPEN_LOOPS.md`、相关 summaries
2. 写 `01-context.md`
3. `novel-plot-architect` 产出 `02-plan.json`
4. `novel-scene-dramatizer` 产出 `03-draft.md`
5. `novel-continuity-auditor` 产出 `04-continuity-audit.json`
6. 如 manifest 要求，再由 `novel-dialogue-editor` 产出 `05-dialogue-audit.json`
7. 主调度汇总修订，产出 `06-revised.md`
8. `novel-chapter-summarizer` 产出 `07-summary.json`
9. 主调度写 `08-writeback.md`
10. 通过 lint 后，才归档到 `chapters/`、`summaries/` 和状态文件

## Default Commands

初始化新章节：

```bash
python3 scripts/novel_workflow.py init stories/messi-series CH005 "替补席尽头的灯"
```

检查当前章节：

```bash
python3 scripts/novel_workflow.py check stories/messi-series CH005
```

检查全部 workflow 章节：

```bash
python3 scripts/novel_workflow.py check stories/messi-series --all
```

推进 manifest 状态并立即校验：

```bash
python3 scripts/novel_workflow.py set-status stories/messi-series CH005 planned
```

在 `06-revised.md` 和 `07-summary.json` 完成后自动归档：

```bash
python3 scripts/novel_workflow.py archive stories/messi-series CH005
```

## Gate Command

归档前必须运行：

```bash
python3 scripts/novel_workflow.py check stories/messi-series CH005
```

如果不传章节 id，脚本会尝试从 `CURRENT_STATE.md` 推断。
`archive` 命令内部会自动再次运行 lint。

## Fail-Closed Rules

出现以下任一情况，不得归档正式章节：

- workflow manifest 缺失
- `02-plan.json` 缺失
- 必需审计文件缺失
- `07-summary.json` 缺失
- `08-writeback.md` 缺失
- 正文含元叙事 / 作者工作台泄漏
- manifest 的章节 id 与目录或正式章节不一致

## Notes

- `chapters/` 只收稳定稿，不收初稿
- 来源说明继续写入 `SOURCES.md` 或 `08-writeback.md`，不写进正文
- CH001-CH004 属于 workflow 建立前的 legacy 章节，可继续保留，但不作为新章节流程范例
