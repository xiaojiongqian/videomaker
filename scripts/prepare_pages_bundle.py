#!/usr/bin/env python3
"""Prepare a GitHub Pages bundle from the host/ directory.

This script copies host/ to an output directory, rewrites markdown/cover paths
in content-index.json to deploy-safe paths under ./content/, and copies the
referenced markdown/assets into that content/ tree.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from xml.sax.saxutils import escape

ABSOLUTE_REF = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", re.IGNORECASE)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
ASSET_REF = re.compile(r'(?P<prefix>\b(?:href|src)=["\'])(?P<path>(?:\./)?assets/[^"\']+)(?P<suffix>["\'])')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare deploy-ready Pages bundle")
    parser.add_argument("--src", default="host", help="Source host directory")
    parser.add_argument("--out", default="_site", help="Output bundle directory")
    parser.add_argument("--site-url", default="", help="Public site URL for sitemap/robots")
    parser.add_argument(
        "--asset-version",
        default="",
        help="Optional cache-busting version appended to local CSS/JS assets in HTML",
    )
    return parser.parse_args()


def is_relative_local_ref(raw: str) -> bool:
    value = raw.strip()
    if not value:
        return False
    if ABSOLUTE_REF.match(value):
        return False

    parsed = urlsplit(value)
    path = unquote(parsed.path)
    if not path or path.startswith("/"):
        return False

    return True


def clean_markdown_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()

    if ' "' in target:
        target = target.split(' "', 1)[0]
    elif " '" in target:
        target = target.split(" '", 1)[0]

    return target.strip()


def copy_ref_to_content(
    ref: str,
    context_file: Path,
    repo_root: Path,
    out_root: Path,
) -> str | None:
    if not is_relative_local_ref(ref):
        return None

    parsed = urlsplit(ref)
    ref_path = unquote(parsed.path)
    source_path = (context_file.parent / ref_path).resolve()

    if not source_path.exists() or not source_path.is_file():
        return None

    rel = source_path.relative_to(repo_root)
    dest_path = out_root / "content" / rel
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, dest_path)

    rewritten = Path("content") / rel
    new_path = f"./{rewritten.as_posix()}"

    rebuilt = urlunsplit(("", "", new_path, parsed.query, parsed.fragment))
    return rebuilt


def extract_markdown_local_refs(markdown_text: str) -> Iterable[str]:
    for match in MARKDOWN_LINK.finditer(markdown_text):
        raw_target = match.group(1)
        if not raw_target:
            continue
        target = clean_markdown_target(raw_target)
        if is_relative_local_ref(target):
            yield target


def rewrite_index_and_copy_content(out_root: Path, repo_root: Path) -> list[dict]:
    index_path = out_root / "data" / "content-index.json"
    items = json.loads(index_path.read_text(encoding="utf-8"))

    host_root = repo_root / "host"

    for item in items:
        source_ref = item.get("source", "")
        source_context = host_root / "post.html"
        rewritten_source = copy_ref_to_content(source_ref, source_context, repo_root, out_root)

        if rewritten_source:
            item["source"] = rewritten_source
            source_file = (source_context.parent / source_ref).resolve()
            markdown_text = source_file.read_text(encoding="utf-8")

            for md_ref in extract_markdown_local_refs(markdown_text):
                copy_ref_to_content(md_ref, source_file, repo_root, out_root)

        cover_ref = item.get("cover", "")
        if cover_ref:
            cover_context = host_root / "index.html"
            rewritten_cover = copy_ref_to_content(cover_ref, cover_context, repo_root, out_root)
            if rewritten_cover:
                item["cover"] = rewritten_cover

    index_path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return items


def append_asset_version_to_html(out_root: Path, asset_version: str) -> None:
    version = asset_version.strip()
    if not version:
        return

    html_files = list(out_root.glob("*.html"))

    for html_path in html_files:
        text = html_path.read_text(encoding="utf-8")

        def _replace(match: re.Match[str]) -> str:
            raw_path = match.group("path")
            if not raw_path.endswith((".css", ".js")):
                return match.group(0)
            if "v=" in raw_path:
                return match.group(0)

            separator = "&" if "?" in raw_path else "?"
            updated = f"{raw_path}{separator}v={quote(version, safe='')}"
            return f'{match.group("prefix")}{updated}{match.group("suffix")}'

        rewritten = ASSET_REF.sub(_replace, text)
        if rewritten != text:
            html_path.write_text(rewritten, encoding="utf-8")


def normalize_site_url(site_url: str) -> str:
    return site_url.strip().rstrip("/")


def write_robots(out_root: Path, site_url: str) -> None:
    lines = ["User-agent: *", "Allow: /"]
    if site_url:
        lines.append(f"Sitemap: {site_url}/sitemap.xml")
    (out_root / "robots.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sitemap(out_root: Path, site_url: str, items: list[dict]) -> None:
    if not site_url:
        return

    entries = [f"{site_url}/", f"{site_url}/index.html"]
    for item in items:
        item_id = item.get("id", "")
        if not item_id:
            continue
        entries.append(f"{site_url}/post.html?id={quote(str(item_id), safe='')}")

    unique_entries = list(dict.fromkeys(entries))

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for url in unique_entries:
        body.append("  <url>")
        body.append(f"    <loc>{escape(url)}</loc>")
        body.append("  </url>")

    body.append("</urlset>")
    (out_root / "sitemap.xml").write_text("\n".join(body) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    src_root = (repo_root / args.src).resolve()
    out_root = (repo_root / args.out).resolve()
    site_url = normalize_site_url(args.site_url)

    if not src_root.exists() or not src_root.is_dir():
        raise SystemExit(f"Source directory not found: {src_root}")

    if out_root.exists():
        shutil.rmtree(out_root)

    shutil.copytree(src_root, out_root)

    items = rewrite_index_and_copy_content(out_root, repo_root)
    append_asset_version_to_html(out_root, args.asset_version)
    write_robots(out_root, site_url)
    write_sitemap(out_root, site_url, items)

    print(f"Prepared Pages bundle: {out_root}")
    print(f"Content items: {len(items)}")


if __name__ == "__main__":
    main()
