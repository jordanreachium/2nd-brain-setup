# `_raw/`

Drop source material here: PDFs, audio, video, transcripts, articles, originals — anything you want this brain to know.

`/update-brain <brain> extract` walks this folder per the wiring in `<brain>/_meta/extract.md` and produces cleaned `.md` files in `_pipeline/`.

## Subpath layout

The wiring in `_meta/extract.md` decides what subpaths exist. Typical shapes:

```
_raw/
  transcripts/      # audio/video transcripts (.md, .vtt, .srt) or media (.mp4, .mp3, ...)
  pdfs/             # books, papers, decks
  articles/         # web articles
  notes/            # hand-written markdown
```

`/new-brain` creates the subpaths you specified during scaffolding. Add more by editing `_meta/extract.md` and running `/update-brain <brain> extract`.

## Commit policy

By default, contents of `_raw/` are gitignored — raw bundles are local-only. The brain's `.gitignore` un-ignores this README so the directory survives a fresh clone. If you want to commit specific raw sources, edit the brain's `.gitignore` to whitelist them.
