from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap so `lib._bootstrap` is importable, then delegate to it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib._bootstrap import ensure_lib_on_path  # noqa: E402
ensure_lib_on_path()
