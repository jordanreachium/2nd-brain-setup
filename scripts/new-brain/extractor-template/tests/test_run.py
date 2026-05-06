"""Sanity test for the extractor template's default markdown pass-through."""
from __future__ import annotations

from pathlib import Path

from code.run import extract


def test_extract_markdown_passthrough(tmp_path: Path):
    src = tmp_path / "in.md"
    src.write_text("# Hello\n\nbody\n", encoding="utf-8")
    out = tmp_path / "sub" / "out.md"
    extract(src, out)
    assert out.exists()
    assert "Hello" in out.read_text(encoding="utf-8")


def test_extract_strips_leading_frontmatter(tmp_path: Path):
    src = tmp_path / "in.md"
    src.write_text("---\ntitle: t\n---\n# Hello\n", encoding="utf-8")
    out = tmp_path / "out.md"
    extract(src, out)
    text = out.read_text(encoding="utf-8")
    assert "title: t" not in text
    assert "Hello" in text
