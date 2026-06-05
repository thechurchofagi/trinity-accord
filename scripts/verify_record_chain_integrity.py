#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from record_chain_hashing import (
    DEFAULT_CHAIN_ID,
    build_chain_head,
    load_json,
    load_ledger,
    verify_entries,
    write_json_atomic,
)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify Trinity Record-Chain global hash ledger integrity."
    )
    parser.add_argument("--ledger", default="record-chain/hash-chain/main.chain.jsonl")
    parser.add_argument("--head", default="api/record-chain-head.json")
    parser.add_argument("--chain-id", default=DEFAULT_CHAIN_ID)
    parser.add_argument("--verify-payload-files", action="store_true")
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--write-report", default=None)
    parser.add_argument("--update-head", action="store_true")
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    head_path = Path(args.head)
    base_dir = Path(args.base_dir)

    entries = load_ledger(ledger_path)
    errors = verify_entries(
        entries,
        chain_id=args.chain_id,
        verify_payload_files=args.verify_payload_files,
        base_dir=base_dir,
    )

    head = build_chain_head(
        entries,
        chain_id=args.chain_id,
        generated_at=utc_now(),
    )

    head_errors: list[str] = []
    if head_path.exists():
        existing_head = load_json(head_path)
        if existing_head.get("head_entry_hash") != head.get("head_entry_hash"):
            head_errors.append(
                f"head_entry_hash mismatch: expected {head.get('head_entry_hash')}, "
                f"got {existing_head.get('head_entry_hash')}"
            )
        if existing_head.get("height") != head.get("height"):
            head_errors.append(
                f"height mismatch: expected {head.get('height')}, got {existing_head.get('height')}"
            )
        if existing_head.get("entry_count") != head.get("entry_count"):
            head_errors.append(
                f"entry_count mismatch: expected {head.get('entry_count')}, "
                f"got {existing_head.get('entry_count')}"
            )

    all_errors = errors + head_errors

    report = {
        "schema": "trinity_record_chain_integrity_report.v1",
        "ledger": str(ledger_path),
        "head": str(head_path),
        "chain_id": args.chain_id,
        "entry_count": len(entries),
        "height": head.get("height"),
        "head_entry_hash": head.get("head_entry_hash"),
        "verify_payload_files": args.verify_payload_files,
        "errors": all_errors,
        "result": "pass" if not all_errors else "fail",
        "generated_at": utc_now(),
    }

    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False))

    if args.write_report:
        write_json_atomic(Path(args.write_report), report)

    if args.update_head:
        write_json_atomic(head_path, head)

    if all_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
