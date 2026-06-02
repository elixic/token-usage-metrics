#!/usr/bin/env python3
"""Scrape Claude Code JSONL transcripts into data/data.js.

Stub — full implementation tracked in tasks/TUM-implement-scraper.
"""

import argparse
import sys
from pathlib import Path


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

    print(f"scrape.py stub — would scan {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
