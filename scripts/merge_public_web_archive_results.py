#!/usr/bin/env python3
"""Merge completed batch manifests into one auditable archive result."""

import argparse
import json
import sys
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--software-heritage", type=Path)
    args = parser.parse_args()

    paths = sorted(args.input_dir.glob("batch-*.json"))
    if not paths:
        raise SystemExit("no batch manifests found")
    batches = [load(path) for path in paths]
    schema = "trinityaccord.public-internet-archive-results.v1"
    if any(batch.get("schema") != schema for batch in batches):
        raise SystemExit("unexpected batch schema")
    sitemap_hashes = {batch.get("sitemap_sha256") for batch in batches}
    scopes = {batch.get("scope") for batch in batches}
    dry_run_values = {batch.get("dry_run") for batch in batches}
    if len(sitemap_hashes) != 1 or len(scopes) != 1 or len(dry_run_values) != 1:
        raise SystemExit("batch manifests disagree on sitemap, scope, or dry-run state")

    items = []
    for batch in sorted(batches, key=lambda item: item["selected_start_index"]):
        items.extend(batch.get("wayback", []))
    urls = [item.get("url") for item in items]
    if len(urls) != len(set(urls)):
        raise SystemExit("duplicate URLs across batch manifests")

    counts = {}
    for item in items:
        status = item.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    result = {
        "schema": "trinityaccord.public-internet-archive-aggregate.v1",
        "sitemap_sha256": next(iter(sitemap_hashes)),
        "scope": next(iter(scopes)),
        "dry_run": next(iter(dry_run_values)),
        "expected_url_count": args.expected_count,
        "observed_url_count": len(items),
        "batch_count": len(batches),
        "summary": counts,
        "wayback": items,
        "software_heritage": (
            load(args.software_heritage)
            if args.software_heritage and args.software_heritage.exists()
            else None
        ),
        "boundary": batches[0].get("boundary"),
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(counts, sort_keys=True))
    complete = len(items) == args.expected_count
    failed = counts.get("failed", 0) > 0
    return 0 if complete and not failed else 1


if __name__ == "__main__":
    sys.exit(main())
