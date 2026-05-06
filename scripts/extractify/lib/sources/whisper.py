"""Whisper handler — local transcription via faster-whisper.

The model is loaded lazily and cached per-process. Brain overrides pass
a WhisperConfig.

EXTENSIONS is the canonical list of file extensions this handler claims;
__init__.py imports it to build the relevant rows of REGISTRY.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol


@dataclass(frozen=True)
class WhisperConfig:
    """Per-brain Whisper tuning. Defaults aim for 90% of brains needing
    zero overrides — small model, English, CPU+int8, no vocabulary prompt."""
    model: str = "small"
    device: str = "cpu"
    compute_type: str = "int8"
    language: str = "en"
    initial_prompt: str = ""


DEFAULT_WHISPER_CONFIG = WhisperConfig()


# Audio/video extensions handled by Whisper. auto_extract uses this to
# decide whether to thread a WhisperConfig through. Add to this set when
# adding new audio/video formats — __init__.py picks it up automatically.
EXTENSIONS: frozenset[str] = frozenset({".mp4", ".mov", ".m4a", ".mp3", ".wav"})


class _Segment(Protocol):
    start: float
    text: str


def _mmss(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


def format_segments(segments: Iterable[_Segment]) -> str:
    """Render segments as `[mm:ss] text` lines, one per segment."""
    lines = [f"[{_mmss(s.start)}] {s.text.strip()}" for s in segments]
    return "\n".join(lines) + ("\n" if lines else "")


_model_cache: dict[WhisperConfig, object] = {}


def _load_model(config: WhisperConfig):
    """Return a cached faster_whisper.WhisperModel for this config."""
    if config in _model_cache:
        return _model_cache[config]
    from faster_whisper import WhisperModel
    model = WhisperModel(
        config.model,
        device=config.device,
        compute_type=config.compute_type,
    )
    _model_cache[config] = model
    return model


def extract(input_path: Path, *, config: WhisperConfig | None = None) -> str:
    """Transcribe input_path to formatted markdown body. Raises ValueError
    if the file produces no segments (silent or VAD-filtered)."""
    cfg = config or DEFAULT_WHISPER_CONFIG
    model = _load_model(cfg)
    segments, _info = model.transcribe(
        str(input_path),
        beam_size=5,
        vad_filter=True,
        initial_prompt=cfg.initial_prompt,
        language=cfg.language,
    )
    body = format_segments(segments)
    if not body.strip():
        raise ValueError(f"no segments produced for {input_path}")
    return body
