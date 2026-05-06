from __future__ import annotations
from pathlib import Path

from lib.state import empty_state, load, save, record_synthesis


def test_empty_state_shape():
    s = empty_state()
    assert s == {
        "version": 1,
        "last_run": None,
        "entries": {},
        "orphan_vault_notes": [],
    }


def test_load_missing_returns_empty(tmp_path: Path):
    assert load(tmp_path / "missing.json") == empty_state()


def test_save_load_roundtrip(tmp_path: Path):
    p = tmp_path / "state.json"
    s = empty_state()
    s["last_run"] = "2026-04-24T15:00:00Z"
    s["entries"]["_pipeline/a.md"] = {
        "content_hash": "sha256:abc",
        "synthesized_at": "2026-04-24T15:00:00Z",
        "generated_vault_notes": ["Vault/concepts/a.md"],
    }
    save(p, s)
    assert load(p) == s


def test_record_synthesis_adds_entry():
    s = empty_state()
    record_synthesis(
        s,
        pipeline_path="_pipeline/books/x.md",
        content_hash="sha256:xx",
        synthesized_at="2026-04-24T15:00:00Z",
        generated_vault_notes=["Vault/concepts/x.md", "Vault/sources/x.md"],
    )
    entry = s["entries"]["_pipeline/books/x.md"]
    assert entry["content_hash"] == "sha256:xx"
    assert entry["generated_vault_notes"] == [
        "Vault/concepts/x.md",
        "Vault/sources/x.md",
    ]


def test_record_synthesis_replaces_existing():
    s = empty_state()
    s["entries"]["_pipeline/x.md"] = {
        "content_hash": "sha256:old",
        "synthesized_at": "2026-04-23T10:00:00Z",
        "generated_vault_notes": ["Vault/concepts/x-old.md"],
    }
    record_synthesis(
        s,
        pipeline_path="_pipeline/x.md",
        content_hash="sha256:new",
        synthesized_at="2026-04-24T10:00:00Z",
        generated_vault_notes=["Vault/concepts/x-new.md"],
    )
    entry = s["entries"]["_pipeline/x.md"]
    assert entry["content_hash"] == "sha256:new"
    assert entry["generated_vault_notes"] == ["Vault/concepts/x-new.md"]
