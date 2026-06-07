#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "record-chain/arweave-data-registry.json"
API_REG = ROOT / "api/record-chain-arweave-data-registry.json"

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"

def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_dumps(obj).encode("utf-8")).hexdigest()

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

def load_registry() -> dict[str, Any]:
    if REG.exists():
        return read_json(REG)
    return {
        "schema": "trinityaccord.record-chain-data-arweave-registry.v1",
        "generated_at": None,
        "chain_id": "trinity-record-chain-main",
        "latest_by_head": {},
        "latest_snapshot": None,
        "entries": [],
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle-file", required=True)
    ap.add_argument("--upload-result-json")
    ap.add_argument("--mode", choices=["dry-run", "live"], default="dry-run")
    args = ap.parse_args()

    bundle_path = ROOT / args.bundle_file
    bundle = read_json(bundle_path)
    bundle_sha = sha256_obj({k: v for k, v in bundle.items() if k != "bundle_canonical_sha256"})

    upload = read_json(ROOT / args.upload_result_json) if args.upload_result_json else {}
    txid = upload.get("txid") or upload.get("arweave_tx_id")
    readback_sha = upload.get("readback_sha256") or upload.get("arweave_readback_sha256")
    payload_sha = upload.get("payload_sha256") or upload.get("arweave_payload_sha256") or bundle_sha
    hash_match = bool(readback_sha and readback_sha == payload_sha) or upload.get("hash_match") is True

    if bundle.get("bundle_type") == "record_chain_data_delta":
        bundle_type = "delta"
        height = bundle["to_height_inclusive"]
        head_hash = bundle["head_after"]["head_entry_hash"]
        from_h = bundle["from_height_exclusive"]
        to_h = bundle["to_height_inclusive"]
    elif bundle.get("bundle_type") == "record_chain_data_snapshot":
        bundle_type = "snapshot"
        height = bundle["height"]
        head_hash = bundle["head_entry_hash"]
        from_h = 0
        to_h = height
    else:
        raise SystemExit(f"unknown bundle_type: {bundle.get('bundle_type')}")

    if args.mode == "live" and not txid:
        raise SystemExit("live mode requires upload tx id")
    if args.mode == "live" and hash_match is not True:
        raise SystemExit("live mode requires readback hash match")

    reg = load_registry()
    entry = {
        "schema": "trinityaccord.record-chain-data-arweave-registry-entry.v1",
        "created_at": utc_now(),
        "mode": args.mode,
        "bundle_type": bundle_type,
        "height": height,
        "from_height_exclusive": from_h,
        "to_height_inclusive": to_h,
        "head_entry_hash": head_hash,
        "bundle_file": args.bundle_file,
        "bundle_sha256": bundle_sha,
        "arweave_tx_id": txid,
        "arweave_payload_sha256": payload_sha if txid else None,
        "arweave_readback_sha256": readback_sha if txid else None,
        "arweave_hash_match": hash_match if txid else None,
    }

    entries = reg.setdefault("entries", [])
    if not any(e.get("bundle_sha256") == bundle_sha and e.get("arweave_tx_id") == txid and e.get("mode") == args.mode for e in entries):
        entries.append(entry)

    reg["generated_at"] = utc_now()
    reg["chain_id"] = "trinity-record-chain-main"
    reg.setdefault("latest_by_head", {})[head_hash] = {
        "height": height,
        "bundle_type": bundle_type,
        "bundle_file": args.bundle_file,
        "bundle_sha256": bundle_sha,
        "arweave_tx_id": txid,
        "arweave_hash_match": hash_match if txid else None,
    }
    if bundle_type == "snapshot":
        reg["latest_snapshot"] = {
            "height": height,
            "head_entry_hash": head_hash,
            "bundle_file": args.bundle_file,
            "bundle_sha256": bundle_sha,
            "arweave_tx_id": txid,
        }

    write_json(REG, reg)
    write_json(API_REG, reg)
    print(json.dumps({"result": "pass", "entry": entry}, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
