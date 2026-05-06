---
name: obsidianify
description: Produce <brain>/Vault/ from <brain>/_pipeline/ per <brain>/_meta/obsidian.md. Incremental synthesis + structural sync.
---

# Obsidianify

Produces and maintains `<brain>/Vault/` from `<brain>/_pipeline/`. Incremental — only synthesizes new/changed pipeline entries. Structural sync (indexes, stats, drift, wikilinks) always runs.

## Inputs

- **brain folder** — absolute path.
- **`--dry-run`** (optional) — plan only, no LLM, no writes.
- **`--verbose`** (optional) — emit per-step info logs to stderr (per-entry synthesis decisions, structural-sync details). Composable with `--dry-run`.
- **`--drift-only`** (optional) — skip synthesis entirely; only run `.obsidian/*.json` drift detection (step 7f) against `_brain_template/.obsidian/`. Composable with `--dry-run` (= report-only, no overwrite prompts) and `--verbose`. Pre-flight is relaxed in this mode — see Pre-flight section.

## Pre-flight

Refuse and exit non-zero if:

1. `<brain>/_meta/obsidian.md` does not exist. Error: `No _meta/obsidian.md — fill in from _brain_template/_meta/obsidian.md before running obsidian phase.`
2. `<brain>/_meta/obsidian.md` contains any literal placeholder token: `<folder-1>`, `<folder-2>`, `<kind-a>`, `<kind-b>`, `<source-kind>`, `<section-headers>`, `<field-1>`, `<field-2>`, `<x>`, `<y>`, `<same shape, different prompt>`. Error: `_meta/obsidian.md has unfilled placeholders: <list>.`
3. `<brain>/_pipeline/_manifest.json` does not exist. Error: `No pipeline manifest — run /update-brain <brain> extract first.`
4. `<brain>/_meta/taxonomy.md` does not exist (required for Stats). Error: `Missing _meta/taxonomy.md.`

**Drift-only mode (`--drift-only`):** the four pre-flight checks above are skipped. Instead:

1. `<brain>/.obsidian/` does not exist → print `no .obsidian dir, nothing to drift` and exit 0.
2. `_brain_template/.obsidian/` does not exist → print error `template .obsidian missing` and exit non-zero.

If both exist, proceed directly to step 7f (skipping all other steps).

## Steps

### 1. Announce

Print `Obsidianifying <brain-folder>` (prefix `DRY RUN — ` if `--dry-run`; suffix ` [drift-only]` if `--drift-only`).

### 1a. Drift-only short-circuit

If `--drift-only` is set: skip steps 2–6 and steps 7a–7e + 7g + 8. Run only step 7f, then jump to step 9 (summary) — but emit a drift-only-flavored summary:

````
Obsidianify drift-only complete
  - <D> .obsidian drift prompts (<A> applied, <S> skipped)
````

Exit 0 after the summary.

### 2. Load state and manifest

- Read `<brain>/_pipeline/_manifest.json` via `scripts/extractify/lib/manifest.py` (or equivalent).
- Read `<brain>/_meta/synthesis-state.json` via `scripts/obsidianify/lib/state.py`. If missing, treat as empty.

### 3. Diff

Call `scripts/obsidianify/lib/pipeline_diff.py diff()` with `manifest["entries"]` vs `state["entries"]`. Get `DiffResult(new, changed, unchanged, removed)`.

Print:

```
Obsidian plan for <brain>:
  NEW      (N): <list, up to 20; then "... (<remaining> more)" if longer>
  CHANGED  (M): <same>
  UNCHANGED(K): <count only>
  REMOVED  (O): <list>
```

### 4. If `--dry-run`

Print the plan and proceed to step 7 (structural sync in read-only mode). Do not invoke LLM, do not write Vault notes.

### 5. Synthesize NEW + CHANGED entries

For each pipeline path in `new + changed`:

- Read the pipeline file via `scripts/extractify/lib/frontmatter.py`.
- Walk the current Vault tree (folder listing + note basenames — don't load bodies) for cross-linking context.
- Read `<brain>/_meta/obsidian.md` verbatim.
- Read `scripts/obsidianify/prompts/synthesize-note.md` verbatim.
- **Invoke LLM** (in-session Claude step, not via API): send the prompt + brain rules + pipeline body + Vault tree context. Parse the returned JSON.
- For each `generated_notes` entry:
  - Write the file at `path` using `scripts/extractify/lib/frontmatter.py` (frontmatter + body).
  - If the file already exists and action is `create`, this is a filename clash. Skip with warning: `WARN: <path> already exists; synthesis skipped for this note.`
- For each `updated_existing` entry:
  - Read the target file; skip entirely if its frontmatter has `locked: true`.
  - Find the `## Related` section. If present, append the new lines after the existing content. If missing, append the whole section at end-of-file.
  - Write back.
- Call `scripts/obsidianify/lib/state.py record_synthesis()` for the pipeline path with the list of `generated_notes` paths.

### 6. Handle REMOVED (orphans)

For each removed pipeline path:

- Look up its `generated_vault_notes` in the state file.
- **Do NOT delete** those Vault notes.
- Add each to `state["orphan_vault_notes"]` (dedupe on path).
- Print warning: `ORPHAN: <vault-note> — its source pipeline entry <pipeline-path> was removed. Delete manually if desired.`
- Remove the entry from `state["entries"]`.

### 7. Structural sync (always runs)

All sub-steps are idempotent. If `--dry-run` is set, each sub-step computes what would change and prints a unified diff or summary line per file, prefixed with `(dry-run, not applied)`, then does NOT write.

**7a. Walk Vault.** Build in-memory tree of `<brain>/Vault/`: per folder, count of `.md` files and sub-folder list. Exclude `Vault/` itself from the folder set — its entry file is `Vault/README.md`, not `_index.md`. Treat any file literally named `README.md` as a pseudo-`_index.md` (never listed as a regular note).

**7b. Leaf `_index.md` regen.** For every folder containing `.md` files (not counting `_index.md` or `README.md`):

- If `_index.md` exists: preserve everything above `## Index`; replace from `## Index` to the next `## ` or EOF with a fresh alphabetical listing (case-sensitive, locale-independent):

  ```markdown
  ## Index

  - [<basename>](<basename>.md)
  - [<basename>](<basename>.md)
  ```

- If `_index.md` does not exist: create with:

  ```markdown
  # <folder-name>

  > <short description — TODO>

  ## Index

  <listing>
  ```

  Warn: `WARN: created _index.md at <path> — add a description.`

**7c. Top-level `_index.md` `## Sub-folders` bullets.** For every folder whose children are all directories (no notes directly inside):

- Read/create `_index.md`.
- Parse `## Sub-folders`. Bullet shape: `` - [`<name>/`](<name>/_index.md) — <annotation>. (<count> note<s>) `` (singular "note" if count == 1).
- Match bullets by `<name>`. Update `<count>` from tree.
- New sub-folders on disk: append bullet with `— TODO: describe.` annotation and real count. Warn: `WARN: new sub-folder <name> — add annotation.`
- Bullets whose sub-folder no longer exists: remove.
- Preserve original bullet order. Alphabetize and append new ones.

**7d. `Vault/README.md` Stats.** Find `## Stats`.

- If missing: insert after `## Contents` (or at EOF if no Contents).
- Read existing section. **Preserve prose paragraphs that appear before the first table row.** Preserve trailing breakdown line (`^Concepts by topic:` or similar) — refresh its numbers from the walked tree.
- Rebuild the table using bucket list from `_meta/obsidian.md` `## Vault structure` bullets.

  Missing `## Vault structure` in `obsidian.md` → refuse step 7d/7e: `Cannot build stats without ## Vault structure in _meta/obsidian.md.`

**7e. `_meta/vault-stats.md`** — overwrite entirely:

```markdown
# Vault stats — generated <YYYY-MM-DD>

## Totals

| Bucket | Count |
|---|---:|
| <bucket-1> | <n> |
...
| **Total** | <sum> |

## Per sub-folder

### <bucket-1>/

| Sub-folder | Count |
|---|---:|
| <sub-1> | <n> |
...
```

Timestamp on line 1 is the only non-idempotent content.

**7f. `.obsidian/*.json` drift — prompt per file.** For each file that exists in `_brain_template/.obsidian/`:

- Diff byte-exact against `<brain>/.obsidian/<file>`. Identical → skip.
- Different: print unified diff (prefix each line with four spaces). Ask: `Overwrite <brain>/.obsidian/<file> with template? (yes/no/skip-all)`.
  - `yes` → copy template version over brain's version.
  - `no` → leave as-is.
  - `skip-all` → leave remaining files in this run untouched.

If `--dry-run`: don't prompt, just print diffs with `(dry-run, not applied)`.

Never touch `<brain>/.obsidian/` files not present in the template (`workspace.json` etc.).

**7g. Wikilink report.** Walk every `.md` under `<brain>/Vault/`. Scan each line with regex `\[\[([^\]|]+)(\|[^\]]+)?\]\]`. For each target:

- Strip `#anchor` or `|display`, keep leading path component.
- Resolve against `.md` files in `<brain>/Vault/` OR `<brain>/_pipeline/` (case-insensitive, basename-only). Resolved → skip. Unresolved → broken.

Write `<brain>/_meta/wikilink-report.md`:

```markdown
# Wikilink report — generated <YYYY-MM-DD>

<N> broken wikilinks found.

- `<vault-path>:<line>` → `[[<target>]]` (not found)
...
```

If N=0, write `0 broken wikilinks.` on its own line.

If `--dry-run`: print the summary but don't write.

### 8. Save state

Update `state["last_run"]` to current ISO 8601 UTC. Call `save()` to `<brain>/_meta/synthesis-state.json`. Skip if `--dry-run`.

### 9. Print summary

```
Obsidianify complete
  - <N> new, <M> changed, <K> unchanged, <O> removed-as-orphan
  - <L> leaf indexes regenerated (<C> created new)
  - <T> top-level indexes updated (<Nn> new sub-folders flagged)
  - Vault/README.md Stats refreshed (<B> buckets)
  - _meta/vault-stats.md regenerated
  - <D> .obsidian drift prompts (<A> applied, <S> skipped)
  - <W> broken wikilinks → _meta/wikilink-report.md
```

## Notes

- When `--verbose` is passed, helper functions in `scripts/obsidianify/lib/` emit `INFO: …` lines to stderr via `lib/log.py:log_info`. Synthesis prompts continue to surface via the agent loop as usual; verbose only adds deterministic-step visibility.
- `--drift-only` lets you check whether a brain's `.obsidian/*.json` config has diverged from `_brain_template/.obsidian/`. Multi-brain drift checks are a one-line shell loop:

  ````bash
  for brain in $(scripts/_lib/discover-brains.sh); do
    # Invoke obsidianify skill with: <brain> --drift-only --dry-run
  done
  ````
