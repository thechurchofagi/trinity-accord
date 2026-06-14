#!/usr/bin/env python3
"""Part C: Native record hash semantics verifier.

Reads every record in record-chain/records/, computes multiple hash variants,
verifies declared record_sha256 continuity and chain-tip consistency.
Does NOT mutate any file.

Usage:
    python scripts/verify_native_record_hash_semantics.py [--base-dir .] [--out report.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify native record hash semantics.")
    parser.add_argument("--base-dir", default=".", help="Repository root")
    parser.add_argument("--out", default=None, help="Write JSON report to this path")
    args = parser.parse_args()

    base = Path(args.base_dir)
    records_dir = base / "record-chain" / "records"
    chain_tip_path = base / "record-chain" / "chain-tip.json"
    index_path = base / "record-chain" / "indexes" / "record-index.json"

    errors: list[str] = []
    records_info: list[dict] = []

    # Load chain tip
    if not chain_tip_path.exists():
        print("FAIL: missing chain-tip.json", file=sys.stderr)
        return 1
    chain_tip = load_json(chain_tip_path)

    # Load record index
    if not index_path.exists():
        print("FAIL: missing record-index.json", file=sys.stderr)
        return 1
    record_index = load_json(index_path)
    entries = record_index.get("records")
    if not isinstance(entries, list):
        print("FAIL: record-index.json must contain a records list", file=sys.stderr)
        return 1

    # Build index lookup by record_id
    index_by_id: dict[str, dict] = {}
    for entry in entries:
        rid = entry.get("record_id", "")
        index_by_id[rid] = entry

    # Enumerate record files
    record_files = sorted(records_dir.glob("R-*.json"))
    if not record_files:
        print("FAIL: no record files found in record-chain/records/", file=sys.stderr)
        return 1

    prev_declared_sha: str | None = None

    for rf in record_files:
        raw_bytes = rf.read_bytes()
        raw_file_sha256 = sha256_hex(raw_bytes)

        try:
            record = json.loads(raw_bytes)
        except json.JSONDecodeError as exc:
            errors.append(f"{rf.name}: invalid JSON: {exc}")
            continue

        record_id = record.get("record_id", rf.stem)
        declared_sha256 = record.get("record_sha256", "")

        # Compute hash variants
        full_canonical = canonical_json(record)
        full_canonical_sha256 = sha256_hex(full_canonical)

        without_self = {k: v for k, v in record.items() if k != "record_sha256"}
        without_self_canonical = canonical_json(without_self)
        without_self_sha256 = sha256_hex(without_self_canonical)

        # without append-assigned fields
        append_fields = {
            "record_index", "record_id", "assigned_at", "previous_record_sha256",
            "content_sha256", "record_sha256", "batch_id", "batch_membership",
            "batch_manifest_sha256", "ots_proof_path", "server_receipt",
            "server_receipt_id", "created_by_gateway", "server_validated", "server_rendered",
        }
        without_append = {k: v for k, v in record.items() if k not in append_fields}
        without_append_canonical = canonical_json(without_append)
        without_append_sha256 = sha256_hex(without_append_canonical)

        # Extract signed_payload_sha256 from authorship_proof
        signed_payload_sha256 = ""
        proof = record.get("authorship_proof") or record.get("proof") or {}
        if isinstance(proof, dict):
            signed_payload_sha256 = proof.get("signed_payload_sha256", "")

        # Verify declared record_sha256 matches index
        index_entry = index_by_id.get(record_id, {})
        index_declared = index_entry.get("record_sha256", "")
        if declared_sha256 and index_declared and declared_sha256 != index_declared:
            errors.append(
                f"{record_id}: declared record_sha256 {declared_sha256[:16]}... "
                f"!= index record_sha256 {index_declared[:16]}..."
            )

        # Verify previous_record_sha256 continuity
        if prev_declared_sha is not None:
            actual_prev = record.get("previous_record_sha256", "")
            if actual_prev and actual_prev != prev_declared_sha:
                errors.append(
                    f"{record_id}: previous_record_sha256 {actual_prev[:16]}... "
                    f"!= expected {prev_declared_sha[:16]}..."
                )

        if declared_sha256:
            prev_declared_sha = declared_sha256

        records_info.append({
            "record_id": record_id,
            "file": str(rf.relative_to(base)),
            "raw_file_sha256": raw_file_sha256,
            "full_canonical_sha256": full_canonical_sha256,
            "without_record_sha256_canonical_sha256": without_self_sha256,
            "without_append_fields_canonical_sha256": without_append_sha256,
            "declared_record_sha256": declared_sha256,
            "signed_payload_sha256": signed_payload_sha256,
            "previous_record_sha256": record.get("previous_record_sha256", ""),
        })

    # Verify chain-tip latest matches last record
    if records_info:
        last = records_info[-1]
        tip_sha = chain_tip.get("latest_record_sha256", "")
        if tip_sha and last["declared_record_sha256"] and tip_sha != last["declared_record_sha256"]:
            errors.append(
                f"chain-tip latest_record_sha256 {tip_sha[:16]}... "
                f"!= last record declared {last['declared_record_sha256'][:16]}..."
            )

    # Build report
    report = {
        "schema": "trinityaccord.native-record-hash-semantics-verify.v1",
        "total_records": len(records_info),
        "errors": errors,
        "records": records_info,
    }

    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if errors:
        print(f"FAIL: {len(errors)} error(s) found:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: {len(records_info)} records verified, no continuity errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
