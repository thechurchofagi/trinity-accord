#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
import hashlib


TX_RE = re.compile(r"^[A-Za-z0-9_-]{20,}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="record-chain/ots/arweave-registry.json")
    parser.add_argument("--verify-local-bundles", action="store_true")
    args = parser.parse_args()

    registry = load_json(Path(args.registry))
    errors: list[str] = []

    if registry.get("schema") != "trinity_record_chain_ots_arweave_registry.v1":
        errors.append("schema mismatch")

    entries = registry.get("entries")
    if not isinstance(entries, list):
        errors.append("entries must be list")
        entries = []

    seen_tx: set[str] = set()
    seen_keys: set[str] = set()

    for i, entry in enumerate(entries):
        tx = entry.get("arweave_tx_id")
        key = entry.get("registry_key")
        if not isinstance(key, str) or not key:
            errors.append(f"entry[{i}]: registry_key missing")
        elif key in seen_keys:
            errors.append(f"entry[{i}]: duplicate registry_key {key}")
        else:
            seen_keys.add(key)

        if not isinstance(tx, str) or not TX_RE.match(tx):
            errors.append(f"entry[{i}]: invalid arweave_tx_id")
        elif tx in seen_tx:
            errors.append(f"entry[{i}]: duplicate arweave_tx_id {tx}")
        else:
            seen_tx.add(tx)

        if entry.get("arweave_hash_match") is not True:
            errors.append(f"entry[{i}]: arweave_hash_match must be true")

        if entry.get("arweave_payload_sha256") != entry.get("arweave_readback_sha256"):
            errors.append(f"entry[{i}]: payload/readback sha mismatch")

        if args.verify_local_bundles:
            bundle_file = entry.get("bundle_file")
            if not bundle_file:
                errors.append(f"entry[{i}]: bundle_file missing")
            else:
                path = Path(bundle_file)
                if not path.exists():
                    errors.append(f"entry[{i}]: local bundle missing: {path}")
                else:
                    actual_sha = sha256_bytes(path.read_bytes())
                    if actual_sha != entry.get("bundle_sha256"):
                        errors.append(f"entry[{i}]: bundle sha mismatch")

    report = {
        "schema": "trinity_record_chain_ots_arweave_registry_verify_report.v1",
        "registry": args.registry,
        "entry_count": len(entries),
        "errors": errors,
        "result": "pass" if not errors else "fail",
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
