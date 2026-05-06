# Brain extractor (template)

Seeded by `/new-brain` into `scripts/extractify/brains/<your-brain-slug>/`.

## What it does

Calls `lib.sources.auto_extract`, which dispatches to a shared handler
based on the input file's extension. Built-in source kinds:

| Extension(s) | Handler |
|---|---|
| `.md` | markdown pass-through (strips leading frontmatter) |
| `.pdf` | pypdf text extraction |
| `.docx` | python-docx (preserves H1/H2/H3, flattens tables) |
| `.epub` | ebooklib (chapter text, blank-line separated) |
| `.mp4` `.mov` `.m4a` `.mp3` `.wav` | faster-whisper local transcription |

## Customizing per brain

If your brain only ingests the built-in kinds with default behavior, leave
`code/run.py` alone — the one-liner re-export is enough.

If your brain needs custom Whisper settings (vocabulary prompt, larger
model), see the docstring inside `code/run.py` for the override pattern.

If your brain has a brand-new source kind: **add a handler to
`scripts/extractify/lib/sources/` and register it in REGISTRY.** Don't
duplicate it per-brain — every future brain gets the new kind for free.

## Running

From this directory:

    python -m code <input-path> <output-path>

Extractify (`scripts/extractify/skill.md`) calls this for each raw file
matched by the brain's `_meta/extract.md` source wirings.
