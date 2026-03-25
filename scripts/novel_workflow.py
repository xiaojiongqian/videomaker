#!/usr/bin/env python3
"""Automated runner for the novel workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from novel_workflow_check import (
    MEDIUM_BLOCKING_DIMENSIONS,
    SEVERITY_RANK,
    STATUS_ORDER,
    check_chapter,
    infer_chapter_id,
    iter_workflow_chapters,
    print_result,
)

DEFAULT_CONTRACT_VERSION = "2026-03"
DEFAULT_MANIFEST_SCHEMA_VERSION = "1.1"
DEFAULT_EXECUTION_LOG_FILE = "09-execution-log.json"
DEFAULT_CODEX_BIN = shutil.which("codex") or "codex"
MAX_AUTO_REDRAFT_PASSES = 2
DEFAULT_REQUIRED_DISPATCHES = [
    {"agent_role": "novel-plot-architect", "output_refs": ["02-plan.json"], "when": "always"},
    {"agent_role": "novel-scene-dramatizer", "output_refs": ["03-draft.md"], "when": "always"},
    {"agent_role": "novel-continuity-auditor", "output_refs": ["04-continuity-audit.json"], "when": "required_steps.continuity_audit"},
    {"agent_role": "novel-dialogue-editor", "output_refs": ["05-dialogue-audit.json"], "when": "required_steps.dialogue_audit"},
    {"agent_role": "novel-chapter-summarizer", "output_refs": ["07-summary.json"], "when": "always"},
]
TASK_SPECS = {
    "plan": {
        "filename": "02-plan.json",
        "task_slug": "plan",
        "task_type": "chapter-plan",
        "agent_role": "novel-plot-architect",
    },
    "draft": {
        "filename": "03-draft.md",
        "task_slug": "draft",
        "task_type": "chapter-draft",
        "agent_role": "novel-scene-dramatizer",
    },
    "redraft": {
        "filename": "06-revised.md",
        "task_slug": "redraft",
        "task_type": "prose-revision",
        "agent_role": "novel-scene-dramatizer",
    },
    "continuity": {
        "filename": "04-continuity-audit.json",
        "task_slug": "continuity",
        "task_type": "continuity-audit",
        "agent_role": "novel-continuity-auditor",
    },
    "dialogue": {
        "filename": "05-dialogue-audit.json",
        "task_slug": "dialogue",
        "task_type": "dialogue-audit",
        "agent_role": "novel-dialogue-editor",
    },
    "summary": {
        "filename": "07-summary.json",
        "task_slug": "summary",
        "task_type": "chapter-summary",
        "agent_role": "novel-chapter-summarizer",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the novel chapter workflow with built-in gates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize workflow files for a new chapter")
    init_parser.add_argument("project_root")
    init_parser.add_argument("chapter_id")
    init_parser.add_argument("chapter_title")
    init_parser.add_argument("--dialogue-audit", action="store_true")
    init_parser.add_argument(
        "--execution-policy",
        choices=["subagent_required", "flexible"],
        default="subagent_required",
        help="subagent_required enforces real sub-agent provenance in lint; flexible keeps contract checks without strict provenance.",
    )

    run_parser = subparsers.add_parser(
        "run-chapter",
        help="Run the standard multi-skill chapter workflow through isolated Codex sub-agents",
    )
    run_parser.add_argument("project_root")
    run_parser.add_argument("chapter_id")
    run_parser.add_argument(
        "--execution-policy",
        choices=["subagent_required", "flexible"],
        default="subagent_required",
        help="Normalize the manifest to this execution policy before dispatch.",
    )
    run_parser.add_argument(
        "--codex-bin",
        default=DEFAULT_CODEX_BIN,
        help="Path to the Codex CLI used for isolated sub-agent dispatch",
    )
    run_parser.add_argument("--model", default="", help="Optional model override passed to `codex exec`")
    run_parser.add_argument("--archive", action="store_true", help="Archive after the workflow reaches summarized")

    check_parser = subparsers.add_parser("check", help="Run workflow lint")
    check_parser.add_argument("project_root")
    check_parser.add_argument("chapter_id", nargs="?")
    check_parser.add_argument("--all", action="store_true")

    set_status_parser = subparsers.add_parser("set-status", help="Update manifest status and validate it immediately")
    set_status_parser.add_argument("project_root")
    set_status_parser.add_argument("chapter_id")
    set_status_parser.add_argument("status", choices=STATUS_ORDER)

    archive_parser = subparsers.add_parser("archive", help="Archive a chapter after passing lint gates")
    archive_parser.add_argument("project_root")
    archive_parser.add_argument("chapter_id")

    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, text: str) -> None:
    normalized = text.strip()
    if not normalized:
        raise ValueError(f"Refusing to write empty markdown artifact: {path}")
    path.write_text(normalized + "\n", encoding="utf-8")


def get_template_dir(project_root: Path) -> Path:
    return project_root / "workflows" / "_template"


def get_workflow_dir(project_root: Path, chapter_id: str) -> Path:
    return project_root / "workflows" / chapter_id


def create_file_from_template(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)


def infer_current_scene(project_root: Path) -> str:
    current_state = project_root / "CURRENT_STATE.md"
    if not current_state.exists():
        return ""

    text = current_state.read_text(encoding="utf-8")
    marker = "- Current scene:"
    for line in text.splitlines():
        if line.startswith(marker):
            return line[len(marker):].strip()
    return ""


def infer_current_chapter(project_root: Path) -> str:
    current_state = project_root / "CURRENT_STATE.md"
    if not current_state.exists():
        return ""

    for line in current_state.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Current chapter:"):
            raw = line.split(":", 1)[1].strip()
            if raw.startswith("CH"):
                return raw.split("《", 1)[0].strip()
    return ""


def infer_chapter_title(project_root: Path, chapter_id: str) -> str:
    manifest_path = get_workflow_dir(project_root, chapter_id) / "00-manifest.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        title = manifest.get("chapter_title")
        if isinstance(title, str) and title.strip():
            return title.strip()

    chapter_path = project_root / "chapters" / f"{chapter_id}.md"
    if chapter_path.exists():
        for line in chapter_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith("#"):
                continue
            heading = stripped.lstrip("#").strip()
            if heading.startswith(f"{chapter_id} "):
                return heading[len(chapter_id):].strip()
            if heading:
                return heading

    return chapter_id


def build_execution_policy(mode: str) -> dict[str, Any]:
    require_subagents = mode == "subagent_required"
    return {
        "orchestration_mode": "multi-skill-subagents" if require_subagents else "multi-skill-flexible",
        "require_subagents": require_subagents,
        "trace_file": DEFAULT_EXECUTION_LOG_FILE,
        "required_dispatches": DEFAULT_REQUIRED_DISPATCHES,
        "fallback_policy": {
            "allow_modes": [] if require_subagents else ["approved-fallback"],
            "require_exception_entry": True,
        },
    }


def load_template_json(project_root: Path, filename: str, chapter_id: str, chapter_title: str | None = None) -> dict[str, Any]:
    template_path = get_template_dir(project_root) / filename
    text = template_path.read_text(encoding="utf-8").replace("CHXXX", chapter_id)
    if chapter_title is not None:
        text = text.replace("Chapter Title", chapter_title)
    return json.loads(text)


def ensure_workflow_scaffold(project_root: Path, chapter_id: str, chapter_title: str) -> None:
    template_dir = get_template_dir(project_root)
    workflow_dir = get_workflow_dir(project_root, chapter_id)
    workflow_dir.mkdir(parents=True, exist_ok=True)

    for template in sorted(template_dir.iterdir()):
        if not template.is_file():
            continue
        dst = workflow_dir / template.name
        if dst.exists():
            continue
        text = template.read_text(encoding="utf-8").replace("CHXXX", chapter_id).replace("Chapter Title", chapter_title)
        dst.write_text(text, encoding="utf-8")


def normalize_manifest_for_run(project_root: Path, chapter_id: str, execution_policy_mode: str) -> dict[str, Any]:
    workflow_dir = get_workflow_dir(project_root, chapter_id)
    manifest_path = workflow_dir / "00-manifest.json"
    chapter_title = infer_chapter_title(project_root, chapter_id)
    if manifest_path.exists():
        manifest = load_json(manifest_path)
    else:
        manifest = load_template_json(project_root, "00-manifest.json", chapter_id, chapter_title)

    required_steps = manifest.get("required_steps")
    if not isinstance(required_steps, dict):
        required_steps = {}
    required_steps.setdefault("continuity_audit", True)
    required_steps.setdefault("dialogue_audit", False)

    manifest["schema_version"] = DEFAULT_MANIFEST_SCHEMA_VERSION
    manifest["contract_version"] = str(manifest.get("contract_version", DEFAULT_CONTRACT_VERSION))
    manifest["chapter_id"] = chapter_id
    manifest["chapter_title"] = str(manifest.get("chapter_title") or chapter_title)
    manifest["required_steps"] = required_steps
    manifest["execution_policy"] = build_execution_policy(execution_policy_mode)
    manifest["status"] = "initialized"
    manifest.setdefault("notes", "Update status as the workflow advances. Do not archive the chapter until lint passes.")
    write_json(manifest_path, manifest)
    return manifest


def reset_execution_trace(project_root: Path, chapter_id: str) -> Path:
    workflow_dir = get_workflow_dir(project_root, chapter_id)
    trace_path = workflow_dir / DEFAULT_EXECUTION_LOG_FILE
    trace = load_template_json(project_root, DEFAULT_EXECUTION_LOG_FILE, chapter_id)
    trace["status"] = "ready"
    trace["dispatches"] = []
    trace["exceptions"] = []
    write_json(trace_path, trace)
    return trace_path


def set_trace_status(trace_path: Path, status: str) -> None:
    trace = load_json(trace_path)
    trace["status"] = status
    write_json(trace_path, trace)


def append_dispatch(trace_path: Path, dispatch: dict[str, Any]) -> None:
    trace = load_json(trace_path)
    dispatches = trace.get("dispatches")
    if not isinstance(dispatches, list):
        dispatches = []
    dispatches.append(dispatch)
    trace["dispatches"] = dispatches
    write_json(trace_path, trace)


def make_task_id(trace_path: Path, chapter_id: str, key: str) -> str:
    spec = TASK_SPECS[key]
    slug = str(spec["task_slug"])
    trace = load_json(trace_path)
    dispatches = trace.get("dispatches")
    if not isinstance(dispatches, list):
        dispatches = []
    count = 0
    prefix = f"{chapter_id}-{slug}-"
    for dispatch in dispatches:
        if not isinstance(dispatch, dict):
            continue
        task_id = str(dispatch.get("task_id", ""))
        if task_id.startswith(prefix):
            count += 1
    return f"{chapter_id}-{slug}-{count + 1:03d}"


def set_manifest_status(project_root: Path, chapter_id: str, status: str) -> None:
    manifest_path = get_workflow_dir(project_root, chapter_id) / "00-manifest.json"
    manifest = load_json(manifest_path)
    manifest["status"] = status
    write_json(manifest_path, manifest)


def compute_context_hash(workflow_dir: Path, context_refs: list[str]) -> str:
    digest = hashlib.sha256()
    for ref in context_refs:
        path = workflow_dir / ref
        digest.update(ref.encode("utf-8"))
        digest.update(b"\0")
        if path.exists():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def listify(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def ensure_list(value: object) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def sanitize_agent_message(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()
    return cleaned


def parse_json_payload(text: str) -> dict[str, Any]:
    cleaned = sanitize_agent_message(text)
    candidates = [cleaned]

    if "```json" in text:
        start = text.find("```json")
        end = text.find("```", start + 7)
        if start != -1 and end != -1:
            candidates.append(text[start + 7 : end].strip())

    first_object = cleaned.find("{")
    last_object = cleaned.rfind("}")
    if first_object != -1 and last_object != -1 and last_object > first_object:
        candidates.append(cleaned[first_object : last_object + 1])

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data

    raise ValueError("Sub-agent response was not valid JSON")


def _render_bullet_list(items: list[str], fallback: str = "无", *, indent: str = "") -> str:
    if not items:
        return f"{indent}- {fallback}"
    return "\n".join(f"{indent}- {item}" for item in items)


def render_summary_markdown(chapter_id: str, payload: dict[str, Any]) -> str:
    one_line = str(payload.get("one_line_summary", "")).strip()
    actor_refs = listify(payload.get("actor_refs"))
    major_beats = listify(payload.get("major_beats"))
    state_changes = listify(payload.get("state_changes"))
    carry_forward = listify(payload.get("carry_forward"))
    open_loops = payload.get("open_loops", {})
    opened = listify(open_loops.get("opened")) if isinstance(open_loops, dict) else []
    advanced = listify(open_loops.get("advanced")) if isinstance(open_loops, dict) else []
    resolved = listify(open_loops.get("resolved")) if isinstance(open_loops, dict) else []

    return "\n".join(
        [
            f"# Chapter Summary: {chapter_id}",
            "",
            "## One-Line Summary",
            f"- {one_line or '待补充'}",
            "",
            "## Actor Refs",
            _render_bullet_list(actor_refs),
            "",
            "## Major Beats",
            _render_bullet_list(major_beats),
            "",
            "## State Changes",
            _render_bullet_list(state_changes),
            "",
            "## Open Loops",
            "- Opened:",
            _render_bullet_list(opened, indent="  "),
            "- Advanced:",
            _render_bullet_list(advanced, indent="  "),
            "- Resolved:",
            _render_bullet_list(resolved, indent="  "),
            "",
            "## Carry Forward",
            _render_bullet_list(carry_forward),
            "",
        ]
    )


def extract_summary_payload(summary_json: dict[str, Any]) -> dict[str, Any]:
    artifacts = summary_json.get("artifacts", [])
    for artifact in artifacts:
        if artifact.get("type") == "chapter_summary":
            content = artifact.get("content")
            if isinstance(content, dict):
                return content
    return {}


def render_writeback_markdown(project_root: Path, chapter_id: str, summary_payload: dict[str, Any]) -> str:
    major_beats = listify(summary_payload.get("major_beats"))
    advanced = []
    opened = []
    resolved = []
    open_loops = summary_payload.get("open_loops", {})
    if isinstance(open_loops, dict):
        opened = listify(open_loops.get("opened"))
        advanced = listify(open_loops.get("advanced"))
        resolved = listify(open_loops.get("resolved"))

    current_frontier = infer_current_chapter(project_root)
    frontier_note = (
        "- `CURRENT_STATE.md`, `INDEX.md`, `ARC_STATUS.md`, `RECENT_EVENTS.md`, `OPEN_LOOPS.md`"
        if current_frontier == chapter_id
        else "- 本次重跑不回滚全局写作位置；frontier 状态文件保持当前章节进度不变"
    )

    canon_lines = major_beats or ["本章 admitted facts 见 `07-summary.json` 的 `major_beats`。"]
    return "\n".join(
        [
            "# Writeback",
            "",
            "## Canon Admission",
            "- Facts entering canon:",
            *[f"- {item}" for item in canon_lines],
            "- Candidate ideas kept outside canon:",
            "- 叙事修辞、比喻和章节命名意象不自动写回状态文件。",
            "",
            "## State Files To Update",
            f"- `chapters/{chapter_id}.md`",
            f"- `summaries/{chapter_id}.summary.md`",
            frontier_note,
            "",
            "## Open Loops",
            "- Opened:",
            _render_bullet_list(opened),
            "- Advanced:",
            _render_bullet_list(advanced),
            "- Resolved:",
            _render_bullet_list(resolved),
            "",
            "## Source Sync",
            "- `SOURCES.md` updates:",
            "- 若 `01-context.md` 使用的事实已被 `SOURCES.md` 覆盖，本次重跑无需新增来源条目。",
            "",
            "## Archive Decision",
            "- Ready to archive: yes",
            "- Notes:",
            "- 本次归档刷新 strict workflow 工件与真实 sub-agent provenance。",
            "",
        ]
    )


def severity_from_entry(entry: object) -> int:
    if not isinstance(entry, dict):
        return 0
    return SEVERITY_RANK.get(str(entry.get("severity", "none")).lower(), 0)


def entry_is_blocking(entry: object) -> bool:
    if not isinstance(entry, dict):
        return False
    severity = severity_from_entry(entry)
    if severity >= SEVERITY_RANK["high"]:
        return True
    dimension = str(entry.get("analysis_dimension", "")).strip()
    return severity >= SEVERITY_RANK["medium"] and dimension in MEDIUM_BLOCKING_DIMENSIONS


def audit_is_blocking(audit_data: dict[str, Any]) -> bool:
    status = str(audit_data.get("status", "")).strip()
    if status in {"blocked", "invalid", "needs_review"}:
        return True

    if any(entry_is_blocking(item) for item in listify_diagnostics(audit_data)):
        return True

    artifacts = audit_data.get("artifacts", [])
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            findings = artifact.get("findings")
            if isinstance(findings, list) and any(entry_is_blocking(item) for item in findings):
                return True
    return False


def listify_diagnostics(data: dict[str, Any]) -> list[object]:
    diagnostics = data.get("diagnostics")
    if isinstance(diagnostics, list):
        return diagnostics
    return []


def extract_audit_findings(audit_data: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = audit_data.get("artifacts")
    if not isinstance(artifacts, list):
        return []
    findings: list[dict[str, Any]] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        entries = artifact.get("findings")
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict):
                findings.append(entry)
    return findings


def summarize_findings_for_prompt(audit_data: dict[str, Any], *, limit: int = 6) -> str:
    findings = sorted(extract_audit_findings(audit_data), key=severity_from_entry, reverse=True)
    if not findings:
        return "- 无 blocking findings"
    lines: list[str] = []
    for entry in findings[:limit]:
        dimension = str(entry.get("analysis_dimension", "")).strip() or "unknown"
        severity = str(entry.get("severity", "none")).strip() or "none"
        note = str(entry.get("note", "")).strip()
        fix = str(entry.get("fix", "")).strip()
        lines.append(f"- [{severity}] {dimension}: {note}")
        if fix:
            lines.append(f"  fix: {fix}")
    return "\n".join(lines)


def ensure_successful_status(payload: dict[str, Any], task_label: str) -> None:
    status = str(payload.get("status", "")).strip()
    if status in {"blocked", "invalid", "needs_review"}:
        raise ValueError(f"{task_label} returned non-runnable status `{status}`")


def ensure_codex_bin(codex_bin: str) -> str:
    resolved = shutil.which(codex_bin) if "/" not in codex_bin else codex_bin
    if not resolved:
        raise FileNotFoundError(f"Codex CLI not found: {codex_bin}")
    return resolved


def run_codex_exec(prompt: str, *, codex_bin: str, workdir: Path, model: str) -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix="novel-workflow-") as tmpdir:
        output_path = Path(tmpdir) / "last_message.txt"
        command = [
            codex_bin,
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--json",
            "-C",
            str(workdir),
            "--output-last-message",
            str(output_path),
            "--dangerously-bypass-approvals-and-sandbox",
        ]
        if model.strip():
            command.extend(["--model", model.strip()])
        command.append("-")

        completed = subprocess.run(
            command,
            input=prompt,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "codex exec failed with "
                f"exit code {completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

        agent_session_id = ""
        for line in completed.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "thread.started":
                agent_session_id = str(event.get("thread_id", "")).strip()
                if agent_session_id:
                    break

        if not output_path.exists():
            raise RuntimeError("codex exec did not produce an output-last-message artifact")
        return agent_session_id, output_path.read_text(encoding="utf-8")


def _append_failed_dispatch(
    trace_path: Path,
    spec: dict[str, Any],
    task_id: str,
    context_refs: list[str],
    started_at: str,
    model: str,
    exc: Exception,
) -> None:
    append_dispatch(
        trace_path,
        {
            "task_id": task_id,
            "agent_role": spec["agent_role"],
            "mode": "subagent",
            "status": "failed",
            "agent_session_id": "",
            "agent_run_id": "",
            "input_refs": context_refs,
            "output_refs": [spec["filename"]],
            "started_at": started_at,
            "completed_at": utc_now_iso(),
            "model": model.strip(),
            "notes": str(exc),
        },
    )


def build_execution_block(
    *,
    context_refs: list[str],
    workflow_dir: Path,
    agent_session_id: str,
    external_invocation_id: str,
) -> dict[str, Any]:
    return {
        "mode": "subagent",
        "trace_ref": DEFAULT_EXECUTION_LOG_FILE,
        "provenance": {
            "agent_session_id": agent_session_id,
            "agent_run_id": "",
            "external_invocation_id": external_invocation_id,
        },
        "input_snapshot": {
            "context_refs": context_refs,
            "context_hash": compute_context_hash(workflow_dir, context_refs),
        },
    }


def dispatch_json_task(
    *,
    project_root: Path,
    chapter_id: str,
    chapter_title: str,
    workflow_dir: Path,
    trace_path: Path,
    key: str,
    context_refs: list[str],
    prompt: str,
    codex_bin: str,
    model: str,
) -> dict[str, Any]:
    spec = TASK_SPECS[key]
    task_id = make_task_id(trace_path, chapter_id, key)
    started_at = utc_now_iso()
    external_invocation_id = f"{task_id}:{started_at}"
    try:
        agent_session_id, message = run_codex_exec(prompt, codex_bin=codex_bin, workdir=project_root, model=model)
        payload = parse_json_payload(message)
        ensure_successful_status(payload, task_id)
        completed_at = utc_now_iso()
    except Exception as exc:
        _append_failed_dispatch(trace_path, spec, task_id, context_refs, started_at, model, exc)
        raise(project_root, spec["filename"], chapter_id, chapter_title)
    template["task_id"] = task_id
    template["task_type"] = spec["task_type"]
    template["agent_role"] = spec["agent_role"]
    template["status"] = str(payload.get("status", "completed"))
    template["execution"] = build_execution_block(
        context_refs=context_refs,
        workflow_dir=workflow_dir,
        agent_session_id=agent_session_id,
        external_invocation_id=external_invocation_id,
    )
    template["artifacts"] = ensure_list(payload.get("artifacts", template.get("artifacts", [])))
    template["diagnostics"] = ensure_list(payload.get("diagnostics", []))
    template["recommendations"] = listify(payload.get("recommendations"))
    template["proposed_writebacks"] = listify(payload.get("proposed_writebacks"))
    if "change_set" in payload or "change_set" in template:
        change_set = payload.get("change_set", template.get("change_set", []))
        if isinstance(change_set, (list, dict)):
            template["change_set"] = change_set
        else:
            template["change_set"] = template.get("change_set", [])

    write_json(workflow_dir / spec["filename"], template)
    append_dispatch(
        trace_path,
        {
            "task_id": task_id,
            "agent_role": spec["agent_role"],
            "mode": "subagent",
            "status": "completed",
            "agent_session_id": agent_session_id,
            "agent_run_id": "",
            "input_refs": context_refs,
            "output_refs": [spec["filename"]],
            "started_at": started_at,
            "completed_at": completed_at,
            "model": model.strip(),
            "notes": "",
        },
    )
    return template


def dispatch_markdown_task(
    *,
    project_root: Path,
    chapter_id: str,
    workflow_dir: Path,
    trace_path: Path,
    context_refs: list[str],
    prompt: str,
    codex_bin: str,
    model: str,
    key: str = "draft",
) -> str:
    spec = TASK_SPECS[key]
    task_id = make_task_id(trace_path, chapter_id, key)
    started_at = utc_now_iso()
    try:
        agent_session_id, message = run_codex_exec(prompt, codex_bin=codex_bin, workdir=project_root, model=model)
        completed_at = utc_now_iso()
    except Exception as exc:
        _append_failed_dispatch(trace_path, spec, task_id, context_refs, started_at, model, exc)
        raise

    markdown = sanitize_agent_message(message)
    write_markdown(workflow_dir / spec["filename"], markdown)
    append_dispatch(
        trace_path,
        {
            "task_id": task_id,
            "agent_role": spec["agent_role"],
            "mode": "subagent",
            "status": "completed",
            "agent_session_id": agent_session_id,
            "agent_run_id": "",
            "input_refs": context_refs,
            "output_refs": [spec["filename"]],
            "started_at": started_at,
            "completed_at": completed_at,
            "model": model.strip(),
            "notes": "",
        },
    )
    return markdown


def build_plan_prompt(chapter_id: str, chapter_title: str, context_text: str) -> str:
    return f"""
使用 `$novel-plot-architect` skill。你是 `novel-orchestrator-main` 调度的独立 sub-agent。

任务：为纪实成长小说章节 `{chapter_id}《{chapter_title}》` 生成结构化章节计划。

硬约束：
- 只使用下方上下文中已经给出的公开、可核验事实。
- 不发明对白、隐私细节、未经证实心理活动或未来事实。
- 中文输出。
- 计划必须能直接供 `novel-scene-dramatizer` 扩写。
- 章节计划必须由具体事件、决定、冲突或互动推动，不要写成履历综述、人物评述或主题说明。
- 先在内部确认本章的 `disturbance / pursuit / escalation / irreversible turn / residue`，再拆成 plan units；不要直接把时间线摊平。
- 如果 public/source/canon 已给出关键人物名字，优先直接使用名字；如果没有，不要虚构，用稳定角色标签或群体标签。
- 每个 plan unit 都要尽量写清：谁在场、想得到什么、什么阻力拦住了他、哪个动作或事件改变了局面、结果留下了什么余波。
- 计划单元应能让下游直接从人物和动作开段；不要设计只能靠抽象过桥句、概念解释或赛季评论来承接的 unit。
- 至少一个 plan unit 必须是本章最值得被复述的硬节点，不能所有 units 都是桥接概述。
- 关键人物尽量带出最小角色引擎：此刻想保住什么、失败会失去什么、压力落下时会怎样行动或回避。
- 可以用简短桥接概述处理时间跳跃，但桥接不能取代本章主干场面。
- 不要运行 shell 命令、不要读取额外文件、不要调用任何工具；只使用下方内嵌上下文直接完成。

只返回一个 JSON 对象，不要代码块，不要解释。格式必须是：
{{
  "status": "completed",
  "artifacts": [
    {{
      "type": "chapter_plan",
      "title": "{chapter_id} plan",
      "content": [
        {{"unit": "...", "goal": "...", "obstacle": "...", "beat": "...", "turn": "...", "aftermath": "..."}}
      ]
    }}
  ],
  "diagnostics": [
    {{"analysis_dimension": "structure|story-quality", "severity": "none|low|medium|high", "confidence": "low|medium|high", "note": "..."}}
  ],
  "recommendations": ["..."],
  "proposed_writebacks": ["..."],
  "change_set": []
}}

上下文：
```md
{context_text}
```
""".strip()


def build_draft_prompt(chapter_id: str, chapter_title: str, context_text: str, plan_json: dict[str, Any]) -> str:
    plan_block = json.dumps(plan_json.get("artifacts", []), ensure_ascii=False, indent=2)
    return f"""
使用 `$novel-scene-dramatizer` skill。你是 `novel-orchestrator-main` 调度的独立 sub-agent。

任务：把已批准的计划扩写成 `{chapter_id}《{chapter_title}》` 的完整章节初稿。

硬约束：
- 只使用上下文与计划中已给出的公开、可核验事实。
- 写成真正面向读者的纪实小说正文，不写工作台解释。
- 禁止出现“本章”“下一章”“根据资料”“如果说上一章”等元叙事提示。
- 不虚构可被误认为真实发生过的对白、私密细节、采访语句或确定性心理描写。
- 段落必须主要通过可观察的动作、阻力、反应和后果推进，不能长期退化成“这标志着”“这意味着”“这说明”一类意义总结。
- 开头尽量靠近本章的扰动点，不要先用多段热身式回顾把真正的事件往后拖。
- 对关键 beat，尽量按“进入压力 -> 即时目标 -> 阻力 -> 主动动作 -> 偏转 -> 余波”展开，不要只把结果讲出来。
- 让主要段落至少改变 `position / risk / knowledge / relation / public consequence` 里的某一项；如果什么都没变，这段通常还在解释而不是叙事。
- 默认把正文主干压在 2 到 4 个硬节点上；桥接段只负责跨时间，不负责替代场面。
- 不要连续写两段以上的赛季综述、履历压缩或统计归纳；如果必须写统计，把它嵌进事件后果里，而不是独立成段接管章节。
- 如果 public/source/canon 已给出关键人物名字，优先直接使用名字；不要把无名角色擅自升级成具名人物，也不要把群体角色硬写成有完整个性的单独人物。
- 不要把一次亮相、试训、友谊赛、临时机会或阶段性信号，擅自写成“已经正式确立地位”，除非上下文明确给出这种变化。
- 可以有桥接概述，但桥接段只能承担转场，不能替代场面本身。
- 安静、克制、留白可以用，但必须携带压力，而不是空转抒情。
- 语言先求顺读，再求漂亮。段首优先落到人、动作、比分、空间和结果，不要先挂抽象判断。
- 抽象判断后必须尽快回到可见事实；不要连续依赖“这意味着”“这说明”“真正重要的是”一类句子推动段落。
- 少用连续的模板句式，例如“不是……而是……”“不再只是……”“真正……是……”，不要让 prose 像排版整齐的判断稿。
- 允许短段，但短段必须承担推进、压力或偏转，不能只做标题式提要。
- 比喻可以有，但必须贴着现场，不能替代事件本身。
- 只返回 Markdown 正文，不要代码块，不要解释。
- 正文第一行必须是 `# {chapter_id} {chapter_title}`。
- 不要运行 shell 命令、不要读取额外文件、不要调用任何工具；只使用下方内嵌上下文和计划直接完成。

上下文：
```md
{context_text}
```

已批准计划：
```json
{plan_block}
```
""".strip()


def build_redraft_prompt(
    chapter_id: str,
    chapter_title: str,
    context_text: str,
    plan_json: dict[str, Any],
    current_text: str,
    audit_data: dict[str, Any],
    *,
    pass_index: int,
) -> str:
    plan_block = json.dumps(plan_json.get("artifacts", []), ensure_ascii=False, indent=2)
    findings_block = summarize_findings_for_prompt(audit_data)
    return f"""
使用 `$novel-scene-dramatizer` skill。你是 `novel-orchestrator-main` 调度的独立 sub-agent。

任务：根据 continuity/story-quality 审计结果，重写 `{chapter_id}《{chapter_title}》`，产出可过门禁的更强版本。

这是第 {pass_index} 次定向 redraft。目标不是小修辞，而是把差稿修成能成立的章节。

硬约束：
- 只使用上下文、已批准计划、当前草稿和审计 findings 中允许的事实边界。
- 不新增未经来源支持的事实、对白、采访语句、私密心理、机构态度或更衣室细节。
- 必须正面修复下方 findings，不要只换同义句。
- 如果审计指出“总结腔/履历式压缩/赛季综述”，就必须把至少 2 处相关段落改写成事件节点或在场场面。
- 如果审计指出“人物发虚”，就必须补出人物当下的即时目标、外部 stakes 或可观察压力反应，但不能越过事实边界乱编心理。
- 如果审计指出“章末像作者总结”，就必须改成余波式收束，让未完成处境留在事件后果里。
- 如果审计指出 `readability` 或 `prose-naturalness`，就必须重写被点名段落的开头和句群：删掉空心过桥句、模板化对照句和悬空抽象判断，换成更清楚的事件化 prose。
- 默认把正文主干压在 2 到 4 个硬节点上；桥接只能短，不能连续吞掉章节。
- 语言先求顺读，再求漂亮；不要只换同义词，不要把原有坏句式原样保留。
- 只返回 Markdown 正文，不要解释，不要复述审计，不要代码块。
- 正文第一行必须是 `# {chapter_id} {chapter_title}`。

上下文：
```md
{context_text}
```

已批准计划：
```json
{plan_block}
```

当前草稿：
```md
{current_text}
```

必须修复的 findings：
```text
{findings_block}
```
""".strip()


def build_continuity_prompt(chapter_id: str, context_text: str, draft_text: str) -> str:
    return f"""
使用 `$novel-continuity-auditor` skill。你是 `novel-orchestrator-main` 调度的独立 sub-agent。

任务：审计 `{chapter_id}` 草稿是否与上下文约束、时间线、纪实边界和小说性底线一致。

硬约束：
- 只基于给定上下文与草稿判断，不补充外部事实。
- 重点检查：时间线、事实边界、是否把阶段性机会误写成正式确立、是否有元叙事泄漏、是否出现 unsupported character attribution、unsupported internal-state inference、summary/commentary drift。
- 即使事实没错，只要草稿主要靠总结句推进、关键人物长期没有具名或稳定辨识度、冲突没有落到事件节点，也要报问题。
- 同时检查本章是否具备最小 story engine：是否存在清楚的扰动点、追求线、升级、偏转和余波；如果 chapter contour 发平，也要报问题。
- 检查关键人物是否只是功能位，还是能看见即时目标、外部 stakes 和压力反应；如果人物只剩身份标签，也要报问题。
- 还要检查语言表面是否顺读，是否频繁先给概念判断、空心短段或模板化对照句，再把真正动作往后拖；如果 prose 读起来像模板拼接，也要报问题。
- `diagnostics` 至少覆盖 `timeline`、`fact-boundary`、`character-source`、`narrative-surface`、`character-embodiment`、`commentary-drift`、`tension`、`readability`、`prose-naturalness` 九个维度；即使没问题也要返回 `severity: "none"`。
- 如果没有问题，明确返回空 findings。
- 不要运行 shell 命令、不要读取额外文件、不要调用任何工具；只使用下方内嵌上下文和草稿直接完成。

只返回一个 JSON 对象，不要代码块，不要解释。格式必须是：
{{
  "status": "completed",
  "artifacts": [
    {{
      "type": "audit_report",
      "findings": [
        {{
          "analysis_dimension": "timeline|fact-boundary|character-source|narrative-surface|character-embodiment|commentary-drift|tension|readability|prose-naturalness|continuity",
          "severity": "low|medium|high",
          "confidence": "low|medium|high",
          "evidence_refs": ["01-context.md", "03-draft.md"],
          "note": "...",
          "fix": "..."
        }}
      ]
    }}
  ],
  "diagnostics": [
    {{"analysis_dimension": "...", "severity": "none|low|medium|high", "confidence": "low|medium|high", "evidence_refs": ["..."], "note": "..."}}
  ],
  "recommendations": ["..."],
  "proposed_writebacks": ["..."],
  "change_set": []
}}

上下文：
```md
{context_text}
```

草稿：
```md
{draft_text}
```
""".strip()


def build_dialogue_prompt(chapter_id: str, draft_text: str) -> str:
    return f"""
使用 `$novel-dialogue-editor` skill。你是 `novel-orchestrator-main` 调度的独立 sub-agent。

任务：判断 `{chapter_id}` 是否需要对白层面的专门修订。

只返回一个 JSON 对象，不要代码块，不要解释。格式必须是：
{{
  "status": "completed|skipped",
  "artifacts": [
    {{
      "type": "dialogue_revision",
      "content": []
    }}
  ],
  "diagnostics": [
    {{"analysis_dimension": "dialogue", "severity": "none|low|medium|high", "confidence": "low|medium|high", "note": "..."}}
  ],
  "recommendations": ["..."],
  "proposed_writebacks": [],
  "change_set": []
}}

如果本章几乎没有对白，返回 `status: "skipped"` 并说明原因。
- 如果问题根源不是台词本身，而是人物过于标签化、说话人没有稳定身份、场面缺少关系摩擦，请在 `recommendations` 里明确建议回退到上游结构或正文重写，而不是假装对白润色就能解决。
- 不要运行 shell 命令、不要读取额外文件、不要调用任何工具；只使用下方草稿直接完成。

草稿：
```md
{draft_text}
```
""".strip()


def build_summary_prompt(chapter_id: str, chapter_title: str, context_text: str, revised_text: str) -> str:
    return f"""
使用 `$novel-chapter-summarizer` skill。你是 `novel-orchestrator-main` 调度的独立 sub-agent。

任务：为 `{chapter_id}《{chapter_title}》` 生成结构化摘要与最小 forward-memory。

硬约束：
- 只使用上下文与稳定稿里已经确认发生的事实。
- 不新增剧情，不把推测写成事实。
- 摘要服务于后续章节续写，而不是复述全文。
- `one_line_summary` 必须写出本章真正发生的门槛事件或局面变化，不要只写主题判断。
- `major_beats`、`state_changes`、`carry_forward` 都必须是 actor-anchored 的事件 / 变化 / 后果陈述，不要写成抽象成长总结。
- 如果本章的真正抓力在章末余波或公开后果，`carry_forward` 必须保留这股压力，不要把章节压成平面的事件年表。
- 如果 public/source/canon 已给出关键人物名字，优先在摘要里保留名字；如果没有，不要虚构，用稳定角色标签或群体标签。
- 如果某个变化只是解释性推断、正文没有明确支撑，不要写进 `state_changes`。
- 不要运行 shell 命令、不要读取额外文件、不要调用任何工具；只使用下方内嵌上下文和稳定稿直接完成。

只返回一个 JSON 对象，不要代码块，不要解释。格式必须是：
{{
  "status": "completed",
  "artifacts": [
    {{
      "type": "chapter_summary",
      "content": {{
        "one_line_summary": "...",
        "actor_refs": ["..."],
        "major_beats": ["..."],
        "state_changes": ["..."],
        "open_loops": {{
          "opened": [],
          "advanced": [],
          "resolved": []
        }},
        "carry_forward": ["..."]
      }}
    }}
  ],
  "diagnostics": [
    {{"analysis_dimension": "summary|unsupported-inference", "confidence": "low|medium|high", "evidence_refs": ["01-context.md", "06-revised.md"], "note": "..."}}
  ],
  "recommendations": ["..."],
  "proposed_writebacks": ["..."],
  "change_set": []
}}

上下文：
```md
{context_text}
```

稳定稿：
```md
{revised_text}
```
""".strip()


def init_workflow(
    project_root: Path, chapter_id: str, chapter_title: str, dialogue_audit: bool, execution_policy_mode: str
) -> int:
    ensure_workflow_scaffold(project_root, chapter_id, chapter_title)

    manifest_path = get_workflow_dir(project_root, chapter_id) / "00-manifest.json"
    manifest = load_json(manifest_path)
    manifest["schema_version"] = str(manifest.get("schema_version", DEFAULT_MANIFEST_SCHEMA_VERSION))
    manifest["contract_version"] = str(manifest.get("contract_version", DEFAULT_CONTRACT_VERSION))
    manifest["chapter_id"] = chapter_id
    manifest["chapter_title"] = chapter_title
    manifest["required_steps"]["dialogue_audit"] = dialogue_audit
    manifest["execution_policy"] = build_execution_policy(execution_policy_mode)
    manifest["status"] = "initialized"
    write_json(manifest_path, manifest)

    context_path = get_workflow_dir(project_root, chapter_id) / "01-context.md"
    if context_path.exists():
        context = context_path.read_text(encoding="utf-8")
        scene = infer_current_scene(project_root)
        if scene and "- Current scene:\n" in context:
            context = context.replace("- Current scene:\n", f"- Current scene: {scene}\n")
        context_path.write_text(context, encoding="utf-8")

    result = check_chapter(project_root, chapter_id)
    print_result(result)
    return 1 if result.issues else 0


def run_check(project_root: Path, chapter_id: str | None, check_all: bool) -> int:
    if check_all:
        chapter_ids = iter_workflow_chapters(project_root)
        if not chapter_ids:
            print("FAIL: no workflow chapter directories found")
            return 1
        failed = False
        for cid in chapter_ids:
            result = check_chapter(project_root, cid)
            print_result(result)
            if result.issues:
                failed = True
        return 1 if failed else 0

    resolved = chapter_id or infer_chapter_id(project_root)
    result = check_chapter(project_root, resolved)
    print_result(result)
    return 1 if result.issues else 0


def set_status(project_root: Path, chapter_id: str, status: str) -> int:
    manifest_path = get_workflow_dir(project_root, chapter_id) / "00-manifest.json"
    manifest = load_json(manifest_path)
    old_status = manifest.get("status")
    manifest["status"] = status
    write_json(manifest_path, manifest)

    result = check_chapter(project_root, chapter_id)
    if result.issues:
        manifest["status"] = old_status
        write_json(manifest_path, manifest)
    print_result(result)
    return 1 if result.issues else 0


def run_chapter(
    project_root: Path,
    chapter_id: str,
    execution_policy_mode: str,
    codex_bin: str,
    model: str,
    archive_output: bool,
) -> int:
    workflow_dir = get_workflow_dir(project_root, chapter_id)
    if not workflow_dir.exists():
        print(f"FAIL: {chapter_id}")
        print(f"- workflow directory not found: {workflow_dir}")
        print("- run `python3 scripts/novel_workflow.py init <project_root> <chapter_id> \"<chapter_title>\"` first")
        return 1

    try:
        codex_bin = ensure_codex_bin(codex_bin)
        chapter_title = infer_chapter_title(project_root, chapter_id)
        ensure_workflow_scaffold(project_root, chapter_id, chapter_title)
        manifest = normalize_manifest_for_run(project_root, chapter_id, execution_policy_mode)
        trace_path = reset_execution_trace(project_root, chapter_id)
        set_trace_status(trace_path, "in_progress")

        context_path = workflow_dir / "01-context.md"
        if not context_path.exists():
            print(f"FAIL: {chapter_id}")
            print(f"- missing context artifact: {context_path}")
            return 1
        context_text = context_path.read_text(encoding="utf-8").strip()
        if not context_text:
            print(f"FAIL: {chapter_id}")
            print(f"- empty context artifact: {context_path}")
            return 1

        dialogue_path = workflow_dir / TASK_SPECS["dialogue"]["filename"]
        if not manifest["required_steps"].get("dialogue_audit", False) and dialogue_path.exists():
            dialogue_path.unlink()

        plan_data = dispatch_json_task(
            project_root=project_root,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            workflow_dir=workflow_dir,
            trace_path=trace_path,
            key="plan",
            context_refs=["01-context.md"],
            prompt=build_plan_prompt(chapter_id, chapter_title, context_text),
            codex_bin=codex_bin,
            model=model,
        )
        set_manifest_status(project_root, chapter_id, "planned")

        draft_text = dispatch_markdown_task(
            project_root=project_root,
            chapter_id=chapter_id,
            workflow_dir=workflow_dir,
            trace_path=trace_path,
            context_refs=["01-context.md", "02-plan.json"],
            prompt=build_draft_prompt(chapter_id, chapter_title, context_text, plan_data),
            codex_bin=codex_bin,
            model=model,
            key="draft",
        )
        set_manifest_status(project_root, chapter_id, "drafted")

        candidate_text = draft_text
        candidate_ref = "03-draft.md"
        continuity_data: dict[str, Any] | None = None
        if manifest["required_steps"].get("continuity_audit", True):
            for pass_index in range(MAX_AUTO_REDRAFT_PASSES + 1):
                continuity_data = dispatch_json_task(
                    project_root=project_root,
                    chapter_id=chapter_id,
                    chapter_title=chapter_title,
                    workflow_dir=workflow_dir,
                    trace_path=trace_path,
                    key="continuity",
                    context_refs=["01-context.md", candidate_ref],
                    prompt=build_continuity_prompt(chapter_id, context_text, candidate_text),
                    codex_bin=codex_bin,
                    model=model,
                )
                if not audit_is_blocking(continuity_data):
                    break
                if pass_index >= MAX_AUTO_REDRAFT_PASSES:
                    raise ValueError(f"{chapter_id} continuity audit returned blocking issues after {pass_index + 1} pass(es)")

                candidate_text = dispatch_markdown_task(
                    project_root=project_root,
                    chapter_id=chapter_id,
                    workflow_dir=workflow_dir,
                    trace_path=trace_path,
                    context_refs=["01-context.md", "02-plan.json", candidate_ref, "04-continuity-audit.json"],
                    prompt=build_redraft_prompt(
                        chapter_id,
                        chapter_title,
                        context_text,
                        plan_data,
                        candidate_text,
                        continuity_data,
                        pass_index=pass_index + 1,
                    ),
                    codex_bin=codex_bin,
                    model=model,
                    key="redraft",
                )
                candidate_ref = "06-revised.md"

        if manifest["required_steps"].get("dialogue_audit", False):
            dialogue_data = dispatch_json_task(
                project_root=project_root,
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                workflow_dir=workflow_dir,
                trace_path=trace_path,
                key="dialogue",
                context_refs=["01-context.md", candidate_ref],
                prompt=build_dialogue_prompt(chapter_id, candidate_text),
                codex_bin=codex_bin,
                model=model,
            )
            if audit_is_blocking(dialogue_data):
                raise ValueError(f"{chapter_id} dialogue audit returned blocking issues")

        set_manifest_status(project_root, chapter_id, "audited")
        write_markdown(workflow_dir / "06-revised.md", candidate_text)
        set_manifest_status(project_root, chapter_id, "revised")

        revised_text = candidate_text.strip()
        summary_data = dispatch_json_task(
            project_root=project_root,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            workflow_dir=workflow_dir,
            trace_path=trace_path,
            key="summary",
            context_refs=["01-context.md", "06-revised.md"],
            prompt=build_summary_prompt(chapter_id, chapter_title, context_text, revised_text),
            codex_bin=codex_bin,
            model=model,
        )
        summary_payload = extract_summary_payload(summary_data)
        write_markdown(workflow_dir / "08-writeback.md", render_writeback_markdown(project_root, chapter_id, summary_payload))
        set_trace_status(trace_path, "completed")
        set_manifest_status(project_root, chapter_id, "summarized")

        result = check_chapter(project_root, chapter_id)
        print_result(result)
        if result.issues:
            return 1

        if archive_output:
            return archive(project_root, chapter_id)
        return 0
    except Exception as exc:
        print(f"FAIL: {chapter_id}")
        print(f"- run-chapter aborted: {exc}")
        return 1


def archive(project_root: Path, chapter_id: str) -> int:
    workflow_dir = get_workflow_dir(project_root, chapter_id)
    manifest_path = workflow_dir / "00-manifest.json"
    manifest = load_json(manifest_path)
    status = manifest.get("status")
    if status not in {"summarized", "archived"}:
        print(f"FAIL: {chapter_id}")
        print(f"- archive requires workflow status `summarized` or `archived`, got `{status}`")
        return 1

    precheck = check_chapter(project_root, chapter_id)
    if precheck.issues:
        print_result(precheck)
        return 1

    revised_path = workflow_dir / "06-revised.md"
    summary_json_path = workflow_dir / "07-summary.json"
    summary_payload = extract_summary_payload(load_json(summary_json_path))

    chapter_path = project_root / "chapters" / f"{chapter_id}.md"
    summary_md_path = project_root / "summaries" / f"{chapter_id}.summary.md"
    chapter_path.parent.mkdir(parents=True, exist_ok=True)
    summary_md_path.parent.mkdir(parents=True, exist_ok=True)

    chapter_path.write_text(revised_path.read_text(encoding="utf-8"), encoding="utf-8")
    summary_md_path.write_text(render_summary_markdown(chapter_id, summary_payload), encoding="utf-8")

    manifest["status"] = "archived"
    write_json(manifest_path, manifest)

    result = check_chapter(project_root, chapter_id)
    if result.issues:
        manifest["status"] = status
        write_json(manifest_path, manifest)
        if chapter_path.exists():
            chapter_path.unlink()
        if summary_md_path.exists():
            summary_md_path.unlink()
    print_result(result)
    return 1 if result.issues else 0


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()

    if args.command == "init":
        return init_workflow(
            project_root,
            args.chapter_id,
            args.chapter_title,
            args.dialogue_audit,
            args.execution_policy,
        )
    if args.command == "run-chapter":
        return run_chapter(
            project_root,
            args.chapter_id,
            args.execution_policy,
            args.codex_bin,
            args.model,
            args.archive,
        )
    if args.command == "check":
        return run_check(project_root, args.chapter_id, args.all)
    if args.command == "set-status":
        return set_status(project_root, args.chapter_id, args.status)
    if args.command == "archive":
        return archive(project_root, args.chapter_id)

    raise RuntimeError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
