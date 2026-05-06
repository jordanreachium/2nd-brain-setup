from __future__ import annotations
from pathlib import Path

from lib.hashing import content_hash


def test_same_content_same_hash(tmp_path: Path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello world", encoding="utf-8")
    b.write_text("hello world", encoding="utf-8")
    assert content_hash(a) == content_hash(b)


def test_different_content_different_hash(tmp_path: Path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello", encoding="utf-8")
    b.write_text("world", encoding="utf-8")
    assert content_hash(a) != content_hash(b)


def test_hash_is_sha256_hex_prefix(tmp_path: Path):
    a = tmp_path / "a.txt"
    a.write_text("x", encoding="utf-8")
    h = content_hash(a)
    assert h.startswith("sha256:")
    assert len(h) == len("sha256:") + 64  # sha256 hex is 64 chars
