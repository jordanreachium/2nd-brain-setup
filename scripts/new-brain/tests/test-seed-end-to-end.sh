#!/usr/bin/env bash
# End-to-end: seed a brain folder + its extractor, then run the extractor's tests.
set -euo pipefail

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Mirror minimum repo layout
mkdir -p "$tmp/scripts/new-brain"
cp -r "scripts/new-brain/extractor-template" "$tmp/scripts/new-brain/extractor-template"
cp scripts/new-brain/seed-brain.sh "$tmp/scripts/new-brain/seed-brain.sh"
cp scripts/new-brain/seed-extractor.sh "$tmp/scripts/new-brain/seed-extractor.sh"
chmod +x "$tmp/scripts/new-brain/seed-brain.sh" "$tmp/scripts/new-brain/seed-extractor.sh"
mkdir -p "$tmp/scripts/extractify/brains"
cp -r "_brain_template" "$tmp/_brain_template"

cd "$tmp"

# Seed the brain folder
bash scripts/new-brain/seed-brain.sh "Test Brain"
test -d "Test Brain" || { echo "FAIL: brain folder not seeded"; exit 1; }

# Seed the extractor
bash scripts/new-brain/seed-extractor.sh "test-brain"
test -f "scripts/extractify/brains/test-brain/code/run.py" || { echo "FAIL: extractor not seeded"; exit 1; }

# Run the seeded extractor's tests
cd "scripts/extractify/brains/test-brain"
python -m pytest tests/ -q
cd "$tmp"

echo "PASS"
