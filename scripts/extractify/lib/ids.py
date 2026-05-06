from __future__ import annotations

import re
import unicodedata


_NON_WORD = re.compile(r"[^\w\s-]", flags=re.UNICODE)
_WHITESPACE = re.compile(r"[\s_]+", flags=re.UNICODE)
_MULTI_DASH = re.compile(r"-+")


def kebab_slug(text: str) -> str:
    """Lowercase kebab-case slug. Unicode letters are preserved (NFC, lowercased).
    Punctuation stripped. Whitespace collapses to single dash. No leading/trailing dashes.
    """
    text = unicodedata.normalize("NFC", text).lower()
    text = _NON_WORD.sub("", text)
    text = _WHITESPACE.sub("-", text)
    text = _MULTI_DASH.sub("-", text)
    return text.strip("-")
