#!/usr/bin/env python3
"""Lint-style gate for chapter workflow artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


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

CONTRACT_FIELDS = [
    "schema_version",
    "task_type",
    "agent_role",
    "status",
    "artifacts",
    "diagnostics",
    "proposed_writebacks",
]

META_PATTERNS = [
    r"本章",
    r"这一章",
    r"下一章",
    r"下一节",
    r"如果说上一章",
    r"如果说前一章",
    r"这(?:一章|一节)要写",
    r"要写的并不是",
    r"根据[^。\n]{0,20}(?:资料|回顾|报道|采访|统计)",
    r"这里(?:真正重要|最值得写)",
]


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


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def validate_contract_json(path: Path, issues: list[str]) -> None:
    data = load_json(path)
    for field in CONTRACT_FIELDS:
        if field not in data:
            issues.append(f"Missing `{field}` in {path}")


def validate_manifest(path: Path, chapter_id: str, issues: list[str]) -> dict | None:
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

    return data


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

    required_markdown = [workflow_dir / "01-context.md"]
    for path in required_markdown:
        require_nonempty_markdown(path, issues)

    if status_rank >= STATUS_INDEX["planned"]:
        plan_path = workflow_dir / "02-plan.json"
        if not plan_path.exists():
            issues.append(f"Missing planning artifact: {plan_path}")
        else:
            try:
                validate_contract_json(plan_path, issues)
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
                    validate_contract_json(audit_path, issues)
                except ValueError as exc:
                    issues.append(str(exc))

        if required_steps.get("dialogue_audit", False):
            dialogue_path = workflow_dir / "05-dialogue-audit.json"
            if not dialogue_path.exists():
                issues.append(f"Missing required dialogue audit: {dialogue_path}")
            else:
                try:
                    validate_contract_json(dialogue_path, issues)
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
                validate_contract_json(summary_json, issues)
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
