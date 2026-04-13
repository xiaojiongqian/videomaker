#!/usr/bin/env python3
"""Prepare a GitHub Pages bundle from the host/ directory.

This script copies host/ to an output directory, rewrites markdown/cover paths
in content-index.json to deploy-safe paths under ./content/, and copies the
referenced markdown/assets into that content/ tree.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from xml.sax.saxutils import escape

ABSOLUTE_REF = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", re.IGNORECASE)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
ASSET_REF = re.compile(r'(?P<prefix>\b(?:href|src)=["\'])(?P<path>(?:\./)?assets/[^"\']+)(?P<suffix>["\'])')
HEADING_LINE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
UL_LINE = re.compile(r"^\s*[-*+]\s+(.+?)\s*$")
OL_LINE = re.compile(r"^\s*\d+\.\s+(.+?)\s*$")
IMAGE_LINE = re.compile(r"^\s*!\[(.*?)\]\((.+?)\)\s*$")
INLINE_CODE = re.compile(r"`([^`]+)`")
INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INLINE_BOLD = re.compile(r"(?<!\\)\*\*(.+?)(?<!\\)\*\*")
INLINE_ITALIC = re.compile(r"(?<!\\)\*(?!\*)(.+?)(?<!\\)\*(?!\*)")
INLINE_HTML_TAG = re.compile(r"</?(?:strong|b|em|i|span)(?:\s+[^>]*?)?>", re.IGNORECASE)
SAFE_COLOR_VALUE = re.compile(r"^(#[0-9a-fA-F]{3,8}|[a-zA-Z]+)$")
TABLE_COLUMN_SPLIT = re.compile(r"(?<!\\)\|")
TABLE_SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")
CODE_FENCE_LINE = re.compile(r"^\s*```(?P<lang>[\w-]+)?(?:\s+.*)?\s*$")
FALLBACK_LIST_BLOCK = re.compile(
    r"(?P<start><!-- AUTO_FALLBACK_LIST_START -->)(?P<body>.*?)(?P<end><!-- AUTO_FALLBACK_LIST_END -->)",
    re.DOTALL,
)
FRONT_MATTER_BLOCK = re.compile(r"^---\r?\n[\s\S]*?\r?\n---\r?\n?")
DEFAULT_CHANNEL = "ai"
TYPE_LABELS = {
    "article": "文章",
    "video-note": "视频总结",
    "audio-note": "音频总结",
}
DEFAULT_LANGUAGE = "zh-CN"
ENGLISH_LANGUAGE = "en"
UI_STRINGS = {
    DEFAULT_LANGUAGE: {
        "channels": {
            "ai": "AI时代",
            "novel": "小说",
        },
        "skip_link": "跳到正文",
        "main_nav": "主导航",
        "toc_title": "目录",
        "toc_aria_label": "目录",
        "no_toc": "暂无目录",
        "intro_label": "文章简介",
        "post_nav_label": "上一篇下一篇",
        "no_more_content": "没有更多内容",
        "footer_template": "作者：Vik Qian · 版权所有 © 2026 {label}",
        "type_fallback": "未分类",
        "date_unknown": "日期未知",
        "novel_meta_label": "小说",
        "novel_chapter_fallback": "小说章节",
    },
    ENGLISH_LANGUAGE: {
        "channels": {
            "ai": "AI Era",
            "novel": "Novel",
        },
        "skip_link": "Skip to content",
        "main_nav": "Main navigation",
        "toc_title": "Contents",
        "toc_aria_label": "Table of contents",
        "no_toc": "No table of contents",
        "intro_label": "Chapter intro",
        "post_nav_label": "Previous and next chapters",
        "no_more_content": "No more content",
        "footer_template": "Author: Vik Qian · Copyright © 2026 {label}",
        "type_fallback": "Uncategorized",
        "date_unknown": "Unknown date",
        "novel_meta_label": "Novel",
        "novel_chapter_fallback": "Novel chapter",
    },
}


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


def strip_front_matter(markdown_text: str) -> str:
    match = FRONT_MATTER_BLOCK.match(markdown_text)
    return markdown_text[match.end():] if match else markdown_text


def normalize_channel(value: str) -> str:
    channel = value.strip()
    return channel or DEFAULT_CHANNEL


def get_item_channel(item: dict) -> str:
    return normalize_channel(str(item.get("channel", DEFAULT_CHANNEL)))


def normalize_language(value: str) -> str:
    language = value.strip().lower()
    return ENGLISH_LANGUAGE if language.startswith("en") else DEFAULT_LANGUAGE


def get_item_language(item: dict) -> str:
    return normalize_language(str(item.get("language", DEFAULT_LANGUAGE)))


def get_strings(language: str = DEFAULT_LANGUAGE) -> dict[str, str | dict[str, str]]:
    return UI_STRINGS.get(normalize_language(language), UI_STRINGS[DEFAULT_LANGUAGE])


def get_item_type_label(item: dict) -> str:
    type_label = str(item.get("typeLabel", "")).strip()
    if type_label:
        return type_label
    return TYPE_LABELS.get(str(item.get("type", "")).strip(), str(item.get("type", "")).strip() or "未分类")


def get_channel_label(channel: str, language: str = DEFAULT_LANGUAGE) -> str:
    strings = get_strings(language)
    channels = strings["channels"]
    return str(channels["novel"] if channel == "novel" else channels["ai"])


def get_novel_sequence_label(sequence_value: object, language: str = DEFAULT_LANGUAGE) -> str:
    if str(sequence_value).isdigit():
        if normalize_language(language) == ENGLISH_LANGUAGE:
            return f"Chapter {sequence_value}"
        return f"第{sequence_value}章"

    return str(get_strings(language)["novel_chapter_fallback"])


def get_channel_index_href(channel: str, relative_prefix: str = ".") -> str:
    base = f"{relative_prefix}/index.html"
    if channel == DEFAULT_CHANNEL:
        return base
    return f"{base}?channel={quote(channel, safe='')}"


def parse_markdown_h1(markdown_text: str) -> str:
    for line in strip_front_matter(markdown_text).splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def parse_summary_one_line(markdown_text: str) -> str:
    in_summary = False
    for line in strip_front_matter(markdown_text).splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_summary:
                break
            in_summary = stripped == "## One-Line Summary"
            continue

        if in_summary and stripped.startswith("- "):
            return stripped[2:].strip()

    return ""


def truncate_summary(text: str, limit: int = 220) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= limit:
        return normalized

    cut = normalized[: limit + 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    if len(cut) < int(limit * 0.6):
        cut = normalized[:limit]
    return cut.rstrip(" .,;:") + "..."


def parse_markdown_lead_paragraph(markdown_text: str) -> str:
    lines = strip_front_matter(markdown_text).splitlines()
    paragraph_lines: list[str] = []
    title_skipped = False
    in_code_block = False

    for raw_line in lines:
        fence_match = CODE_FENCE_LINE.match(raw_line)
        if fence_match:
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        stripped = raw_line.strip()
        if not stripped:
            if paragraph_lines:
                break
            continue

        if not title_skipped and stripped.startswith("# "):
            title_skipped = True
            continue

        if stripped.startswith("#") or stripped == "-------":
            if paragraph_lines:
                break
            continue

        if stripped.startswith(("- ", "* ", "+ ")) or OL_LINE.match(stripped):
            if paragraph_lines:
                break
            continue

        if IMAGE_LINE.match(stripped):
            if paragraph_lines:
                break
            continue

        paragraph_lines.append(stripped)

    return truncate_summary(" ".join(paragraph_lines))


def parse_project_snapshot_value(markdown_text: str, key: str) -> str:
    in_snapshot = False
    key_prefix = f"- {key}:"

    for line in strip_front_matter(markdown_text).splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_snapshot:
                break
            in_snapshot = stripped == "## Project Snapshot"
            continue

        if in_snapshot and stripped.startswith(key_prefix):
            return stripped[len(key_prefix) :].strip()

    return ""


def parse_chapter_sequence(chapter_id: str, fallback: int) -> int:
    match = re.search(r"(\d+)", chapter_id)
    if match:
        return int(match.group(1))
    return fallback


def build_story_site_items(repo_root: Path) -> list[dict]:
    stories_root = repo_root / "stories"
    if not stories_root.exists():
        return []

    items: list[dict] = []

    for config_path in sorted(stories_root.glob("*/site.json")):
        config = json.loads(config_path.read_text(encoding="utf-8"))
        series_root = config_path.parent
        channel = normalize_channel(str(config.get("channel", "novel")))
        type_value = str(config.get("type", series_root.name)).strip() or series_root.name
        topics = config.get("topic") if isinstance(config.get("topic"), list) else []
        chapters_dir = series_root / str(config.get("chaptersDir", "chapters"))
        summaries_dir = series_root / str(config.get("summariesDir", "summaries"))
        index_path = series_root / str(config.get("indexFile", "INDEX.md"))

        if not chapters_dir.exists():
            raise SystemExit(f"Chapters directory not found for site config: {chapters_dir}")
        if not index_path.exists():
            raise SystemExit(f"Index file not found for site config: {index_path}")

        project_index_text = index_path.read_text(encoding="utf-8")
        series_title = str(config.get("typeLabel", "")).strip() or parse_project_snapshot_value(project_index_text, "Title") or type_value
        default_summary = str(config.get("seriesSummary", "")).strip() or parse_project_snapshot_value(project_index_text, "Premise")

        chapter_ids = config.get("publishedChapters")
        if isinstance(chapter_ids, list) and chapter_ids:
            published_chapters = [str(chapter_id).strip() for chapter_id in chapter_ids if str(chapter_id).strip()]
        else:
            published_chapters = [path.stem for path in sorted(chapters_dir.glob("CH*.md"))]

        for fallback_sequence, chapter_id in enumerate(published_chapters, start=1):
            chapter_path = chapters_dir / f"{chapter_id}.md"
            if not chapter_path.exists():
                raise SystemExit(f"Published chapter not found: {chapter_path}")

            chapter_text = chapter_path.read_text(encoding="utf-8")
            chapter_title = parse_markdown_h1(chapter_text) or chapter_id
            summary_path = summaries_dir / f"{chapter_id}.summary.md"
            chapter_summary = ""
            if summary_path.exists():
                chapter_summary = parse_summary_one_line(summary_path.read_text(encoding="utf-8"))
            if not chapter_summary:
                chapter_summary = parse_markdown_lead_paragraph(chapter_text)

            items.append(
                {
                    "id": f"{type_value}-{chapter_id.lower()}",
                    "title": chapter_title,
                    "type": type_value,
                    "typeLabel": series_title,
                    "topic": topics,
                    "summary": chapter_summary or default_summary or chapter_title,
                    "source": f"../{chapter_path.relative_to(repo_root).as_posix()}",
                    "status": "published",
                    "channel": channel,
                    "language": normalize_language(str(config.get("language", DEFAULT_LANGUAGE))),
                    "sequence": parse_chapter_sequence(chapter_id, fallback_sequence),
                    "chapterId": chapter_id,
                    "seriesTitle": series_title,
                }
            )

    return items


def ensure_unique_item_ids(items: list[dict]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for item in items:
        item_id = str(item.get("id", "")).strip()
        if not item_id:
            continue
        if item_id in seen:
            duplicates.add(item_id)
        seen.add(item_id)

    if duplicates:
        duplicate_text = ", ".join(sorted(duplicates))
        raise SystemExit(f"Duplicate content ids found: {duplicate_text}")


def sort_items_for_channel(items: list[dict], channel: str) -> list[dict]:
    relevant = [item for item in items if get_item_channel(item) == channel and item.get("status") == "published" and item.get("id")]

    if channel == "novel":
        return sorted(
            relevant,
            key=lambda item: (
                str(item.get("typeLabel") or item.get("seriesTitle") or item.get("type") or ""),
                int(item.get("sequence")) if str(item.get("sequence", "")).isdigit() else 10**9,
                str(item.get("title", "")),
            ),
        )

    return sorted(
        relevant,
        key=lambda item: (str(item.get("date") or item.get("updatedAt") or ""), str(item.get("title", ""))),
        reverse=True,
    )


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
    items.extend(build_story_site_items(repo_root))
    ensure_unique_item_ids(items)

    host_root = repo_root / "host"

    for item in items:
        item["channel"] = get_item_channel(item)
        item_id = str(item.get("id", "")).strip()
        if item_id:
            item["page"] = f"./post/{quote(item_id, safe='')}.html"

        source_ref = item.get("source", "")
        source_context = host_root / "post.html"
        rewritten_source = copy_ref_to_content(source_ref, source_context, repo_root, out_root)

        if rewritten_source:
            item["source"] = rewritten_source
            source_file = (source_context.parent / source_ref).resolve()
            markdown_text = strip_front_matter(source_file.read_text(encoding="utf-8"))

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


def slugify_heading(value: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", value.strip().lower(), flags=re.UNICODE)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "section"


def resolve_local_href(target: str, source_file: Path, page_dir: Path, out_root: Path) -> str:
    value = target.strip()
    if not value or ABSOLUTE_REF.match(value):
        return value

    parsed = urlsplit(value)
    file_path = unquote(parsed.path)
    resolved = (source_file.parent / file_path).resolve()
    if not resolved.exists():
        return value

    rel_to_page = Path(os.path.relpath(resolved, page_dir)).as_posix()
    rebuilt = urlunsplit(("", "", rel_to_page, parsed.query, parsed.fragment))
    return rebuilt


def sanitize_inline_html_tag(raw_tag: str) -> str | None:
    close_match = re.fullmatch(r"</\s*(strong|b|em|i|span)\s*>", raw_tag, flags=re.IGNORECASE)
    if close_match:
        return f"</{close_match.group(1).lower()}>"

    open_match = re.fullmatch(r"<\s*(strong|b|em|i|span)(?P<attrs>\s+[^>]*)?>", raw_tag, flags=re.IGNORECASE)
    if not open_match:
        return None

    tag_name = open_match.group(1).lower()
    attrs = (open_match.group("attrs") or "").strip()
    if not attrs:
        return f"<{tag_name}>"

    style_match = re.fullmatch(r"""style\s*=\s*(["'])(.*?)\1""", attrs, flags=re.IGNORECASE | re.DOTALL)
    if not style_match:
        return f"<{tag_name}>"

    style_value = style_match.group(2).strip()
    color_match = re.fullmatch(r"color\s*:\s*([^;]+)\s*;?", style_value, flags=re.IGNORECASE)
    if not color_match:
        return f"<{tag_name}>"

    color_value = color_match.group(1).strip()
    if not SAFE_COLOR_VALUE.fullmatch(color_value):
        return f"<{tag_name}>"

    safe_color = html.escape(color_value, quote=True)
    return f'<{tag_name} style="color:{safe_color};">'


def preserve_allowed_inline_html(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}

    def replace_tag(match: re.Match[str]) -> str:
        safe_tag = sanitize_inline_html_tag(match.group(0))
        if not safe_tag:
            return match.group(0)
        token = f"__INLINE_HTML_TOKEN_{len(placeholders)}__"
        placeholders[token] = safe_tag
        return token

    rewritten = INLINE_HTML_TAG.sub(replace_tag, text)
    return rewritten, placeholders


def render_inline_text(text: str, source_file: Path, page_dir: Path, out_root: Path) -> str:
    text_with_tokens, html_tokens = preserve_allowed_inline_html(text)
    escaped = html.escape(text_with_tokens)

    code_tokens: dict[str, str] = {}

    def replace_code(match: re.Match[str]) -> str:
        token = f"__INLINE_CODE_TOKEN_{len(code_tokens)}__"
        code_tokens[token] = f"<code>{match.group(1)}</code>"
        return token

    escaped = INLINE_CODE.sub(replace_code, escaped)
    escaped = INLINE_BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", escaped)
    escaped = INLINE_ITALIC.sub(lambda m: f"<em>{m.group(1)}</em>", escaped)

    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        target = resolve_local_href(match.group(2), source_file, page_dir, out_root)
        href = html.escape(target, quote=True)
        return f'<a href="{href}">{label}</a>'

    rendered = INLINE_LINK.sub(replace_link, escaped)

    for token, content in code_tokens.items():
        rendered = rendered.replace(token, content)

    for token, tag in html_tokens.items():
        rendered = rendered.replace(token, tag)

    return rendered


def parse_table_cells(line: str) -> list[str]:
    raw = line.strip()
    if "|" not in raw:
        return []
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    if "|" not in raw and not raw.strip():
        return []
    cells = [cell.replace(r"\|", "|").strip() for cell in TABLE_COLUMN_SPLIT.split(raw)]
    return cells


def is_table_separator_row(line: str, expected_cols: int) -> bool:
    cells = parse_table_cells(line)
    if len(cells) != expected_cols:
        return False
    return all(TABLE_SEPARATOR_CELL.fullmatch(cell.replace(" ", "")) for cell in cells)


def table_alignments(line: str, expected_cols: int) -> list[str | None]:
    cells = parse_table_cells(line)
    if len(cells) != expected_cols:
        return [None] * expected_cols

    alignments: list[str | None] = []
    for cell in cells:
        marker = cell.replace(" ", "")
        left = marker.startswith(":")
        right = marker.endswith(":")
        if left and right:
            alignments.append("center")
        elif right:
            alignments.append("right")
        elif left:
            alignments.append("left")
        else:
            alignments.append(None)
    return alignments


def render_table_html(
    header_cells: list[str],
    body_rows: list[list[str]],
    alignments: list[str | None],
    source_file: Path,
    page_dir: Path,
    out_root: Path,
) -> str:
    rows: list[str] = ["<table>", "<thead>", "<tr>"]

    for index, cell in enumerate(header_cells):
        alignment = alignments[index] if index < len(alignments) else None
        attr = f' style="text-align:{alignment}"' if alignment else ""
        rendered = render_inline_text(cell, source_file, page_dir, out_root)
        rows.append(f"<th{attr}>{rendered}</th>")

    rows.extend(["</tr>", "</thead>"])

    if body_rows:
        rows.append("<tbody>")
        for row in body_rows:
            rows.append("<tr>")
            for index, cell in enumerate(row):
                alignment = alignments[index] if index < len(alignments) else None
                attr = f' style="text-align:{alignment}"' if alignment else ""
                rendered = render_inline_text(cell, source_file, page_dir, out_root)
                rows.append(f"<td{attr}>{rendered}</td>")
            rows.append("</tr>")
        rows.append("</tbody>")

    rows.append("</table>")
    return "\n".join(rows)


def render_code_block(code_text: str, language: str) -> str:
    lang = (language or "").strip().lower()
    escaped = html.escape(code_text)
    if lang == "mermaid":
        return f'<div class="mermaid">{escaped}</div>'
    return f"<pre><code>{escaped}</code></pre>"


def render_markdown_basic(markdown_text: str, source_file: Path, page_dir: Path, out_root: Path) -> tuple[str, list[dict]]:
    lines = markdown_text.splitlines()
    parts: list[str] = []
    toc: list[dict] = []
    id_counter: dict[str, int] = {}

    in_code = False
    code_language = ""
    code_lines: list[str] = []
    paragraph_lines: list[str] = []
    list_type: str | None = None

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines if line.strip())
        if text:
            parts.append(f"<p>{render_inline_text(text, source_file, page_dir, out_root)}</p>")
        paragraph_lines = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            parts.append(f"</{list_type}>")
            list_type = None

    index = 0
    while index < len(lines):
        stripped = lines[index].rstrip("\n")

        fence_match = CODE_FENCE_LINE.match(stripped)
        if fence_match:
            flush_paragraph()
            close_list()
            if in_code:
                parts.append(render_code_block("\n".join(code_lines), code_language))
                code_lines = []
                in_code = False
                code_language = ""
            else:
                in_code = True
                code_language = (fence_match.group("lang") or "").strip()
            index += 1
            continue

        if in_code:
            code_lines.append(stripped)
            index += 1
            continue

        if not stripped.strip():
            flush_paragraph()
            close_list()
            index += 1
            continue

        heading_match = HEADING_LINE.match(stripped)
        if heading_match:
            flush_paragraph()
            close_list()
            level = min(6, len(heading_match.group(1)))
            title = heading_match.group(2).strip()
            base_id = slugify_heading(title)
            count = id_counter.get(base_id, 0) + 1
            id_counter[base_id] = count
            final_id = base_id if count == 1 else f"{base_id}-{count}"
            if level in (2, 3):
                toc.append({"id": final_id, "text": title, "level": level})
            parts.append(f'<h{level} id="{html.escape(final_id, quote=True)}">{html.escape(title)}</h{level}>')
            index += 1
            continue

        image_match = IMAGE_LINE.match(stripped)
        if image_match:
            flush_paragraph()
            close_list()
            alt = html.escape(image_match.group(1))
            src = resolve_local_href(image_match.group(2), source_file, page_dir, out_root)
            parts.append(f'<p><img src="{html.escape(src, quote=True)}" alt="{alt}" loading="lazy" decoding="async" /></p>')
            index += 1
            continue

        ul_match = UL_LINE.match(stripped)
        if ul_match:
            flush_paragraph()
            if list_type != "ul":
                close_list()
                parts.append("<ul>")
                list_type = "ul"
            parts.append(f"<li>{render_inline_text(ul_match.group(1), source_file, page_dir, out_root)}</li>")
            index += 1
            continue

        ol_match = OL_LINE.match(stripped)
        if ol_match:
            flush_paragraph()
            if list_type != "ol":
                close_list()
                parts.append("<ol>")
                list_type = "ol"
            parts.append(f"<li>{render_inline_text(ol_match.group(1), source_file, page_dir, out_root)}</li>")
            index += 1
            continue

        if index + 1 < len(lines):
            header_cells = parse_table_cells(stripped)
            if len(header_cells) >= 2 and is_table_separator_row(lines[index + 1], len(header_cells)):
                flush_paragraph()
                close_list()
                alignments = table_alignments(lines[index + 1], len(header_cells))

                body_rows: list[list[str]] = []
                index += 2
                while index < len(lines):
                    row_line = lines[index].rstrip("\n")
                    if not row_line.strip():
                        break
                    row_cells = parse_table_cells(row_line)
                    if len(row_cells) != len(header_cells):
                        break
                    body_rows.append(row_cells)
                    index += 1

                parts.append(
                    render_table_html(header_cells, body_rows, alignments, source_file, page_dir, out_root)
                )
                continue

        paragraph_lines.append(stripped)
        index += 1

    flush_paragraph()
    close_list()
    if in_code:
        parts.append(render_code_block("\n".join(code_lines), code_language))

    return "\n".join(parts), toc


def build_post_static_html(
    item: dict,
    body_html: str,
    toc: list[dict],
    prev_item: dict | None,
    next_item: dict | None,
    asset_version: str,
) -> str:
    version = quote(asset_version, safe="") if asset_version else ""
    suffix = f"?v={version}" if version else ""
    channel = get_item_channel(item)
    language = get_item_language(item)
    strings = get_strings(language)
    channel_label = get_channel_label(channel, language)
    brand_href = get_channel_index_href(channel, "..")
    ai_href = get_channel_index_href(DEFAULT_CHANNEL, "..")
    novel_href = get_channel_index_href("novel", "..")
    ai_current = ' aria-current="page"' if channel == DEFAULT_CHANNEL else ""
    novel_current = ' aria-current="page"' if channel == "novel" else ""

    def asset(path: str) -> str:
        return f"{path}{suffix}"

    toc_html = "\n".join(
        f'<li data-level="{entry["level"]}"><a href="#{html.escape(entry["id"], quote=True)}">{html.escape(entry["text"])}</a></li>'
        for entry in toc
        if entry["level"] == 2
    )
    if not toc_html:
        toc_html = f'<li class="muted">{html.escape(str(strings["no_toc"]))}</li>'

    def nav_link(prefix: str, suffix_text: str, nav_item: dict) -> str:
        href = nav_item.get("page") or f'./post.html?id={quote(str(nav_item.get("id", "")), safe="")}'
        rel_href = href.replace("./", "../", 1)
        title_text = html.escape(str(nav_item.get("title", "")))
        return (
            f'<a class="chip" href="{html.escape(rel_href, quote=True)}">'
            f"{prefix}{title_text}{suffix_text}</a>"
        )

    nav_links: list[str] = []
    if prev_item:
        nav_links.append(nav_link("← ", "", prev_item))
    if next_item:
        nav_links.append(nav_link("", " →", next_item))
    nav_html = (
        "".join(nav_links)
        if nav_links
        else f'<span class="muted">{html.escape(str(strings["no_more_content"]))}</span>'
    )

    topics = item.get("topic") or []
    topic_text = " / ".join(topics) if isinstance(topics, list) and topics else str(strings["type_fallback"])
    type_label = html.escape(get_item_type_label(item))
    if channel == "novel":
        sequence_text = get_novel_sequence_label(item.get("sequence"), language)
        post_meta = f'{html.escape(str(strings["novel_meta_label"]))} · {type_label} · {html.escape(sequence_text)}'
    else:
        date_value = item.get("date") or item.get("updatedAt") or str(strings["date_unknown"])
        post_meta = f"{type_label} · {html.escape(str(date_value))} · {html.escape(topic_text)}"
    summary = html.escape(str(item.get("summary", "")))
    title = html.escape(str(item.get("title", "未命名内容")))

    return f"""<!doctype html>
<html lang="{language}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} - {channel_label}</title>
    <meta name="description" content="{summary or title}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{title} - {channel_label}" />
    <meta property="og:description" content="{summary or title}" />
    <meta name="twitter:card" content="summary" />
    <link rel="stylesheet" href="{asset('../assets/css/theme.css')}" />
    <link rel="stylesheet" href="{asset('../assets/css/base.css')}" />
    <link rel="stylesheet" href="{asset('../assets/css/components.css')}" />
  </head>
  <body data-page="post-static">
    <a class="skip-link" href="#main-content">{html.escape(str(strings["skip_link"]))}</a>
    <header class="site-header">
      <div class="container site-header__inner">
        <a id="siteBrand" class="brand" href="{brand_href}">{channel_label}</a>
        <nav class="nav" aria-label="{html.escape(str(strings["main_nav"]))}">
          <a id="navAi"{ai_current} href="{ai_href}">{html.escape(get_channel_label(DEFAULT_CHANNEL, language))}</a>
          <a id="navNovel"{novel_current} href="{novel_href}">{html.escape(get_channel_label("novel", language))}</a>
        </nav>
      </div>
    </header>
    <main id="main-content">
      <section class="section section--compact">
        <div class="container post-layout">
          <aside class="toc" aria-label="{html.escape(str(strings["toc_aria_label"]))}">
            <h2>{html.escape(str(strings["toc_title"]))}</h2>
            <ul id="tocList">{toc_html}</ul>
          </aside>
          <div class="toc-resizer" aria-hidden="true"></div>
          <article class="post" aria-labelledby="post-title">
            <header class="post-intro-panel" aria-label="{html.escape(str(strings["intro_label"]))}">
              <p id="postMeta" class="muted">{post_meta}</p>
              <h1 id="post-title">{title}</h1>
              <p id="postSummary" class="post-intro-summary muted">{summary}</p>
            </header>
            <div id="postContent" class="stack">{body_html}</div>
            <nav aria-label="{html.escape(str(strings["post_nav_label"]))}" class="chips" id="postNav">{nav_html}</nav>
          </article>
        </div>
      </section>
    </main>
    <footer class="site-footer">
      <div class="container">
        <p id="siteFooterText">{html.escape(str(strings["footer_template"]).replace("{label}", channel_label))}</p>
      </div>
    </footer>
    <script type="module" src="{asset('../assets/js/post-static.js')}"></script>
  </body>
</html>
"""


def write_static_post_pages(out_root: Path, items: list[dict], asset_version: str) -> None:
    post_dir = out_root / "post"
    post_dir.mkdir(parents=True, exist_ok=True)
    channels = sorted({get_item_channel(item) for item in items if item.get("status") == "published"})

    for channel in channels:
        published_items = sort_items_for_channel(items, channel)

        for item in published_items:
            source_ref = str(item.get("source", "")).strip()
            if not source_ref:
                continue

            source_path = (out_root / source_ref.lstrip("./")).resolve()
            if not source_path.exists():
                continue

            markdown_text = strip_front_matter(source_path.read_text(encoding="utf-8"))
            body_html, toc = render_markdown_basic(markdown_text, source_path, post_dir, out_root)
            nav_items = published_items
            if channel == "novel" and item.get("type"):
                nav_items = [candidate for candidate in published_items if candidate.get("type") == item.get("type")]

            nav_index = nav_items.index(item) if item in nav_items else -1
            prev_item = nav_items[nav_index - 1] if nav_index > 0 else None
            next_item = nav_items[nav_index + 1] if 0 <= nav_index < len(nav_items) - 1 else None
            page_html = build_post_static_html(item, body_html, toc, prev_item, next_item, asset_version)
            output_path = post_dir / f'{quote(str(item["id"]), safe="")}.html'
            output_path.write_text(page_html, encoding="utf-8")


def inject_post_fallback_list(out_root: Path, items: list[dict]) -> None:
    post_html_path = out_root / "post.html"
    if not post_html_path.exists():
        return

    entries: list[str] = []
    for channel in sorted({get_item_channel(item) for item in items if item.get("status") == "published"}):
        for item in sort_items_for_channel(items, channel):
            item_id = str(item.get("id", "")).strip()
            if not item_id:
                continue

            title = html.escape(str(item.get("title", item_id)))
            summary = html.escape(str(item.get("summary", "")))
            href = item.get("page") or f"./post/{quote(item_id, safe='')}.html"
            entries.append(
                f'<li><a href="{html.escape(str(href), quote=True)}">{title}</a>'
                + (f'<span class="muted"> · {summary}</span>' if summary else "")
                + "</li>"
            )

    if not entries:
        return

    text = post_html_path.read_text(encoding="utf-8")
    replacement = (
        "<!-- AUTO_FALLBACK_LIST_START -->\n"
        "                <ul id=\"postFallbackList\">\n"
        + "\n".join(f"                  {entry}" for entry in entries)
        + "\n                </ul>\n"
        "                <!-- AUTO_FALLBACK_LIST_END -->"
    )
    rewritten = FALLBACK_LIST_BLOCK.sub(replacement, text)
    if rewritten != text:
        post_html_path.write_text(rewritten, encoding="utf-8")


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
    channels = sorted({get_item_channel(item) for item in items if item.get("status") == "published"})
    for channel in channels:
        if channel == DEFAULT_CHANNEL:
            continue
        entries.append(f"{site_url}/index.html?channel={quote(channel, safe='')}")

    for item in items:
        item_id = item.get("id", "")
        if not item_id:
            continue
        page_ref = str(item.get("page", "")).strip()
        if page_ref:
            page_path = page_ref.lstrip("./")
            entries.append(f"{site_url}/{page_path}")
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
    write_static_post_pages(out_root, items, args.asset_version)
    inject_post_fallback_list(out_root, items)
    append_asset_version_to_html(out_root, args.asset_version)
    write_robots(out_root, site_url)
    write_sitemap(out_root, site_url, items)

    print(f"Prepared Pages bundle: {out_root}")
    print(f"Content items: {len(items)}")


if __name__ == "__main__":
    main()
