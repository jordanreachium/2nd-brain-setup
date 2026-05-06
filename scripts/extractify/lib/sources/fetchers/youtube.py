"""Fetch YouTube auto-captions and clean to markdown.

CLI (run from scripts/extractify/):
    python -m lib.sources.fetchers.youtube <url> [<url>...] --out DIR

Writes `<video_id>.md` to --out (defaults to ./_raw/transcripts) with YAML
frontmatter (url, video_id, title, channel, duration_minutes, fetched_at)
followed by deduped prose. Extractify's markdown handler strips the
frontmatter when this file is later extracted into _pipeline/.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc == "youtu.be":
        return parsed.path.lstrip("/").split("?")[0]
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
    raise ValueError(f"Could not extract video ID from {url!r}")


def parse_vtt(content: str) -> list[str]:
    cues: list[str] = []
    lines = content.splitlines()
    i = 0
    in_cue = False
    current: list[str] = []
    while i < len(lines) and not re.match(r"\d{2}:\d{2}:\d{2}", lines[i]):
        i += 1
    while i < len(lines):
        line = lines[i]
        if re.match(r"\d{2}:\d{2}:\d{2}.*-->", line):
            if current:
                cues.append("\n".join(current).strip())
                current = []
            in_cue = True
        elif line.strip() == "":
            if current:
                cues.append("\n".join(current).strip())
                current = []
            in_cue = False
        elif in_cue:
            cleaned = re.sub(r"<[^>]+>", "", line).strip()
            if cleaned:
                current.append(cleaned)
        i += 1
    if current:
        cues.append("\n".join(current).strip())
    return [c for c in cues if c]


def dedupe_lines(cues: list[str]) -> str:
    """Collapse YouTube's rolling-window caption overlap into a single prose line."""
    seen_last: str | None = None
    kept: list[str] = []
    for cue in cues:
        for line in cue.splitlines():
            line = line.strip()
            if not line:
                continue
            if line == seen_last:
                continue
            kept.append(line)
            seen_last = line
    return " ".join(kept)


def _build_ytdlp_args(url: str, out_dir: Path) -> list[str]:
    return [
        sys.executable, "-m", "yt_dlp",
        "--write-auto-subs",
        "--sub-langs", "en",
        "--skip-download",
        "--sub-format", "vtt",
        "--write-info-json",
        "-o", str(out_dir / "%(id)s.%(ext)s"),
        url,
    ]


def _pick_vtt(out_dir: Path, video_id: str) -> Path | None:
    """Pick the best VTT for video_id from out_dir.

    Preference: `<id>.en.vtt` (exact English) → `<id>.en-*.vtt` (English variant
    like en-US, en-GB) → any `<id>*.vtt` (sorted for determinism). Returns None
    if no matching VTT exists.
    """
    candidates = sorted(out_dir.glob(f"{video_id}*.vtt"))
    if not candidates:
        return None
    en_exact = out_dir / f"{video_id}.en.vtt"
    if en_exact in candidates:
        return en_exact
    en_variants = [
        c for c in candidates
        if c.name.startswith(f"{video_id}.en-") and c.suffix == ".vtt"
    ]
    if en_variants:
        return en_variants[0]
    return candidates[0]


def fetch_one(url: str, out_dir: Path) -> Path:
    """Fetch caption + metadata for one URL, write the cleaned markdown.
    Returns the path to the written .md file."""
    video_id = extract_video_id(url)
    out_dir.mkdir(parents=True, exist_ok=True)

    args = _build_ytdlp_args(url, out_dir)
    result = subprocess.run(args, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed for {url}: {result.stderr}")

    vtt_path = _pick_vtt(out_dir, video_id)
    if vtt_path is None:
        raise FileNotFoundError(f"No VTT file produced for {video_id}")

    # Read metadata from the info.json written by --write-info-json.
    info_path = out_dir / f"{video_id}.info.json"
    title, channel, duration_sec = "", "", 0
    if info_path.exists():
        metadata = json.loads(info_path.read_text(encoding="utf-8"))
        title = metadata.get("title", "")
        channel = metadata.get("uploader", "")
        raw_duration = metadata.get("duration", 0)
        duration_sec = int(raw_duration) if raw_duration else 0

    cues = parse_vtt(vtt_path.read_text(encoding="utf-8"))
    prose = dedupe_lines(cues)

    md_path = out_dir / f"{video_id}.md"
    duration_min = duration_sec // 60
    frontmatter = (
        "---\n"
        f"url: {url}\n"
        f"video_id: {video_id}\n"
        f"title: {json.dumps(title)}\n"
        f"channel: {json.dumps(channel)}\n"
        f"duration_minutes: {duration_min}\n"
        f"fetched_at: {datetime.now(timezone.utc).isoformat()}\n"
        "---\n\n"
    )
    md_path.write_text(frontmatter + prose + "\n", encoding="utf-8")

    vtt_path.unlink()
    return md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch YouTube auto-captions.")
    parser.add_argument("urls", nargs="+", help="YouTube URLs")
    parser.add_argument("--out", type=Path, default=Path("_raw/transcripts"),
                        help="Output dir (default: ./_raw/transcripts)")
    args = parser.parse_args()

    for url in args.urls:
        print(f"[fetch_youtube] {url}")
        path = fetch_one(url, args.out)
        print(f"  -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
