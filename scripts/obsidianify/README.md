# Obsidianify

Produces `<brain>/Vault/` from `<brain>/_pipeline/`. Incremental — only synthesizes new or changed pipeline entries; existing Vault notes stay stable.

- `skill.md` — entry point Claude follows per `/update-brain <brain> obsidian`.
- `lib/` — deterministic Python helpers (state-file I/O, pipeline-vs-state diff).
- `prompts/` — shared synthesis prompt templates. Per-brain rules live in each brain's `_meta/obsidian.md`.
- `tests/` — pytest suite for `lib/` helpers.

## Running tests

```bash
pip install pyyaml pytest
cd scripts/obsidianify
pytest
```

## Synthesis state

Each brain tracks its synthesis history in `<brain>/_meta/synthesis-state.json`. This file records which pipeline entries have been synthesized and which Vault notes each produced — used for incremental runs.
