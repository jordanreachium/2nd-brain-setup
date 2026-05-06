# Obsidian synthesis rules

> This file tells `/update-brain <brain> obsidian` how to synthesize Vault notes from pipeline entries. Fill in every section before running the obsidian phase. Placeholder tokens (`<folder-1>`, `<kind-a>`, `<source-kind>`, etc.) cause obsidian to refuse until replaced.

## Vault structure

Top-level folders under `Vault/` this brain's Obsidianify run produces. `/update-brain` uses this to build per-brain stats.

- **<folder-1>** — <what lives here>
- **<folder-2>** — <what lives here>

## Synthesis prompts

One section per Vault note kind. Each section is an LLM-readable instruction: when to emit this kind, what frontmatter + body shape to use, and how to link back to the source pipeline entry.

### <kind-a> notes

When a pipeline entry's `source_kind` is `<source-kind>`, <describe the synthesis>: one Vault note in `Vault/<folder-1>/<kebab-slug>.md` with frontmatter `{<field-1>, <field-2>}` and body sections `<section-headers>`. Link back to source as `[[_pipeline/<path>]]`.

### <kind-b> notes

<same shape, different prompt>

## Classification

How to map a pipeline entry's `source_kind` (and body, if relevant) to which Vault note kind(s) it produces:

- `source_kind: <x>` → <kind-a> note(s)
- `source_kind: <y>` → <kind-a> + <kind-b> note(s)

## Cross-ref discipline

When Obsidianify synthesizes a new note, it may append links to existing Vault notes' `## Related` section if the new note creates a backlink. Existing prose in other sections is never touched. Notes with `locked: true` in their frontmatter are skipped entirely — not even `## Related` updates.
