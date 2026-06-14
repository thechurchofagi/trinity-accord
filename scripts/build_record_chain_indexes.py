#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from record_chain_hashing import (
    CHAIN_INDEX_MANIFEST_SCHEMA,
    DEFAULT_CHAIN_ID,
    build_all_index,
    build_chain_head,
    build_type_index,
    load_ledger,
    record_type_slug,
    verify_entries,
    write_json_atomic,
)


DEFAULT_KNOWN_TYPES = [
    "echo",
    "verification",
    "guardian_application",
    "guardian_exit_application",
    "exit_application",
]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build public Record-Chain head and derived type indexes."
    )
    parser.add_argument("--ledger", default="record-chain/hash-chain/main.chain.jsonl")
    parser.add_argument("--out-dir", default="api")
    parser.add_argument("--chain-id", default=DEFAULT_CHAIN_ID)
    parser.add_argument(
        "--record-types",
        default="auto",
        help="Comma-separated record types, or 'auto' to discover all ledger record_type values.",
    )
    parser.add_argument("--verify-payload-files", action="store_true")
    parser.add_argument("--base-dir", default=".")
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    out_dir = Path(args.out_dir)
    generated_at = utc_now()

    entries = load_ledger(ledger_path)
    errors = verify_entries(
        entries,
        chain_id=args.chain_id,
        verify_payload_files=args.verify_payload_files,
        base_dir=Path(args.base_dir),
    )
    if errors:
        print("Ledger verification failed; refusing to build indexes.")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    if args.record_types == "auto":
        discovered = sorted(
            {
                entry.get("record", {}).get("record_type")
                for entry in entries
                if isinstance(entry.get("record"), dict)
                and entry.get("record", {}).get("record_type")
            }
        )
        record_types = sorted(set(DEFAULT_KNOWN_TYPES) | set(discovered))
    else:
        record_types = [x.strip() for x in args.record_types.split(",") if x.strip()]

    slug_to_type: dict[str, str] = {}
    for record_type in record_types:
        slug = record_type_slug(record_type)
        existing = slug_to_type.get(slug)
        if existing and existing != record_type:
            raise SystemExit(
                f"record_type slug collision: {existing!r} and {record_type!r} both map to {slug!r}"
            )
        slug_to_type[slug] = record_type

    head = build_chain_head(entries, chain_id=args.chain_id, generated_at=generated_at)
    all_index = build_all_index(entries, chain_id=args.chain_id, generated_at=generated_at)

    # Part D: fail-closed metadata for legacy APIs
    _FAIL_CLOSED_META = {
        "historical_archive_only": True,
        "legacy_hash_chain_view": True,
        "not_current_native_record_chain_head": True,
        "replacement_current_status_api": "/api/record-chain-status.json",
        "replacement_native_record_index": "/record-chain/indexes/record-index.json",
        "replacement_native_chain_tip": "/record-chain/chain-tip.json",
        "authority": "legacy hash-chain view; not current native Record-Chain head",
    }
    head.update(_FAIL_CLOSED_META)
    all_index.update({
        "historical_archive_only": True,
        "legacy_hash_chain_view": True,
        "not_current_native_record_chain_index": True,
        "replacement_current_status_api": "/api/record-chain-status.json",
        "replacement_native_record_index": "/record-chain/indexes/record-index.json",
        "replacement_native_chain_tip": "/record-chain/chain-tip.json",
        "authority": "legacy hash-chain derived index; not current native Record-Chain index",
    })

    write_json_atomic(out_dir / "record-chain-head.json", head)
    write_json_atomic(out_dir / "record-chain-index.all.json", all_index)
    write_json_atomic(out_dir / "record-chain-index.all.json", all_index)

    written_indexes = []
    _INDEX_FAIL_CLOSED_META = {
        "historical_archive_only": True,
        "legacy_hash_chain_view": True,
        "not_current_native_record_chain_index": True,
        "replacement_current_status_api": "/api/record-chain-status.json",
        "replacement_native_record_index": "/record-chain/indexes/record-index.json",
        "replacement_native_chain_tip": "/record-chain/chain-tip.json",
        "authority": "legacy hash-chain derived index; not current native Record-Chain index",
    }
    for record_type in record_types:
        index = build_type_index(
            entries,
            chain_id=args.chain_id,
            record_type=record_type,
            generated_at=generated_at,
        )
        index.update(_INDEX_FAIL_CLOSED_META)
        out_file = out_dir / index["index_file"]
        write_json_atomic(out_file, index)
        written_indexes.append(str(out_file))

    manifest = {
        "schema": CHAIN_INDEX_MANIFEST_SCHEMA,
        "chain_id": args.chain_id,
        "generated_at": generated_at,
        "source_ledger": str(ledger_path),
        "historical_archive_only": True,
        "legacy_hash_chain_view": True,
        "not_current_native_record_chain_index": True,
        "replacement_current_status_api": "/api/record-chain-status.json",
        "replacement_native_record_index": "/record-chain/indexes/record-index.json",
        "replacement_native_chain_tip": "/record-chain/chain-tip.json",
        "authority": "legacy hash-chain derived indexes; not current native Record-Chain authority",
        "record_types": [
            {
                "record_type": record_type,
                "record_type_slug": record_type_slug(record_type),
                "index_file": f"record-chain-index.{record_type_slug(record_type)}.json",
            }
            for record_type in record_types
        ],
        "authority": "derived indexes; main.chain.jsonl is authoritative",
    }
    write_json_atomic(out_dir / "record-chain-index.manifest.json", manifest)

    print("[RECORD CHAIN INDEXES BUILT]")
    print(json.dumps({
        "ledger": str(ledger_path),
        "out_dir": str(out_dir),
        "entry_count": len(entries),
        "head_entry_hash": head.get("head_entry_hash"),
        "record_types": record_types,
        "written_indexes": written_indexes,
    }, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
