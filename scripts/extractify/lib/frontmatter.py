from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def read(path: Path) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body). If no frontmatter block, dict is empty
    and body is the whole file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return {}, text
    # Find closing fence.
    lines = text.splitlines(keepends=True)
    end_idx: int | None = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r\n") == "---":
            end_idx = i
            break
    if end_idx is None:
        # Malformed — treat as no frontmatter.
        return {}, text
    fm_text = "".join(lines[1:end_idx])
    fm = yaml.safe_load(fm_text) or {}
    body = "".join(lines[end_idx + 1 :])
    return fm, body


def write(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    """Write frontmatter + body to path. Frontmatter serialized with yaml.safe_dump
    (sort_keys=False preserves insertion order)."""
    fm_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
    content = f"---\n{fm_text}---\n{body}"
    path.write_text(content, encoding="utf-8")
