# Project Context (opt-in tier)

This folder holds **Project Context brains** — knowledge bases the router does *not* automatically consult.

Use this tier when a brain is about a specific project, company, or private subject matter that shouldn't be picked by default when you ask a general question. The router will only consult these brains if you explicitly name them or ask for cross-tier work (e.g. "have <General Brain X> audit the <Project Context Y> offer").

## How to add one

```
/new-brain "My Company" --project-context
```

`/new-brain` will scaffold the brain at `.Project Context/My Company/` with the same shape as a General Brain (`_raw/`, `_pipeline/`, `Vault/`, `_meta/`, `.obsidian/`). It uses the same `_brain_template/` seed and the same `_meta/{extract,obsidian,taxonomy}.md` rules.

The only differences from a General Brain:

- Lives under `.Project Context/` instead of the repo root.
- Listed under the **Project Context** section of the router (`CLAUDE.md`) instead of **General Brains**.
- `/update-brain` prompts a "you sure?" confirmation before running (skip with `--yes`).
- `/ask-brain` skips it unless you explicitly name it.

Everything else — the pipeline, synthesis, graphify, Obsidian config — works exactly the same.

## What goes here

- A brain about a specific company, client, or product (e.g. "Acme Inc — pipeline, contracts, financials, GTM").
- A brain about a private project (e.g. "Side Project — design notes, decisions, contractor contacts").
- A brain holding raw transcripts of past Claude Code sessions, scoped to a project (e.g. "Project Sessions").

## What doesn't

General-purpose knowledge that would be useful across questions (e.g. "Marketing Frameworks", "Python Patterns") — those belong in a top-level General Brain so the router can find them by default.

---

This README is just a tier marker. It stays here whether or not the folder has any brains in it.
