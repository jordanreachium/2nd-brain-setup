---
description: Scaffold a new General or Project Context brain via conversational fill-in. No placeholder tokens left.
argument-hint: "<Brain Name>" [--project-context]
---

Scaffold a new brain end-to-end. Asks four questions, writes every `_meta/*.md` file plus `Vault/README.md`, top-level `README.md`, real Vault folders, `_raw/<subpath>/.gitkeep` stubs, and (for General Brains) router + alias entries. Both Extractify and Obsidianify pre-flights pass on the result.

**Argument:** $ARGUMENTS

## What this does

Delegates to `scripts/new-brain/skill.md`. The skill drives the conversation, calls `scripts/new-brain/seed-brain.sh` for the deterministic copy, then overwrites the template files with content derived from the user's answers.

Never auto-stages, auto-commits, or auto-pushes. Always ends with `git status --short` (if the repo is a git repo).

## Steps

### 1. Parse arguments

First quoted/positional token → brain name (required, string).

Remaining tokens → scan for `--project-context`. Anything else → ask user, don't guess.

Brain name validation (refuse with the specific reason):
- Non-empty after trimming whitespace
- Does not contain `/`, `\`, or `..`
- Does not start with `--`

### 2. Refuse on router root or existing target

- If brain name is `.` or `..` or empty after validation → refuse.
- If `<repo-root>/<name>/` exists (default) → refuse: `Target already exists. rm -rf manually if you want a redo.`
- If `--project-context` set and `<repo-root>/.Project Context/<name>/` exists → same refusal.

### 3. Delegate to skill

Follow `scripts/new-brain/skill.md`. Pass:
- `<name>` (required)
- `--project-context` (if set)

### 4. End-of-run

Skill prints summary and runs `git status --short` from the repo root. Do not stage, commit, or push.

## Guardrails

- Refuse the router root itself — it's not a valid brain name.
- Never modify files under existing brain folders.
- Never auto-stage, auto-commit, or auto-push.
- Anchor-mismatch in `CLAUDE.md` or `.claude/commands/update-brain.md` → skip with warning + paste-snippet, don't corrupt the file.
- No `--force` exposed at this level. Manual `rm -rf` is the redo path.
