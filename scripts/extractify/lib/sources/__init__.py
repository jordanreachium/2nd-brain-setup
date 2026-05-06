"""Source-type library — shared extractors for every brain.

Handlers in this package have signature `extract(input_path: Path) -> str`,
returning clean markdown body (no frontmatter — Extractify overlays that).
Every handler returns a body that ends in `\n` or is the empty string.

`auto_extract(input_path, output_path)` is the brain-facing orchestrator:
it picks a handler by file extension, gets the body, writes the file.

Brains that need per-kind tuning (e.g. custom Whisper vocabulary) pass a
config object — see WhisperConfig (defined in whisper.py, re-exported here).

To add a new source kind: add a module here, register its handler in
REGISTRY, write tests in scripts/extractify/tests/sources/. Brains pick
it up automatically via auto_extract.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from lib.sources import markdown as _markdown
from lib.sources import pdf as _pdf
from lib.sources import docx as _docx
from lib.sources import epub as _epub
from lib.sources import whisper as _whisper
from lib.sources.whisper import (
    EXTENSIONS as _WHISPER_EXTENSIONS,
    WhisperConfig,
    DEFAULT_WHISPER_CONFIG,
)


__all__ = ["auto_extract", "REGISTRY", "WhisperConfig", "DEFAULT_WHISPER_CONFIG"]


# Populated as handlers are added. Maps lowercase extension (with leading dot)
# to a handler callable. Most handlers have signature `extract(Path) -> str`.
# The Whisper handler is the one exception — it accepts an extra `config`
# keyword argument and is invoked via the dedicated branch in `auto_extract`
# below, not as a generic registry lookup. The Callable[..., str] type is
# deliberately loose to accommodate Whisper's signature; future handler
# authors should still follow the standard `extract(Path) -> str` contract
# unless their handler has a similarly clear reason to differ.
REGISTRY: dict[str, Callable[..., str]] = {
    ".md": _markdown.extract,
    ".pdf": _pdf.extract,
    ".docx": _docx.extract,
    ".epub": _epub.extract,
    **{ext: _whisper.extract for ext in _WHISPER_EXTENSIONS},
}


def auto_extract(
    input_path: Path,
    output_path: Path,
    *,
    whisper_config: WhisperConfig | None = None,
) -> None:
    """Dispatch to the registered handler for input_path's extension, write
    the result to output_path. Creates output_path's parent dir.

    Handler contract: each handler returns a body that ends with `\\n` or
    is the empty string. auto_extract writes the body verbatim — Extractify
    overlays YAML frontmatter on top.
    """
    ext = input_path.suffix.lower()
    handler = REGISTRY.get(ext)
    if handler is None:
        raise KeyError(
            f"No source handler for extension {ext!r}. "
            f"Add a handler module to scripts/extractify/lib/sources/ "
            f"and register it in REGISTRY."
        )
    # Whisper handler accepts a config kwarg; others don't.
    if ext in _WHISPER_EXTENSIONS:
        body = handler(input_path, config=whisper_config or DEFAULT_WHISPER_CONFIG)
    else:
        body = handler(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body, encoding="utf-8")
