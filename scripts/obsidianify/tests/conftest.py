from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_OBSIDIANIFY = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_OBSIDIANIFY) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_OBSIDIANIFY))
