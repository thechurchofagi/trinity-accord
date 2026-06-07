#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAIN_ID = "trinity-record-chain-main"
LEDGER = ROOT / "record-chain/hash-chain/main.chain.jsonl"
HEAD = ROOT / "api/record-chain-head.json"
OUT_DIR = ROOT / "record-chain/arweave-data-bundles"

FORBIDDEN_PATTERNS = [
    re.compile(r"BEGIN\s+PRIVATE\s+KEY", re.I),
    re.compile(r"BEGIN\s+OPENSSH\s+PRIVATE\s+KEY", re.I),
    re.compile(r"authorship-private\.pem", re.I),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"ARKEY", re.I),
    re.compile(r'"client_oath_readback"\s*:'),
    re.compile(r'"readback_text"\s*:'),
    re.compile(r'"raw_oath"\s*:'),
]

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
    path.write_text(canonical_dumps(obj), encoding="utf-8")

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def scan_no_forbidden(obj: Any, label: str) -> None:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    hits = [p.pattern for p in FORBIDDEN_PATTERNS if p.search(raw)]
    if hits:
        raise SystemExit(f"{label} contains forbidden material: {hits}")

def entries_by_height() -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for entry in read_jsonl(LEDGER):
        h = entry.get("height")
        if not isinstance(h, int):
            raise SystemExit(f"ledger entry missing integer height: {entry}")
        out[h] = entry
    return out

def load_payload(entry: dict[str, Any]) -> dict[str, Any]:
    rec = entry.get("record", entry)
    payload_file = rec.get("payload_file")
    record_id = rec.get("record_id")
    if not payload_file:
        if not isinstance(record_id, str):
            raise SystemExit(f"entry missing record_id and payload_file: {entry}")
        payload_file = f"record-chain/records/{record_id}.json"
    p = ROOT / str(payload_file)
    if not p.exists():
        raise SystemExit(f"missing payload file: {payload_file}")
    obj = read_json(p)
    scan_no_forbidden(obj, str(payload_file))
    return obj

def build_delta(from_height_exclusive: int, to_height_inclusive: int) -> dict[str, Any]:
    head = read_json(HEAD)
    by_h = entries_by_height()
    selected = [h for h in sorted(by_h) if from_height_exclusive < h <= to_height_inclusive]
    if not selected:
        raise SystemExit("delta selected no entries")

    records = []
    entries = []
    for h in selected:
        entry = by_h[h]
        payload = load_payload(entry)
        rec = entry.get("record", entry)
        records.append({
            "height": h,
            "record_id": rec.get("record_id"),
            "record_type": rec.get("record_type"),
            "payload_file": rec.get("payload_file"),
            "entry_hash": entry.get("entry_hash"),
            "payload_raw_sha256": rec.get("payload_raw_sha256"),
            "payload_canonical_sha256": rec.get("payload_canonical_sha256"),
            "record_payload": payload,
        })
        entries.append(entry)

    before = by_h.get(from_height_exclusive)
    after = by_h.get(to_height_inclusive)
    if not after:
        raise SystemExit(f"missing to height: {to_height_inclusive}")

    bundle = {
        "schema": "trinityaccord.record-chain-data-delta-bundle.v1",
        "bundle_type": "record_chain_data_delta",
        "created_at": utc_now(),
        "chain_id": CHAIN_ID,
        "from_height_exclusive": from_height_exclusive,
        "to_height_inclusive": to_height_inclusive,
        "head_before": {
            "height": from_height_exclusive,
            "head_entry_hash": before.get("entry_hash") if before else None,
        },
        "head_after": {
            "height": to_height_inclusive,
            "head_entry_hash": after.get("entry_hash"),
            "api_head_height": head.get("height"),
            "api_head_entry_hash": head.get("head_entry_hash"),
        },
        "hash_chain_entries": entries,
        "records": records,
        "privacy_scan": {
            "contains_private_key": False,
            "contains_client_oath_readback": False,
            "contains_readback_text": False,
            "contains_token": False,
        },
        "boundary": {
            "arweave_data_archive_is_backup_only": True,
            "arweave_data_archive_is_not_authority": True,
            "arweave_data_archive_is_not_attestation": True,
            "arweave_data_archive_is_not_amendment": True,
            "arweave_data_archive_is_not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }
    scan_no_forbidden(bundle, "delta bundle")
    bundle["bundle_canonical_sha256"] = sha256_obj(bundle)
    return bundle

def build_snapshot(height: int) -> dict[str, Any]:
    head = read_json(HEAD)
    by_h = entries_by_height()
    if height not in by_h:
        raise SystemExit(f"snapshot height not found: {height}")

    selected = [h for h in sorted(by_h) if h <= height]
    records = []
    entries = []
    for h in selected:
        entry = by_h[h]
        payload = load_payload(entry)
        rec = entry.get("record", entry)
        records.append({
            "height": h,
            "record_id": rec.get("record_id"),
            "record_type": rec.get("record_type"),
            "payload_file": rec.get("payload_file"),
            "entry_hash": entry.get("entry_hash"),
            "record_payload": payload,
        })
        entries.append(entry)

    chain_tip_path = ROOT / "record-chain/chain-tip.json"
    chain_tip = read_json(chain_tip_path) if chain_tip_path.exists() else None

    bundle = {
        "schema": "trinityaccord.record-chain-data-snapshot-bundle.v1",
        "bundle_type": "record_chain_data_snapshot",
        "created_at": utc_now(),
        "chain_id": CHAIN_ID,
        "height": height,
        "entry_count": len(selected),
        "head_entry_hash": by_h[height].get("entry_hash"),
        "api_head": head,
        "native_chain_tip": chain_tip,
        "hash_chain_entries": entries,
        "records": records,
        "main_chain_jsonl": "\n".join(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in entries) + "\n",
        "privacy_scan": {
            "contains_private_key": False,
            "contains_client_oath_readback": False,
            "contains_readback_text": False,
            "contains_token": False,
        },
        "boundary": {
            "arweave_data_archive_is_backup_only": True,
            "arweave_data_archive_is_not_authority": True,
            "arweave_data_archive_is_not_attestation": True,
            "arweave_data_archive_is_not_amendment": True,
            "arweave_data_archive_is_not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }
    scan_no_forbidden(bundle, "snapshot bundle")
    bundle["bundle_canonical_sha256"] = sha256_obj(bundle)
    return bundle

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["delta", "snapshot"])
    ap.add_argument("--from-height-exclusive", type=int)
    ap.add_argument("--to-height-inclusive", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    head = read_json(HEAD)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "delta":
        if args.from_height_exclusive is None:
            raise SystemExit("--from-height-exclusive required for delta")
        to_h = args.to_height_inclusive if args.to_height_inclusive is not None else int(head["height"])
        bundle = build_delta(args.from_height_exclusive, to_h)
        name = f"data-delta-height-{args.from_height_exclusive + 1}-to-{to_h}-{bundle['head_after']['head_entry_hash'][:12]}.json"
    else:
        h = args.height if args.height is not None else int(head["height"])
        bundle = build_snapshot(h)
        name = f"data-snapshot-height-{h}-{bundle['head_entry_hash'][:12]}.json"

    path = out_dir / name
    write_json(path, bundle)
    print(json.dumps({
        "result": "pass",
        "bundle_file": str(path.relative_to(ROOT)),
        "bundle_type": bundle["bundle_type"],
        "bundle_sha256": sha256_obj(bundle),
    }, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
