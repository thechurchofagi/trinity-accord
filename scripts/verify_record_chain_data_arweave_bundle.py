#!/usr/bin/env python3
"""Verify a historical legacy hash-chain data bundle.

Unlike the old registry verifier, this validates the embedded self-hash and
rescans actual content instead of trusting privacy flag booleans.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_record_chain_data_arweave_bundle import (
    FORBIDDEN_PATTERNS,
    ROOT,
    logical_bundle_view,
    sha256_obj,
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"bundle must be a JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def scan_actual_content(bundle: dict[str, Any], label: str) -> None:
    raw = json.dumps(bundle, ensure_ascii=False, sort_keys=True)
    hits = [pattern.pattern for pattern in FORBIDDEN_PATTERNS if pattern.search(raw)]
    require(not hits, f"{label}: actual content contains forbidden material: {hits}")


def verify_bundle(path: Path) -> dict[str, Any]:
    require(path.exists() and path.is_file(), f"bundle missing: {path}")
    bundle = read_json(path)
    schema = bundle.get("schema")
    allowed_schemas = {
        "trinityaccord.record-chain-data-delta-bundle.v1",
        "trinityaccord.record-chain-data-snapshot-bundle.v1",
        "trinityaccord.legacy-hash-chain-data-delta-bundle.v2",
        "trinityaccord.legacy-hash-chain-data-snapshot-bundle.v2",
    }
    require(schema in allowed_schemas, f"unsupported historical bundle schema: {schema}")
    require(bundle.get("chain_id") == "trinity-record-chain-main", "bad historical chain_id")
    require(bundle.get("bundle_type") in {"record_chain_data_delta", "record_chain_data_snapshot"}, "bad bundle_type")

    embedded_hash = bundle.get("bundle_canonical_sha256")
    require(isinstance(embedded_hash, str) and len(embedded_hash) == 64, "bundle self-hash missing")
    calculated_hash = sha256_obj({key: value for key, value in bundle.items() if key != "bundle_canonical_sha256"})
    require(calculated_hash == embedded_hash, "bundle_canonical_sha256 does not match actual bundle content")

    identity = bundle.get("bundle_identity_sha256")
    if identity is not None:
        require(isinstance(identity, str) and len(identity) == 64, "bad bundle_identity_sha256")
        require(identity == sha256_obj(logical_bundle_view(bundle)), "bundle_identity_sha256 mismatch")

    scan_actual_content(bundle, str(path))
    privacy = bundle.get("privacy_scan")
    require(isinstance(privacy, dict), "privacy_scan missing")
    for field in (
        "contains_private_key",
        "contains_client_oath_readback",
        "contains_readback_text",
        "contains_token",
    ):
        require(privacy.get(field) is False, f"privacy_scan.{field} must be false")

    entries = bundle.get("hash_chain_entries")
    records = bundle.get("records")
    require(isinstance(entries, list) and entries, "hash_chain_entries missing")
    require(isinstance(records, list) and records, "records missing")
    require(len(entries) == len(records), "entry/record count mismatch")
    heights = [entry.get("height") for entry in entries]
    require(all(isinstance(value, int) for value in heights), "entry height must be integer")
    require(heights == list(range(heights[0], heights[-1] + 1)), "bundle heights are not contiguous")
    require(all("record_payload" in record for record in records), "record_payload missing")

    if bundle.get("bundle_type") == "record_chain_data_snapshot":
        require(heights[0] == 0, "snapshot must begin at legacy height zero")
        require(bundle.get("height") == heights[-1], "snapshot height mismatch")
        require(bundle.get("entry_count") == len(entries), "snapshot entry_count mismatch")
        require(isinstance(bundle.get("main_chain_jsonl"), str) and bundle["main_chain_jsonl"], "snapshot main_chain_jsonl missing")
    else:
        require(bundle.get("from_height_exclusive") == heights[0] - 1, "delta start boundary mismatch")
        require(bundle.get("to_height_inclusive") == heights[-1], "delta end boundary mismatch")

    if schema.endswith(".v2"):
        boundary = bundle.get("boundary") or {}
        require(boundary.get("legacy_hash_chain_view") is True, "v2 bundle must declare legacy_hash_chain_view")
        require(boundary.get("historical_archive_only") is True, "v2 bundle must declare historical_archive_only")
        require(boundary.get("not_current_native_record_chain") is True, "v2 bundle must reject current-native interpretation")
        require("native_chain_tip" not in bundle, "v2 historical bundle must not embed moving native_chain_tip state")

    return {
        "schema": schema,
        "bundle_type": bundle.get("bundle_type"),
        "height_first": heights[0],
        "height_last": heights[-1],
        "entry_count": len(entries),
        "bundle_canonical_sha256": calculated_hash,
        "bundle_raw_file_sha256": sha256_file(path),
        "bundle_identity_sha256": identity,
        "historical_archive_only": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-file", required=True)
    args = parser.parse_args()
    result = verify_bundle(resolve_path(args.bundle_file))
    print(json.dumps({"result": "pass", **result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
