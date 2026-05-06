#!/usr/bin/env bash
# Print every brain root in the repo, one per line, relative to repo root.
# A "brain" is any directory that contains `.obsidian/` and is either:
#   - a top-level repo dir (excluding `_*` and `.*`), or
#   - a direct child of `.Project Context/`.
# Usage: scripts/_lib/discover-brains.sh
# Must be run from repo root (or a script that cd'd there).

set -euo pipefail

# Top-level brains.
while IFS= read -r -d '' dir; do
  name="$(basename "$dir")"
  [[ "$name" == _* ]] && continue
  [[ "$name" == .* ]] && continue
  if [[ -d "$dir/.obsidian" ]]; then
    echo "${dir#./}"
  fi
done < <(find . -maxdepth 1 -mindepth 1 -type d -print0)

# Project Context brains.
if [[ -d ".Project Context" ]]; then
  while IFS= read -r -d '' dir; do
    if [[ -d "$dir/.obsidian" ]]; then
      echo "${dir#./}"
    fi
  done < <(find ".Project Context" -maxdepth 1 -mindepth 1 -type d -print0)
fi
