---
name: extractify
description: Produce <brain>/_pipeline/ from <brain>/_raw/ per <brain>/_meta/extract.md
---

# Extractify

Produces cleaned, hashed, frontmattered `.md` files under `<brain>/_pipeline/` from raw sources in `<brain>/_raw/`. Called by `/update-brain <brain> extract` or standalone.

## Inputs

- **brain folder** — absolute path to the brain (e.g. `<repo-root>/My Brain`).
- **`--dry-run`** (optional) — plan only, write nothing.
- **`--verbose`** (optional) — emit per-step info logs to stderr (file walks, classification decisions, manifest upserts). Helpful for debugging extract runs against new brains. Composable with `--dry-run`.

## Pre-flight

Refuse and exit non-zero if:

1. `<brain>/_meta/extract.md` does not exist. Error: `No _meta/extract.md — fill in from _brain_template/_meta/extract.md before extracting.`
2. `<brain>/_meta/extract.md` contains any literal placeholder token: `<kind-1>`, `<kind-2>`, `<raw-path-1>`, `<raw-path-2>`, `<ext>`, `<extractor-cmd-1>`, `<extractor-cmd-2>`, `<gotcha-1>`, `<gotcha-2>`. Error: `_meta/extract.md has unfilled placeholders: <list of tokens found>.`
3. `<brain>/_raw/` does not exist. Error: `No _raw/ directory — nothing to extract from.`

## Steps

1. **Announce:** `Extracting <brain-folder>` (prefix `DRY RUN — ` if `--dry-run`).

2. **Parse `_meta/extract.md` `## Sources`.** Each bullet is a source-kind wiring. Extract three fields per bullet:
   - `kind` — the bolded name.
   - `raw_glob` — the `_raw/...` path pattern (everything between the first backticks).
   - `extractor_cmd` — the command to run (everything between the "run" and "write to" segments).
   - `pipeline_subfolder` — the `_pipeline/<kind>/` target.

3. **Load manifest.** Read `<brain>/_pipeline/_manifest.json` via `python scripts/extractify/lib/manifest.py` (or import and call). If missing, start from `empty_manifest()`.

4. **For each source kind, walk raw glob:**
   - For each matched raw file:
     - Compute `content_hash` with `scripts/extractify/lib/hashing.py`.
     - Derive target pipeline path: `_pipeline/<kind>/<kebab_slug(stem)>.md` (use `scripts/extractify/lib/ids.py`).
     - Look up existing manifest entry for that target path.
     - **Classify:**
       - `UNCHANGED` — target path in manifest AND hashes match.
       - `CHANGED` — target path in manifest AND hashes differ.
       - `NEW` — target path not in manifest.
     - Record in the plan structure.

5. **Detect orphans.** For each manifest entry whose target pipeline path has NO matching raw source this run, mark `ORPHAN` in the plan.

6. **Print plan:**

   ```
   Extract plan for <brain>:
     NEW      (N): <path> ← <raw>
     CHANGED  (M): <path> ← <raw>
     UNCHANGED(K): <count only, no list>
     ORPHAN   (O): <path> — <raw source missing>
   ```

7. **If `--dry-run`:** stop. Do not write.

8. **Apply NEW + CHANGED:** for each entry:
   - Run the brain's extractor command (from source wiring) on the raw file. The extractor is responsible for writing the pipeline `.md` with cleaned body text (no frontmatter — the skill adds that).
   - After the extractor writes, overlay YAML frontmatter via `scripts/extractify/lib/frontmatter.py`:
     - `source_path`: raw file path (brain-relative).
     - `source_kind`: kind from wiring.
     - `extracted_at`: ISO 8601 UTC timestamp.
     - `content_hash`: hash computed in step 4.
   - Upsert the manifest entry.

9. **Leave ORPHANs in place.** Do NOT delete from pipeline or manifest. Print warning per orphan.

10. **Save manifest** to `<brain>/_pipeline/_manifest.json`.

11. **Print summary:** `Extractify complete — N new, M changed, K unchanged, O orphan.`

## Notes

- All LLM work is handled by the brain's extractor command (if any). This skill does not invoke an LLM directly — deterministic orchestration only.
- The extractor command is responsible for its own Python environment (venv, etc.). This skill only calls it as a subprocess.
- If an extractor command fails for a single source, print the error, skip that entry (don't update manifest for it), continue with the next. Final summary reports error count.
- When `--verbose` is passed, helper functions in `scripts/extractify/lib/` emit `INFO: …` lines to stderr via `lib/log.py:log_info`. The skill's deterministic helpers respect this; the brain's extractor command does not (it has its own logging or none).

## Universal gotchas

These failure modes show up regardless of source kind. Per-brain `_meta/extract.md` may add brain-specific gotchas; every extractor should handle these.

- **Video transcripts arrive as single-paragraph walls.** Whisper and most third-party transcription services return the entire transcript as one continuous line with no sentence or paragraph breaks. The extractor (or a downstream cleanup pass) must insert breaks before synthesis can index the content. Rule of thumb: split on `. ` at boundary detection, then group every 3–5 sentences into a paragraph.

- **Filename → slug mapping is lossy.** Numeric prefixes (`3. Section Title.mp4` → `03-section-title`), case sensitivity, special characters, and platform-specific identifiers (short URLs, video IDs) all degrade through slugification. Always preserve the original name in `source_path:` frontmatter so the round-trip is recoverable.

- **PDF glued tokens.** Text extracted from PDFs frequently merges adjacent words at line wraps and column boundaries (`thequickbrown` instead of `the quick brown`). Downstream synthesis should normalize, or the extractor should run a token-splitting pass.
