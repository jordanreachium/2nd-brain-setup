---
name: new-brain
description: Scaffold a new General or Project Context brain. Asks four questions, then writes every _meta/*.md plus Vault/README.md, top-level README.md, real Vault folders, _raw/<subpath>/.gitkeep stubs, and (for General Brains) router/alias entries. Result has no placeholder tokens left.
---

# New Brain

Scaffold a new brain end-to-end. Called by `/new-brain "<name>" [--project-context]`.

After this skill runs:
- Every `_meta/*.md` file (`extract.md`, `obsidian.md`, `taxonomy.md`) contains real content — **no placeholder tokens** like `<kind-1>` or `<folder-1>` remain.
- `Vault/README.md` has all five sections filled.
- Real Vault folders exist (with `_index.md` per folder); `example-folder/` is removed.
- `_raw/<subpath>/.gitkeep` stubs exist per source-kind.
- For General Brains: `CLAUDE.md` and `.claude/commands/update-brain.md` have new entries.
- Both Extractify and Obsidianify pre-flights pass.

## Inputs

- **brain name** — display name, e.g. `"Foo Brain"`. Required.
- **`--project-context`** (optional) — write under `.Project Context/<name>/` instead of `<repo>/<name>/`.

## Pre-flight

Refuse and exit non-zero if:

1. CWD is not the repo root (the folder containing `_brain_template/` and `scripts/`). Error: `Run /new-brain from the brains repo root.`
2. `_brain_template/` does not exist. Error: `No _brain_template/ — repo is not in expected shape.`
3. `scripts/new-brain/seed-brain.sh` does not exist. Error: `seed-brain.sh missing.`
4. Target folder already exists:
   - General: `<repo>/<name>/`
   - Project Context: `<repo>/.Project Context/<name>/`
   Error: `Target already exists: <path>. rm -rf manually if you want a redo (no --force at the slash level).`
5. Brain name fails validation (empty/whitespace, contains `/`/`\`/`..`, starts with `--`). Error: surface the specific reason.

## Steps

### 1. Announce

Print `Scaffolding "<name>"` (suffix ` (Project Context tier)` if `--project-context`).

### 2. Q1 — Scope and call-out

Ask the user:

> Describe the brain in 2 sentences: what does it know (and *not* know), and when should the router pick it?

Wait for response. Capture:
- `scope_paragraph` — full answer
- `call_out_clause` — the "router should pick this brain when..." part, restated as imperative ("Call it for: ...")

### 3. Q2 — Source kinds

Ask:

> What kinds of raw inputs will you dump into `_raw/`? For each, give: a kebab-case name, the subpath under `_raw/`, and a one-line note about the format.
>
> Example: `transcripts → _raw/transcripts/, audio transcripts as .md`

Wait for response. Parse into a list of `{kind, raw_subpath, format_note}` triples. Each `kind` must be kebab-case; `raw_subpath` must be a relative path with no `..`. If parsing fails or an entry is malformed, ask the user to clarify before proceeding.

If the user provides 0 source-kinds, warn: `No source kinds — extract phase will be a no-op until you add some.` Accept and continue.

### 4. Q3 — Vault folder structure

Ask:

> What top-level folders should `Vault/` have? For each: kebab-case name, one-line purpose, optional 'what doesn't go here'.

Wait for response. Parse into a list of `{folder, purpose, excludes}` (where `excludes` is optional). Each `folder` must be kebab-case.

If 0 folders → refuse: `Brain needs at least one Vault folder.` Re-ask Q3.

### 5. Q4 — Synthesis intent

Ask:

> For each source-kind from Q2, which Vault folder(s) does it produce, what frontmatter fields, what body sections?
>
> Example: `transcripts → notes/, frontmatter {topic, speakers, duration_minutes}, body sections "Summary, Key points, Open questions"`

Wait for response. Parse into a list of `{source_kind, vault_folders, frontmatter_fields, body_sections}`.

Validate:
- Each `source_kind` must match a kind from Q2.
- Each entry in `vault_folders` must match a folder from Q3.
- If mismatch, surface specifically which token is unrecognized and ask user to fix.

### 6. Build the plan

Compute:
- `bare_name` — strip a trailing ` Brain` (case-insensitive) from the brain name. Examples: `"Foo Bar Brain"` → `"Foo Bar"`; `"Foo"` → `"Foo"`; `"My Brain"` → `"My"`.
- `slug` — kebab-case form of `bare_name`. Examples: `"Foo Bar"` → `foo-bar`; `"My Project"` → `my-project`; `"Foo"` → `foo`.
- `aliases`:
  - If `slug` contains `-`: `[slug.split("-")[0], slug]` (e.g. `foo`, `foo-bar`).
  - Otherwise: `[slug, slug + "-brain"]` (e.g. `foo`, `foo-brain`).
- `target_dir`:
  - If `--project-context`: `<repo>/.Project Context/<name>/`.
  - Otherwise: `<repo>/<name>/`.
- `tier_label` — `"General"` or `"Project Context"`.

Check alias collisions (General Brains only): read `.claude/commands/update-brain.md`, parse the existing alias table, and check for overlap with the computed `aliases`. If collision, drop the colliding alias and surface a warning.

### 7. Print plan and confirm

Print:

```
Plan for "<name>":
  Tier: <tier_label>
  Folder: <target_dir>
  Vault structure: <comma-list of folders from Q3>
  Sources: <comma-list of kinds from Q2>
  Synthesis: <kind> → <folder> mappings from Q4 (one per line)
  Router entry: <CLAUDE.md anchor location>
  Aliases: <list>                    (only if General; "—" if Project Context)
  Files: 5 base + <Q3-folder-count> folder _index.md + <Q2-source-count> raw .gitkeep

Proceed? (yes/no)
```

Wait for response. Anything other than `yes` (case-insensitive) → exit cleanly without writing.

### 8. Run seed-brain.sh

Execute:

```bash
bash scripts/new-brain/seed-brain.sh "<name>" [--project-context]
```

If exit code is non-zero, surface stderr and abort.

### 8.5. Seed the extractor stub

After `seed-brain.sh` succeeds, seed the extractor stub:

```bash
bash scripts/new-brain/seed-extractor.sh "<slug>"
```

Where `<slug>` is the kebab-case slug derived during the conversation (e.g. `Foo Bar Brain` → `foo-bar`). This drops a runnable extension-dispatch extractor at `scripts/extractify/brains/<slug>/` so `/update-brain <brain> extract` works on day one. The user can extend the extractor in `code/run.py` as new source kinds are added to `_meta/extract.md`.

### 9. Overwrite _meta/extract.md

Write `<target>/_meta/extract.md`:

```markdown
# Extract rules

> This file tells `/update-brain <brain> extract` what raw sources to process and where their pipeline outputs live.

## Sources

<one bullet per Q2 entry, in this exact form:>
- **<kind>** — `_raw/<raw_subpath>/*` → run `python -m code` from `scripts/extractify/brains/<slug>/`, write to `_pipeline/<kind>/`

## Output contract

Every pipeline file this brain produces:

- Is `.md` with YAML frontmatter containing at minimum: `source_path`, `source_kind`, `extracted_at` (ISO 8601), `content_hash` (sha256).
- Lives under `_pipeline/<kind>/<stable-slug>.md`. The slug is kebab-case derived from the source's primary identifier.
- Body is cleaned prose — NOT classified or synthesized yet. That's Obsidianify's job.

## Skip / gotchas

- (none yet — add per-source rules here as they emerge)
```

The seeded `scripts/extractify/brains/<slug>/code/` module handles the built-in source kinds (`.md`, `.pdf`, `.docx`, `.epub`, audio/video) out of the box via `lib.sources.auto_extract`. First `/update-brain extract` should succeed for any built-in kind. For new source kinds, add a handler to `scripts/extractify/lib/sources/` and register it in `REGISTRY` — every brain picks it up automatically.

### 10. Overwrite _meta/obsidian.md

Write `<target>/_meta/obsidian.md`:

```markdown
# Obsidian synthesis rules

> This file tells `/update-brain <brain> obsidian` how to synthesize Vault notes from pipeline entries.

## Vault structure

<one bullet per Q3 entry:>
- **<folder>** — <purpose>

## Synthesis prompts

<one section per Q2 source-kind, pulling vault target + frontmatter + body sections from Q4:>

### <kind> → <vault_folder> notes

When a pipeline entry has `source_kind: <kind>`, synthesize one Vault note in `Vault/<vault_folder>/<kebab-slug>.md` with frontmatter `{<frontmatter_fields>}` and body sections `<body_sections>`. Link back to source as `[[_pipeline/<kind>/<slug>]]`.

## Classification

<map each Q2 source-kind to its Q4 vault_folder(s):>
- `source_kind: <kind>` → <vault_folder> note(s)

## Cross-ref discipline

When Obsidianify synthesizes a new note, it may append links to existing Vault notes' `## Related` section if the new note creates a backlink. Existing prose in other sections is never touched. Notes with `locked: true` in their frontmatter are skipped entirely — not even `## Related` updates.
```

### 11. Overwrite _meta/taxonomy.md

Write `<target>/_meta/taxonomy.md`:

```markdown
# Taxonomy

The brain's vocabulary and folder map.

## Folder map

<one bullet per Q3 entry:>
- **`Vault/<folder>/`** — <purpose>. <if excludes provided: "Doesn't include <excludes>.">

## Note types

- `concept` — atomic mental model
- `pattern` — reusable structure with slots
- `source` — primary text the brain was distilled from

## Naming

Slugs are kebab-case. Example: `state-machine-pattern.md`, not `StateMachinePattern.md`.
```

### 12. Overwrite Vault/README.md

Write `<target>/Vault/README.md`:

```markdown
# <name>

> <one-line tagline derived from Q1 scope>

## Scope

<scope_paragraph from Q1>

## Contents

<one bullet per Q3 folder:>
- **`<folder>/`** — <purpose>

Each folder has its own `_index.md`.

## Stats

<empty 2-column table — Obsidianify regenerates on first synth run:>

| Category | Count |
|---|---:|

## How to use this brain

<dispatch table — one bullet per Q4 vault_folder, derived from source-kind → folder mapping:>

- **For <Q1-derived intent>** → open `<folder>/_index.md`, then drill to a specific note

## Taxonomy

Vocabulary and folder conventions are in [`_meta/taxonomy.md`](../_meta/taxonomy.md).
```

### 13. Overwrite top-level README.md

Write `<target>/README.md`:

```markdown
# <name>

<one-line description from Q1>

**Entry file:** [`Vault/README.md`](Vault/README.md). The router lands here.

**Call it for:** <call_out_clause from Q1>
```

### 14. Replace Vault/example-folder/

Delete `<target>/Vault/example-folder/` (recursively).

For each Q3 folder, create `<target>/Vault/<folder>/_index.md`:

```markdown
# <Folder Name (title-cased from kebab)>

> <purpose from Q3>

## Index

(empty — Obsidianify will populate this when the first notes land here)
```

### 15. Stub _raw/<subpath>/.gitkeep

For each Q2 source-kind:
- Create the directory `<target>/_raw/<raw_subpath>/` (parents as needed).
- Write empty file `<target>/_raw/<raw_subpath>/.gitkeep`.

### 16. Router edits — General Brains only

Skip the rest of this step if `--project-context`.

**16a. CLAUDE.md.** Find the exact anchor `## General Brains` (literal heading line). If not found, print:

```
WARN: Couldn't find "## General Brains" anchor in CLAUDE.md. Paste this entry manually:

---

### <name> — <one-line tagline from Q1>

- **Entry file:** [<name>/Vault/README.md](<URL-encoded-name>/Vault/README.md) (five-section index — Scope, Contents, Stats, How to use, Taxonomy).
- **Knows:** <scope_paragraph from Q1>
- **Call it for:** <call_out_clause from Q1>
```

If anchor found: locate the alphabetically-correct insertion point (existing brain entries are `### Foo — ...` headings under that anchor). Insert the new entry there, with `---` separator before/after as needed to match existing formatting. Use `<name>` URL-encoded for the link target (e.g. `Foo Brain` → `Foo%20Brain`).

**16b. `.claude/commands/update-brain.md`.** Find the existing alias table (header `| Alias | Folder |`). If not found, print snippet to paste manually. If found: insert the new row alphabetically by alias:

```
| `<alias-1>`, `<alias-2>` | `<repo-root>/<name>` |
```

### 17. Router edit — Project Context only

Skip if not `--project-context`.

Find `## Project Context (opt-in only)` anchor in `CLAUDE.md`. Insert this entry under that section (alphabetically among existing entries):

```markdown
### <name> — <one-line tagline from Q1>

- **Entry file:** [<name>/Vault/README.md](<URL-encoded-name>/Vault/README.md) (entry index — Scope, Contents, How to use, Taxonomy).
- **Knows:** <scope_paragraph from Q1>
- **Call it for:** <call_out_clause from Q1>
```

Skip the `.claude/commands/update-brain.md` edit (`/update-brain` refuses Project Context brains by design).

If anchor not found, print the snippet above with `WARN: Couldn't find "## Project Context (opt-in only)" anchor in CLAUDE.md. Paste this entry manually.`

### 18. Print summary

```
/new-brain complete

Brain: <target>
Files written: 5 base + <N> folder _index.md + <M> raw .gitkeep
Router entry: <added under <anchor> | skipped — paste manually>
Alias row: <added | skipped — paste manually | n/a (Project Context)>

Next steps:
  1. Drop raw files into <target>/_raw/<subpath>/
  2. (When ready to extract) write the extractor at scripts/extractify/brains/<slug>/extract.sh
  3. Run /update-brain <slug> all     (General Brains only)
```

Then run `git status --short` from the repo root (skip silently if the repo isn't a git repo).

## Notes

- Never auto-stages, auto-commits, or auto-pushes.
- All file writes overwrite the seed-brain template versions in place. Re-running the skill on an existing brain folder is blocked at pre-flight (target exists). Manual `rm -rf <target>` is the redo path.
- The skill is LLM-driven — the four parsed-input lists from Q1–Q4 are fed into deterministic templates here, but the prose around them (e.g. the Q4 synthesis prompts) benefits from the LLM rendering it cleanly.
