#!/usr/bin/env python3
"""Local preview server with simple extensionless HTML fallback."""

from __future__ import annotations

import argparse
import posixpath
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve static preview with HTML fallback")
    parser.add_argument("--port", type=int, default=8001, help="Port number")
    parser.add_argument("--dir", default="_site", help="Directory to serve")
    return parser.parse_args()


class PreviewHandler(SimpleHTTPRequestHandler):
    def _with_html_fallback(self, raw_path: str) -> str:
        parsed = urlsplit(raw_path)
        clean_path = posixpath.normpath(unquote(parsed.path))

        if clean_path.endswith("/") or "." in clean_path.rsplit("/", 1)[-1]:
            return raw_path

        candidate = clean_path + ".html"
        target = Path(self.directory) / candidate.lstrip("/")
        if target.is_file():
            return urlunsplit(("", "", candidate, parsed.query, parsed.fragment))
        return raw_path

    def send_head(self):  # type: ignore[override]
        parsed = urlsplit(self.path)
        if parsed.path == "/favicon.ico":
            favicon = Path(self.directory) / "favicon.ico"
            if not favicon.is_file():
                self.send_response(204)
                self.end_headers()
                return None

        original = self.path
        self.path = self._with_html_fallback(self.path)
        try:
            return super().send_head()
        finally:
            self.path = original


def main() -> None:
    args = parse_args()
    directory = str(Path(args.dir).resolve())
    handler = lambda *h_args, **h_kwargs: PreviewHandler(*h_args, directory=directory, **h_kwargs)
    with ThreadingHTTPServer(("", args.port), handler) as server:
        print(f"Serving HTTP on :: port {args.port} (http://[::]:{args.port}/) ...")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
