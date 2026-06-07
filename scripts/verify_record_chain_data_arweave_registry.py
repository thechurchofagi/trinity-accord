#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

def canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"

def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_dumps(obj).encode("utf-8")).hexdigest()

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def require(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(msg)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="record-chain/arweave-data-registry.json")
    ap.add_argument("--verify-local-bundles", action="store_true")
    args = ap.parse_args()

    reg = read_json(ROOT / args.registry)
    require(reg.get("schema") == "trinityaccord.record-chain-data-arweave-registry.v1", "bad registry schema")
    require(reg.get("chain_id") == "trinity-record-chain-main", "bad chain id")
    require(isinstance(reg.get("entries"), list), "entries must be list")
    require(isinstance(reg.get("latest_by_head"), dict), "latest_by_head must be object")

    for i, entry in enumerate(reg["entries"]):
        label = f"entry[{i}]"
        require(entry.get("bundle_type") in {"delta", "snapshot"}, f"{label}: bad bundle_type")
        require(isinstance(entry.get("height"), int), f"{label}: bad height")
        require(isinstance(entry.get("head_entry_hash"), str) and len(entry["head_entry_hash"]) == 64, f"{label}: bad head hash")
        require(isinstance(entry.get("bundle_file"), str), f"{label}: missing bundle_file")
        require(isinstance(entry.get("bundle_sha256"), str) and len(entry["bundle_sha256"]) == 64, f"{label}: bad bundle_sha256")
        if entry.get("mode") == "live":
            require(isinstance(entry.get("arweave_tx_id"), str) and len(entry["arweave_tx_id"]) >= 20, f"{label}: missing tx")
            require(entry.get("arweave_hash_match") is True, f"{label}: hash_match not true")

        if args.verify_local_bundles:
            p = ROOT / entry["bundle_file"]
            require(p.exists(), f"{label}: missing bundle file {entry['bundle_file']}")
            bundle = read_json(p)
            bundle_for_hash = {k: v for k, v in bundle.items() if k != "bundle_canonical_sha256"}
            require(sha256_obj(bundle_for_hash) == entry["bundle_sha256"], f"{label}: bundle sha mismatch")
            require(bundle.get("chain_id") == "trinity-record-chain-main", f"{label}: bad bundle chain_id")
            privacy = bundle.get("privacy_scan") or {}
            require(privacy.get("contains_private_key") is False, f"{label}: private key flag not false")
            require(privacy.get("contains_client_oath_readback") is False, f"{label}: client oath flag not false")
            require(privacy.get("contains_readback_text") is False, f"{label}: readback flag not false")
            require(privacy.get("contains_token") is False, f"{label}: token flag not false")
            if bundle.get("bundle_type") == "record_chain_data_delta":
                records = bundle.get("records")
                require(isinstance(records, list) and records, f"{label}: delta records missing")
                require(all("record_payload" in r for r in records), f"{label}: record_payload missing")
            if bundle.get("bundle_type") == "record_chain_data_snapshot":
                require(isinstance(bundle.get("records"), list) and bundle["records"], f"{label}: snapshot records missing")
                require(isinstance(bundle.get("main_chain_jsonl"), str) and bundle["main_chain_jsonl"], f"{label}: main_chain_jsonl missing")

    print(json.dumps({"result": "pass", "entries": len(reg["entries"])}, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
