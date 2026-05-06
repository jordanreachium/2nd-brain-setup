#!/usr/bin/env bash
# Smoke test for discover-brains.sh against a fake repo.
set -euo pipefail

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Build a fake repo layout.
mkdir -p "$tmp/Brain A/.obsidian"
mkdir -p "$tmp/Brain B/.obsidian"
mkdir -p "$tmp/_brain_template/.obsidian"   # excluded (leading _)
mkdir -p "$tmp/.git"                         # excluded (leading .)
mkdir -p "$tmp/Not A Brain"                  # excluded (no .obsidian)
mkdir -p "$tmp/.Project Context/PC One/.obsidian"
mkdir -p "$tmp/.Project Context/Not A Brain" # excluded (no .obsidian)

# Run the helper.
script="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/discover-brains.sh"
cd "$tmp"
output="$(bash "$script" | sort)"

expected="$(printf "%s\n" \
  "Brain A" \
  "Brain B" \
  ".Project Context/PC One" | sort)"

if [[ "$output" != "$expected" ]]; then
  echo "FAIL"
  echo "expected:"
  echo "$expected"
  echo "got:"
  echo "$output"
  exit 1
fi

echo "PASS"
