# token-usage-metrics — agent context

Local dashboard for understanding Claude Code token efficiency. Reads raw JSONL
transcripts, emits `data/data.js`, rendered by a static HTML page (no server).

## Stack

- Language / runtime: Python 3 (standard library only so far)
- Frontend: static HTML + Chart.js (planned), opened directly in a browser
- Package manager: none yet (stdlib); add `requirements.txt` if deps appear

## Commands

| Action | Command |
|--------|---------|
| Run scraper | `python3 scrape.py` (writes `data/data.js`) |
| Scraper opts | `python3 scrape.py --transcripts <dir>` (default `~/.claude/projects`) |
| View dashboard | `open index.html` |
| Test | _none yet_ |
| Lint | _none yet_ |

## Layout

See `MAP.md`. In short: `scrape.py` (CLI scraper) → `data/data.js` (generated,
gitignored) → `index.html` (loads the data). `.maps/symbols.tsv` is the symbol
index.

## Documentation & decisions

- Design specs live in the vault, not here:
  - `~/Projects/claude/projects/token-usage-metrics/spec-data-model.md`
  - `…/spec-scraper.md`
  - `…/spec-dashboard.md`
- Raw transcript schema: vault `wiki/claude-code-transcripts.md`
- Cross-session status / next steps: vault `projects/token-usage-metrics/CONTEXT.md`

## Conventions / gotchas

- Commit format: `<reason>: [Ticket if applicable] <heading>`
- `data/data.js` is generated output — gitignored, never hand-edited
- Transcripts prune at ~30 days; run the scraper regularly (no archiving in MVP)
