---
description: Build a graphify knowledge graph for one of your brains. Outputs land inside that brain's own folder so each brain stays self-contained.
argument-hint: <brain> [extra graphify flags]
---

Build a graphify knowledge graph for a specific brain.

**Argument:** $ARGUMENTS

## What this does

Runs the full graphify pipeline (detect → extract → cluster → HTML + JSON + `GRAPH_REPORT.md`) on **one** brain. Output always goes to `<brain>/graphify-out/` — never to the repo root. Each brain stays self-contained: its graph never leaks into another brain's folder, and the router root never contains a merged graph of everything.

## Steps

1. **Parse `$ARGUMENTS`.** First token is the brain selector. Anything after it is forwarded verbatim as graphify flags (e.g. `--mode deep`, `--update`, `--svg`, `--obsidian`).

   Brain aliases:

   | Alias | Folder |
   |-------|--------|
   | _(populated by `/new-brain` as you create brains)_ | |

   If the first token doesn't match an alias, treat it as a folder name relative to the repo root. If that folder doesn't exist, stop and ask the user — do not guess.

   If the first token resolves to the repo root itself (the router root), **refuse** — that would merge every brain into one graph and put a `graphify-out/` at the root. Tell the user to pick a specific brain.

2. **Announce the target.** Print one line: `Graphifying <brain-name> → <brain-folder>/graphify-out/`.

3. **Read the graphify pipeline.** Open `scripts/graphify/skill.md` — that file contains the full procedure (Steps 1–9). You will follow it exactly, with these substitutions:
   - All bash commands run with the brain folder as cwd. Use `cd "<brain-folder>" && <command>` on every bash call so `graphify-out/` is created inside the brain.
   - `INPUT_PATH` in the skill is `.` (the brain folder itself).
   - Forward any flags captured in step 1.

4. **Run the pipeline.** Execute Steps 1–9 of the skill in order. Do not skip steps. Use parallel subagents in Step 3 Part B as the skill requires (one Agent tool call per chunk, all in the same message).

5. **Report back.** Per the skill's Step 9, tell the user where the outputs live:
   - `<brain-folder>/graphify-out/graph.html`
   - `<brain-folder>/graphify-out/GRAPH_REPORT.md`
   - `<brain-folder>/graphify-out/graph.json`

   Then paste the **God Nodes**, **Surprising Connections**, and **Suggested Questions** sections from `GRAPH_REPORT.md` (and only those), and offer to trace the most interesting question.

## Guardrails

- Never graphify the repo root (the router root). The one and only `graphify-out/` per run lives inside the chosen brain.
- Do not modify any file in the target brain other than creating/updating its `graphify-out/` directory.
- The brains are otherwise read-only. If the pipeline wants to edit source notes (e.g. `--obsidian` writing into the vault), confirm with the user first.
