---
description: Query your local brains for an answer. Routes to the right brain via CLAUDE.md.
argument-hint: <question>
---

Answer this question by consulting the brains in this repo:

**Question:** $ARGUMENTS

## Steps

1. **Read the router first:** `CLAUDE.md` at the repo root. It describes each brain in one paragraph and lists the entry file to start with.
2. **Pick the brain(s)** that match the question's domain. Route to **General Brains only** (top-level folders) unless the user's question explicitly names a Project Context brain (under `.Project Context/`) or asks for cross-tier work. If multiple brains apply, consult each. If none applies, say so and stop — don't invent an answer from general knowledge and claim it came from a brain.
3. **State which brain(s) you're consulting and why** before searching, in one short line.
4. **Open the brain's entry file:** `<Brain>/Vault/README.md` — read **Scope** first (reject mismatches early), then **How to use** (find the right content folder), then drill into that folder's `_index.md` to pick the specific note. Do NOT read every file in the brain — use the index.
5. **If `<brain>/graphify-out/GRAPH_REPORT.md` exists,** also read its **God Nodes** and **Surprising Connections** sections after the entry file — they surface central concepts and non-obvious links the curated index misses.
6. **Follow pointers** into specific notes / templates / transcripts as needed. Use Grep and Glob for targeted searches across the brain.
7. **Answer the question directly.** Cite the files you used with clickable markdown links of the form `[name](path/to/file.md)`. If you pulled insights from multiple brains, label which insight came from which brain.

## Rules

- These brains are **read-only for this query**. Do not edit, create, or delete any file inside a brain folder — if the user asks to update a brain, treat that as a separate request and confirm first.
- Keep the answer grounded in what's actually in the brain. Quote or paraphrase specific notes rather than speaking in generalities.
- If the brain has the topic but the specific answer isn't there, say "the brain covers X but doesn't answer this specific question" rather than padding with guesses.

## Calling this command from another project

This is a project-local slash command — it works inside this repo. To make it callable from other projects on your machine, copy this file to `~/.claude/commands/ask-brain.md` and edit it to hard-code the absolute path to your brains repo (replace each reference to `the repo root` with that path). Then `/ask-brain <question>` works from any project.
