# Brains — Router

This folder holds local knowledge bases ("brains"). Any Claude Code session started here auto-loads this router. Each brain is a self-contained folder built from the same template (`_brain_template/`) and answered by the same scripts (`scripts/`).

## The two tiers

**General Brains** — root-level folders, default routing pool. The router picks from these when answering a question unless a Project Context brain is explicitly named.

_(populated by `/new-brain` as you create brains)_

**Project Context** — under `.Project Context/`, opt-in only. Use this tier for brains about a specific project, company, or private context where you don't want the router consulting them by default.

_(populated by `/new-brain "<name>" --project-context` as you create them)_

**Do NOT route to Project Context** unless the user's question explicitly names one of those brains, or asks for cross-tier work (e.g. *"have <General Brain X> audit the <Project Context Y> offer"* → General Brain = analyst, Project Context = subject).

## How to answer a question

1. Pick from **General Brains only**, unless the user named a Project Context brain or asked for cross-tier work.
2. Open that brain's **`Vault/README.md`** — the entry index. It has five sections in fixed order: **Scope**, **Contents**, **Stats**, **How to use**, **Taxonomy**. Use **Scope** to bail fast if the brain doesn't cover the question; use **How to use** to find the right content folder; drill into `<folder>/_index.md` to find the right note.
3. If `<brain>/graphify-out/GRAPH_REPORT.md` exists, also skim its **God Nodes** and **Surprising Connections** sections — they surface central concepts and non-obvious links the curated index misses.
4. From the entry file (and graphify report, if present), follow pointers into specific notes using Grep/Glob/Read.
5. Cite the files you used with clickable links.
6. If no brain covers the question, say so — don't invent an answer from general knowledge and claim it came from the brain.
7. These brains are **read-only for queries**. Don't edit files inside them unless explicitly asked.

---

## Slash commands

- **`/new-brain "<Brain Name>"`** — scaffold a new brain. Asks four questions, fills in `_meta/*.md`, creates real Vault folders, registers the brain in this router. Add `--project-context` to scaffold under `.Project Context/`. See `scripts/new-brain/skill.md` for the full conversation flow.
- **`/update-brain <alias> [phase]`** — refresh a brain's pipeline (extract), Vault (obsidian synthesis), and graph. Phase defaults to `all`. Add `--dry-run` to plan without writing.
- **`/graphify <alias>`** — build a knowledge graph for one brain. Output lands in `<brain>/graphify-out/`.
- **`/ask-brain <question>`** — query the brains. Routes via this file.

## Calling from another project

Two ways:

1. **`/ask-brain <question>`** — copy `.claude/commands/ask-brain.md` to your user-level `~/.claude/commands/` and hard-code the absolute path to this repo. Then it works from any Claude Code session.
2. **Add this folder as an additional working directory** in any session — then the router loads there too.

---

## Architecture in one paragraph

Each brain has the shape: `_raw/` (whatever you dump in) → `_pipeline/` (cleaned `.md` with frontmatter, content-hashed, manifest-tracked) → `Vault/` (LLM-synthesized notes organized for retrieval) → `graphify-out/` (knowledge graph + audit report). `_meta/{extract,obsidian,taxonomy}.md` per brain are the rules files that drive each phase. `scripts/extractify/` walks `_raw/` and produces `_pipeline/`. `scripts/obsidianify/` diffs the pipeline manifest against synthesis state and runs LLM synthesis on new/changed entries. `scripts/graphify/` turns the curated content into a graph. `scripts/new-brain/` scaffolds a fresh brain with no placeholder tokens left. `_brain_template/` is the seed.
