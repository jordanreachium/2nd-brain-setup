from __future__ import annotations

from pathlib import Path
from lib.sources.pdf import extract


def test_extract_returns_text_per_page(sample_pdf: Path):
    body = extract(sample_pdf)
    assert "Page one greeting" in body
    assert "Page two answer" in body
    # Pages should be separated by a blank line; ordering preserved.
    assert body.index("Page one") < body.index("Page two")


def test_extract_empty_pdf_returns_empty_string(tmp_path: Path):
    """A PDF with pages but no extractable text (e.g. image-only or blank
    pages) should return the empty string, not '\\n' or anything else."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()  # blank page — no text added
    out = tmp_path / "blank.pdf"
    pdf.output(str(out))

    assert extract(out) == ""
