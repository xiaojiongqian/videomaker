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
FALLBACK_LIST_BLOCK = re.compile(
    r"(?P<start><!-- AUTO_FALLBACK_LIST_START -->)(?P<body>.*?)(?P<end><!-- AUTO_FALLBACK_LIST_END -->)",
    re.DOTALL,
)


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
        item_id = str(item.get("id", "")).strip()
        if item_id:
            item["page"] = f"./post/{quote(item_id, safe='')}.html"

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


def render_inline_text(text: str, source_file: Path, page_dir: Path, out_root: Path) -> str:
    escaped = html.escape(text)
    escaped = INLINE_CODE.sub(lambda m: f"<code>{html.escape(m.group(1))}</code>", escaped)

    def replace_link(match: re.Match[str]) -> str:
        label = html.escape(match.group(1))
        target = resolve_local_href(match.group(2), source_file, page_dir, out_root)
        href = html.escape(target, quote=True)
        return f'<a href="{href}">{label}</a>'

    return INLINE_LINK.sub(replace_link, escaped)


def render_markdown_basic(markdown_text: str, source_file: Path, page_dir: Path, out_root: Path) -> tuple[str, list[dict]]:
    lines = markdown_text.splitlines()
    parts: list[str] = []
    toc: list[dict] = []
    id_counter: dict[str, int] = {}

    in_code = False
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

    for line in lines:
        stripped = line.rstrip("\n")

        if stripped.strip().startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                code_html = html.escape("\n".join(code_lines))
                parts.append(f"<pre><code>{code_html}</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(stripped)
            continue

        if not stripped.strip():
            flush_paragraph()
            close_list()
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
            continue

        image_match = IMAGE_LINE.match(stripped)
        if image_match:
            flush_paragraph()
            close_list()
            alt = html.escape(image_match.group(1))
            src = resolve_local_href(image_match.group(2), source_file, page_dir, out_root)
            parts.append(f'<p><img src="{html.escape(src, quote=True)}" alt="{alt}" loading="lazy" decoding="async" /></p>')
            continue

        ul_match = UL_LINE.match(stripped)
        if ul_match:
            flush_paragraph()
            if list_type != "ul":
                close_list()
                parts.append("<ul>")
                list_type = "ul"
            parts.append(f"<li>{render_inline_text(ul_match.group(1), source_file, page_dir, out_root)}</li>")
            continue

        ol_match = OL_LINE.match(stripped)
        if ol_match:
            flush_paragraph()
            if list_type != "ol":
                close_list()
                parts.append("<ol>")
                list_type = "ol"
            parts.append(f"<li>{render_inline_text(ol_match.group(1), source_file, page_dir, out_root)}</li>")
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    close_list()
    if in_code:
        code_html = html.escape("\n".join(code_lines))
        parts.append(f"<pre><code>{code_html}</code></pre>")

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

    def asset(path: str) -> str:
        return f"{path}{suffix}"

    toc_html = "\n".join(
        f'<li data-level="{entry["level"]}"><a href="#{html.escape(entry["id"], quote=True)}">{html.escape(entry["text"])}</a></li>'
        for entry in toc
        if entry["level"] == 2
    )
    if not toc_html:
        toc_html = '<li class="muted">暂无目录</li>'

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
    nav_html = "".join(nav_links) if nav_links else '<span class="muted">没有更多内容</span>'

    topics = item.get("topic") or []
    topic_text = " / ".join(topics) if isinstance(topics, list) and topics else "未分类"
    date_value = item.get("date") or item.get("updatedAt") or "日期未知"
    post_meta = f'{html.escape(str(item.get("type", "article")))} · {html.escape(str(date_value))} · {html.escape(topic_text)}'
    summary = html.escape(str(item.get("summary", "")))
    title = html.escape(str(item.get("title", "未命名内容")))

    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} - AI时代</title>
    <meta name="description" content="{summary or title}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{title} - AI时代" />
    <meta property="og:description" content="{summary or title}" />
    <meta name="twitter:card" content="summary" />
    <link rel="stylesheet" href="{asset('../assets/css/theme.css')}" />
    <link rel="stylesheet" href="{asset('../assets/css/base.css')}" />
    <link rel="stylesheet" href="{asset('../assets/css/components.css')}" />
  </head>
  <body data-page="post-static">
    <a class="skip-link" href="#main-content">跳到正文</a>
    <header class="site-header">
      <div class="container site-header__inner">
        <a class="brand" href="../index.html">AI时代</a>
        <nav class="nav" aria-label="主导航">
          <a href="../index.html">首页</a>
          <a aria-current="page" href="#">详情页</a>
        </nav>
      </div>
    </header>
    <main id="main-content">
      <section class="section section--compact">
        <div class="container post-layout">
          <aside class="toc" aria-label="目录">
            <h2>目录</h2>
            <ul id="tocList">{toc_html}</ul>
          </aside>
          <article class="post" aria-labelledby="post-title">
            <header class="post-intro-panel" aria-label="文章简介">
              <p id="postMeta" class="muted">{post_meta}</p>
              <h1 id="post-title">{title}</h1>
              <p id="postSummary" class="post-intro-summary muted">{summary}</p>
            </header>
            <div id="postContent" class="stack">{body_html}</div>
            <nav aria-label="上一篇下一篇" class="chips" id="postNav">{nav_html}</nav>
          </article>
        </div>
      </section>
    </main>
    <footer class="site-footer">
      <div class="container">
        <p>作者：Vik Qian · 版权所有 © 2026 AI时代</p>
      </div>
    </footer>
  </body>
</html>
"""


def write_static_post_pages(out_root: Path, items: list[dict], asset_version: str) -> None:
    post_dir = out_root / "post"
    post_dir.mkdir(parents=True, exist_ok=True)
    published_items = [item for item in items if item.get("status") == "published" and item.get("id")]

    for index, item in enumerate(published_items):
        source_ref = str(item.get("source", "")).strip()
        if not source_ref:
            continue

        source_path = (out_root / source_ref.lstrip("./")).resolve()
        if not source_path.exists():
            continue

        markdown_text = source_path.read_text(encoding="utf-8")
        body_html, toc = render_markdown_basic(markdown_text, source_path, post_dir, out_root)
        prev_item = published_items[index - 1] if index > 0 else None
        next_item = published_items[index + 1] if index < len(published_items) - 1 else None
        page_html = build_post_static_html(item, body_html, toc, prev_item, next_item, asset_version)
        output_path = post_dir / f'{quote(str(item["id"]), safe="")}.html'
        output_path.write_text(page_html, encoding="utf-8")


def inject_post_fallback_list(out_root: Path, items: list[dict]) -> None:
    post_html_path = out_root / "post.html"
    if not post_html_path.exists():
        return

    entries: list[str] = []
    for item in items:
        if item.get("status") != "published":
            continue
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
