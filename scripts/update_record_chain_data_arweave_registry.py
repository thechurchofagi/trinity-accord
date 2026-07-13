#!/usr/bin/env python3
"""Preview a legacy hash-chain data-registry entry without mutating evidence.

The historical registry already contains two paid uploads for the same frozen
height-15 snapshot. The legacy upload path is retired; current native archives
are maintained by ``record-chain-arweave-archive.yml``. This tool therefore
supports read-only candidate inspection only and refuses live updates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from verify_record_chain_data_arweave_bundle import ROOT, verify_bundle

REG = ROOT / "record-chain/arweave-data-registry.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-file", required=True)
    parser.add_argument("--upload-result-json")
    parser.add_argument("--mode", choices=["dry-run", "live"], default="dry-run")
    args = parser.parse_args()

    if args.mode == "live":
        raise SystemExit(
            "legacy record-chain data Arweave uploads are retired; refusing to modify the "
            "historical registry. Use .github/workflows/record-chain-arweave-archive.yml "
            "for current native Record-Chain archives."
        )
    if args.upload_result_json:
        raise SystemExit("upload-result-json is not accepted in retired dry-run mode")

    bundle_path = resolve_path(args.bundle_file)
    verification = verify_bundle(bundle_path)
    bundle = read_json(bundle_path)

    if bundle.get("bundle_type") == "record_chain_data_delta":
        bundle_type = "delta"
        height = bundle["to_height_inclusive"]
        head_hash = bundle["head_after"]["head_entry_hash"]
        from_height = bundle["from_height_exclusive"]
        to_height = bundle["to_height_inclusive"]
    elif bundle.get("bundle_type") == "record_chain_data_snapshot":
        bundle_type = "snapshot"
        height = bundle["height"]
        head_hash = bundle["head_entry_hash"]
        from_height = 0
        to_height = height
    else:
        raise SystemExit(f"unknown bundle_type: {bundle.get('bundle_type')}")

    candidate: dict[str, Any] = {
        "schema": "trinityaccord.record-chain-data-arweave-registry-entry.v1",
        "mode": "dry-run",
        "historical_archive_only": True,
        "current_native_record_chain": False,
        "bundle_type": bundle_type,
        "height": height,
        "from_height_exclusive": from_height,
        "to_height_inclusive": to_height,
        "head_entry_hash": head_hash,
        "bundle_file": str(bundle_path),
        "bundle_sha256": verification["bundle_canonical_sha256"],
        "bundle_raw_file_sha256": verification["bundle_raw_file_sha256"],
        "arweave_tx_id": None,
        "arweave_hash_match": None,
        "would_write_registry": False,
        "replacement_native_archive_workflow": ".github/workflows/record-chain-arweave-archive.yml",
    }

    existing = read_json(REG)
    matching = [
        entry
        for entry in existing.get("entries", [])
        if entry.get("bundle_type") == bundle_type
        and entry.get("from_height_exclusive") == from_height
        and entry.get("to_height_inclusive") == to_height
        and entry.get("head_entry_hash") == head_hash
    ]

    print(
        json.dumps(
            {
                "result": "pass",
                "retired_read_only_preview": True,
                "candidate": candidate,
                "existing_same_historical_target": len(matching),
                "existing_tx_ids": sorted(
                    entry.get("arweave_tx_id") for entry in matching if entry.get("arweave_tx_id")
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
