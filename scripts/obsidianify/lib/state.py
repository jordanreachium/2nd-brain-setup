from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def empty_state() -> dict[str, Any]:
    return {
        "version": 1,
        "last_run": None,
        "entries": {},
        "orphan_vault_notes": [],
    }


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_state()
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")


def record_synthesis(
    state: dict[str, Any],
    *,
    pipeline_path: str,
    content_hash: str,
    synthesized_at: str,
    generated_vault_notes: list[str],
) -> None:
    """In-place upsert of a synthesis entry. Replaces existing entry for the same pipeline_path."""
    state["entries"][pipeline_path] = {
        "content_hash": content_hash,
        "synthesized_at": synthesized_at,
        "generated_vault_notes": list(generated_vault_notes),
    }
