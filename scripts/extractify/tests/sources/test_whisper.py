from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lib.sources import WhisperConfig
from lib.sources.whisper import extract, format_segments


class _Seg:
    def __init__(self, start: float, text: str):
        self.start = start
        self.text = text


def test_format_segments_mmss_prefix():
    segs = [_Seg(0.0, "Hello world."), _Seg(75.5, "Later text.")]
    out = format_segments(segs)
    assert out == "[00:00] Hello world.\n[01:15] Later text.\n"


def test_format_segments_empty():
    assert format_segments([]) == ""


def test_extract_uses_default_config_when_none(tmp_path: Path):
    fake_segments = [_Seg(0.0, "transcribed text")]
    fake_model = MagicMock()
    fake_model.transcribe.return_value = (fake_segments, MagicMock())
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"\x00")  # placeholder; loader is mocked

    with patch("lib.sources.whisper._load_model", return_value=fake_model):
        body = extract(f)

    assert "transcribed text" in body
    # Default config — initial_prompt empty.
    call_kwargs = fake_model.transcribe.call_args.kwargs
    assert call_kwargs.get("initial_prompt") == ""


def test_extract_threads_custom_config(tmp_path: Path):
    fake_segments = [_Seg(0.0, "x")]
    fake_model = MagicMock()
    fake_model.transcribe.return_value = (fake_segments, MagicMock())
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"\x00")
    cfg = WhisperConfig(model="medium", initial_prompt="Foo Bar Baz")

    with patch("lib.sources.whisper._load_model", return_value=fake_model) as load:
        extract(f, config=cfg)

    load.assert_called_once_with(cfg)
    assert fake_model.transcribe.call_args.kwargs["initial_prompt"] == "Foo Bar Baz"


def test_extract_raises_on_empty_transcription(tmp_path: Path):
    fake_model = MagicMock()
    fake_model.transcribe.return_value = ([], MagicMock())
    f = tmp_path / "silent.mp4"
    f.write_bytes(b"\x00")

    with patch("lib.sources.whisper._load_model", return_value=fake_model):
        with pytest.raises(ValueError, match="no segments"):
            extract(f)


def test_whisper_extensions_frozenset_contents():
    """Pins the audio/video extension set so an accidental removal regresses
    auto_extract's whisper dispatch."""
    from lib.sources.whisper import EXTENSIONS
    assert EXTENSIONS == frozenset({".mp4", ".mov", ".m4a", ".mp3", ".wav"})


def test_load_model_caches_per_config():
    """Calling _load_model twice with the same config invokes WhisperModel once.

    The cache requires WhisperConfig to be hashable (frozen=True). This test
    guards against accidental removal of frozen=True breaking the cache.
    """
    import sys
    import types
    from lib.sources import whisper as _whisper

    # Reset any cached models from prior tests.
    _whisper._model_cache.clear()

    call_count = {"n": 0}

    class FakeWhisperModel:
        def __init__(self, *args, **kwargs):
            call_count["n"] += 1

    # _load_model does `from faster_whisper import WhisperModel` lazily.
    # Inject a fake faster_whisper module so the import resolves without the
    # real package, then restore it afterwards.
    fake_fw = types.ModuleType("faster_whisper")
    fake_fw.WhisperModel = FakeWhisperModel
    prev = sys.modules.get("faster_whisper")
    sys.modules["faster_whisper"] = fake_fw
    try:
        cfg = _whisper.WhisperConfig()
        _whisper._load_model(cfg)
        _whisper._load_model(cfg)

        assert call_count["n"] == 1, (
            "WhisperModel should be constructed exactly once per config"
        )

        # Different config → second construction.
        cfg2 = _whisper.WhisperConfig(model="medium")
        _whisper._load_model(cfg2)
        assert call_count["n"] == 2
    finally:
        if prev is None:
            sys.modules.pop("faster_whisper", None)
        else:
            sys.modules["faster_whisper"] = prev
        _whisper._model_cache.clear()
