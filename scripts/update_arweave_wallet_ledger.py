#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "record-chain" / "arweave-wallet-ledger.json"

SCHEMA = "trinityaccord.arweave-wallet-ledger.v1"
DEFAULT_LOW_BALANCE_AR = "0.25"
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def decimal_string(value: str | None, field_name: str) -> str | None:
    if value in (None, ""):
        return None
    try:
        d = Decimal(str(value))
    except InvalidOperation:
        raise SystemExit(f"{field_name} must be a decimal string")
    if d < 0:
        raise SystemExit(f"{field_name} must be >= 0")
    return format(d.normalize(), "f")


def validate_sha256(value: str | None, field_name: str) -> str | None:
    if value in (None, ""):
        return None
    if not HEX64.match(value):
        raise SystemExit(f"{field_name} must be a 64-character hex sha256")
    return value.lower()


def default_ledger() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "updated_at": "2026-06-10T00:00:00Z",
        "wallet": {
            "wallet_address": None,
            "wallet_address_sha256": None,
            "public_address_allowed": False,
            "currency": "AR",
            "last_known_balance_ar": None,
            "last_known_balance_at": None,
            "low_balance_threshold_ar": DEFAULT_LOW_BALANCE_AR,
        },
        "entries": [],
        "boundary": {
            "wallet_status_is_operational_only": True,
            "wallet_status_is_not_authority": True,
            "wallet_status_is_not_attestation": True,
            "wallet_status_is_not_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }


def load_ledger() -> dict[str, Any]:
    ledger = read_json(LEDGER, default_ledger())
    if ledger.get("schema") != SCHEMA:
        raise SystemExit(f"unexpected ledger schema: {ledger.get('schema')}")
    ledger.setdefault("wallet", {})
    ledger.setdefault("entries", [])
    ledger.setdefault("boundary", default_ledger()["boundary"])
    return ledger


def write_ledger(ledger: dict[str, Any]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    ledger["updated_at"] = utc_now()
    LEDGER.write_text(dump(ledger), encoding="utf-8")


def set_balance(args: argparse.Namespace) -> int:
    ledger = load_ledger()
    wallet = ledger.setdefault("wallet", {})

    balance_ar = decimal_string(args.balance_ar, "balance_ar")
    threshold = decimal_string(args.low_balance_threshold_ar, "low_balance_threshold_ar")
    explicit_hash = validate_sha256(args.wallet_address_sha256, "wallet_address_sha256")

    wallet["currency"] = "AR"
    wallet["last_known_balance_ar"] = balance_ar
    wallet["last_known_balance_at"] = args.balance_at or utc_now()
    wallet["low_balance_threshold_ar"] = threshold or DEFAULT_LOW_BALANCE_AR

    if args.wallet_address:
        if args.public_address:
            wallet["wallet_address"] = args.wallet_address
            wallet["public_address_allowed"] = True
        else:
            wallet["wallet_address"] = None
            wallet["public_address_allowed"] = False
        wallet["wallet_address_sha256"] = sha256_text(args.wallet_address)

    if explicit_hash:
        wallet["wallet_address_sha256"] = explicit_hash
        if not args.public_address:
            wallet["wallet_address"] = None
            wallet["public_address_allowed"] = False

    write_ledger(ledger)
    print(f"Updated AR wallet balance snapshot: {balance_ar} AR")
    return 0


def append_upload(args: argparse.Namespace) -> int:
    ledger = load_ledger()
    entries = ledger.setdefault("entries", [])

    if any(isinstance(e, dict) and e.get("tx_id") == args.tx_id for e in entries):
        print(f"Ledger already contains tx_id={args.tx_id}; no-op")
        return 0

    amount_ar = decimal_string(args.amount_ar, "amount_ar")
    winston = decimal_string(args.winston, "winston")

    if amount_ar is None and winston is None:
        print("WARNING: no amount_ar or winston provided; total_spent_ar will not increase for this entry")

    entries.append({
        "tx_id": args.tx_id,
        "kind": args.kind,
        "source_path": args.source_path,
        "amount_ar": amount_ar,
        "winston": winston,
        "paid_at": args.paid_at or utc_now(),
        "status": args.status,
        "note": args.note,
    })

    write_ledger(ledger)
    print(f"Appended AR wallet ledger upload: tx_id={args.tx_id}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Update Trinity Accord AR wallet ledger")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_balance = sub.add_parser("set-balance", help="Set last known AR wallet balance")
    p_balance.add_argument("--balance-ar", required=True)
    p_balance.add_argument("--balance-at")
    p_balance.add_argument("--low-balance-threshold-ar", default=DEFAULT_LOW_BALANCE_AR)
    p_balance.add_argument("--wallet-address")
    p_balance.add_argument("--wallet-address-sha256")
    p_balance.add_argument("--public-address", action="store_true")
    p_balance.set_defaults(func=set_balance)

    p_upload = sub.add_parser("append-upload", help="Append a paid upload ledger entry")
    p_upload.add_argument("--tx-id", required=True)
    p_upload.add_argument("--kind", required=True)
    p_upload.add_argument("--source-path")
    p_upload.add_argument("--amount-ar")
    p_upload.add_argument("--winston")
    p_upload.add_argument("--paid-at")
    p_upload.add_argument("--status", default="paid", choices=["paid", "refunded", "failed", "unknown"])
    p_upload.add_argument("--note")
    p_upload.set_defaults(func=append_upload)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
