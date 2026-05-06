---
description: Update a General Brain end-to-end — extract pipeline from raw, synthesize Vault from pipeline, build graph.
argument-hint: <brain> [phase] [--dry-run] [--full-rebuild] [--yes]
---

Update a General Brain's pipeline, derived Vault, and graph. Pipeline is the committed source of truth; Vault and graphify-out are derived.

**Argument:** $ARGUMENTS

## What this does

Three phases, run in order by default:

1. **Extract** — walk `<brain>/_raw/` per `<brain>/_meta/extract.md` wiring, produce cleaned `.md` files with YAML frontmatter in `<brain>/_pipeline/`, update `<brain>/_pipeline/_manifest.json`.
2. **Obsidian** — diff pipeline manifest against `<brain>/_meta/synthesis-state.json`; invoke LLM synthesis (Claude in-session) on new/changed pipeline entries per `<brain>/_meta/obsidian.md` rules; write derived notes into `<brain>/Vault/`; regenerate all structural files (`_index.md`, `Vault/README.md` Stats, `_meta/vault-stats.md`, `_meta/wikilink-report.md`, `.obsidian/*.json` drift prompts).
3. **Graph** — delegate to `scripts/graphify/skill.md` in `--mode deep`, scoping its corpus walk to `Vault/`, `_pipeline/`, and `_meta/` via graphify's `include` kwarg on `graphify.detect.detect()`.

Never auto-stages, auto-commits, or auto-pushes. Always ends with `git status --short` (if the repo is a git repo).

## Steps

### 1. Parse arguments

First token → brain alias.

| Alias | Folder | Tier |
|-------|--------|------|
| _(populated by `/new-brain` as you create brains)_ | | |

- Unrecognized token → fall back to treating it as a folder name relative to the repo root (e.g. `My Brain` → `<repo>/My Brain`). If that folder doesn't exist either, ask the user.
- The repo root itself (router root) → refuse.

Second token (optional) → phase. One of: `extract`, `obsidian`, `graph`, `all`. Default: `all`. Anything else → ask user.

Remaining tokens → scan for:

- `--dry-run` — propagate to all phases.
- `--full-rebuild` — when present, suppress `--update` from the graphify invocation in Phase 3 (no effect on extract or obsidian phases — those use manifest/state-file diffs).
- `--yes` — bypass the project-context confirmation prompt in Step 1a (see below).

Other flags pass through to Phase 3 (graph) only.

### 1a. Project-context confirmation

If the resolved brain is **project-context** (lives under `.Project Context/`) AND `--yes` was not in `$ARGUMENTS`:

Print:

```
'<alias>' is a project-context brain. Proceed? (yes/no)
```

Wait for user response. Accept `y`, `yes`, `Y`, `YES` as proceed. Accept `n`, `no`, `N`, `NO` as abort. Anything else → re-prompt.

On abort: print `Aborted.` and exit 0.

Project-context brains follow the **same flow** as General Brains. The prompt is a small "you sure?" speed bump — the user drops raw files into `_raw/` the same way.

The prompt fires regardless of which phase is invoked.

### 2. Announce

Print: `Updating <brain-folder>: <phases-that-will-run>`. Example: `Updating My Brain: [extract → obsidian → graph]`.

If `--dry-run` was set, prefix with `DRY RUN — `.

### 3. Phase 1: Extract

**Skip if phase argument isn't `extract` or `all`.**

Delegate to `scripts/extractify/skill.md`. Pass `<brain-folder>` and `--dry-run` (if set).

Pre-flights are handled by Extractify itself.

**Summary:** `Extractify complete — <N> new, <M> changed, <K> unchanged, <O> orphan.`

### 4. Phase 2: Obsidian

**Skip if phase argument isn't `obsidian` or `all`.**

Delegate to `scripts/obsidianify/skill.md`. Pass `<brain-folder>` and `--dry-run` (if set).

Pre-flights are handled by Obsidianify itself.

**Summary** (from Obsidianify's step 9 output): new/changed/unchanged/orphan counts + indexes regenerated + drift prompts + wikilink stats.

### 5. Phase 3: Graph

**Skip if phase argument isn't `graph` or `all`.**

**Pre-flight:**
- `<brain>/Vault/` must contain at least one `.md` file. Empty → refuse: "No curated content in Vault/ — run obsidian phase first."
- `<brain>/_meta/` must exist. Missing → refuse.
- `scripts/graphify/skill.md` must exist. Missing → refuse.

**If `--dry-run`:** print `Would graphify <brain-folder> in --mode deep, scoped to Vault/ + _pipeline/ + _meta/ via include kwarg`, skip the actual run.

**Otherwise, execute:**

Follow `scripts/graphify/skill.md` with:
- All commands run `cd "<brain-folder>" && <command>`.
- `INPUT_PATH = .`
- When invoking `from graphify.detect import detect`, pass `include=['Vault', '_pipeline', '_meta']` to scope the corpus walk.
- Flag `--mode deep` (always, in v1).
- Flag `--update` — incremental rebuild, **default**. Suppressed when `--full-rebuild` is in `$ARGUMENTS`.
- Any other flags captured from `$ARGUMENTS` (e.g. `--svg`) are appended.

Outputs land in `<brain>/graphify-out/`.

**Summary:** print God Nodes, Surprising Connections, Suggested Questions from the new `<brain>/graphify-out/GRAPH_REPORT.md`.

### 6. End-of-run

Print the per-phase summaries in order, then (if running inside a git repo):

```bash
git status --short
```

Do not stage, commit, or push.

## Guardrails

- Refuse the router root (the repo root itself).
- Refuse aliases not found in the alias table AND not resolving to an existing brain folder.
- Never modify files under `_raw/` directly — only through the brain's Extractify code.
- Never auto-stage or auto-commit.
- Pre-flight refusals come from the delegated skills (Extractify / Obsidianify / Graphify), each with specific error messages.
- All phases run in order — if one fails, stop and surface the failure with its phase name.
