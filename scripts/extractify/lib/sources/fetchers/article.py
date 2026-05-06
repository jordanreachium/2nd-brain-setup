"""Fetch a web article and save it as clean markdown.

CLI (run from scripts/extractify/):
    python -m lib.sources.fetchers.article <url> [<url>...] --out DIR

Uses readability-lxml to extract article body, then markdownify to convert
to markdown. Writes `<slug>.md` with YAML frontmatter (url, title,
fetched_at, word_count) to --out (default ./_raw/articles).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def slugify(text: str) -> str:
    if text.startswith("http"):
        parsed = urlparse(text)
        segments = [s for s in parsed.path.split("/") if s]
        if segments:
            text = segments[-1]
    text = text.lower()
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _clean_body(body_md: str) -> str:
    """Clean markdown body: normalize CRLF to LF, collapse multiple blank lines.

    Pages with \\r\\n line endings keep extra blank runs because the \\n{3,}
    regex doesn't match \\r\\n\\r\\n\\r\\n. Replace CRLF with LF first, then
    collapse.
    """
    body_md = body_md.replace("\r\n", "\n")
    body_md = re.sub(r"\n{3,}", "\n\n", body_md)
    return body_md.strip()


def html_to_markdown(html: str) -> tuple[str, str]:
    """Returns (markdown_body, title)."""
    from bs4 import BeautifulSoup
    from readability import Document
    from markdownify import markdownify as md_convert

    doc = Document(html)
    title = doc.title()
    body_html = doc.summary()
    soup = BeautifulSoup(body_html, "html.parser")
    for tag in soup.find_all(["nav", "header", "footer", "aside", "script", "style"]):
        tag.decompose()
    body_html = str(soup)
    body_md = md_convert(body_html, heading_style="ATX", strip=["a", "img"])
    body_md = _clean_body(body_md)
    return body_md, title


def _build_output(url: str, title: str, body: str, fetched_at: str) -> str:
    word_count = len(body.split())
    return (
        "---\n"
        f"url: {url}\n"
        f"title: {json.dumps(title)}\n"
        f"fetched_at: {fetched_at}\n"
        f"word_count: {word_count}\n"
        "---\n\n"
        f"{body}\n"
    )


def fetch_one(url: str, out_dir: Path) -> Path:
    import requests

    out_dir.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (brain-ingest)",
    })
    resp.raise_for_status()
    body_md, title = html_to_markdown(resp.text)
    fetched_at = datetime.now(timezone.utc).isoformat()
    doc = _build_output(url, title, body_md, fetched_at)
    slug = slugify(url)
    path = out_dir / f"{slug}.md"
    path.write_text(doc, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch web article as markdown.")
    parser.add_argument("urls", nargs="+", help="Article URLs")
    parser.add_argument("--out", type=Path, default=Path("_raw/articles"),
                        help="Output dir (default: ./_raw/articles)")
    args = parser.parse_args()

    for url in args.urls:
        print(f"[fetch_article] {url}")
        path = fetch_one(url, args.out)
        print(f"  -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
