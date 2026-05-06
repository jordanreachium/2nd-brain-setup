from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiffResult:
    new: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)


def diff(
    manifest_entries: dict[str, dict[str, Any]],
    state_entries: dict[str, dict[str, Any]],
) -> DiffResult:
    """Compare a pipeline manifest (Extractify output) against a synthesis state
    (Obsidianify output). Output lists are deterministically sorted."""
    r = DiffResult()
    for path in sorted(manifest_entries.keys()):
        m_hash = manifest_entries[path].get("content_hash")
        if path not in state_entries:
            r.new.append(path)
            continue
        s_hash = state_entries[path].get("content_hash")
        if m_hash == s_hash:
            r.unchanged.append(path)
        else:
            r.changed.append(path)
    for path in sorted(state_entries.keys()):
        if path not in manifest_entries:
            r.removed.append(path)
    return r
