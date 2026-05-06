"""Verbose-aware info logger for extractify.

Helpers in lib/ accept `verbose: bool`. When False, log_info is a no-op.
When True, each call prints `INFO: <msg>` to stderr. No structured logging
library — this is intentional (single boolean, no levels).
"""
from __future__ import annotations

import sys


def log_info(msg: str, *, verbose: bool) -> None:
    if verbose:
        print(f"INFO: {msg}", file=sys.stderr)
