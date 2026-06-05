#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

from record_chain_hashing import (
    CHAIN_HEAD_SCHEMA,
    DEFAULT_CHAIN_ID,
    OTS_ANCHOR_SCHEMA,
    OTS_LATEST_SCHEMA,
    build_chain_head,
    build_head_commitment,
    canonical_json_bytes,
    load_json,
    load_ledger,
    sha256_bytes,
    verify_entries,
    write_bytes_atomic,
    write_json_atomic,
)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an OpenTimestamps anchor for the current Record-Chain head commitment."
    )
    parser.add_argument("--ledger", default="record-chain/hash-chain/main.chain.jsonl")
    parser.add_argument("--head", default="api/record-chain-head.json")
    parser.add_argument("--chain-id", default=DEFAULT_CHAIN_ID)
    parser.add_argument("--out-dir", default="record-chain/ots/anchors")
    parser.add_argument("--api-out", default="api/record-chain-ots-latest.json")
    parser.add_argument("--ots-bin", default="ots")
    parser.add_argument("--mode", choices=["dry-run", "stamp"], default="dry-run")
    parser.add_argument("--verify-ledger", action="store_true")
    parser.add_argument("--verify-payload-files", action="store_true")
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    head_path = Path(args.head)
    out_dir = Path(args.out_dir)
    api_out = Path(args.api_out)

    entries = load_ledger(ledger_path)
    if args.verify_ledger:
        errors = verify_entries(
            entries,
            chain_id=args.chain_id,
            verify_payload_files=args.verify_payload_files,
            base_dir=Path(args.base_dir),
        )
        if errors:
            print("Ledger verification failed; refusing OTS anchor.")
            for error in errors:
                print(f"- {error}")
            raise SystemExit(1)

    if not head_path.exists():
        raise SystemExit(f"head file does not exist: {head_path}")

    head = load_json(head_path)
    if head.get("schema") != CHAIN_HEAD_SCHEMA:
        raise SystemExit(f"head schema mismatch: {head.get('schema')}")
    if head.get("chain_id") != args.chain_id:
        raise SystemExit(f"head chain_id mismatch: {head.get('chain_id')} != {args.chain_id}")

    expected_head = build_chain_head(
        entries,
        chain_id=args.chain_id,
        generated_at=head.get("generated_at", ""),
    )
    if head.get("head_entry_hash") != expected_head.get("head_entry_hash"):
        raise SystemExit(
            f"head_entry_hash mismatch: head file={head.get('head_entry_hash')} "
            f"ledger={expected_head.get('head_entry_hash')}"
        )
    if head.get("height") != expected_head.get("height"):
        raise SystemExit(
            f"height mismatch: head file={head.get('height')} ledger={expected_head.get('height')}"
        )
    if head.get("entry_count") != expected_head.get("entry_count"):
        raise SystemExit(
            f"entry_count mismatch: head file={head.get('entry_count')} ledger={expected_head.get('entry_count')}"
        )

    commitment = build_head_commitment(head)
    commitment_bytes = canonical_json_bytes(commitment)
    commitment_sha256 = sha256_bytes(commitment_bytes)

    height = commitment["height"]
    entry_count = commitment["entry_count"]
    head_entry_hash = commitment["head_entry_hash"]

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"height-{height}-{head_entry_hash[:16]}-{commitment_sha256[:16]}"
    snapshot_path = out_dir / f"{prefix}.record-chain-head-commitment.json"
    ots_path = Path(str(snapshot_path) + ".ots")
    anchor_path = out_dir / f"{prefix}.anchor.json"

    if not args.overwrite:
        for p in (snapshot_path, ots_path, anchor_path):
            if p.exists():
                raise SystemExit(f"refusing to overwrite existing file without --overwrite: {p}")

    write_bytes_atomic(snapshot_path, commitment_bytes)

    ots_command = None
    ots_stdout = None
    ots_stderr = None
    ots_exit_code = None
    ots_file_exists = False
    ots_file_sha256 = None

    if args.mode == "stamp":
        if not shutil.which(args.ots_bin):
            raise SystemExit(
                f"OpenTimestamps CLI not found: {args.ots_bin}. "
                "Install opentimestamps-client or run with --mode dry-run for tests."
            )

        ots_command = [args.ots_bin, "stamp", str(snapshot_path)]
        result = run_cmd(ots_command)
        ots_stdout = result.stdout
        ots_stderr = result.stderr
        ots_exit_code = result.returncode

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise SystemExit("ots stamp failed")

        ots_file_exists = ots_path.exists()
        if not ots_file_exists:
            raise SystemExit(f"ots stamp succeeded but proof file was not created: {ots_path}")

        ots_file_sha256 = sha256_bytes(ots_path.read_bytes())

    anchor = {
        "schema": OTS_ANCHOR_SCHEMA,
        "chain_id": args.chain_id,
        "chain_version": 1,
        "anchored_file": str(snapshot_path),
        "anchored_file_sha256": commitment_sha256,
        "anchored_file_semantics": "stable record-chain head commitment; generated_at excluded",
        "source_head_file": str(head_path),
        "source_head_generated_at": head.get("generated_at"),
        "head_entry_hash": head_entry_hash,
        "height": height,
        "entry_count": entry_count,
        "ots_file": str(ots_path) if args.mode == "stamp" else None,
        "ots_file_sha256": ots_file_sha256,
        "ots_status": "pending" if args.mode == "stamp" else "dry_run",
        "ots_command": ots_command,
        "ots_exit_code": ots_exit_code,
        "ots_stdout": ots_stdout,
        "ots_stderr": ots_stderr,
        "ots_file_exists": ots_file_exists,
        "created_at": utc_now(),
        "verified_at": None,
        "bitcoin_verified": False,
        "bitcoin_pending": args.mode == "stamp",
        "bitcoin_attestation": None,
        "semantics": "OTS anchors a stable head commitment snapshot; it does not modify chain entries.",
    }

    write_json_atomic(anchor_path, anchor)

    latest = {
        "schema": OTS_LATEST_SCHEMA,
        "chain_id": args.chain_id,
        "latest_anchor_file": str(anchor_path),
        "latest_ots_file": anchor.get("ots_file"),
        "latest_anchored_file": str(snapshot_path),
        "anchored_file_sha256": commitment_sha256,
        "head_entry_hash": head_entry_hash,
        "height": height,
        "entry_count": entry_count,
        "ots_status": anchor["ots_status"],
        "bitcoin_verified": False,
        "bitcoin_pending": args.mode == "stamp",
        "created_at": anchor["created_at"],
        "updated_at": utc_now(),
        "semantics": "Latest OTS anchor for a stable Record-Chain head commitment snapshot.",
    }
    write_json_atomic(api_out, latest)

    print("[OTS RECORD CHAIN HEAD ANCHOR]")
    print(json.dumps(anchor, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
