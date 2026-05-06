from __future__ import annotations

import sys
from pathlib import Path

# Make `scripts/new-brain/` importable in tests if needed.
_SCRIPTS_NEW_BRAIN = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_NEW_BRAIN) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_NEW_BRAIN))
