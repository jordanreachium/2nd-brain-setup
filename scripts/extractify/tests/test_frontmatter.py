from __future__ import annotations
from pathlib import Path

from lib.frontmatter import read, write


def test_read_roundtrip(tmp_path: Path):
    p = tmp_path / "note.md"
    p.write_text(
        "---\n"
        "source_kind: book\n"
        "content_hash: sha256:abc\n"
        "---\n"
        "Body line one.\nBody line two.\n",
        encoding="utf-8",
    )
    fm, body = read(p)
    assert fm == {"source_kind": "book", "content_hash": "sha256:abc"}
    assert body == "Body line one.\nBody line two.\n"


def test_read_no_frontmatter(tmp_path: Path):
    p = tmp_path / "note.md"
    p.write_text("Just body text.\n", encoding="utf-8")
    fm, body = read(p)
    assert fm == {}
    assert body == "Just body text.\n"


def test_write_new_file(tmp_path: Path):
    p = tmp_path / "out.md"
    write(p, {"source_kind": "transcript", "topic": "offers"}, "Body.\n")
    text = p.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "source_kind: transcript" in text
    assert "topic: offers" in text
    assert text.endswith("Body.\n")


def test_write_roundtrip(tmp_path: Path):
    p = tmp_path / "out.md"
    original_fm = {"a": 1, "b": "two"}
    original_body = "Hello.\n"
    write(p, original_fm, original_body)
    fm, body = read(p)
    assert fm == original_fm
    assert body == original_body


def test_read_only_frontmatter_no_body(tmp_path: Path):
    p = tmp_path / "meta.md"
    p.write_text("---\nkey: value\n---\n", encoding="utf-8")
    fm, body = read(p)
    assert fm == {"key": "value"}
    assert body == ""
