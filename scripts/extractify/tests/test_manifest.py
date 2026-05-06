from __future__ import annotations
from pathlib import Path

from lib.manifest import empty_manifest, load, save, upsert_entry, ManifestEntry


def test_empty_manifest_shape():
    m = empty_manifest()
    assert m == {"version": 1, "entries": {}}


def test_load_missing_file_returns_empty(tmp_path: Path):
    assert load(tmp_path / "missing.json") == empty_manifest()


def test_save_load_roundtrip(tmp_path: Path):
    p = tmp_path / "manifest.json"
    m = empty_manifest()
    m["entries"]["_pipeline/books/a.md"] = {
        "source_path": "_raw/books/a.pdf",
        "source_kind": "book",
        "extracted_at": "2026-04-24T10:00:00Z",
        "content_hash": "sha256:abc",
    }
    save(p, m)
    loaded = load(p)
    assert loaded == m


def test_upsert_entry_adds_new(tmp_path: Path):
    m = empty_manifest()
    entry = ManifestEntry(
        source_path="_raw/x.pdf",
        source_kind="book",
        extracted_at="2026-04-24T10:00:00Z",
        content_hash="sha256:xx",
    )
    upsert_entry(m, "_pipeline/x.md", entry)
    assert "_pipeline/x.md" in m["entries"]
    assert m["entries"]["_pipeline/x.md"]["content_hash"] == "sha256:xx"


def test_upsert_entry_updates_existing(tmp_path: Path):
    m = empty_manifest()
    m["entries"]["_pipeline/x.md"] = {
        "source_path": "_raw/x.pdf",
        "source_kind": "book",
        "extracted_at": "2026-04-24T10:00:00Z",
        "content_hash": "sha256:old",
    }
    entry = ManifestEntry(
        source_path="_raw/x.pdf",
        source_kind="book",
        extracted_at="2026-04-24T11:00:00Z",
        content_hash="sha256:new",
    )
    upsert_entry(m, "_pipeline/x.md", entry)
    assert m["entries"]["_pipeline/x.md"]["content_hash"] == "sha256:new"


def test_save_creates_parent_dir(tmp_path: Path):
    p = tmp_path / "deep/nested/manifest.json"
    save(p, empty_manifest())
    assert p.exists()
