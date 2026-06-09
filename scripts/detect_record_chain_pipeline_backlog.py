#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAIN_TIP = ROOT / "record-chain/chain-tip.json"
OTS_LATEST = ROOT / "api/record-chain-native-ots-latest.json"
ARWEAVE_INDEX = ROOT / "api/record-chain-arweave-index.json"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def latest_live_native_archive(index: dict[str, Any]) -> dict[str, Any] | None:
    live = [
        a for a in index.get("archives", [])
        if a.get("source_type") == "native-record-chain"
        and a.get("mode") == "live"
        and a.get("arweave_txid")
    ]
    if not live:
        return None
    live.sort(key=lambda a: (a.get("native_record_count") or 0, a.get("created_at") or ""))
    return live[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args()

    tip = read_json(CHAIN_TIP)
    ots = read_json(OTS_LATEST)
    ar = latest_live_native_archive(read_json(ARWEAVE_INDEX)) or {}

    chain_id = tip.get("latest_record_id") or ""
    chain_sha = tip.get("latest_record_sha256") or ""
    chain_count = tip.get("native_record_count") or ""

    ots_id = ots.get("latest_record_id") or ""
    ots_sha = ots.get("latest_record_sha256") or ""
    ots_count = ots.get("native_record_count") or ""

    ar_id = ar.get("native_latest_record_id") or ""
    ar_sha = ar.get("native_latest_record_sha256") or ""
    ar_count = ar.get("native_record_count") or ""

    ots_matches_chain = (
        ots_id == chain_id
        and ots_sha == chain_sha
        and ots_count == chain_count
        and ots.get("legacy_main_chain_jsonl_is_not_source") is True
    )

    arweave_matches_ots = (
        ar_id == ots_id
        and ar_sha == ots_sha
        and ar_count == ots_count
        and bool(ar_id)
    )

    arweave_matches_chain = (
        ar_id == chain_id
        and ar_sha == chain_sha
        and ar_count == chain_count
        and bool(ar_id)
    )

    result = {
        "chain_latest_record_id": chain_id,
        "chain_latest_record_sha256": chain_sha,
        "chain_native_record_count": str(chain_count),
        "ots_latest_record_id": ots_id,
        "ots_latest_record_sha256": ots_sha,
        "ots_native_record_count": str(ots_count),
        "arweave_latest_record_id": ar_id,
        "arweave_latest_record_sha256": ar_sha,
        "arweave_native_record_count": str(ar_count),
        "ots_matches_chain": str(ots_matches_chain).lower(),
        "arweave_matches_ots": str(arweave_matches_ots).lower(),
        "arweave_matches_chain": str(arweave_matches_chain).lower(),
        "ots_anchor_needed": str(not ots_matches_chain).lower(),
        "arweave_archive_needed": str(ots_matches_chain and not arweave_matches_ots).lower(),
        "pipeline_current": str(ots_matches_chain and arweave_matches_chain).lower(),
    }

    if args.github_output:
        for key, value in result.items():
            print(f"{key}={value}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
