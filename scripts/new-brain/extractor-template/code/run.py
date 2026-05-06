"""Default brain extractor — uses the shared source library.

Most new brains do not need to modify this file. The library handles
.md, .pdf, .docx, .epub, .mp4, .mov, .m4a, .mp3, .wav out of the box.

To customize Whisper for video/audio (e.g. add brain-specific vocabulary):

    from pathlib import Path
    from lib.sources import auto_extract, WhisperConfig

    WHISPER = WhisperConfig(initial_prompt="Term1, Term2, Term3")

    def extract(input_path: Path, output_path: Path) -> None:
        auto_extract(input_path, output_path, whisper_config=WHISPER)

To add a brand-new source kind: add a handler module in
scripts/extractify/lib/sources/ and register it in REGISTRY. Future
brains pick it up automatically.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap helper, then library
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from lib._bootstrap import ensure_lib_on_path  # noqa: E402
ensure_lib_on_path()

from lib.sources import auto_extract  # noqa: E402


def extract(input_path: Path, output_path: Path) -> None:
    auto_extract(input_path, output_path)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python -m code <input-path> <output-path>", file=sys.stderr)
        return 2
    raw = Path(argv[0])
    out = Path(argv[1])
    if not raw.exists():
        print(f"raw file not found: {raw}", file=sys.stderr)
        return 1
    try:
        extract(raw, out)
    except Exception as exc:
        print(f"error extracting {raw}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
