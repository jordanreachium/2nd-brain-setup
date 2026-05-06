"""PDF handler — extracts text page-by-page via pypdf, joins with blank lines.
Empty pages are dropped."""
from __future__ import annotations

from pathlib import Path


def extract(input_path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(input_path))
    chunks: list[str] = []
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if text:
            chunks.append(text)
    if not chunks:
        return ""
    return "\n\n".join(chunks) + "\n"
