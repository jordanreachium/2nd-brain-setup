from __future__ import annotations

from pathlib import Path
from lib.sources.epub import extract


def test_extract_includes_both_chapters(sample_epub: Path):
    body = extract(sample_epub)
    assert "First chapter body" in body
    assert "Second chapter body" in body


def test_extract_preserves_chapter_order(sample_epub: Path):
    body = extract(sample_epub)
    assert body.index("First chapter") < body.index("Second chapter")


def test_extract_warns_on_replacement_chars(tmp_path: Path, capsys):
    """When a chapter contains undecodable bytes, log a warning to stderr."""
    from unittest.mock import MagicMock, patch

    # Build a fake item whose get_content() returns bytes with a non-UTF-8 byte
    bad_content = b"<html><body><p>hello \xff world</p></body></html>"
    fake_item = MagicMock()
    fake_item.get_content.return_value = bad_content

    fake_book = MagicMock()
    fake_book.get_items_of_type.return_value = [fake_item]

    fixture = tmp_path / "broken.epub"
    fixture.write_bytes(b"placeholder")  # path just needs to exist for the message

    with patch("ebooklib.epub.read_epub", return_value=fake_book):
        from lib.sources.epub import extract as epub_extract
        body = epub_extract(fixture)

    captured = capsys.readouterr()
    assert "warning" in captured.err.lower(), repr(captured.err)
    assert str(fixture) in captured.err, repr(captured.err)
    # Body should still be returned (non-empty) — warning is operational, not blocking
    assert body  # non-empty


def test_extract_no_warning_for_clean_epub(sample_epub: Path, capsys):
    """Clean UTF-8 epub doesn't emit a warning."""
    from lib.sources.epub import extract as epub_extract

    epub_extract(sample_epub)

    captured = capsys.readouterr()
    assert "warning" not in captured.err.lower(), repr(captured.err)


def test_extract_preserves_paragraph_breaks(tmp_path: Path):
    """Two HTML <p> tags become two prose paragraphs separated by \\n\\n."""
    from ebooklib import epub
    from lib.sources.epub import extract as epub_extract

    book = epub.EpubBook()
    book.set_identifier("test-paragraphs")
    book.set_title("Paragraphs")
    book.set_language("en")

    chapter = epub.EpubHtml(title="Ch1", file_name="ch1.xhtml", lang="en")
    chapter.content = (
        b"<html><body>"
        b"<p>First paragraph.</p>"
        b"<p>Second paragraph.</p>"
        b"</body></html>"
    )
    book.add_item(chapter)
    book.spine = ["nav", chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    fixture = tmp_path / "paragraphs.epub"
    epub.write_epub(str(fixture), book, {})

    body = epub_extract(fixture)

    assert "First paragraph." in body
    assert "Second paragraph." in body
    # The contract: paragraphs separated by \n\n inside the same chapter
    assert "First paragraph.\n\nSecond paragraph." in body, repr(body)


def test_extract_preserves_heading_with_paragraph(tmp_path: Path):
    """A heading followed by a paragraph yields two prose paragraphs separated by \\n\\n."""
    from ebooklib import epub
    from lib.sources.epub import extract as epub_extract

    book = epub.EpubBook()
    book.set_identifier("test-heading")
    book.set_title("Heading")
    book.set_language("en")

    chapter = epub.EpubHtml(title="Ch1", file_name="ch1.xhtml", lang="en")
    chapter.content = (
        b"<html><body>"
        b"<h1>Section Heading</h1>"
        b"<p>Body text follows.</p>"
        b"</body></html>"
    )
    book.add_item(chapter)
    book.spine = ["nav", chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    fixture = tmp_path / "heading.epub"
    epub.write_epub(str(fixture), book, {})

    body = epub_extract(fixture)

    assert "Section Heading" in body
    assert "Body text follows." in body
    assert "Section Heading\n\nBody text follows." in body, repr(body)


def test_extract_preserves_inline_text_with_spaces(tmp_path: Path):
    """Inline `<em>` etc. inside a single paragraph stays on one line, joined by spaces."""
    from ebooklib import epub
    from lib.sources.epub import extract as epub_extract

    book = epub.EpubBook()
    book.set_identifier("test-inline")
    book.set_title("Inline")
    book.set_language("en")

    chapter = epub.EpubHtml(title="Ch1", file_name="ch1.xhtml", lang="en")
    chapter.content = (
        b"<html><body>"
        b"<p>Hello <em>world</em>!</p>"
        b"</body></html>"
    )
    book.add_item(chapter)
    book.spine = ["nav", chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    fixture = tmp_path / "inline.epub"
    epub.write_epub(str(fixture), book, {})

    body = epub_extract(fixture)

    # Inline em should stay on one line, joined with spaces
    assert "Hello world !" in body or "Hello world!" in body, repr(body)
    # Should NOT have a paragraph break between "Hello" and "world"
    assert "Hello\n\nworld" not in body
