from __future__ import annotations

import hashlib
from pathlib import Path


def content_hash(path: Path, *, chunk_size: int = 65536) -> str:
    """Return `sha256:<hex>` for the file at path. Streams in chunks."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"
