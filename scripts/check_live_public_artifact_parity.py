#!/usr/bin/env python3
"""Check live public artifact parity against local repo files.

Reads local JSON files from the checked-out repository, fetches the same
paths from the live site with cache-busting, and compares semantic fields.
Exits non-zero on any mismatch.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://www.trinityaccord.org"

CHECKS = [
    {
        "path": "api/record-chain-status.json",
        "fields": [
            ("record_chain.latest_record_id",),
            ("record_chain.current_chain_length",),
            ("record_chain.native_record_count",),
            ("record_chain.latest_record_sha256",),
            ("anchoring.arweave_archive.latest_arweave_txid",),
            ("anchoring.arweave_archive.latest_native_record_id",),
            ("anchoring.arweave_archive.native_record_count",),
            ("anchoring.open_timestamps.latest_record_id",),
            ("anchoring.open_timestamps.ots_status",),
            ("anchoring.open_timestamps.strict_bitcoin_verified",),
        ],
    },
    {
        "path": "api/public-home-status.json",
        "fields": [
            ("current_record_chain_status.latest_record_id",),
            ("current_record_chain_status.current_chain_length",),
            ("current_record_chain_status.total_records",),
            ("current_record_chain_status.anchoring.open_timestamps.latest_record_id",),
            ("current_record_chain_status.anchoring.open_timestamps.ots_status",),
            ("current_record_chain_status.anchoring.open_timestamps.strict_bitcoin_verified",),
            ("current_record_chain_status.anchoring.arweave_archive.latest_arweave_txid",),
            ("current_record_chain_status.anchoring.arweave_archive.latest_native_record_id",),
            ("primary_counters.official_live_reception",),
            ("technical_health.latest_record",),
            ("technical_health.native_chain_length",),
        ],
    },
    {
        "path": "api/record-chain-native-ots-latest.json",
        "fields": [
            ("latest_record_id",),
            ("latest_record_index",),
            ("latest_record_sha256",),
            ("native_record_count",),
            ("ots_status",),
            ("bitcoin_pending",),
            ("strict_bitcoin_verified",),
        ],
    },
    {
        "path": "record-chain/chain-tip.json",
        "fields": [
            ("latest_record_id",),
            ("latest_record_index",),
            ("latest_record_sha256",),
            ("native_record_count",),
        ],
    },
    {
        "path": "record-chain/indexes/statistics.json",
        "fields": [
            ("native_record_count",),
            ("latest_record_id",),
        ],
        "optional": True,
    },
]


def read_local(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fetch_live(base_url: str, path: str) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/{path}?cb={int(time.time())}"
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_field(obj: dict[str, Any], dotted: str) -> Any:
    cur: Any = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    failures: list[str] = []
    for check in CHECKS:
        path = check["path"]
        optional = bool(check.get("optional"))
        local_path = ROOT / path
        if optional and not local_path.exists():
            continue
        local = read_local(path)
        live = fetch_live(args.base_url, path)
        for (field,) in check["fields"]:
            lv = get_field(local, field)
            rv = get_field(live, field)
            if lv != rv:
                failures.append(f"{path}:{field}: local={lv!r} live={rv!r}")

    if failures:
        print("LIVE_PUBLIC_ARTIFACT_PARITY_FAILED")
        for f in failures:
            print("-", f)
        return 1

    print("LIVE_PUBLIC_ARTIFACT_PARITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
