#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TESTNET_CHAIN_ID = "trinity-record-chain-testnet"
TESTNET_LEDGER = ROOT / "record-chain/testnet/hash-chain/testnet.chain.jsonl"
TESTNET_HEAD = ROOT / "api/record-chain-testnet/record-chain-head.json"
CONFIRM = "I_UNDERSTAND_THIS_APPENDS_TO_TESTNET_ONLY_NOT_MAINNET"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Finalize an external agent submission into the testnet record chain."
    )
    parser.add_argument("--submission-json", required=True)
    parser.add_argument("--receipt-json", required=True)
    parser.add_argument("--enable-testnet-append", action="store_true")
    parser.add_argument("--confirm-testnet-append", default="")
    args = parser.parse_args()

    if not args.enable_testnet_append:
        raise SystemExit("must pass --enable-testnet-append")
    if args.confirm_testnet_append != CONFIRM:
        raise SystemExit(f"--confirm-testnet-append must be exactly {CONFIRM!r}")

    submission = read_json(Path(args.submission_json))
    receipt = read_json(Path(args.receipt_json))

    record_type = submission.get("record_type")
    if not record_type:
        raise SystemExit("submission missing record_type")

    # Extract record_id from submission or receipt, or auto-generate for testnet
    record_id = submission.get("record_id") or receipt.get("record_id")
    if not record_id:
        # Auto-generate testnet record_id from ledger position
        ledger_lines = 0
        if TESTNET_LEDGER.exists():
            ledger_lines = sum(1 for line in TESTNET_LEDGER.read_text(encoding="utf-8").splitlines() if line.strip())
        # Genesis is T-000000000 (entry 0), first record is T-000000001 (entry 1)
        next_num = ledger_lines + 1
        record_id = f"T-{next_num:09d}"

    # Verify testnet markers
    if submission.get("chain_id") and submission.get("chain_id") != TESTNET_CHAIN_ID:
        raise SystemExit(f"submission chain_id mismatch: {submission.get('chain_id')}")

    # Extract hashes — do NOT embed raw readback
    submission_sha = sha256_bytes(
        json.dumps(submission, sort_keys=True, ensure_ascii=False).encode()
    )
    receipt_sha = sha256_bytes(
        json.dumps(receipt, sort_keys=True, ensure_ascii=False).encode()
    )
    receipt_id = receipt.get("receipt_id", "")
    oath = submission.get("client_oath_readback", {})
    oath_policy_sha = oath.get("oath_policy_sha256") or submission.get("oath_policy_sha256", "")
    canonical_oath_sha = oath.get("canonical_oath_text_sha256") or submission.get("canonical_oath_text_sha256", "")
    participant_readback_sha = oath.get("readback_text_sha256") or submission.get("participant_readback_sha256", "")

    # Build finalized payload — NO raw oath readback
    finalized_payload = {
        "record_type": record_type,
        "record_id": record_id,
        "chain_id": TESTNET_CHAIN_ID,
        "test_only": True,
        "not_mainnet": True,
        "submission_sha256": submission_sha,
        "receipt_sha256": receipt_sha,
        "receipt_id": receipt_id,
        "oath_policy_sha256": oath_policy_sha,
        "canonical_oath_text_sha256": canonical_oath_sha,
        "participant_readback_sha256": participant_readback_sha,
        "finalized_at": utc_now(),
    }

    # Add source_summary if present (for verification records)
    source_summary = submission.get("source_summary")
    if source_summary:
        finalized_payload["source_summary"] = source_summary

    # Write payload file
    payload_dir = ROOT / "record-chain/testnet/payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)
    payload_file = payload_dir / f"{record_id}.json"
    write_json(payload_file, finalized_payload)

    # Append to testnet ledger using existing script
    import subprocess

    cmd = [
        sys.executable,
        "scripts/append_record_chain_link.py",
        "--ledger", str(TESTNET_LEDGER),
        "--head-out", str(TESTNET_HEAD),
        "--record-file", str(payload_file),
        "--record-type", record_type,
        "--record-id", record_id,
        "--chain-id", TESTNET_CHAIN_ID,
    ]
    # If ledger is empty, allow genesis
    if TESTNET_LEDGER.stat().st_size == 0:
        cmd.append("--allow-genesis")

    print(f"[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(f"append failed ({result.returncode})")

    print(f"[OK] Finalized {record_type} record {record_id} into testnet ledger")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
