# token-usage-metrics

Agent entry point. Start by reading:

- **`CONTEXT.md`** — stack, commands, where the specs/docs live.
- **`MAP.md`** — source map (entry points, layout, key files).
- **`.maps/symbols.tsv`** — symbol index for definition lookups.

## Hard rules

- Commit format: `<reason>: [Ticket if applicable] <heading>`.
- `data/data.js` is generated — never hand-edit; it's gitignored.
- Design specs are authoritative and live in the vault under
  `~/Projects/claude/projects/token-usage-metrics/spec-*.md`.
