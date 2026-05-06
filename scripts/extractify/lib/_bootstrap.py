"""Sys.path bootstrap helper for extractify consumers.

Brain extractors and tests need `scripts/extractify/` on sys.path so they
can `import lib.sources`. This helper centralizes the path computation
and idempotency check.

Usage from a consumer at any depth below scripts/extractify/:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[N]))
    from lib._bootstrap import ensure_lib_on_path
    ensure_lib_on_path()

The consumer's one-line sys.path insert is required to bootstrap *this*
module's import — the chicken-and-egg is intrinsic without packaging
extractify. This helper's value: a single source of truth for path
computation + idempotency, plus a future extension point for additional
bootstrap logic (logging, supplemental paths, version checks).
"""
from __future__ import annotations

import sys
from pathlib import Path

# scripts/extractify/ — the directory containing lib/, brains/, tests/
_EXTRACTIFY_ROOT = Path(__file__).resolve().parent.parent


def ensure_lib_on_path() -> None:
    """Idempotently insert scripts/extractify/ on sys.path so `lib.*` resolves."""
    p = str(_EXTRACTIFY_ROOT)
    if p not in sys.path:
        sys.path.insert(0, p)
