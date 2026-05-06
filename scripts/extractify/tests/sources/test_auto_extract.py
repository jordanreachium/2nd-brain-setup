from __future__ import annotations

from pathlib import Path
import pytest
from lib.sources import (
    REGISTRY,
    WhisperConfig,
    DEFAULT_WHISPER_CONFIG,
    auto_extract,
)


def test_default_whisper_config_values():
    assert DEFAULT_WHISPER_CONFIG.model == "small"
    assert DEFAULT_WHISPER_CONFIG.device == "cpu"
    assert DEFAULT_WHISPER_CONFIG.compute_type == "int8"
    assert DEFAULT_WHISPER_CONFIG.language == "en"
    assert DEFAULT_WHISPER_CONFIG.initial_prompt == ""


def test_registry_has_expected_handlers():
    """REGISTRY covers all currently-supported source kinds."""
    from lib.sources import REGISTRY

    expected = {".md", ".pdf", ".docx", ".epub", ".mp4", ".mov", ".m4a", ".mp3", ".wav"}
    assert set(REGISTRY.keys()) == expected


def test_auto_extract_unknown_extension_raises(tmp_path: Path):
    f = tmp_path / "file.xyz"
    f.write_text("ignored")
    out = tmp_path / "out.md"
    with pytest.raises(KeyError, match=r"\.xyz"):
        auto_extract(f, out)


def test_auto_extract_writes_markdown_via_md_handler(tmp_path: Path):
    src = tmp_path / "in.md"
    src.write_text("---\nx: 1\n---\nbody only.\n", encoding="utf-8")
    out = tmp_path / "subdir" / "out.md"
    auto_extract(src, out)
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "x: 1" not in text  # frontmatter stripped
    assert "body only." in text


def test_auto_extract_creates_parent_dir(tmp_path: Path):
    src = tmp_path / "in.md"
    src.write_text("hi", encoding="utf-8")
    out = tmp_path / "deep" / "nested" / "out.md"
    auto_extract(src, out)
    assert out.exists()


def test_auto_extract_uppercase_extension(tmp_path: Path):
    src = tmp_path / "FILE.MD"
    src.write_text("hello", encoding="utf-8")
    out = tmp_path / "out.md"
    auto_extract(src, out)
    assert out.read_text(encoding="utf-8") == "hello"


def test_all_handler_outputs_end_in_newline_or_empty(
    tmp_path: Path,
    sample_pdf: Path,
    sample_docx: Path,
    sample_epub: Path,
):
    """Every handler's body must end with \\n or be the empty string.

    Pinning this contract prevents downstream brains from getting silently
    different concatenation behavior between source kinds. Whisper is
    omitted — it requires a real model load (M8 covers it).
    """
    from lib.sources import REGISTRY

    md = tmp_path / "sample.md"
    md.write_text("hello\n", encoding="utf-8")

    cases = {
        ".md": md,
        ".pdf": sample_pdf,
        ".docx": sample_docx,
        ".epub": sample_epub,
    }
    for ext, path in cases.items():
        handler = REGISTRY[ext]
        body = handler(path)
        assert body == "" or body.endswith("\n"), (
            f"{ext} handler returned body that doesn't end in newline: {body!r}"
        )
