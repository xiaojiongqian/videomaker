#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def replace_placeholders(text: str, chapter_id: str, chapter_title: str) -> str:
    return text.replace("CHXXX", chapter_id).replace("Chapter Title", chapter_title)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a Messi-series chapter workflow from the shared template."
    )
    parser.add_argument("chapter_id", help="Chapter id, for example CH021")
    parser.add_argument("chapter_title", help="Chapter title")
    parser.add_argument(
        "--dialogue-audit",
        action="store_true",
        help="Enable the optional dialogue audit in the generated manifest.",
    )
    args = parser.parse_args()

    workflow_root = Path(__file__).resolve().parent
    template_dir = workflow_root / "_template"
    target_dir = workflow_root / args.chapter_id

    if not template_dir.is_dir():
        raise SystemExit(f"Template directory not found: {template_dir}")
    if target_dir.exists():
        raise SystemExit(f"Target workflow already exists: {target_dir}")

    shutil.copytree(template_dir, target_dir)

    for path in sorted(target_dir.iterdir()):
        if not path.is_file():
            continue
        text = path.read_text()
        text = replace_placeholders(text, args.chapter_id, args.chapter_title)
        path.write_text(text)

    manifest_path = target_dir / "00-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["chapter_id"] = args.chapter_id
    manifest["chapter_title"] = args.chapter_title
    manifest["required_steps"]["dialogue_audit"] = bool(args.dialogue_audit)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    print(f"Initialized workflow: {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
