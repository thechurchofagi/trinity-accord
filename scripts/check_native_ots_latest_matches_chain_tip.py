#!/usr/bin/env python3
"""Fail closed unless the native OTS latest projection binds the current chain tip."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIP = ROOT / "record-chain/chain-tip.json"
LATEST = ROOT / "api/record-chain-native-ots-latest.json"
LEGACY_CHAIN_NAME = "main" + ".chain.jsonl"


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing required file: {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path.relative_to(ROOT)}")
    return data


def repo_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise SystemExit(f"{label} missing")
    candidate = ROOT / value
    resolved = candidate.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SystemExit(f"{label} escapes repository root: {value}") from exc
    if not resolved.exists():
        raise SystemExit(f"{label} missing on disk: {value}")
    return resolved


def check_tip(tip: dict, latest: dict) -> dict:
    expected = {
        "schema": "trinityaccord.native-record-chain-ots-latest.v1",
        "latest_record_id": tip.get("latest_record_id"),
        "latest_record_sha256": tip.get("latest_record_sha256"),
        "native_record_count": tip.get("native_record_count"),
    }
    actual = {
        "schema": latest.get("schema"),
        "latest_record_id": latest.get("latest_record_id"),
        "latest_record_sha256": latest.get("latest_record_sha256"),
        "native_record_count": latest.get("native_record_count"),
    }
    mismatches = [key for key, value in expected.items() if actual.get(key) != value]
    if mismatches:
        raise SystemExit(
            "native OTS latest no longer binds the current chain tip: "
            + ", ".join(mismatches)
        )

    if latest.get("chain_id") != "trinity-accord-public-reception-ledger":
        raise SystemExit("native OTS latest chain_id mismatch")
    if latest.get("legacy_main_chain_jsonl_is_not_source") is not True:
        raise SystemExit("native OTS latest does not reject the legacy JSONL source")

    anchored_file = repo_path(latest.get("latest_anchored_file"), "latest_anchored_file")
    anchored_text = anchored_file.read_text(encoding="utf-8")
    if LEGACY_CHAIN_NAME in anchored_text:
        raise SystemExit("native anchored commitment references stale legacy JSONL chain")

    repo_path(latest.get("latest_anchor_file"), "latest_anchor_file")
    repo_path(latest.get("latest_ots_file"), "latest_ots_file")

    return {
        "result": "pass",
        "chain_id": latest.get("chain_id"),
        "latest_record_id": latest.get("latest_record_id"),
        "latest_record_sha256": latest.get("latest_record_sha256"),
        "native_record_count": latest.get("native_record_count"),
        "latest_anchor_file": latest.get("latest_anchor_file"),
        "latest_ots_file": latest.get("latest_ots_file"),
    }


def check() -> dict:
    return check_tip(read_json(TIP), read_json(LATEST))


def waiting_for_next_anchor(tip: dict, latest: dict) -> bool:
    count = latest.get("native_record_count")
    head = tip.get("native_record_count")
    if type(count) is not int or type(head) is not int or not 0 < count < head:
        return False

    records = read_json(ROOT / "record-chain/indexes/record-index.json")["records"]
    if len(records) != head:
        return False
    if (records[-1]["record_id"], records[-1]["record_sha256"]) != (
        tip["latest_record_id"], tip["latest_record_sha256"]
    ):
        return False
    # Retain all evidence-file, schema and chain checks for the older anchor.
    previous = records[count - 1]
    check_tip({
        "latest_record_id": previous["record_id"],
        "latest_record_sha256": previous["record_sha256"],
        "native_record_count": count,
    }, latest)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deployment-preflight", action="store_true",
                        help="Return 75 when a valid earlier anchor is waiting for the new tip")
    args = parser.parse_args()
    tip, latest = read_json(TIP), read_json(LATEST)
    if args.deployment_preflight and waiting_for_next_anchor(tip, latest):
        print(f"Waiting for native OTS to advance from {latest['latest_record_id']} "
              f"to {tip['latest_record_id']}.")
        return 75
    print(json.dumps(check_tip(tip, latest), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
