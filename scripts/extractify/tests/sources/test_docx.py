from __future__ import annotations

from pathlib import Path
from lib.sources.docx import extract


def test_extract_preserves_heading_levels(sample_docx: Path):
    body = extract(sample_docx)
    assert "# Top Title" in body
    assert "## Section A" in body
    assert "### Subsection" in body


def test_extract_includes_paragraphs(sample_docx: Path):
    body = extract(sample_docx)
    assert "Intro paragraph." in body
    assert "Body of section A." in body
    assert "Detail." in body


def test_extract_flattens_table_cells(sample_docx: Path):
    body = extract(sample_docx)
    for cell in ("cell-1", "cell-2", "cell-3", "cell-4"):
        assert cell in body
