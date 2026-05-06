from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ManifestEntry:
    source_path: str
    source_kind: str
    extracted_at: str
    content_hash: str


def empty_manifest() -> dict[str, Any]:
    return {"version": 1, "entries": {}}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_manifest()
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")


def upsert_entry(
    manifest: dict[str, Any], pipeline_path: str, entry: ManifestEntry
) -> None:
    """In-place upsert. `pipeline_path` is the key; entry replaces existing or adds new."""
    manifest["entries"][pipeline_path] = asdict(entry)
