# Synthesize-note prompt (generic)

This is a shared prompt template. It's loaded by `scripts/obsidianify/skill.md` once per pipeline entry being synthesized. Per-brain specifics (Vault structure, per-kind rules, frontmatter shape) come from `<brain>/_meta/obsidian.md`.

---

## Role

You are synthesizing a single pipeline entry from a knowledge brain into one or more Vault notes.

## Inputs you will be given

1. The full body text of the pipeline entry (cleaned prose, possibly with frontmatter metadata).
2. The pipeline entry's frontmatter (`source_kind`, `source_path`, `content_hash`, `extracted_at`).
3. The brain's `_meta/obsidian.md` rules file verbatim.
4. The brain's current `Vault/` tree (folder listing + existing note basenames) — used so you can link to existing notes and know which folder to write to.

## Your job

1. Apply the brain's `_meta/obsidian.md` `## Classification` rules to decide which Vault note kind(s) this pipeline entry produces.
2. For each note kind, apply its `## Synthesis prompts` section to produce the note body.
3. Use the brain's `_meta/obsidian.md` `## Vault structure` to choose the right folder.
4. Each note's filename is kebab-case derived from its primary concept; use the brain's naming convention if the rules file specifies one.
5. Frontmatter must include a `source_refs` array listing the pipeline path you synthesized from (e.g. `[_pipeline/sources/example-source.md]`). Additional frontmatter fields come from the brain's rules.
6. Body must include a wikilink back to the source pipeline entry, e.g. `[[_pipeline/sources/example-source]]`.
7. Update the `## Related` section of existing Vault notes (but only that section — never touch prose bodies) if the new note creates a relevant backlink. Respect `locked: true` frontmatter on any existing note — skip those entirely.

## Output format

Return a JSON object:

```json
{
  "generated_notes": [
    {
      "path": "Vault/concepts/example-concept.md",
      "action": "create",
      "frontmatter": { "topic": "example-topic", "source_refs": ["_pipeline/sources/example-source.md"] },
      "body": "<markdown body>"
    }
  ],
  "updated_existing": [
    {
      "path": "Vault/concepts/related-concept.md",
      "section": "## Related",
      "appended_lines": ["- [[example-concept]] — related framework"]
    }
  ]
}
```

The skill consuming this output will write the files. Do not write files yourself.
