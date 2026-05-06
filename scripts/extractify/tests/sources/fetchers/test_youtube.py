from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

import pytest

from lib.sources.fetchers.youtube import (
    extract_video_id,
    parse_vtt,
    dedupe_lines,
    fetch_one,
)


def test_extract_video_id_youtu_be():
    assert extract_video_id("https://youtu.be/abc12345xyz") == "abc12345xyz"


def test_extract_video_id_youtube_com_v_param():
    assert extract_video_id("https://www.youtube.com/watch?v=abc12345xyz&t=10") == "abc12345xyz"


def test_extract_video_id_invalid_raises():
    with pytest.raises(ValueError):
        extract_video_id("https://example.com/foo")


def test_parse_vtt_extracts_cues():
    vtt = (
        "WEBVTT\n"
        "\n"
        "00:00:01.000 --> 00:00:03.000\n"
        "Line one\n"
        "\n"
        "00:00:03.000 --> 00:00:05.000\n"
        "Line one\nLine two\n"
        "\n"
        "00:00:05.000 --> 00:00:07.000\n"
        "Line two\nLine three\n"
    )
    cues = parse_vtt(vtt)
    assert "Line one" in cues[0]
    assert "Line three" in cues[-1]


def test_dedupe_lines_collapses_overlap():
    cues = ["Line one", "Line one\nLine two", "Line two\nLine three"]
    out = dedupe_lines(cues)
    # Each unique line appears once, separated by spaces.
    assert out == "Line one Line two Line three"


def test_fetch_one_writes_markdown_with_frontmatter(tmp_path: Path):
    video_id = "abc12345xyz"
    vtt_path = tmp_path / f"{video_id}.en.vtt"
    info_path = tmp_path / f"{video_id}.info.json"

    def fake_run(args, **kw):
        # Single call — write both VTT and info.json (simulates --write-info-json).
        vtt_path.write_text(
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nHello world\n",
            encoding="utf-8",
        )
        info_path.write_text(
            '{"id": "abc12345xyz", "title": "Test Title", "uploader": "Test Channel",'
            ' "duration": 120, "upload_date": "20250101"}',
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(args, 0, "", "")

    with patch("subprocess.run", side_effect=fake_run):
        out_path = fetch_one("https://youtu.be/abc12345xyz", tmp_path)

    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "video_id: abc12345xyz" in text
    assert 'title: "Test Title"' in text
    assert 'channel: "Test Channel"' in text
    assert "duration_minutes: 2" in text
    assert "Hello world" in text
    # VTT cleaned up after parse.
    assert not vtt_path.exists()


def test_fetch_one_calls_yt_dlp_exactly_once(tmp_path: Path):
    """yt-dlp should be invoked once per video — not twice (subs + --print)."""
    video_id = "abc12345xyz"
    call_count = {"n": 0}

    def fake_run(cmd, **kwargs):
        call_count["n"] += 1
        # Simulate yt-dlp writing both files when --write-info-json is in cmd.
        out_dir = tmp_path
        for i, arg in enumerate(cmd):
            if arg in ("-o", "--output") and i + 1 < len(cmd):
                out_dir = Path(cmd[i + 1]).parent
                break
        (out_dir / f"{video_id}.en.vtt").write_text(
            "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nhello\n", encoding="utf-8"
        )
        (out_dir / f"{video_id}.info.json").write_text(
            '{"id": "abc12345xyz", "title": "Test", "uploader": "TestChannel",'
            ' "duration": 60, "upload_date": "20250101"}',
            encoding="utf-8",
        )
        from types import SimpleNamespace
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    import lib.sources.fetchers.youtube as yt
    monkeypatch_target = yt.subprocess
    original_run = monkeypatch_target.run
    monkeypatch_target.run = fake_run
    try:
        yt.fetch_one("https://youtube.com/watch?v=abc12345xyz", out_dir=tmp_path)
    finally:
        monkeypatch_target.run = original_run

    assert call_count["n"] == 1, f"yt-dlp invoked {call_count['n']} times; expected 1"


def test_pick_vtt_prefers_en_exact(tmp_path: Path):
    """Prefer `<id>.en.vtt` over `<id>.en-US.vtt` and `<id>.es.vtt`."""
    from lib.sources.fetchers.youtube import _pick_vtt

    video_id = "abc123"
    (tmp_path / f"{video_id}.es.vtt").write_text("es")
    (tmp_path / f"{video_id}.en-US.vtt").write_text("en-US")
    (tmp_path / f"{video_id}.en.vtt").write_text("en")

    assert _pick_vtt(tmp_path, video_id).name == f"{video_id}.en.vtt"


def test_pick_vtt_falls_back_to_en_dash(tmp_path: Path):
    """When `.en.vtt` is missing but `.en-*.vtt` exists, pick the en-* variant."""
    from lib.sources.fetchers.youtube import _pick_vtt

    video_id = "abc123"
    (tmp_path / f"{video_id}.es.vtt").write_text("es")
    (tmp_path / f"{video_id}.en-US.vtt").write_text("en-US")

    assert _pick_vtt(tmp_path, video_id).name == f"{video_id}.en-US.vtt"


def test_pick_vtt_falls_back_to_any_when_no_en(tmp_path: Path):
    """When no English variant exists, pick any (deterministic via sort)."""
    from lib.sources.fetchers.youtube import _pick_vtt

    video_id = "abc123"
    (tmp_path / f"{video_id}.es.vtt").write_text("es")
    (tmp_path / f"{video_id}.fr.vtt").write_text("fr")

    result = _pick_vtt(tmp_path, video_id)
    # Sort is alphabetical: .es < .fr
    assert result.name == f"{video_id}.es.vtt"


def test_pick_vtt_returns_none_when_no_vtt(tmp_path: Path):
    """No VTT files present → None."""
    from lib.sources.fetchers.youtube import _pick_vtt

    assert _pick_vtt(tmp_path, "abc123") is None
