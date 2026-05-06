from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

from lib.sources.fetchers.article import (
    slugify,
    html_to_markdown,
    fetch_one,
)

SAMPLE_HTML = """
<!doctype html>
<html><head><title>Article Title</title></head>
<body>
<nav>Skip me</nav>
<article>
  <h1>Article Title</h1>
  <p>First paragraph.</p>
  <p>Second paragraph.</p>
</article>
<footer>Skip me too</footer>
</body></html>
"""


def test_slugify_url():
    assert slugify("https://example.com/foo/bar-baz/") == "bar-baz"


def test_slugify_title():
    assert slugify("My Awesome Article!") == "my-awesome-article"


def test_html_to_markdown_extracts_body():
    body, title = html_to_markdown(SAMPLE_HTML)
    assert title == "Article Title"
    assert "First paragraph." in body
    assert "Second paragraph." in body
    assert "Skip me" not in body
    assert "Skip me too" not in body


def test_fetch_one_writes_markdown(tmp_path: Path):
    fake_resp = MagicMock()
    fake_resp.text = SAMPLE_HTML
    fake_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=fake_resp):
        out_path = fetch_one("https://example.com/foo/article-slug/", tmp_path)

    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "url: https://example.com/foo/article-slug/" in text
    assert 'title: "Article Title"' in text
    assert "First paragraph." in text


def test_clean_body_normalizes_crlf_before_blank_collapse():
    """Pages with \\r\\n line endings get CRLF→LF before \\n{3,} collapse."""
    from lib.sources.fetchers.article import _clean_body

    raw = "para1\r\n\r\n\r\n\r\npara2"
    cleaned = _clean_body(raw)
    assert "\r" not in cleaned, "CRLF should be normalized to LF"
    # Should collapse to two newlines between paragraphs (not five)
    assert cleaned.count("\n") <= 4, f"Expected <= 4 newlines, got {cleaned.count(chr(10))}: {repr(cleaned)}"
