#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from record_chain_hashing import (
    DEFAULT_CHAIN_ID,
    build_chain_entry,
    build_chain_head,
    load_ledger,
    verify_entries,
    write_json_atomic,
    write_ledger_atomic,
)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def nullable_arg(value: str | None) -> str | None:
    if value is None:
        return None
    if value == "" or value.lower() == "null":
        return None
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append a finalized record to the Trinity Record-Chain global hash ledger."
    )
    parser.add_argument("--ledger", default="record-chain/hash-chain/main.chain.jsonl")
    parser.add_argument("--head-out", default="api/record-chain-head.json")
    parser.add_argument("--chain-id", default=DEFAULT_CHAIN_ID)
    parser.add_argument("--record-file", required=True)
    parser.add_argument("--record-type", required=True)
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--receipt-id", default=None)
    parser.add_argument("--source-run-id", default=None)
    parser.add_argument("--finalized-at", default=None)
    parser.add_argument("--finalized-by", default="record-chain-processor")
    parser.add_argument("--arweave-tx-id", default=None)
    parser.add_argument("--arweave-gateway-url", default=None)
    parser.add_argument("--arweave-payload-sha256", default=None)
    parser.add_argument("--arweave-readback-sha256", default=None)
    parser.add_argument("--arweave-hash-match", choices=["true", "false"], default=None)
    parser.add_argument("--verify-payload-files", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-genesis", action="store_true")
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    head_path = Path(args.head_out)
    record_file = Path(args.record_file)

    if not record_file.exists():
        raise SystemExit(f"record file does not exist: {record_file}")

    entries = load_ledger(ledger_path)
    existing_errors = verify_entries(
        entries,
        chain_id=args.chain_id,
        verify_payload_files=args.verify_payload_files,
        base_dir=Path("."),
    )
    if existing_errors:
        print("Existing ledger verification failed:")
        for error in existing_errors:
            print(f"- {error}")
        raise SystemExit(1)

    if not entries and not args.allow_genesis:
        raise SystemExit("Refusing to create genesis entry without --allow-genesis")

    previous_hash = entries[-1]["entry_hash"] if entries else None
    height = len(entries)

    arweave_hash_match = None
    if args.arweave_hash_match is not None:
        arweave_hash_match = args.arweave_hash_match == "true"

    entry = build_chain_entry(
        chain_id=args.chain_id,
        height=height,
        previous_entry_hash=previous_hash,
        record_file=record_file,
        record_type=args.record_type,
        record_id=args.record_id,
        receipt_id=nullable_arg(args.receipt_id),
        source_run_id=nullable_arg(args.source_run_id),
        finalized_at=args.finalized_at or utc_now(),
        finalized_by=args.finalized_by,
        arweave_tx_id=nullable_arg(args.arweave_tx_id),
        arweave_gateway_url=nullable_arg(args.arweave_gateway_url),
        arweave_payload_sha256=nullable_arg(args.arweave_payload_sha256),
        arweave_readback_sha256=nullable_arg(args.arweave_readback_sha256),
        arweave_hash_match=arweave_hash_match,
    )

    new_entries = entries + [entry]
    new_errors = verify_entries(
        new_entries,
        chain_id=args.chain_id,
        verify_payload_files=args.verify_payload_files,
        base_dir=Path("."),
    )
    if new_errors:
        print("New ledger verification failed:")
        for error in new_errors:
            print(f"- {error}")
        raise SystemExit(1)

    head = build_chain_head(
        new_entries,
        chain_id=args.chain_id,
        generated_at=utc_now(),
    )

    print("[RECORD CHAIN LINK APPEND]")
    print(f"ledger: {ledger_path}")
    print(f"height: {entry['height']}")
    print(f"chain_id: {entry['chain_id']}")
    print(f"record_type: {args.record_type}")
    print(f"record_id: {args.record_id}")
    print(f"receipt_id: {args.receipt_id}")
    print(f"previous_entry_hash: {entry['previous_entry_hash']}")
    print(f"entry_hash: {entry['entry_hash']}")
    print(f"payload_raw_sha256: {entry['record']['payload_raw_sha256']}")
    print(f"payload_canonical_sha256: {entry['record']['payload_canonical_sha256']}")
    print(f"dry_run: {args.dry_run}")

    if args.dry_run:
        print(json.dumps(entry, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False))
        return

    write_ledger_atomic(ledger_path, new_entries)
    write_json_atomic(head_path, head)

    print("[RECORD CHAIN LINK APPENDED]")
    print(f"head_out: {head_path}")
    print(f"head_entry_hash: {head['head_entry_hash']}")


if __name__ == "__main__":
    main()
