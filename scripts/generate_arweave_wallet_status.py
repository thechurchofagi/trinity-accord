#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "record-chain" / "arweave-wallet-ledger.json"
STATUS = ROOT / "api" / "arweave-wallet-status.json"
WINSTON_PER_AR = Decimal("1000000000000")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def dump(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def dec(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def winston_to_ar(value: Decimal) -> Decimal:
    return value / WINSTON_PER_AR


def money(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def default_ledger() -> dict[str, Any]:
    return {
        "schema": "trinityaccord.arweave-wallet-ledger.v1",
        "updated_at": "2026-06-10T00:00:00Z",
        "wallet": {
            "wallet_address": None,
            "wallet_address_sha256": None,
            "public_address_allowed": False,
            "currency": "AR",
            "last_known_balance_ar": None,
            "last_known_balance_at": None,
            "low_balance_threshold_ar": "0.25",
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


def semantic_without_generated_at(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if k != "generated_at"}


def entry_cost_ar(entry: dict[str, Any]) -> Decimal:
    amount = dec(entry.get("amount_ar"))
    if amount is not None:
        return amount
    winston = dec(entry.get("winston"))
    if winston is not None:
        return winston_to_ar(winston)
    return Decimal("0")


def compute_status(use_env_balance: bool = False) -> dict[str, Any]:
    ledger = read_json(LEDGER, default_ledger())
    wallet = ledger.get("wallet") if isinstance(ledger.get("wallet"), dict) else {}

    public_address_allowed = wallet.get("public_address_allowed") is True
    wallet_address = wallet.get("wallet_address") if public_address_allowed else None
    wallet_address_sha256 = wallet.get("wallet_address_sha256")

    if use_env_balance:
        env_wallet_address = os.environ.get("ARWEAVE_WALLET_ADDRESS")
        if env_wallet_address and public_address_allowed:
            wallet_address = env_wallet_address
        if env_wallet_address and not wallet_address_sha256:
            wallet_address_sha256 = sha256_text(env_wallet_address)

    entries = [e for e in ledger.get("entries", []) if isinstance(e, dict)]
    paid_entries = [e for e in entries if e.get("status", "paid") == "paid"]

    total_spent = sum((entry_cost_ar(e) for e in paid_entries), Decimal("0"))
    last_entry = paid_entries[-1] if paid_entries else None
    last_cost = entry_cost_ar(last_entry) if last_entry else None

    threshold = dec(wallet.get("low_balance_threshold_ar")) or Decimal("0.25")
    balance = dec(wallet.get("last_known_balance_ar"))

    if use_env_balance:
        env_balance_ar = dec(os.environ.get("ARWEAVE_WALLET_BALANCE_AR"))
        env_balance_winston = dec(os.environ.get("ARWEAVE_WALLET_BALANCE_WINSTON"))
        if env_balance_ar is not None:
            balance = env_balance_ar
        elif env_balance_winston is not None:
            balance = winston_to_ar(env_balance_winston)

    balance_known = balance is not None
    low_balance = bool(balance_known and balance < threshold)

    return {
        "schema": "trinityaccord.arweave-wallet-status.v1",
        "generated_at": utc_now(),
        "currency": "AR",
        "wallet": {
            "wallet_address": wallet_address,
            "wallet_address_sha256": wallet_address_sha256,
            "public_address_allowed": public_address_allowed,
        },
        "spending": {
            "total_paid_uploads": len(paid_entries),
            "total_spent_ar": money(total_spent),
            "last_upload_cost_ar": money(last_cost),
            "last_upload_tx_id": last_entry.get("tx_id") if last_entry else None,
            "last_upload_kind": last_entry.get("kind") if last_entry else None,
            "last_upload_at": last_entry.get("paid_at") if last_entry else None,
        },
        "balance": {
            "balance_known": balance_known,
            "balance_ar": money(balance),
            "low_balance_threshold_ar": money(threshold),
            "low_balance": low_balance,
            "needs_recharge": low_balance,
            "status": "unknown" if not balance_known else ("needs_recharge" if low_balance else "ok"),
        },
        "boundary": {
            "wallet_status_is_operational_only": True,
            "wallet_status_is_not_authority": True,
            "wallet_status_is_not_attestation": True,
            "wallet_status_is_not_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }


def stable_expected_text(use_env_balance: bool = False) -> str:
    expected = compute_status(use_env_balance=use_env_balance)
    existing = read_json(STATUS, {})
    if isinstance(existing, dict) and semantic_without_generated_at(existing) == semantic_without_generated_at(expected):
        expected["generated_at"] = existing.get("generated_at") or expected["generated_at"]
    return dump(expected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--use-env-balance", action="store_true")
    args = parser.parse_args()

    expected_text = stable_expected_text(use_env_balance=args.use_env_balance)

    if args.check:
        if not STATUS.exists():
            print("FAIL: api/arweave-wallet-status.json missing")
            return 1
        actual = STATUS.read_text(encoding="utf-8")
        try:
            actual_data = json.loads(actual)
            expected_data = json.loads(expected_text)
            if semantic_without_generated_at(actual_data) != semantic_without_generated_at(expected_data):
                print("FAIL: api/arweave-wallet-status.json is out of date")
                return 1
        except Exception:
            if actual != expected_text:
                print("FAIL: api/arweave-wallet-status.json is out of date")
                return 1
        print("PASS: api/arweave-wallet-status.json is up to date")
        return 0

    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(expected_text, encoding="utf-8")

    if not LEDGER.exists():
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(dump(default_ledger()), encoding="utf-8")

    print("Updated api/arweave-wallet-status.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
