# data/

Transcripts live here as `transcripts.csv` but are **not committed** — they are
medical consultation transcripts and this is a public repo (see `.gitignore`).

Provide your own `data/transcripts.csv` with two columns:

| column | description |
|--------|-------------|
| `id` | unique id, e.g. `transcript_1` |
| `transcript` | full consultation text, with `[mm:ss]` time markers |

`clinical.load_transcripts()` reads this file (path resolved relative to the repo
root, so it works from any launch directory).
