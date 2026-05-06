# Taxonomy

The brain's vocabulary and folder map. **Mandatory** — the router reads this
when the user asks "where does X go in this brain?".

## Folder map

For each folder inside `Vault/`, define what qualifies as a note in that folder.
Be specific about what gets rejected, not just what gets accepted.

- **`Vault/<folder-1>/`** — TODO: what qualifies as a `<folder-1>` note. What doesn't.
- **`Vault/<folder-2>/`** — TODO: what qualifies as a `<folder-2>` note. What doesn't.

## Note types

If notes use a frontmatter `type:` key, list the allowed values and what each means.
Delete this section if the brain doesn't use typed notes.

- `concept` — atomic mental model
- `pattern` — reusable structure with slots
- `source` — primary text the brain was distilled from

## Naming

Slug conventions (kebab-case, snake_case, etc.), casing rules, punctuation rules.
Example: `state-machine-pattern.md`, not `StateMachinePattern.md`.
