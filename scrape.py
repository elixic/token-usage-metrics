#!/usr/bin/env python3
"""Scrape Claude Code JSONL transcripts into data/data.js.

Reads every `.jsonl` transcript under the transcripts root, normalizes each
session into a SessionRecord, and writes the array to `data/data.js` as a
`window.SESSIONS = [...]` assignment (so the dashboard can load it over
`file://` without a server).

See the specs in the vault for the authoritative schema:
  ~/Projects/claude/projects/token-usage-metrics/spec-scraper.md
  ~/Projects/claude/projects/token-usage-metrics/spec-data-model.md
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SYNTHETIC_MODEL = "<synthetic>"


def parse_timestamp_ms(value):
    """Parse an ISO 8601 timestamp string into epoch milliseconds, or None."""
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return int(dt.timestamp() * 1000)


def read_events(path):
    """Yield parsed JSON events from a .jsonl file, skipping malformed lines."""
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                print(f"WARN: skipped malformed line in {path}:{lineno}")


def build_session_record(path):
    """Read one transcript file and return its SessionRecord (or None on read error)."""
    try:
        events = list(read_events(path))
    except OSError:
        print(f"WARN: could not read {path}")
        return None

    session_id = path.stem

    # Timestamps: sort by parseable timestamp; ignore events without one.
    timestamps = sorted(
        ts for ts in (parse_timestamp_ms(e.get("timestamp")) for e in events)
        if ts is not None
    )
    started_at = timestamps[0] if timestamps else None
    ended_at = timestamps[-1] if timestamps else None
    duration_ms = (ended_at - started_at) if (started_at is not None and ended_at is not None) else 0

    # cwd / version from the first event that carries them.
    cwd = next((e["cwd"] for e in events if e.get("cwd")), None)
    version = next((e["version"] for e in events if e.get("version")), None)

    # Real assistant events: type == "assistant", excluding <synthetic>.
    assistant_events = [
        e for e in events
        if e.get("type") == "assistant"
        and e.get("message", {}).get("model") != SYNTHETIC_MODEL
    ]

    tokens = {
        "input": 0,
        "output": 0,
        "cache_creation": 0,
        "cache_creation_1h": 0,
        "cache_creation_5m": 0,
        "cache_read": 0,
    }
    tool_use = {"web_searches": 0, "web_fetches": 0}
    output_by_model = {}
    models = set()

    for e in assistant_events:
        message = e.get("message", {})
        model = message.get("model")
        if model:
            models.add(model)
        usage = message.get("usage", {}) or {}

        output = usage.get("output_tokens", 0) or 0
        tokens["input"] += usage.get("input_tokens", 0) or 0
        tokens["output"] += output
        tokens["cache_creation"] += usage.get("cache_creation_input_tokens", 0) or 0
        tokens["cache_read"] += usage.get("cache_read_input_tokens", 0) or 0

        cache_creation = usage.get("cache_creation", {}) or {}
        tokens["cache_creation_1h"] += cache_creation.get("ephemeral_1h_input_tokens", 0) or 0
        tokens["cache_creation_5m"] += cache_creation.get("ephemeral_5m_input_tokens", 0) or 0

        server_tool_use = usage.get("server_tool_use", {}) or {}
        tool_use["web_searches"] += server_tool_use.get("web_search_requests", 0) or 0
        tool_use["web_fetches"] += server_tool_use.get("web_fetch_requests", 0) or 0

        if model:
            output_by_model[model] = output_by_model.get(model, 0) + output

    # primary_model = model with the most output tokens; None if no assistant events.
    primary_model = (
        max(output_by_model, key=output_by_model.get) if output_by_model else None
    )

    # turns = human-typed user messages (user events without a toolUseResult).
    turns = sum(
        1 for e in events
        if e.get("type") == "user" and "toolUseResult" not in e
    )

    # tokens_per_minute: null when duration is 0 (single-event / zero-span sessions).
    if duration_ms > 0:
        tokens_per_minute = (tokens["input"] + tokens["output"]) / (duration_ms / 60000)
    else:
        tokens_per_minute = None

    # cache_hit_rate: 0 when there is no input/cache activity at all.
    cache_denominator = tokens["input"] + tokens["cache_read"] + tokens["cache_creation"]
    cache_hit_rate = tokens["cache_read"] / cache_denominator if cache_denominator else 0

    return {
        "session_id": session_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_ms": duration_ms,
        "cwd": cwd,
        "version": version,
        "models": sorted(models),
        "primary_model": primary_model,
        "turns": turns,
        "tokens": tokens,
        "tool_use": tool_use,
        "efficiency": {
            "tokens_per_minute": tokens_per_minute,
            "cache_hit_rate": cache_hit_rate,
        },
    }


def write_data_js(records, out_path):
    """Write the SessionRecord array to data/data.js."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = json.dumps(records, indent=2)
    out_path.write_text(
        "// Generated by scrape.py — do not edit manually\n"
        f"// Last updated: {now}\n"
        f"window.SESSIONS = {payload};\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--transcripts",
        default=str(Path.home() / ".claude" / "projects"),
        help="Root directory containing per-cwd transcript folders.",
    )
    args = parser.parse_args()

    root = Path(args.transcripts)
    if not root.is_dir():
        print(f"ERROR: transcripts root not found: {root}", file=sys.stderr)
        return 1

    records = []
    for path in sorted(root.rglob("*.jsonl")):
        record = build_session_record(path)
        if record is not None:
            records.append(record)

    # Newest first.
    records.sort(key=lambda r: (r["started_at"] is not None, r["started_at"]), reverse=True)

    out_path = Path(__file__).resolve().parent / "data" / "data.js"
    write_data_js(records, out_path)

    print(f"Wrote {len(records)} session(s) to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
