#!/usr/bin/env bash
# Seed a new brain folder from _brain_template/.
# Usage: scripts/new-brain/seed-brain.sh "<Brain Name>" [--force] [--project-context]
#
# This is the deterministic-copy implementation detail of /new-brain. End users
# should call /new-brain (which drives the conversational fill-in); call this
# script directly only for low-level scaffolding or tests.

set -euo pipefail

usage() {
  echo "Usage: $0 \"<Brain Name>\" [--force] [--project-context]" >&2
  exit 2
}

# --- arg parsing ---
brain_name=""
force=0
project_context=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) force=1; shift ;;
    --project-context) project_context=1; shift ;;
    --*)
      echo "ERROR: unknown flag '$1'" >&2
      usage
      ;;
    *)
      if [[ -z "$brain_name" ]]; then
        brain_name="$1"
        shift
      else
        echo "ERROR: too many positional arguments" >&2
        usage
      fi
      ;;
  esac
done

if [[ -z "$brain_name" ]]; then
  usage
fi

# --- input validation (prevents rm -rf of the repo via empty / traversal names) ---
if [[ -z "${brain_name// }" ]]; then
  echo "ERROR: brain name must not be empty or whitespace" >&2
  exit 2
fi
if [[ "$brain_name" == */* || "$brain_name" == *\\* || "$brain_name" == *..* ]]; then
  echo "ERROR: brain name must not contain '/', '\\', or '..'" >&2
  exit 2
fi
if [[ "$brain_name" == --* ]]; then
  echo "ERROR: brain name must not start with '--' (looks like a flag)" >&2
  exit 2
fi

# --- locate repo root (script lives in <repo>/scripts/new-brain/) ---
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"

template_dir="$repo_root/_brain_template"
if [[ $project_context -eq 1 ]]; then
  target_parent="$repo_root/.Project Context"
else
  target_parent="$repo_root"
fi
target_dir="$target_parent/$brain_name"

# --- preconditions ---
if [[ ! -d "$template_dir" ]]; then
  echo "ERROR: template not found at $template_dir" >&2
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

# --- ensure target parent exists (.Project Context/ may not yet exist on a fresh repo) ---
mkdir -p "$target_parent"

# --- copy ---
echo "Seeding: $template_dir -> $target_dir"
cp -r "$template_dir" "$target_dir"

echo "Done. For the full guided setup, run /new-brain instead. Manual next steps:"
echo "  1. Fill $target_dir/Vault/README.md"
echo "  2. Fill $target_dir/_meta/{taxonomy,extract,obsidian}.md"
echo "  3. Replace example-folder/, update README.md, register in CLAUDE.md."
