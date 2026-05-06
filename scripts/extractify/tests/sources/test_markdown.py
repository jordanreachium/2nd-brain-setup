from __future__ import annotations

from pathlib import Path
from lib.sources.markdown import extract


def test_passthrough_no_frontmatter(tmp_path: Path):
    f = tmp_path / "doc.md"
    f.write_text("# Hello\n\nBody text.\n", encoding="utf-8")
    assert extract(f) == "# Hello\n\nBody text.\n"


def test_strips_yaml_frontmatter(tmp_path: Path):
    f = tmp_path / "doc.md"
    f.write_text(
        "---\n"
        "url: https://example.com\n"
        "fetched_at: 2026-04-25\n"
        "---\n"
        "\n"
        "# Body Heading\n"
        "\n"
        "Content here.\n",
        encoding="utf-8",
    )
    assert extract(f) == "# Body Heading\n\nContent here.\n"


def test_malformed_frontmatter_passes_through(tmp_path: Path):
    f = tmp_path / "doc.md"
    f.write_text("---\nbroken\n# Body\n", encoding="utf-8")
    assert extract(f) == "---\nbroken\n# Body\n"


def test_crlf_frontmatter(tmp_path: Path):
    f = tmp_path / "doc.md"
    f.write_text("---\r\ntitle: x\r\n---\r\nBody\r\n", encoding="utf-8")
    out = extract(f)
    assert "title:" not in out
    assert "Body" in out
