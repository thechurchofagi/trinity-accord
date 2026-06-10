#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PAID_RESULTS = {
    "uploaded",
    "readback_failed",
    "posted_pending_readback",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pick(data: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = data.get(name)
        if value not in (None, ""):
            return value
    return None


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Arweave upload result into AR wallet ledger")
    parser.add_argument("--upload-result-json", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--source-path")
    parser.add_argument("--note")
    parser.add_argument("--skip-balance", action="store_true")
    args = parser.parse_args()

    upload_path = Path(args.upload_result_json)
    if not upload_path.is_absolute():
        upload_path = ROOT / upload_path
    if not upload_path.exists():
        raise SystemExit(f"upload result missing: {upload_path}")

    data = read_json(upload_path)

    result = data.get("result")
    tx_id = pick(data, "tx_id", "txid", "arweave_tx_id")
    if not tx_id:
        print("No tx id in upload result; wallet ledger not updated.")
        return 0

    paid_at = pick(data, "uploaded_at", "generated_at")
    wallet_address = pick(data, "wallet_address")
    wallet_hash = pick(data, "wallet_address_sha256")
    if wallet_address and not wallet_hash:
        wallet_hash = sha256_text(wallet_address)

    # Preferred cost order:
    # 1. actual balance delta
    # 2. tx.reward / direct upload cost
    # 3. cost gate estimate
    winston = pick(
        data,
        "actual_delta_winston",
        "upload_cost_winston",
        "estimated_upload_cost_winston",
        "estimated_cost_winston",
    )
    amount_ar = pick(
        data,
        "actual_delta_ar",
        "upload_cost_ar",
        "estimated_upload_cost_ar",
        "estimated_cost_ar",
    )

    # If tx_id exists and result indicates the tx was posted/uploaded, count it as paid.
    # This includes readback_failed: the archive may need repair, but the wallet may already have paid.
    status = "paid" if result in PAID_RESULTS or winston or amount_ar else "unknown"

    append_cmd = [
        sys.executable,
        "scripts/update_arweave_wallet_ledger.py",
        "append-upload",
        "--tx-id",
        str(tx_id),
        "--kind",
        args.kind,
        "--status",
        status,
    ]
    if args.source_path:
        append_cmd += ["--source-path", args.source_path]
    if winston:
        append_cmd += ["--winston", str(winston)]
    elif amount_ar:
        append_cmd += ["--amount-ar", str(amount_ar)]
    if paid_at:
        append_cmd += ["--paid-at", str(paid_at)]
    note = args.note or f"recorded from {upload_path}"
    append_cmd += ["--note", note]
    run(append_cmd)

    if not args.skip_balance:
        balance_ar = pick(data, "balance_after_ar", "wallet_balance_after_ar")
        if balance_ar:
            balance_cmd = [
                sys.executable,
                "scripts/update_arweave_wallet_ledger.py",
                "set-balance",
                "--balance-ar",
                str(balance_ar),
            ]
            if wallet_hash:
                balance_cmd += ["--wallet-address-sha256", str(wallet_hash)]
            if paid_at:
                balance_cmd += ["--balance-at", str(paid_at)]
            run(balance_cmd)
        elif wallet_hash:
            print("Wallet hash is available, but balance_after_ar is unavailable; balance remains unchanged.")

    print(f"Recorded Arweave upload result into wallet ledger: tx_id={tx_id} status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
