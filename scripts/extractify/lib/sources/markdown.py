"""Markdown pass-through handler.

Returns the file body verbatim, with one transformation: a leading YAML
frontmatter block fenced by `---` lines is removed, along with any blank
lines immediately following the closing fence. If no opening fence is
present, or if an opening fence has no matching closing fence, the file
is returned unchanged. CRLF and LF line endings are both supported.
"""
from __future__ import annotations

from pathlib import Path


def extract(input_path: Path) -> str:
    text = input_path.read_text(encoding="utf-8")
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        return text
    lines = text.splitlines(keepends=True)
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r\n") == "---":
            return "".join(lines[i + 1 :]).lstrip("\r\n")
    # No closing fence — pass through unchanged.
    return text
