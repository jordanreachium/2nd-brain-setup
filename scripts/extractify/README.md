# Extractify

Produces `<brain>/_pipeline/` from `<brain>/_raw/`.

- `skill.md` — entry point Claude follows per `/update-brain <brain> extract`.
- `lib/` — deterministic Python helpers (hashing, frontmatter, ids, manifest) imported by both the skill (via CLI) and by per-brain extractors (via import).
- `brains/<brain>/` — per-brain extraction code. Each brain owns its own extractor module; the shared `lib/` is imported for common operations.
- `tests/` — pytest suite for `lib/` helpers.

## Running tests

```bash
pip install pyyaml pytest
cd scripts/extractify
pytest
```

## Wiring a new brain

Populate `brains/<brain>/` with the brain's extractor. Author `<brain>/_meta/extract.md` pointing at the commands to run. See the brain-migration recipe at `docs/brain-migration-recipe.md`.
