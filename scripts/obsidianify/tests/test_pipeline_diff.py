from __future__ import annotations

from lib.pipeline_diff import diff, DiffResult


def test_all_new():
    manifest_entries = {
        "_pipeline/a.md": {"content_hash": "sha256:a"},
        "_pipeline/b.md": {"content_hash": "sha256:b"},
    }
    state_entries: dict[str, dict] = {}
    r = diff(manifest_entries, state_entries)
    assert r == DiffResult(
        new=["_pipeline/a.md", "_pipeline/b.md"],
        changed=[],
        unchanged=[],
        removed=[],
    )


def test_all_unchanged():
    manifest_entries = {"_pipeline/a.md": {"content_hash": "sha256:a"}}
    state_entries = {"_pipeline/a.md": {"content_hash": "sha256:a"}}
    r = diff(manifest_entries, state_entries)
    assert r.unchanged == ["_pipeline/a.md"]
    assert r.new == []
    assert r.changed == []
    assert r.removed == []


def test_one_changed():
    manifest_entries = {"_pipeline/a.md": {"content_hash": "sha256:new"}}
    state_entries = {"_pipeline/a.md": {"content_hash": "sha256:old"}}
    r = diff(manifest_entries, state_entries)
    assert r.changed == ["_pipeline/a.md"]
    assert r.unchanged == []


def test_removed_entry():
    manifest_entries: dict[str, dict] = {}
    state_entries = {"_pipeline/a.md": {"content_hash": "sha256:a"}}
    r = diff(manifest_entries, state_entries)
    assert r.removed == ["_pipeline/a.md"]
    assert r.new == []


def test_mixed():
    manifest_entries = {
        "_pipeline/a.md": {"content_hash": "sha256:a"},          # unchanged
        "_pipeline/b.md": {"content_hash": "sha256:b-new"},       # changed
        "_pipeline/c.md": {"content_hash": "sha256:c"},          # new
    }
    state_entries = {
        "_pipeline/a.md": {"content_hash": "sha256:a"},
        "_pipeline/b.md": {"content_hash": "sha256:b-old"},
        "_pipeline/d.md": {"content_hash": "sha256:d"},          # removed
    }
    r = diff(manifest_entries, state_entries)
    assert sorted(r.new) == ["_pipeline/c.md"]
    assert sorted(r.changed) == ["_pipeline/b.md"]
    assert sorted(r.unchanged) == ["_pipeline/a.md"]
    assert sorted(r.removed) == ["_pipeline/d.md"]


def test_output_is_deterministically_sorted():
    manifest_entries = {
        "_pipeline/z.md": {"content_hash": "sha256:z"},
        "_pipeline/a.md": {"content_hash": "sha256:a"},
        "_pipeline/m.md": {"content_hash": "sha256:m"},
    }
    state_entries: dict[str, dict] = {}
    r = diff(manifest_entries, state_entries)
    assert r.new == ["_pipeline/a.md", "_pipeline/m.md", "_pipeline/z.md"]
