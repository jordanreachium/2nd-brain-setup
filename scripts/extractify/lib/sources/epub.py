"""EPUB handler — extract chapter text from each DOCUMENT item, separate
chapters with a blank line."""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path


class _ChapterParser(HTMLParser):
    """Render epub chapter HTML to plain prose preserving block structure.

    Block-level tags (p, div, h1-h6, li, br) trigger paragraph boundaries.
    Inline content within a paragraph joins with single spaces.
    Paragraphs join with \\n\\n.
    """

    BLOCK_TAGS = frozenset({"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "br"})

    def __init__(self) -> None:
        super().__init__()
        self._paragraphs: list[list[str]] = [[]]

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self.BLOCK_TAGS:
            self._start_new_paragraph()

    def handle_endtag(self, tag: str) -> None:
        if tag in self.BLOCK_TAGS:
            self._start_new_paragraph()

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self._paragraphs[-1].append(text)

    def _start_new_paragraph(self) -> None:
        if self._paragraphs[-1]:  # only start new if current has content
            self._paragraphs.append([])

    def render(self) -> str:
        rendered = [" ".join(p) for p in self._paragraphs if p]
        return "\n\n".join(rendered)


def extract(input_path: Path) -> str:
    import ebooklib
    from ebooklib import epub

    book = epub.read_epub(str(input_path))
    chapters: list[str] = []
    saw_replacement_chars = False
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        decoded = item.get_content().decode("utf-8", errors="replace")
        if "�" in decoded:
            saw_replacement_chars = True
        parser = _ChapterParser()
        parser.feed(decoded)
        body = parser.render().strip()
        if body:
            chapters.append(body)
    if saw_replacement_chars:
        print(
            f"warning: {input_path} contains chapters with non-UTF-8 bytes; "
            f"replacement characters present in extracted text",
            file=sys.stderr,
        )
    if not chapters:
        return ""
    return "\n\n".join(chapters) + "\n"
