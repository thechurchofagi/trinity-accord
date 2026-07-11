#!/usr/bin/env python3
"""Merge archive manifests and overlay retry results into one auditable result."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BATCH_SCHEMA = "trinityaccord.public-internet-archive-results.v1"
AGGREGATE_SCHEMA = "trinityaccord.public-internet-archive-aggregate.v1"
SUCCESS_STATUSES = {"captured", "already_captured", "dry-run"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def collect_batch_manifests(input_dir: Path) -> list[dict]:
    manifests: list[dict] = []
    if not input_dir.exists():
        return manifests
    for path in sorted(input_dir.rglob("*.json")):
        data = load(path)
        if data.get("schema") == BATCH_SCHEMA:
            manifests.append(data)
    return manifests


def merge_results(
    batches: list[dict],
    *,
    expected_count: int,
    software_heritage: dict | None = None,
    base_aggregate: dict | None = None,
) -> dict:
    if base_aggregate is not None:
        if base_aggregate.get("schema") != AGGREGATE_SCHEMA:
            raise ValueError("unexpected base aggregate schema")
        items_by_url = {
            item["url"]: dict(item)
            for item in base_aggregate.get("wayback", [])
            if isinstance(item, dict) and item.get("url")
        }
        ordered_urls = [
            item["url"]
            for item in base_aggregate.get("wayback", [])
            if isinstance(item, dict) and item.get("url")
        ]
        sitemap_sha256 = base_aggregate.get("sitemap_sha256")
        scope = base_aggregate.get("scope")
        dry_run = base_aggregate.get("dry_run")
        boundary = base_aggregate.get("boundary")
        batch_count = int(base_aggregate.get("batch_count", 0))
        software = software_heritage if software_heritage is not None else base_aggregate.get("software_heritage")
    else:
        if not batches:
            raise ValueError("no batch manifests found")
        if any(batch.get("schema") != BATCH_SCHEMA for batch in batches):
            raise ValueError("unexpected batch schema")
        sitemap_hashes = {batch.get("sitemap_sha256") for batch in batches}
        scopes = {batch.get("scope") for batch in batches}
        dry_run_values = {batch.get("dry_run") for batch in batches}
        if len(sitemap_hashes) != 1 or len(scopes) != 1 or len(dry_run_values) != 1:
            raise ValueError("batch manifests disagree on sitemap, scope, or dry-run state")
        items_by_url: dict[str, dict] = {}
        ordered_urls: list[str] = []
        for batch in sorted(batches, key=lambda item: item.get("selected_start_index", 0)):
            for item in batch.get("wayback", []):
                url = item.get("url")
                if not url:
                    raise ValueError("batch result missing URL")
                if url in items_by_url:
                    raise ValueError("duplicate URLs across initial batch manifests")
                ordered_urls.append(url)
                items_by_url[url] = dict(item)
        sitemap_sha256 = next(iter(sitemap_hashes))
        scope = next(iter(scopes))
        dry_run = next(iter(dry_run_values))
        boundary = batches[0].get("boundary")
        batch_count = len(batches)
        software = software_heritage

    retry_updates = 0
    if base_aggregate is not None:
        for batch in batches:
            if batch.get("schema") != BATCH_SCHEMA:
                raise ValueError("unexpected retry batch schema")
            if batch.get("sitemap_sha256") != sitemap_sha256:
                raise ValueError("retry batch sitemap hash does not match base aggregate")
            for item in batch.get("wayback", []):
                url = item.get("url")
                if url not in items_by_url:
                    raise ValueError(f"retry result URL was not present in base aggregate: {url}")
                items_by_url[url] = dict(item)
                retry_updates += 1
        batch_count += len(batches)

    items = [items_by_url[url] for url in ordered_urls]
    counts: dict[str, int] = {}
    for item in items:
        status = item.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1

    unresolved_items = [
        item for item in items if item.get("status") not in SUCCESS_STATUSES
    ]
    software_status = software.get("status") if isinstance(software, dict) else None
    software_heritage_ok = software_status in {None, "requested", "dry-run"}
    result = {
        "schema": AGGREGATE_SCHEMA,
        "sitemap_sha256": sitemap_sha256,
        "scope": scope,
        "dry_run": dry_run,
        "expected_url_count": expected_count,
        "observed_url_count": len(items),
        "batch_count": batch_count,
        "retry_update_count": retry_updates,
        "summary": counts,
        "unresolved_url_count": len(unresolved_items),
        "unresolved_urls": [item.get("url") for item in unresolved_items],
        "wayback": items,
        "software_heritage": software,
        "software_heritage_ok": software_heritage_ok,
        "boundary": boundary,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--software-heritage", type=Path)
    parser.add_argument("--base-aggregate", type=Path)
    parser.add_argument("--allow-unresolved", action="store_true")
    args = parser.parse_args()

    batches = collect_batch_manifests(args.input_dir)
    software = (
        load(args.software_heritage)
        if args.software_heritage and args.software_heritage.exists()
        else None
    )
    base = (
        load(args.base_aggregate)
        if args.base_aggregate and args.base_aggregate.exists()
        else None
    )
    try:
        result = merge_results(
            batches,
            expected_count=args.expected_count,
            software_heritage=software,
            base_aggregate=base,
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))

    complete = result["observed_url_count"] == args.expected_count
    resolved = result["unresolved_url_count"] == 0
    external_ok = result["software_heritage_ok"]
    if args.allow_unresolved:
        return 0 if complete else 1
    return 0 if complete and resolved and external_ok else 1


if __name__ == "__main__":
    sys.exit(main())
