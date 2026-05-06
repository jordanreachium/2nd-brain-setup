#!/usr/bin/env bash
# Test seed-extractor.sh against a fake repo layout.
set -euo pipefail

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Mirror just enough of repo layout: scripts/new-brain/extractor-template/ and
# scripts/extractify/brains/ as the target parent.
mkdir -p "$tmp/scripts/new-brain"
cp -r "scripts/new-brain/extractor-template" "$tmp/scripts/new-brain/extractor-template"
mkdir -p "$tmp/scripts/extractify/brains"
cp scripts/new-brain/seed-extractor.sh "$tmp/scripts/new-brain/seed-extractor.sh"
chmod +x "$tmp/scripts/new-brain/seed-extractor.sh"

cd "$tmp"

# Happy path
bash scripts/new-brain/seed-extractor.sh "test-brain"

# Verify structure copied
test -f "scripts/extractify/brains/test-brain/code/run.py" || { echo "FAIL: run.py not copied"; exit 1; }
test -f "scripts/extractify/brains/test-brain/tests/test_run.py" || { echo "FAIL: tests not copied"; exit 1; }
test -f "scripts/extractify/brains/test-brain/pyproject.toml" || { echo "FAIL: pyproject.toml not copied"; exit 1; }

# Verify slug substitution
if ! grep -q 'name = "brain-extractor-test-brain"' "scripts/extractify/brains/test-brain/pyproject.toml"; then
  echo "FAIL: slug not substituted in pyproject.toml"
  cat "scripts/extractify/brains/test-brain/pyproject.toml"
  exit 1
fi

# Refusal: existing target without --force
set +e
bash scripts/new-brain/seed-extractor.sh "test-brain" 2>/dev/null
rc=$?
set -e
if [[ $rc -eq 0 ]]; then echo "FAIL: should have refused existing target"; exit 1; fi

# --force overwrites
bash scripts/new-brain/seed-extractor.sh "test-brain" --force >/dev/null

# Bad slug rejected
set +e
bash scripts/new-brain/seed-extractor.sh "Bad Slug" 2>/dev/null
rc=$?
set -e
if [[ $rc -eq 0 ]]; then echo "FAIL: should have rejected uppercase slug"; exit 1; fi

echo "PASS"
