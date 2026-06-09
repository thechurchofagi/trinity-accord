#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

from record_chain_hashing import (
    NATIVE_CHAIN_HEAD_COMMITMENT_SCHEMA,
    NATIVE_OTS_ANCHOR_SCHEMA,
    NATIVE_OTS_LATEST_SCHEMA,
    build_native_record_chain_head_commitment,
    canonical_json_bytes,
    sha256_bytes,
    write_bytes_atomic,
    write_json_atomic,
)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an OpenTimestamps anchor for the native Record-Chain head commitment."
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="record-chain/ots/native-anchors")
    parser.add_argument("--api-out", default="api/record-chain-native-ots-latest.json")
    parser.add_argument("--ots-bin", default="ots")
    parser.add_argument("--mode", choices=["dry-run", "stamp"], default="dry-run")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    api_out = Path(args.api_out)

    commitment = build_native_record_chain_head_commitment(root)
    if commitment.get("schema") != NATIVE_CHAIN_HEAD_COMMITMENT_SCHEMA:
        raise SystemExit(f"native commitment schema mismatch: {commitment.get('schema')}")

    commitment_text = json.dumps(commitment, sort_keys=True)
    if "main.chain.jsonl" in commitment_text:
        raise SystemExit("native commitment must not reference legacy main.chain.jsonl")

    tip = json.loads((root / "record-chain" / "chain-tip.json").read_text(encoding="utf-8"))
    expected_id = tip.get("latest_record_id")
    expected_count = tip.get("native_record_count")
    if commitment.get("latest_record_id") != expected_id:
        raise SystemExit(
            f"M9.3 native archive must include {expected_id}, got {commitment.get('latest_record_id')}"
        )
    if commitment.get("native_record_count") != expected_count:
        raise SystemExit(
            f"M9.3 native archive must include native_record_count={expected_count}, got {commitment.get('native_record_count')}"
        )

    commitment_bytes = canonical_json_bytes(commitment)
    commitment_sha256 = sha256_bytes(commitment_bytes)

    latest_record_index = commitment["latest_record_index"]
    native_record_count = commitment["native_record_count"]
    latest_record_id = commitment["latest_record_id"]
    latest_record_sha256 = commitment["latest_record_sha256"]

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = (
        f"native-record-{latest_record_index}-"
        f"{latest_record_id}-{latest_record_sha256[:16]}-{commitment_sha256[:16]}"
    )
    snapshot_path = out_dir / f"{prefix}.native-record-chain-head-commitment.json"
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
        "schema": NATIVE_OTS_ANCHOR_SCHEMA,
        "chain_id": commitment["chain_id"],
        "chain_version": 1,
        "anchored_file": str(snapshot_path),
        "anchored_file_sha256": commitment_sha256,
        "anchored_file_semantics": "stable native record-chain head commitment; generated_at excluded",
        "source_semantics": commitment["source_semantics"],
        "native_record_count": native_record_count,
        "latest_record_index": latest_record_index,
        "latest_record_id": latest_record_id,
        "latest_record_sha256": latest_record_sha256,
        "latest_batch_id": commitment["latest_batch_id"],
        "latest_batch_manifest_sha256": commitment["latest_batch_manifest_sha256"],
        "record_coverage": {
            "source": commitment["record_coverage"]["source"],
            "first_record_id": commitment["record_coverage"]["first_record_id"],
            "last_record_id": commitment["record_coverage"]["last_record_id"],
            "record_count": commitment["record_coverage"]["record_count"],
            "record_ids_sha256": commitment["record_coverage"]["record_ids_sha256"],
            "record_sha256s_sha256": commitment["record_coverage"]["record_sha256s_sha256"],
        },
        "source_files": commitment["source_files"],
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
        "semantics": "Native OTS anchor for current record-chain head; does not modify chain entries.",
        "legacy_main_chain_jsonl_is_not_source": True,
    }
    write_json_atomic(anchor_path, anchor)

    latest = {
        "schema": NATIVE_OTS_LATEST_SCHEMA,
        "chain_id": commitment["chain_id"],
        "latest_anchor_file": str(anchor_path),
        "latest_ots_file": anchor.get("ots_file"),
        "latest_anchored_file": str(snapshot_path),
        "anchored_file_sha256": commitment_sha256,
        "native_record_count": native_record_count,
        "latest_record_index": latest_record_index,
        "latest_record_id": latest_record_id,
        "latest_record_sha256": latest_record_sha256,
        "latest_batch_id": commitment["latest_batch_id"],
        "latest_batch_manifest_sha256": commitment["latest_batch_manifest_sha256"],
        "record_coverage": anchor["record_coverage"],
        "ots_status": anchor["ots_status"],
        "bitcoin_verified": False,
        "bitcoin_pending": args.mode == "stamp",
        "created_at": anchor["created_at"],
        "updated_at": utc_now(),
        "source_semantics": commitment["source_semantics"],
        "legacy_main_chain_jsonl_is_not_source": True,
        "semantics": "Latest native OTS anchor for the native Record-Chain head commitment snapshot.",
    }
    write_json_atomic(api_out, latest)

    print("[NATIVE RECORD CHAIN HEAD OTS ANCHOR]")
    print(json.dumps(anchor, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
