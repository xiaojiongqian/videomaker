#!/usr/bin/env python3
"""Automated runner for the novel workflow."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from novel_workflow_check import check_chapter, infer_chapter_id, iter_workflow_chapters, print_result


STATUS_ORDER = [
    "initialized",
    "planned",
    "drafted",
    "audited",
    "revised",
    "summarized",
    "archived",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the novel chapter workflow with built-in gates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize workflow files for a new chapter")
    init_parser.add_argument("project_root")
    init_parser.add_argument("chapter_id")
    init_parser.add_argument("chapter_title")
    init_parser.add_argument("--dialogue-audit", action="store_true")

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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def init_workflow(project_root: Path, chapter_id: str, chapter_title: str, dialogue_audit: bool) -> int:
    template_dir = get_template_dir(project_root)
    workflow_dir = get_workflow_dir(project_root, chapter_id)
    workflow_dir.mkdir(parents=True, exist_ok=True)

    for template in sorted(template_dir.iterdir()):
        if template.is_file():
            create_file_from_template(template, workflow_dir / template.name)

    for path in sorted(workflow_dir.iterdir()):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace("CHXXX", chapter_id).replace("Chapter Title", chapter_title)
        path.write_text(text, encoding="utf-8")

    manifest_path = workflow_dir / "00-manifest.json"
    manifest = load_json(manifest_path)
    manifest["chapter_id"] = chapter_id
    manifest["chapter_title"] = chapter_title
    manifest["required_steps"]["dialogue_audit"] = dialogue_audit
    manifest["status"] = "initialized"
    write_json(manifest_path, manifest)

    context_path = workflow_dir / "01-context.md"
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


def extract_summary_payload(summary_json: dict) -> dict:
    artifacts = summary_json.get("artifacts", [])
    for artifact in artifacts:
        if artifact.get("type") == "chapter_summary":
            content = artifact.get("content")
            if isinstance(content, dict):
                return content
    return {}


def listify(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def render_summary_markdown(chapter_id: str, payload: dict) -> str:
    one_line = str(payload.get("one_line_summary", "")).strip()
    major_beats = listify(payload.get("major_beats"))
    state_changes = listify(payload.get("state_changes"))
    carry_forward = listify(payload.get("carry_forward"))
    open_loops = payload.get("open_loops", {})
    opened = listify(open_loops.get("opened")) if isinstance(open_loops, dict) else []
    advanced = listify(open_loops.get("advanced")) if isinstance(open_loops, dict) else []
    resolved = listify(open_loops.get("resolved")) if isinstance(open_loops, dict) else []

    def render_list(items: list[str], fallback: str = "无") -> str:
        if not items:
            return f"- {fallback}"
        return "\n".join(f"- {item}" for item in items)

    def render_sublist(items: list[str]) -> str:
        if not items:
            return "  - 无"
        return "\n".join(f"  - {item}" for item in items)

    return "\n".join(
        [
            f"# Chapter Summary: {chapter_id}",
            "",
            "## One-Line Summary",
            f"- {one_line or '待补充'}",
            "",
            "## Major Beats",
            render_list(major_beats),
            "",
            "## State Changes",
            render_list(state_changes),
            "",
            "## Open Loops",
            "- Opened:",
            render_sublist(opened),
            "- Advanced:",
            render_sublist(advanced),
            "- Resolved:",
            render_sublist(resolved),
            "",
            "## Carry Forward",
            render_list(carry_forward),
            "",
        ]
    )


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
        return init_workflow(project_root, args.chapter_id, args.chapter_title, args.dialogue_audit)
    if args.command == "check":
        return run_check(project_root, args.chapter_id, args.all)
    if args.command == "set-status":
        return set_status(project_root, args.chapter_id, args.status)
    if args.command == "archive":
        return archive(project_root, args.chapter_id)

    raise RuntimeError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
