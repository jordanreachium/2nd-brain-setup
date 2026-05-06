# Brain migration recipe

Migrating an existing knowledge folder (an Obsidian vault, a folder of PDFs, a transcript dump, etc.) into a brain that uses the pipeline-as-source-of-truth architecture. Each brain migrates in its own session.

## Overview

Every brain migration goes through the same eight steps.

## Steps

### 1. Author `<brain>/_meta/extract.md`

Declare which `_raw/` sources feed which `_pipeline/` subfolders and which extractor runs each. Copy the template from `_brain_template/_meta/extract.md`, fill in every placeholder, commit.

### 2. Author `<brain>/_meta/obsidian.md`

Synthesis rules: Vault structure, per-kind synthesis prompts, classification, cross-ref discipline. Lift rules from the brain's existing Vault shape (if it has one) — concepts, patterns, sources, etc. Copy from `_brain_template/_meta/obsidian.md`, fill in every placeholder, commit.

### 3. Extractor

Most new brains do not need to write any extractor code. The shared source library at `scripts/extractify/lib/sources/` handles `.md`, `.pdf`, `.docx`, `.epub`, and audio/video files (`.mp4`, `.mov`, `.m4a`, `.mp3`, `.wav` via Whisper) out of the box.

Your brain's `code/run.py` is a one-liner re-export — see `scripts/new-brain/extractor-template/code/run.py` for the default shape. `/new-brain` seeds this for you automatically.

Customize only when:

- **Whisper needs brain-specific tuning** (vocabulary prompt, model size). Override pattern documented in the template's `code/run.py` docstring.
- **The brain has a brand-new source kind** not in the library. **Add the handler to `scripts/extractify/lib/sources/`** (with tests under `scripts/extractify/tests/sources/`), register it in `REGISTRY`, then your brain (and every future brain) gets it automatically. Don't put new source-kind handlers in per-brain code.

#### Fetchers (optional)

If your brain ingests from URLs (YouTube, web articles), use the library fetcher CLIs:

```bash
# Run from scripts/extractify/
cd scripts/extractify
python -m lib.sources.fetchers.youtube <url> --out "../../<brain>/_raw/transcripts/"
python -m lib.sources.fetchers.article <url> --out "../../<brain>/_raw/articles/"
```

Both write `<id>.md` with provenance frontmatter to `_raw/`. The next `/update-brain <brain> extract` phase picks them up via the markdown handler (which strips fetch-time frontmatter and lets Extractify overlay its own).

### 4. Run `/update-brain <brain> extract --dry-run`

Verify the extract plan matches expectations. Fix `_meta/extract.md` wiring if wrong. Re-run until the plan is right.

### 5. Run `/update-brain <brain> extract`

Produces a fresh `_pipeline/` under the contract (one `.md` per source, with YAML frontmatter). Review `_pipeline/` visually. Commit.

### 6. Decide Vault strategy

**Option A: clean rebuild.** If the existing Vault is thin or machine-regenerable:

```bash
git rm -r <brain>/Vault/<content-folders>/  # keep README.md + structural
```

Then `/update-brain <brain> obsidian` rebuilds Vault entirely from pipeline via LLM synthesis. Expensive first run. Loses hand-authored Vault editorial work. Future runs are incremental.

**Option B: seed existing Vault as "already synthesized."** If the existing Vault has hand-authored quality worth preserving:

Hand-author an initial `<brain>/_meta/synthesis-state.json` that maps each new pipeline entry to the existing Vault notes it conceptually produced. Use `scripts/obsidianify/lib/state.py empty_state()` as the starting shape; populate `entries` with the mapping; populate each entry's `content_hash` from the pipeline manifest.

Future `/update-brain <brain> obsidian` runs will only synthesize net-new pipeline entries. Preserves editorial work. Higher friction per brain.

Commit the state file or deleted-Vault either way.

### 7. Run `/update-brain <brain> graph`

Regenerates `graphify-out/` against the new Vault. Review `GRAPH_REPORT.md` for sanity. Commit.

### 8. Decide `_raw/` commit policy

Per-brain call. Options:
- `git rm -r _raw/ && echo "_raw/" >> <brain>/.gitignore` — clean break.
- Keep already-committed raw content committed; add `_raw/**/*` to `.gitignore` so *new* raw content stays local.
- Move raw content that's already cleaned `.md` into `_pipeline/` so files aren't lost.

Commit whatever you choose.
