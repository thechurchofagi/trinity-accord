#!/usr/bin/env python3
"""Verify the frozen legacy hash-chain Arweave data registry.

The registry is historical evidence, not the current native Record-Chain
archive index. Verification checks real bundle bytes and content rather than
trusting the registry's privacy/readback flags.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from verify_record_chain_data_arweave_bundle import ROOT, verify_bundle

KNOWN_DUPLICATE_LIVE_TX_IDS = {
    "aAZ0lUPiRppjYWMjNQZEbOJyePPLSjHdZUs5Ifv2dSg",
    "D1tVrr8vdvFkfY2y8PpLAR1FFNOWXF3f9XbvwLdM2Go",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def historical_target(entry: dict[str, Any]) -> tuple[Any, ...]:
    return (
        entry.get("bundle_type"),
        entry.get("from_height_exclusive"),
        entry.get("to_height_inclusive"),
        entry.get("head_entry_hash"),
    )


def entry_matches_projection(entry: dict[str, Any], projection: dict[str, Any]) -> bool:
    """Compare only fields actually present in a sparse latest projection."""
    fields = {
        "height",
        "bundle_type",
        "bundle_file",
        "bundle_sha256",
        "arweave_tx_id",
        "arweave_hash_match",
        "head_entry_hash",
    }
    return all(projection.get(field) == entry.get(field) for field in fields if field in projection)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="record-chain/arweave-data-registry.json")
    parser.add_argument("--verify-local-bundles", action="store_true")
    parser.add_argument(
        "--allow-known-historical-duplicates",
        action="store_true",
        help="Allow only the exact two preserved June 2026 duplicate transactions for legacy height 15.",
    )
    args = parser.parse_args()

    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = ROOT / registry_path
    registry = read_json(registry_path)
    require(isinstance(registry, dict), "registry must be a JSON object")
    require(registry.get("schema") == "trinityaccord.record-chain-data-arweave-registry.v1", "bad registry schema")
    require(registry.get("chain_id") == "trinity-record-chain-main", "bad chain id")
    require(isinstance(registry.get("entries"), list), "entries must be list")
    require(isinstance(registry.get("latest_by_head"), dict), "latest_by_head must be object")

    entries: list[dict[str, Any]] = registry["entries"]
    live_targets: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    verified: list[dict[str, Any]] = []

    for index, entry in enumerate(entries):
        label = f"entry[{index}]"
        require(isinstance(entry, dict), f"{label}: entry must be object")
        require(entry.get("schema") == "trinityaccord.record-chain-data-arweave-registry-entry.v1", f"{label}: bad entry schema")
        require(entry.get("bundle_type") in {"delta", "snapshot"}, f"{label}: bad bundle_type")
        require(entry.get("mode") in {"dry-run", "live"}, f"{label}: bad mode")
        require(isinstance(entry.get("height"), int), f"{label}: bad height")
        require(isinstance(entry.get("from_height_exclusive"), int), f"{label}: bad from_height_exclusive")
        require(isinstance(entry.get("to_height_inclusive"), int), f"{label}: bad to_height_inclusive")
        require(entry["to_height_inclusive"] == entry["height"], f"{label}: end height mismatch")
        require(isinstance(entry.get("head_entry_hash"), str) and len(entry["head_entry_hash"]) == 64, f"{label}: bad head hash")
        require(isinstance(entry.get("bundle_file"), str), f"{label}: missing bundle_file")
        require(isinstance(entry.get("bundle_sha256"), str) and len(entry["bundle_sha256"]) == 64, f"{label}: bad bundle_sha256")

        if entry.get("mode") == "live":
            tx_id = entry.get("arweave_tx_id")
            require(isinstance(tx_id, str) and len(tx_id) >= 20, f"{label}: missing tx")
            require(entry.get("arweave_hash_match") is True, f"{label}: hash_match not true")
            require(entry.get("arweave_payload_sha256") == entry.get("arweave_readback_sha256"), f"{label}: payload/readback sha mismatch")
            live_targets[historical_target(entry)].append(entry)

        if args.verify_local_bundles:
            bundle_path = ROOT / entry["bundle_file"]
            result = verify_bundle(bundle_path)
            require(result["bundle_canonical_sha256"] == entry["bundle_sha256"], f"{label}: canonical bundle sha mismatch")
            if entry.get("mode") == "live":
                raw_hash = result["bundle_raw_file_sha256"]
                require(entry.get("arweave_payload_sha256") == raw_hash, f"{label}: Arweave payload sha does not match local bundle bytes")
                require(entry.get("arweave_readback_sha256") == raw_hash, f"{label}: Arweave readback sha does not match local bundle bytes")
            verified.append({"entry": index, "bundle_file": entry["bundle_file"], **result})

    duplicate_warnings: list[dict[str, Any]] = []
    for target, group in live_targets.items():
        if len(group) <= 1:
            continue
        tx_ids = {entry.get("arweave_tx_id") for entry in group}
        known = (
            args.allow_known_historical_duplicates
            and len(group) == 2
            and tx_ids == KNOWN_DUPLICATE_LIVE_TX_IDS
            and target == (
                "snapshot",
                0,
                15,
                "42f42d3544627404593de86bd6b3453d3ae95b8829d7aac33471adb8cd473eb1",
            )
        )
        require(
            known,
            "duplicate live uploads for one historical target are not allowed: "
            f"target={target}, tx_ids={sorted(str(value) for value in tx_ids)}",
        )
        duplicate_warnings.append(
            {
                "type": "known_historical_duplicate_paid_upload",
                "target": target,
                "tx_ids": sorted(tx_ids),
                "preserved_not_endorsed": True,
            }
        )

    for head_hash, projection in registry["latest_by_head"].items():
        require(isinstance(head_hash, str) and len(head_hash) == 64, "latest_by_head key must be a sha256")
        require(isinstance(projection, dict), f"latest_by_head[{head_hash}] must be object")
        require(projection.get("height") <= 15, f"latest_by_head[{head_hash}] exceeds frozen legacy height")
        require(
            any(entry.get("head_entry_hash") == head_hash and entry_matches_projection(entry, projection) for entry in entries),
            f"latest_by_head[{head_hash}] does not project a real registry entry",
        )

    latest_snapshot = registry.get("latest_snapshot")
    if latest_snapshot is not None:
        require(isinstance(latest_snapshot, dict), "latest_snapshot must be object or null")
        require(
            any(entry.get("bundle_type") == "snapshot" and entry_matches_projection(entry, latest_snapshot) for entry in entries),
            "latest_snapshot does not project a real snapshot entry",
        )

    print(
        json.dumps(
            {
                "result": "pass",
                "historical_archive_only": True,
                "current_native_record_chain": False,
                "entries": len(entries),
                "verified_local_bundles": len(verified),
                "warnings": duplicate_warnings,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
