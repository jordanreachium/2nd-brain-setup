# scripts/new-brain/

Implementation of the `/new-brain` slash command. Scaffolds a brain with no placeholder tokens left behind — Extractify and Obsidianify pre-flights pass on the result.

## Pieces

- **`skill.md`** — the LLM-driven skill. `/new-brain` delegates here. Drives the four-question conversation, then writes every `_meta/*.md` file plus `Vault/README.md`, top-level `README.md`, real Vault folders, and `_raw/<subpath>/.gitkeep` stubs. For General Brains, also edits `CLAUDE.md` and `.claude/commands/update-brain.md`.
- **`seed-brain.sh`** — the deterministic copy step. Copies `_brain_template/` to either `<repo>/<name>/` (default) or `<repo>/.Project Context/<name>/` (`--project-context`). Called by the skill; not a public entry point.
- **`tests/`** — pytest tests for `seed-brain.sh` (subprocess + tmp-dir fake repo).

## Running

```bash
# Public entry point — runs the full conversation:
/new-brain "My New Brain"
/new-brain "My New Brain" --project-context

# Low-level scaffolding only (no _meta fill-in, no router edits):
bash scripts/new-brain/seed-brain.sh "My New Brain"

# Tests:
python -m pytest scripts/new-brain/tests/ -v
```

## Related

- `scripts/obsidianify/skill.md` — invoke with `--drift-only` to drift-check existing brains' `.obsidian/` config against `_brain_template/.obsidian/`.
- [`docs/brain-migration-recipe.md`](../../docs/brain-migration-recipe.md) — eight-step recipe for migrating an existing knowledge folder into a brain.
