#!/usr/bin/env bash
# Copy extractor-template into scripts/extractify/brains/<slug>/.
# Usage: scripts/new-brain/seed-extractor.sh "<slug>" [--force]
#
# Called by /new-brain after seed-brain.sh has created the brain folder.
# The slug must already match the slug rule (lowercase, kebab-case).

set -euo pipefail

usage() {
  echo "Usage: $0 \"<slug>\" [--force]" >&2
  exit 2
}

slug=""
force=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) force=1; shift ;;
    --*)
      echo "ERROR: unknown flag '$1'" >&2
      usage
      ;;
    *)
      if [[ -z "$slug" ]]; then
        slug="$1"; shift
      else
        echo "ERROR: too many positional arguments" >&2
        usage
      fi
      ;;
  esac
done

if [[ -z "$slug" ]]; then
  usage
fi

# slug shape check (lowercase, digits, hyphens only — no path traversal possible)
if [[ ! "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "ERROR: slug must be lowercase kebab-case (got '$slug')" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"

template_dir="$script_dir/extractor-template"
target_dir="$repo_root/scripts/extractify/brains/$slug"

if [[ ! -d "$template_dir" ]]; then
  echo "ERROR: extractor template not found at $template_dir" >&2
  exit 1
fi

if [[ -e "$target_dir" ]]; then
  if [[ $force -eq 0 ]]; then
    echo "ERROR: target already exists: $target_dir" >&2
    echo "       pass --force to overwrite" >&2
    exit 1
  fi
  echo "Removing existing target (--force): $target_dir"
  rm -rf "$target_dir"
fi

mkdir -p "$(dirname "$target_dir")"
echo "Seeding extractor: $template_dir -> $target_dir"
cp -r "$template_dir" "$target_dir"

# Substitute the placeholder name in pyproject.toml so each brain's extractor
# has a distinct package identity.
pyproject="$target_dir/pyproject.toml"
if [[ -f "$pyproject" ]]; then
  sed -i.bak "s/^name = \"brain-extractor-template\"$/name = \"brain-extractor-$slug\"/" "$pyproject"
  rm -f "$pyproject.bak"
fi

echo "Done. Extractor stub ready at $target_dir."
