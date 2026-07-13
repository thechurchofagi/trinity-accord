#!/usr/bin/env python3
"""Fail closed unless the native OTS latest projection binds the current chain tip."""
from __future__ import annotations

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


def check() -> dict:
    tip = read_json(TIP)
    latest = read_json(LATEST)

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


def main() -> int:
    print(json.dumps(check(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
