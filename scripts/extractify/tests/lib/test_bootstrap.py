"""Tests for the sys.path bootstrap helper."""
from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap: one-line sys.path insert to make lib._bootstrap importable
_EXTRACTIFY_ROOT = Path(__file__).resolve().parents[2]
if str(_EXTRACTIFY_ROOT) not in sys.path:
    sys.path.insert(0, str(_EXTRACTIFY_ROOT))

from lib._bootstrap import ensure_lib_on_path


def test_ensure_lib_on_path_inserts_extractify_root(monkeypatch):
    """Helper inserts scripts/extractify/ at sys.path[0] when absent."""
    expected_root = str(Path(__file__).resolve().parents[2])  # tests/lib/ → tests/ → extractify/
    # Strip the path if a prior import already inserted it
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != expected_root])

    ensure_lib_on_path()

    assert sys.path[0] == expected_root


def test_ensure_lib_on_path_is_idempotent(monkeypatch):
    """Calling twice doesn't insert a second copy."""
    expected_root = str(Path(__file__).resolve().parents[2])
    # Clear the path first to set up a clean state
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != expected_root])

    ensure_lib_on_path()
    before = sys.path.count(expected_root)
    ensure_lib_on_path()
    after = sys.path.count(expected_root)
    assert before == after == 1
