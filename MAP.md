# Source map

Maintained via the vault's `/index-repo`. Pair with `.maps/symbols.tsv` for
definition lookups.

## Entry points

- `scrape.py` — CLI scraper; `main()` parses `--transcripts` and (eventually)
  walks the transcript tree to emit `data/data.js`. Currently a stub.
- `index.html` — dashboard; loads `data/data.js` via `<script>` and renders.

## Layout

- `scrape.py` — the scraper (stdlib `argparse`/`pathlib`)
- `index.html` — static dashboard shell
- `data/` — generated output lands here (`data.js`, gitignored)
- `.maps/` — generated agent-navigation artifacts (`symbols.tsv`)

## Key files

- `scrape.py` — `main()` at line 12 (current sole entry point)
- `index.html` — single-page shell, expects `data/data.js`

## How it fits together

`python3 scrape.py` reads `~/.claude/projects/<cwd>/<session>.jsonl`, aggregates
per-turn token usage, and writes `data/data.js`. Opening `index.html` loads that
file and (planned) renders summary cards, a sessions table, and charts via
Chart.js. No server, no build step.
