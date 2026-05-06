# Brains starter kit

A starter kit for building local, file-based knowledge bases ("brains") that Claude Code can query, extract from, and synthesize into curated Obsidian vaults.

You drop raw stuff into a brain (`_raw/`). The pipeline cleans, frontmatters, and content-hashes each file (`_pipeline/`). Claude synthesizes a curated, cross-linked Vault from the pipeline (`Vault/`). Optionally, you graphify the whole thing (`graphify-out/`) to see the connections you didn't know were there.

The point is to build a knowledge base you can actually query — instead of a folder of PDFs you'll never read again.

---

## What you get

**Folders**

- `_brain_template/` — the seed for a new brain. Copied by `/new-brain` into a new folder.
- `scripts/` — the engine. Four pieces that the slash commands delegate to:
  - `_lib/discover-brains.sh` — finds every brain in the repo (looks for `.obsidian/`).
  - `extractify/` — walks `_raw/` and produces `_pipeline/` with a manifest. Built-in handlers for `.md` `.pdf` `.docx` `.epub` `.mp4` `.mov` `.m4a` `.mp3` `.wav` (Whisper).
  - `obsidianify/` — diffs the pipeline manifest against synthesis state and runs LLM synthesis on new/changed entries; regenerates indexes, stats, wikilink reports, `.obsidian/` drift checks.
  - `graphify/` — turns the curated content into an interactive knowledge graph (HTML + JSON + audit report).
  - `new-brain/` — the scaffolder. Drives a four-question conversation, copies the template, fills in `_meta/*.md`, and registers the brain.
- `.claude/commands/` — slash commands: `/new-brain`, `/update-brain`, `/graphify`, `/ask-brain`.
- `docs/brain-migration-recipe.md` — how to migrate an existing knowledge folder into a brain.

**Slash commands**

- **`/new-brain "<Brain Name>"`** — scaffold a new brain. Add `--project-context` to put it under `.Project Context/` (private/opt-in tier).
- **`/update-brain <alias> [phase]`** — extract → synthesize → graph. Phase defaults to `all`. `extract`, `obsidian`, `graph` are also valid. Add `--dry-run` to plan without writing.
- **`/graphify <alias>`** — build a knowledge graph for one brain.
- **`/ask-brain <question>`** — query the brains. Routes via `CLAUDE.md`.

---

## Mental model

Every brain has the same four-stage shape:

```
_raw/  →  _pipeline/  →  Vault/  →  graphify-out/
(dump)    (cleaned,    (synthesized,  (graph + audit)
          frontmattered, curated,
          hashed,       cross-linked
          manifested)   notes)
```

`_meta/{extract,obsidian,taxonomy}.md` are the rules files that drive the transitions:

- `extract.md` tells Extractify which `_raw/` subfolders feed which `_pipeline/` subfolders, and which extractor command runs each.
- `obsidian.md` tells Obsidianify how to synthesize Vault notes from pipeline entries — folder layout, per-source-kind synthesis prompts, classification, cross-ref discipline.
- `taxonomy.md` is the brain's vocabulary — what qualifies as which kind of note, how things are named.

The pipeline is the **source of truth**. Vault and graphify-out are derived. If you blow away `Vault/` and re-run `/update-brain`, it rebuilds.

---

## Setup

### Prerequisites

- **Claude Code.** The slash commands and synthesis steps live inside Claude Code. Install from <https://claude.com/claude-code>.
- **Python 3.11+.** Used by `extractify`, `obsidianify`, `graphify`.
- **(optional) Obsidian.** `Vault/` is a regular Obsidian vault — open the brain folder in Obsidian to browse with backlinks, graph view, etc.

### One-time install

```bash
# 1. Drop this folder anywhere on disk. The path can have spaces.

# 2. Install the Python dependencies.
cd scripts/extractify
pip install -r requirements-dev.txt

# 3. Install graphify (it ships as a package in the repo).
cd ../graphify
pip install -e .

# 4. (optional) Run the test suite to make sure the install works.
cd ../extractify
pytest
cd ../new-brain
pytest
cd ../obsidianify
pytest
```

### Open this folder in Claude Code

Open the repo root (the folder containing this README) as a Claude Code workspace. The slash commands in `.claude/commands/` will be discovered automatically. `CLAUDE.md` is auto-loaded as the router.

### (optional) Make `/ask-brain` callable from any project

Copy `.claude/commands/ask-brain.md` into your user-level `~/.claude/commands/` and edit the references to "the repo root" to be your absolute path to this folder. Then `/ask-brain <question>` works from any Claude Code session on your machine.

---

## Build your first brain

```
/new-brain "My First Brain"
```

The skill will ask you four questions:

1. **Scope.** What does this brain know, and what does it *not* know? When should the router pick it?
2. **Source kinds.** What raw inputs will you dump into `_raw/`? (e.g. `transcripts → _raw/transcripts/, audio transcripts as .md`)
3. **Vault structure.** What top-level folders should `Vault/` have? (e.g. `concepts/`, `patterns/`, `sources/`)
4. **Synthesis intent.** For each source-kind, which Vault folder(s) does it produce, what frontmatter, what body sections?

When the four questions are answered, the skill writes a fully-fleshed brain — every `_meta/*.md` file filled in, no placeholder tokens left, both Extractify and Obsidianify pre-flights pass.

Then:

```bash
# Drop your raw files into _raw/<subpath>/, then:
/update-brain my-first extract       # _raw/ → _pipeline/
/update-brain my-first obsidian      # _pipeline/ → Vault/  (LLM synthesis, costs tokens)
/update-brain my-first graph         # Vault/ → graphify-out/
# or run all three:
/update-brain my-first all
```

`/update-brain` is incremental — only new/changed pipeline entries get re-synthesized. Re-running on an unchanged brain is cheap.

---

## Project tier (private brains)

If you want a brain that the router does **not** automatically consult — e.g. a brain about your company, a client, a private project — scaffold it with `--project-context`:

```
/new-brain "My Company" --project-context
```

It lives under `.Project Context/My Company/`. `/ask-brain` will only consult it if the user explicitly names it.

---

## Migrating an existing knowledge folder

If you already have a folder of PDFs / notes / transcripts and want to turn it into a brain, follow `docs/brain-migration-recipe.md`. Eight steps. The hard part is deciding whether to clean-rebuild your existing Vault from raw (option A) or seed it as "already synthesized" so future runs only touch net-new entries (option B).

---

## How the slash commands fit together

```
/new-brain      → scripts/new-brain/skill.md     (scaffold)
/update-brain   → scripts/extractify/skill.md     (phase 1)
                → scripts/obsidianify/skill.md    (phase 2)
                → scripts/graphify/skill.md       (phase 3)
/graphify       → scripts/graphify/skill.md       (just the graph)
/ask-brain      → CLAUDE.md (router)              (query-only)
```

The slash commands are thin — they parse arguments, validate, and delegate to the skill files under `scripts/`. The skill files are the actual instructions to Claude.

---

## Conventions

- **Brains are read-only for queries.** `/ask-brain` never edits a brain. Only `/update-brain` and `/new-brain` write to brain folders.
- **No auto-stage, no auto-commit.** Slash commands always end with `git status --short` (if it's a git repo). You decide what to commit.
- **Pipeline is committed; raw is your call.** `_pipeline/` is the source of truth and should be committed. `_raw/` can be committed, gitignored, or partially gitignored — see step 8 of the migration recipe.
- **`graphify-out/` is derived.** Re-runnable. Commit if you want graph-state to round-trip across machines, gitignore otherwise.

---

## Troubleshooting

**`/update-brain` refuses with "unfilled placeholders".** You scaffolded a brain manually (or `/new-brain` was interrupted) and `_meta/extract.md` or `_meta/obsidian.md` still has `<kind-1>`-style tokens. Fill them in (or re-run `/new-brain` on a fresh folder name).

**Extractor errors on a source kind not in the built-in list.** The shared library at `scripts/extractify/lib/sources/` handles `.md`, `.pdf`, `.docx`, `.epub`, and `.mp4 / .mov / .m4a / .mp3 / .wav` via Whisper. For anything else, add a handler module to `scripts/extractify/lib/sources/` and register it in `REGISTRY` — every brain (current and future) picks it up automatically. Don't put new source-kind handlers in per-brain code.

**Whisper is slow / wrong vocabulary.** See the docstring in `scripts/new-brain/extractor-template/code/run.py` for the per-brain Whisper override pattern.

**A new source kind not handled.** Add a handler module to `scripts/extractify/lib/sources/` and register it in `REGISTRY`. Don't put new source-kind handlers in per-brain code — every future brain should pick it up automatically.

---

## License & credits

The `scripts/graphify/` package is included in this repo. Graphify is its own thing — see <https://github.com/sponsors/safishamsi> if it saves you time.

The rest is yours to fork, modify, and ship. No attribution required.
