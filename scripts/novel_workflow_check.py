#!/usr/bin/env python3
"""Lint-style gate for chapter workflow artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STATUS_ORDER = [
    "initialized",
    "planned",
    "drafted",
    "audited",
    "revised",
    "summarized",
    "archived",
]

STATUS_INDEX = {name: idx for idx, name in enumerate(STATUS_ORDER)}

LEGACY_CONTRACT_FIELDS = [
    "schema_version",
    "task_type",
    "agent_role",
    "status",
    "artifacts",
    "diagnostics",
    "proposed_writebacks",
]

STRICT_CONTRACT_FIELDS = LEGACY_CONTRACT_FIELDS + [
    "contract_version",
    "task_id",
    "execution",
    "recommendations",
]

RESULT_STATUS_VALUES = {
    "ready",
    "completed",
    "skipped",
    "blocked",
    "invalid",
    "needs_review",
    "success",
    "partial_success",
}

EXECUTION_MODES = {
    "pending",
    "subagent",
    "approved-fallback",
    "orchestrator",
    "legacy-inferred",
    "skipped",
}

TRACE_STATUS_VALUES = {"ready", "in_progress", "completed"}
DISPATCH_STATUS_VALUES = {"queued", "running", "completed", "skipped", "blocked", "failed"}

JSON_STAGE_SPECS = {
    "02-plan.json": {
        "stage": "planned",
        "task_type": "chapter-plan",
        "agent_role": "novel-plot-architect",
    },
    "04-continuity-audit.json": {
        "stage": "audited",
        "task_type": "continuity-audit",
        "agent_role": "novel-continuity-auditor",
    },
    "05-dialogue-audit.json": {
        "stage": "audited",
        "task_type": "dialogue-audit",
        "agent_role": "novel-dialogue-editor",
    },
    "07-summary.json": {
        "stage": "summarized",
        "task_type": "chapter-summary",
        "agent_role": "novel-chapter-summarizer",
    },
}

OUTPUT_STAGE_SPECS = {
    "02-plan.json": "planned",
    "03-draft.md": "drafted",
    "04-continuity-audit.json": "audited",
    "05-dialogue-audit.json": "audited",
    "07-summary.json": "summarized",
}

META_PATTERNS = [
    r"本章",
    r"这一章",
    r"下一章",
    r"下一节",
    r"如果说上一章",
    r"如果说前一章",
    r"这(?:一章|一节)要写",
    r"到这(?:一章|一节)结束时",
    r"要写的并不是",
    r"根据[^。\n]{0,20}(?:资料|回顾|报道|采访|统计)",
    r"这里(?:真正重要|最值得写)",
]

MEDIUM_BLOCKING_DIMENSIONS = {
    "narrative-surface",
    "commentary-drift",
    "readability",
    "prose-naturalness",
}


@dataclass
class CheckResult:
    chapter_id: str
    status: str | None
    workflow_dir: Path
    issues: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint a novel chapter workflow.")
    parser.add_argument("project_root", help="Novel project root, e.g. stories/messi-series")
    parser.add_argument("chapter_id", nargs="?", help="Chapter id like CH005; inferred from CURRENT_STATE.md when omitted")
    parser.add_argument("--all", action="store_true", help="Check all workflow chapter directories under project_root/workflows")
    return parser.parse_args()


def infer_chapter_id(project_root: Path) -> str:
    current_state = project_root / "CURRENT_STATE.md"
    if current_state.exists():
        text = current_state.read_text(encoding="utf-8")
        match = re.search(r"Current chapter:\s*(CH\d+)", text)
        if match:
            return match.group(1)

    chapters_dir = project_root / "chapters"
    chapter_files = sorted(chapters_dir.glob("CH*.md"))
    if chapter_files:
        return chapter_files[-1].stem

    raise ValueError("Could not infer chapter id from CURRENT_STATE.md or chapters/ directory.")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def require_string(data: dict[str, Any], field: str, path: Path, issues: list[str]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        issues.append(f"`{field}` must be a non-empty string in {path}")
        return None
    return value


def require_list(data: dict[str, Any], field: str, path: Path, issues: list[str]) -> list[Any] | None:
    value = data.get(field)
    if not isinstance(value, list):
        issues.append(f"`{field}` must be a list in {path}")
        return None
    return value


def require_string_list(value: Any, field: str, path: Path, issues: list[str], *, non_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        issues.append(f"`{field}` must be a string list in {path}")
        return []
    if non_empty and not value:
        issues.append(f"`{field}` must be a non-empty string list in {path}")
    return [item.strip() for item in value]


def require_nonempty_markdown(path: Path, issues: list[str]) -> None:
    if not path.exists():
        issues.append(f"Missing markdown artifact: {path}")
        return

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        issues.append(f"Empty markdown artifact: {path}")


def lint_meta_surface(path: Path, issues: list[str]) -> None:
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")
    for pattern in META_PATTERNS:
        match = re.search(pattern, text)
        if match:
            issues.append(f"Meta-narrative leakage in {path}: matched `{pattern}`")


def severity_from_entry(entry: object) -> int:
    if not isinstance(entry, dict):
        return 0
    severity = str(entry.get("severity", "none")).strip().lower()
    return {"none": 0, "low": 1, "medium": 2, "high": 3}.get(severity, 0)


def entry_is_blocking(entry: object) -> bool:
    if not isinstance(entry, dict):
        return False
    severity = severity_from_entry(entry)
    if severity >= 3:
        return True
    dimension = str(entry.get("analysis_dimension", "")).strip()
    return severity >= 2 and dimension in MEDIUM_BLOCKING_DIMENSIONS


def is_strict_manifest(manifest: dict[str, Any]) -> bool:
    execution_policy = manifest.get("execution_policy")
    return isinstance(execution_policy, dict) and bool(execution_policy.get("require_subagents"))


def evaluate_when_rule(when: str, manifest: dict[str, Any]) -> bool:
    if when == "always":
        return True
    if when.startswith("required_steps."):
        key = when.split(".", 1)[1]
        required_steps = manifest.get("required_steps", {})
        if isinstance(required_steps, dict):
            return bool(required_steps.get(key))
        return False
    return False


def minimum_stage_rank(output_refs: list[str]) -> int | None:
    ranks: list[int] = []
    for ref in output_refs:
        stage = OUTPUT_STAGE_SPECS.get(ref)
        if stage is None:
            continue
        ranks.append(STATUS_INDEX[stage])
    if not ranks:
        return None
    return max(ranks)


def validate_manifest(path: Path, chapter_id: str, issues: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        issues.append(f"Missing workflow manifest: {path}")
        return None

    data = load_json(path)
    for field in ["schema_version", "chapter_id", "chapter_title", "status", "required_steps"]:
        if field not in data:
            issues.append(f"Missing `{field}` in {path}")

    if data.get("chapter_id") != chapter_id:
        issues.append(f"Manifest chapter_id `{data.get('chapter_id')}` does not match requested `{chapter_id}`")

    status = data.get("status")
    if status not in STATUS_INDEX:
        issues.append(f"Invalid workflow status `{status}` in {path}")

    required_steps = data.get("required_steps", {})
    if not isinstance(required_steps, dict):
        issues.append(f"`required_steps` must be an object in {path}")
    else:
        for key in ["continuity_audit", "dialogue_audit"]:
            if key not in required_steps:
                issues.append(f"Missing `required_steps.{key}` in {path}")

    if not is_strict_manifest(data):
        return data

    require_string(data, "contract_version", path, issues)
    execution_policy = data.get("execution_policy")
    if not isinstance(execution_policy, dict):
        issues.append(f"Missing or invalid `execution_policy` in {path}")
        return data

    orchestration_mode = require_string(execution_policy, "orchestration_mode", path, issues)
    if orchestration_mode != "multi-skill-subagents":
        issues.append(f"`execution_policy.orchestration_mode` must be `multi-skill-subagents` in {path}")

    if execution_policy.get("require_subagents") is not True:
        issues.append(f"`execution_policy.require_subagents` must be true in {path}")

    trace_file = require_string(execution_policy, "trace_file", path, issues)
    if trace_file and trace_file != "09-execution-log.json":
        issues.append(f"`execution_policy.trace_file` should be `09-execution-log.json` in {path}")

    required_dispatches = execution_policy.get("required_dispatches")
    if not isinstance(required_dispatches, list) or not required_dispatches:
        issues.append(f"`execution_policy.required_dispatches` must be a non-empty list in {path}")
    else:
        for index, dispatch in enumerate(required_dispatches):
            if not isinstance(dispatch, dict):
                issues.append(f"`execution_policy.required_dispatches[{index}]` must be an object in {path}")
                continue
            require_string(dispatch, "agent_role", path, issues)
            output_refs = dispatch.get("output_refs")
            if not isinstance(output_refs, list) or not output_refs or not all(isinstance(ref, str) and ref for ref in output_refs):
                issues.append(f"`execution_policy.required_dispatches[{index}].output_refs` must be a non-empty string list in {path}")
            when = require_string(dispatch, "when", path, issues)
            if when and when != "always" and not when.startswith("required_steps."):
                issues.append(f"Unsupported `when` rule `{when}` in {path}")

    fallback_policy = execution_policy.get("fallback_policy")
    if not isinstance(fallback_policy, dict):
        issues.append(f"Missing or invalid `execution_policy.fallback_policy` in {path}")
    else:
        allow_modes = fallback_policy.get("allow_modes")
        if not isinstance(allow_modes, list) or not all(isinstance(mode, str) for mode in allow_modes):
            issues.append(f"`execution_policy.fallback_policy.allow_modes` must be a string list in {path}")
        if "require_exception_entry" not in fallback_policy:
            issues.append(f"Missing `execution_policy.fallback_policy.require_exception_entry` in {path}")

    return data


def validate_execution_block(data: dict[str, Any], path: Path, issues: list[str], strict: bool) -> None:
    execution = data.get("execution")
    if not strict:
        return
    if not isinstance(execution, dict):
        issues.append(f"Missing or invalid `execution` in {path}")
        return

    mode = require_string(execution, "mode", path, issues)
    if mode and mode not in EXECUTION_MODES:
        issues.append(f"Unsupported execution mode `{mode}` in {path}")

    trace_ref = execution.get("trace_ref")
    if trace_ref is not None and not isinstance(trace_ref, str):
        issues.append(f"`execution.trace_ref` must be a string in {path}")

    provenance = execution.get("provenance")
    if not isinstance(provenance, dict):
        issues.append(f"`execution.provenance` must be an object in {path}")
    else:
        for field in ["agent_session_id", "agent_run_id", "external_invocation_id"]:
            value = provenance.get(field)
            if value is not None and not isinstance(value, str):
                issues.append(f"`execution.provenance.{field}` must be a string in {path}")

        if mode in {"subagent", "approved-fallback"}:
            if not any(isinstance(provenance.get(field), str) and provenance.get(field).strip() for field in ["agent_session_id", "agent_run_id", "external_invocation_id"]):
                issues.append(f"`execution.provenance` must contain at least one identifier when mode is `{mode}` in {path}")

    input_snapshot = execution.get("input_snapshot")
    if not isinstance(input_snapshot, dict):
        issues.append(f"`execution.input_snapshot` must be an object in {path}")
    else:
        context_refs = input_snapshot.get("context_refs")
        if not isinstance(context_refs, list) or not all(isinstance(ref, str) and ref for ref in context_refs):
            issues.append(f"`execution.input_snapshot.context_refs` must be a string list in {path}")
        context_hash = input_snapshot.get("context_hash")
        if context_hash is not None and not isinstance(context_hash, str):
            issues.append(f"`execution.input_snapshot.context_hash` must be a string in {path}")

    status = data.get("status")
    if status in {"completed", "success", "partial_success", "needs_review", "blocked", "invalid", "skipped"} and mode == "pending":
        issues.append(f"`execution.mode` cannot stay `pending` once `{status}` is set in {path}")


def validate_contract_json(
    path: Path,
    issues: list[str],
    *,
    strict: bool,
    expected_task_type: str | None = None,
    expected_agent_role: str | None = None,
) -> dict[str, Any] | None:
    data = load_json(path)
    required_fields = STRICT_CONTRACT_FIELDS if strict else LEGACY_CONTRACT_FIELDS
    for field in required_fields:
        if field not in data:
            issues.append(f"Missing `{field}` in {path}")

    require_string(data, "schema_version", path, issues)
    if strict:
        require_string(data, "contract_version", path, issues)
        require_string(data, "task_id", path, issues)

    task_type = require_string(data, "task_type", path, issues)
    agent_role = require_string(data, "agent_role", path, issues)
    status = require_string(data, "status", path, issues)

    if task_type and expected_task_type and task_type != expected_task_type:
        issues.append(f"`task_type` in {path} should be `{expected_task_type}`, got `{task_type}`")
    if agent_role and expected_agent_role and agent_role != expected_agent_role:
        issues.append(f"`agent_role` in {path} should be `{expected_agent_role}`, got `{agent_role}`")
    if status and status not in RESULT_STATUS_VALUES:
        issues.append(f"Unsupported result status `{status}` in {path}")

    require_list(data, "artifacts", path, issues)
    require_list(data, "diagnostics", path, issues)
    require_list(data, "proposed_writebacks", path, issues)

    recommendations = data.get("recommendations")
    if strict and not isinstance(recommendations, list):
        issues.append(f"`recommendations` must be a list in {path}")

    change_set = data.get("change_set")
    if change_set is not None and not isinstance(change_set, (list, dict)):
        issues.append(f"`change_set` must be a list or object in {path}")

    validate_execution_block(data, path, issues, strict)
    return data


def find_artifact(contract_data: dict[str, Any], artifact_type: str) -> dict[str, Any] | None:
    artifacts = contract_data.get("artifacts")
    if not isinstance(artifacts, list):
        return None
    for artifact in artifacts:
        if isinstance(artifact, dict) and artifact.get("type") == artifact_type:
            return artifact
    return None


def validate_plan_payload(path: Path, contract_data: dict[str, Any], issues: list[str]) -> None:
    artifact = find_artifact(contract_data, "chapter_plan")
    if artifact is None:
        issues.append(f"Missing `chapter_plan` artifact in {path}")
        return

    content = artifact.get("content")
    if not isinstance(content, list) or not content:
        issues.append(f"`chapter_plan.content` must be a non-empty list in {path}")
        return

    for index, item in enumerate(content):
        if not isinstance(item, dict):
            issues.append(f"`chapter_plan.content[{index}]` must be an object in {path}")
            continue
        for field in ["unit", "goal", "obstacle", "beat"]:
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"`chapter_plan.content[{index}].{field}` must be a non-empty string in {path}")


def collect_analysis_dimensions(contract_data: dict[str, Any]) -> set[str]:
    dimensions: set[str] = set()

    diagnostics = contract_data.get("diagnostics")
    if isinstance(diagnostics, list):
        for item in diagnostics:
            if isinstance(item, dict):
                value = item.get("analysis_dimension")
                if isinstance(value, str) and value.strip():
                    dimensions.add(value.strip())

    artifact = find_artifact(contract_data, "audit_report")
    if artifact is not None:
        findings = artifact.get("findings")
        if isinstance(findings, list):
            for item in findings:
                if isinstance(item, dict):
                    value = item.get("analysis_dimension")
                    if isinstance(value, str) and value.strip():
                        dimensions.add(value.strip())

    return dimensions


def validate_continuity_audit_payload(path: Path, contract_data: dict[str, Any], issues: list[str]) -> None:
    artifact = find_artifact(contract_data, "audit_report")
    if artifact is None:
        issues.append(f"Missing `audit_report` artifact in {path}")
        return

    findings = artifact.get("findings")
    if not isinstance(findings, list):
        issues.append(f"`audit_report.findings` must be a list in {path}")

    required_dimensions = {
        "timeline",
        "fact-boundary",
        "character-source",
        "narrative-surface",
        "character-embodiment",
        "commentary-drift",
        "tension",
        "readability",
        "prose-naturalness",
    }
    covered = collect_analysis_dimensions(contract_data)
    missing = sorted(required_dimensions - covered)
    if missing:
        issues.append(f"Continuity audit must cover dimensions {missing} in {path}")

    diagnostics = contract_data.get("diagnostics")
    if isinstance(diagnostics, list) and any(entry_is_blocking(item) for item in diagnostics):
        issues.append(f"Continuity audit still contains blocking diagnostics in {path}")

    if isinstance(findings, list) and any(entry_is_blocking(item) for item in findings):
        issues.append(f"Continuity audit still contains blocking findings in {path}")


def validate_summary_payload(path: Path, contract_data: dict[str, Any], issues: list[str]) -> None:
    artifact = find_artifact(contract_data, "chapter_summary")
    if artifact is None:
        issues.append(f"Missing `chapter_summary` artifact in {path}")
        return

    content = artifact.get("content")
    if not isinstance(content, dict):
        issues.append(f"`chapter_summary.content` must be an object in {path}")
        return

    one_line = content.get("one_line_summary")
    if not isinstance(one_line, str) or not one_line.strip():
        issues.append(f"`chapter_summary.content.one_line_summary` must be a non-empty string in {path}")

    require_string_list(content.get("actor_refs"), "chapter_summary.content.actor_refs", path, issues, non_empty=True)
    require_string_list(content.get("major_beats"), "chapter_summary.content.major_beats", path, issues, non_empty=True)
    require_string_list(content.get("state_changes"), "chapter_summary.content.state_changes", path, issues)
    require_string_list(content.get("carry_forward"), "chapter_summary.content.carry_forward", path, issues)

    open_loops = content.get("open_loops")
    if not isinstance(open_loops, dict):
        issues.append(f"`chapter_summary.content.open_loops` must be an object in {path}")
        return
    for field in ["opened", "advanced", "resolved"]:
        require_string_list(open_loops.get(field), f"chapter_summary.content.open_loops.{field}", path, issues)


def validate_trace_exception(exception: dict[str, Any], trace_path: Path, issues: list[str], fallback_modes: set[str]) -> None:
    for field in ["agent_role", "fallback_mode", "reason_code", "approved_by", "justification", "output_refs"]:
        if field not in exception:
            issues.append(f"Missing `{field}` in trace exception {trace_path}")

    if not isinstance(exception.get("output_refs"), list) or not all(isinstance(ref, str) and ref for ref in exception.get("output_refs", [])):
        issues.append(f"`output_refs` in trace exception must be a non-empty string list in {trace_path}")

    fallback_mode = exception.get("fallback_mode")
    if isinstance(fallback_mode, str) and fallback_mode not in fallback_modes:
        issues.append(f"Trace exception fallback mode `{fallback_mode}` is not allowed by manifest policy in {trace_path}")


def find_matching_exception(
    exceptions: list[dict[str, Any]],
    *,
    agent_role: str,
    output_refs: list[str],
    mode: str,
) -> bool:
    expected = set(output_refs)
    for exception in exceptions:
        if exception.get("agent_role") != agent_role:
            continue
        if exception.get("fallback_mode") != mode:
            continue
        refs = exception.get("output_refs")
        if isinstance(refs, list) and expected.issubset(set(refs)):
            return True
    return False


def validate_execution_trace(
    workflow_dir: Path,
    chapter_id: str,
    manifest: dict[str, Any],
    status_rank: int,
    issues: list[str],
) -> dict[str, Any] | None:
    execution_policy = manifest.get("execution_policy", {})
    if not isinstance(execution_policy, dict):
        return None

    trace_name = execution_policy.get("trace_file", "09-execution-log.json")
    trace_path = workflow_dir / trace_name
    if not trace_path.exists():
        issues.append(f"Missing execution trace: {trace_path}")
        return None

    data = load_json(trace_path)
    for field in ["schema_version", "contract_version", "chapter_id", "orchestrator_role", "status", "dispatches", "exceptions"]:
        if field not in data:
            issues.append(f"Missing `{field}` in {trace_path}")

    require_string(data, "schema_version", trace_path, issues)
    require_string(data, "contract_version", trace_path, issues)
    require_string(data, "chapter_id", trace_path, issues)
    require_string(data, "orchestrator_role", trace_path, issues)
    trace_status = require_string(data, "status", trace_path, issues)

    if data.get("chapter_id") != chapter_id:
        issues.append(f"Trace chapter_id `{data.get('chapter_id')}` does not match `{chapter_id}` in {trace_path}")
    if data.get("orchestrator_role") != "novel-orchestrator-main":
        issues.append(f"`orchestrator_role` must be `novel-orchestrator-main` in {trace_path}")
    if trace_status and trace_status not in TRACE_STATUS_VALUES:
        issues.append(f"Unsupported trace status `{trace_status}` in {trace_path}")

    dispatches = data.get("dispatches")
    if not isinstance(dispatches, list):
        issues.append(f"`dispatches` must be a list in {trace_path}")
        dispatches = []

    exceptions = data.get("exceptions")
    if not isinstance(exceptions, list):
        issues.append(f"`exceptions` must be a list in {trace_path}")
        exceptions = []

    fallback_policy = execution_policy.get("fallback_policy", {})
    allow_modes = fallback_policy.get("allow_modes", [])
    fallback_modes = set(mode for mode in allow_modes if isinstance(mode, str))

    for dispatch in dispatches:
        if not isinstance(dispatch, dict):
            issues.append(f"Dispatch entries must be objects in {trace_path}")
            continue
        for field in ["task_id", "agent_role", "mode", "status", "input_refs", "output_refs"]:
            if field not in dispatch:
                issues.append(f"Missing `{field}` in dispatch entry of {trace_path}")

        mode = dispatch.get("mode")
        status = dispatch.get("status")
        if isinstance(mode, str) and mode not in {"subagent", "approved-fallback", "orchestrator", "legacy-inferred"}:
            issues.append(f"Unsupported dispatch mode `{mode}` in {trace_path}")
        if isinstance(status, str) and status not in DISPATCH_STATUS_VALUES:
            issues.append(f"Unsupported dispatch status `{status}` in {trace_path}")

        input_refs = dispatch.get("input_refs")
        output_refs = dispatch.get("output_refs")
        if not isinstance(input_refs, list) or not all(isinstance(ref, str) and ref for ref in input_refs):
            issues.append(f"`input_refs` in dispatch entry must be a string list in {trace_path}")
        if not isinstance(output_refs, list) or not all(isinstance(ref, str) and ref for ref in output_refs):
            issues.append(f"`output_refs` in dispatch entry must be a string list in {trace_path}")

        for optional_field in ["agent_session_id", "agent_run_id", "model", "started_at", "completed_at", "notes"]:
            value = dispatch.get(optional_field)
            if value is not None and not isinstance(value, str):
                issues.append(f"`{optional_field}` in dispatch entry must be a string in {trace_path}")

        if mode == "subagent" and not any(isinstance(dispatch.get(field), str) and dispatch.get(field).strip() for field in ["agent_session_id", "agent_run_id"]):
            issues.append(f"Subagent dispatches must include `agent_session_id` or `agent_run_id` in {trace_path}")

        if mode == "approved-fallback":
            if not isinstance(output_refs, list):
                output_refs = []
            if not find_matching_exception(
                [exc for exc in exceptions if isinstance(exc, dict)],
                agent_role=str(dispatch.get("agent_role", "")),
                output_refs=[str(ref) for ref in output_refs],
                mode="approved-fallback",
            ):
                issues.append(f"Approved fallback dispatch for `{dispatch.get('agent_role')}` lacks a matching exception entry in {trace_path}")

    for exception in exceptions:
        if not isinstance(exception, dict):
            issues.append(f"Trace exceptions must be objects in {trace_path}")
            continue
        validate_trace_exception(exception, trace_path, issues, fallback_modes)

    required_dispatches = execution_policy.get("required_dispatches", [])
    if not isinstance(required_dispatches, list):
        return data

    dispatch_objects = [dispatch for dispatch in dispatches if isinstance(dispatch, dict)]
    for dispatch_rule in required_dispatches:
        if not isinstance(dispatch_rule, dict):
            continue
        when = dispatch_rule.get("when", "always")
        if not isinstance(when, str) or not evaluate_when_rule(when, manifest):
            continue

        output_refs = dispatch_rule.get("output_refs")
        if not isinstance(output_refs, list):
            continue

        needed_rank = minimum_stage_rank([str(ref) for ref in output_refs if isinstance(ref, str)])
        if needed_rank is None or status_rank < needed_rank:
            continue

        agent_role = str(dispatch_rule.get("agent_role", ""))
        matching = []
        for dispatch in dispatch_objects:
            if dispatch.get("agent_role") != agent_role:
                continue
            dispatch_output_refs = dispatch.get("output_refs")
            if not isinstance(dispatch_output_refs, list):
                continue
            if set(output_refs).issubset(set(dispatch_output_refs)):
                matching.append(dispatch)

        if not matching:
            issues.append(f"Missing required sub-agent dispatch for `{agent_role}` -> {output_refs} in {trace_path}")
            continue

        completed_dispatches = [dispatch for dispatch in matching if dispatch.get("status") == "completed"]
        if not completed_dispatches:
            issues.append(f"Required dispatch for `{agent_role}` -> {output_refs} is not completed in {trace_path}")
            continue

        dispatch = completed_dispatches[-1]
        mode = dispatch.get("mode")
        if mode == "subagent":
            continue
        if mode in fallback_modes and find_matching_exception(
            [exc for exc in exceptions if isinstance(exc, dict)],
            agent_role=agent_role,
            output_refs=[str(ref) for ref in output_refs],
            mode=str(mode),
        ):
            continue
        issues.append(
            f"Required dispatch for `{agent_role}` -> {output_refs} must run as `subagent`"
            f" or an approved fallback in {trace_path}, got `{mode}`"
        )

    return data


def cross_check_contract_with_trace(
    artifact_path: Path,
    contract_data: dict[str, Any],
    trace_data: dict[str, Any] | None,
    issues: list[str],
) -> None:
    if trace_data is None:
        return

    task_id = contract_data.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        return

    dispatches = trace_data.get("dispatches", [])
    if not isinstance(dispatches, list):
        return

    matches = [dispatch for dispatch in dispatches if isinstance(dispatch, dict) and dispatch.get("task_id") == task_id]
    if not matches:
        issues.append(f"`task_id` `{task_id}` in {artifact_path} is not present in 09-execution-log.json")
        return

    dispatch = matches[-1]
    if dispatch.get("agent_role") != contract_data.get("agent_role"):
        issues.append(
            f"`agent_role` mismatch for task `{task_id}`: contract has `{contract_data.get('agent_role')}`,"
            f" trace has `{dispatch.get('agent_role')}`"
        )

    output_refs = dispatch.get("output_refs")
    if isinstance(output_refs, list) and artifact_path.name not in output_refs:
        issues.append(f"Trace dispatch `{task_id}` does not list `{artifact_path.name}` in output_refs")

    execution = contract_data.get("execution", {})
    if not isinstance(execution, dict):
        return

    mode = execution.get("mode")
    if isinstance(mode, str) and mode != dispatch.get("mode"):
        issues.append(f"`execution.mode` in {artifact_path} does not match trace mode for `{task_id}`")


def check_chapter(project_root: Path, chapter_id: str) -> CheckResult:
    workflow_dir = project_root / "workflows" / chapter_id
    manifest_path = workflow_dir / "00-manifest.json"
    issues: list[str] = []

    try:
        manifest = validate_manifest(manifest_path, chapter_id, issues)
    except ValueError as exc:
        issues.append(str(exc))
        manifest = None

    if manifest is None:
        return CheckResult(chapter_id=chapter_id, status=None, workflow_dir=workflow_dir, issues=issues)

    status = manifest["status"]
    required_steps = manifest["required_steps"]
    status_rank = STATUS_INDEX[status]
    strict = is_strict_manifest(manifest)

    require_nonempty_markdown(workflow_dir / "01-context.md", issues)

    trace_data = None
    if strict:
        try:
            trace_data = validate_execution_trace(workflow_dir, chapter_id, manifest, status_rank, issues)
        except ValueError as exc:
            issues.append(str(exc))

    if status_rank >= STATUS_INDEX["planned"]:
        plan_path = workflow_dir / "02-plan.json"
        if not plan_path.exists():
            issues.append(f"Missing planning artifact: {plan_path}")
        else:
            try:
                plan_data = validate_contract_json(
                    plan_path,
                    issues,
                    strict=strict,
                    expected_task_type=JSON_STAGE_SPECS["02-plan.json"]["task_type"],
                    expected_agent_role=JSON_STAGE_SPECS["02-plan.json"]["agent_role"],
                )
                if plan_data:
                    validate_plan_payload(plan_path, plan_data, issues)
                if strict and plan_data:
                    cross_check_contract_with_trace(plan_path, plan_data, trace_data, issues)
            except ValueError as exc:
                issues.append(str(exc))

    if status_rank >= STATUS_INDEX["drafted"]:
        require_nonempty_markdown(workflow_dir / "03-draft.md", issues)

    if status_rank >= STATUS_INDEX["audited"]:
        if required_steps.get("continuity_audit", True):
            audit_path = workflow_dir / "04-continuity-audit.json"
            if not audit_path.exists():
                issues.append(f"Missing required continuity audit: {audit_path}")
            else:
                try:
                    audit_data = validate_contract_json(
                        audit_path,
                        issues,
                        strict=strict,
                        expected_task_type=JSON_STAGE_SPECS["04-continuity-audit.json"]["task_type"],
                        expected_agent_role=JSON_STAGE_SPECS["04-continuity-audit.json"]["agent_role"],
                    )
                    if audit_data:
                        validate_continuity_audit_payload(audit_path, audit_data, issues)
                    if strict and audit_data:
                        cross_check_contract_with_trace(audit_path, audit_data, trace_data, issues)
                except ValueError as exc:
                    issues.append(str(exc))

        dialogue_path = workflow_dir / "05-dialogue-audit.json"
        if required_steps.get("dialogue_audit", False):
            if not dialogue_path.exists():
                issues.append(f"Missing required dialogue audit: {dialogue_path}")
            else:
                try:
                    dialogue_data = validate_contract_json(
                        dialogue_path,
                        issues,
                        strict=strict,
                        expected_task_type=JSON_STAGE_SPECS["05-dialogue-audit.json"]["task_type"],
                        expected_agent_role=JSON_STAGE_SPECS["05-dialogue-audit.json"]["agent_role"],
                    )
                    if strict and dialogue_data:
                        cross_check_contract_with_trace(dialogue_path, dialogue_data, trace_data, issues)
                except ValueError as exc:
                    issues.append(str(exc))
        elif dialogue_path.exists():
            try:
                dialogue_data = validate_contract_json(
                    dialogue_path,
                    issues,
                    strict=strict,
                    expected_task_type=JSON_STAGE_SPECS["05-dialogue-audit.json"]["task_type"],
                    expected_agent_role=JSON_STAGE_SPECS["05-dialogue-audit.json"]["agent_role"],
                )
                if strict and dialogue_data:
                    cross_check_contract_with_trace(dialogue_path, dialogue_data, trace_data, issues)
            except ValueError as exc:
                issues.append(str(exc))

    if status_rank >= STATUS_INDEX["revised"]:
        revised_path = workflow_dir / "06-revised.md"
        require_nonempty_markdown(revised_path, issues)
        lint_meta_surface(revised_path, issues)

    if status_rank >= STATUS_INDEX["summarized"]:
        summary_json = workflow_dir / "07-summary.json"
        writeback_md = workflow_dir / "08-writeback.md"
        if not summary_json.exists():
            issues.append(f"Missing summary artifact: {summary_json}")
        else:
            try:
                summary_data = validate_contract_json(
                    summary_json,
                    issues,
                    strict=strict,
                    expected_task_type=JSON_STAGE_SPECS["07-summary.json"]["task_type"],
                    expected_agent_role=JSON_STAGE_SPECS["07-summary.json"]["agent_role"],
                )
                if summary_data:
                    validate_summary_payload(summary_json, summary_data, issues)
                if strict and summary_data:
                    cross_check_contract_with_trace(summary_json, summary_data, trace_data, issues)
            except ValueError as exc:
                issues.append(str(exc))
        require_nonempty_markdown(writeback_md, issues)

    if status_rank >= STATUS_INDEX["archived"]:
        chapter_path = project_root / "chapters" / f"{chapter_id}.md"
        summary_path = project_root / "summaries" / f"{chapter_id}.summary.md"
        require_nonempty_markdown(chapter_path, issues)
        require_nonempty_markdown(summary_path, issues)
        lint_meta_surface(chapter_path, issues)

    return CheckResult(chapter_id=chapter_id, status=status, workflow_dir=workflow_dir, issues=issues)


def iter_workflow_chapters(project_root: Path) -> list[str]:
    workflows_dir = project_root / "workflows"
    if not workflows_dir.exists():
        return []

    chapter_ids: list[str] = []
    for path in sorted(workflows_dir.iterdir()):
        if not path.is_dir():
            continue
        if path.name.startswith("_"):
            continue
        if re.fullmatch(r"CH\d+", path.name):
            chapter_ids.append(path.name)
    return chapter_ids


def print_result(result: CheckResult) -> None:
    if result.issues:
        print(f"FAIL: {result.chapter_id}")
        for issue in result.issues:
            print(f"- {issue}")
    else:
        print(f"PASS: {result.chapter_id}")
        print(f"- workflow status: {result.status}")
        print(f"- workflow dir: {result.workflow_dir}")


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()

    if args.all:
        chapter_ids = iter_workflow_chapters(project_root)
        if not chapter_ids:
            print("FAIL: no workflow chapter directories found")
            return 1

        failed = False
        for chapter_id in chapter_ids:
            result = check_chapter(project_root, chapter_id)
            print_result(result)
            if result.issues:
                failed = True
        return 1 if failed else 0

    chapter_id = args.chapter_id or infer_chapter_id(project_root)
    result = check_chapter(project_root, chapter_id)
    print_result(result)
    return 1 if result.issues else 0


if __name__ == "__main__":
    sys.exit(main())
