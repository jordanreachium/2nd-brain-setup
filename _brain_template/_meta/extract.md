# Extract rules

> This file tells `/update-brain <brain> extract` what raw sources to process and where their pipeline outputs live. Fill in every section before running the extract phase. Placeholder tokens (`<kind-1>`, `<raw-path-1>`, `<extractor-cmd-1>`, etc.) cause extract to refuse until replaced.

> **Built-in source kinds** (handled by `scripts/extractify/lib/sources/`):
> `.md` `.pdf` `.docx` `.epub` `.mp4` `.mov` `.m4a` `.mp3` `.wav`. Use
> these freely in the wirings below — the brain's `code/run.py` dispatches
> via `auto_extract`. New source kinds belong in the library, not in
> per-brain code.

## Sources

One bullet per distinct source kind. Each bullet names: which raw subpath it lives under, which extractor command to run, and which pipeline subfolder receives the output.

- **<kind-1>** — `_raw/<raw-path-1>/*.<ext>` → run `<extractor-cmd-1>`, write to `_pipeline/<kind-1>/`
- **<kind-2>** — `_raw/<raw-path-2>/*.<ext>` → run `<extractor-cmd-2>`, write to `_pipeline/<kind-2>/`

## Output contract

Every pipeline file this brain produces:

- Is `.md` with YAML frontmatter containing at minimum: `source_path`, `source_kind`, `extracted_at` (ISO 8601), `content_hash` (sha256).
- Lives under `_pipeline/<kind>/<stable-slug>.md`. The slug is kebab-case derived from the source's primary identifier.
- Body is cleaned prose — NOT classified or synthesized yet. That's Obsidianify's job in the next phase.

## Skip / gotchas

Per-brain rules for what Extractify should skip or handle specially.

- <gotcha-1>
- <gotcha-2>
