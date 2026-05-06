"""Verbose-aware info logger for obsidianify. Mirror of extractify's log.py."""
from __future__ import annotations

import sys


def log_info(msg: str, *, verbose: bool) -> None:
    if verbose:
        print(f"INFO: {msg}", file=sys.stderr)
