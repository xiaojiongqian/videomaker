#!/usr/bin/env python3
"""Sync the shared novel-system reference bundle to all novel skills."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


DEFAULT_SOURCE_SKILL = "novel-orchestrator-main"
SKILL_PREFIX = "novel-"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync shared novel-system references across novel skills.")
    parser.add_argument(
        "--skills-root",
        default=".agents/skills",
        help="Root directory that contains novel skill folders",
    )
    parser.add_argument(
        "--source-skill",
        default=DEFAULT_SOURCE_SKILL,
        help="Canonical skill folder to copy references from",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned operations without copying files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skills_root = Path(args.skills_root).resolve()
    source_dir = skills_root / args.source_skill / "references" / "novel-system"
    if not source_dir.exists():
        print(f"FAIL: source novel-system bundle not found: {source_dir}")
        return 1

    targets = []
    for path in sorted(skills_root.iterdir()):
        if not path.is_dir():
            continue
        if not path.name.startswith(SKILL_PREFIX):
            continue
        if path.name == args.source_skill:
            continue
        target_dir = path / "references" / "novel-system"
        if target_dir.exists():
            targets.append(target_dir)

    if not targets:
        print("FAIL: no target novel skill bundles found")
        return 1

    for target_dir in targets:
        if args.dry_run:
            print(f"DRY-RUN: sync {source_dir} -> {target_dir}")
            continue
        shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)
        print(f"SYNCED: {target_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
