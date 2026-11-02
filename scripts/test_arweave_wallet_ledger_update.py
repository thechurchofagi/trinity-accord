#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
import base64
import hashlib
import io
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
import update_arweave_wallet_ledger as updater

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "record-chain/arweave-wallet-ledger.json"
STATUS = ROOT / "api/arweave-wallet-status.json"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def default_ledger() -> dict:
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


def check_live_refresh() -> None:
    # Synthetic public modulus only; tests require no credentials or network.
    modulus = b"test-only-public-modulus"
    jwk = json.dumps({"kty": "RSA", "n": base64.urlsafe_b64encode(modulus).decode().rstrip("=")})
    address = base64.urlsafe_b64encode(hashlib.sha256(modulus).digest()).decode().rstrip("=")
    with tempfile.TemporaryDirectory() as tmp:
        ledger_path = Path(tmp) / "ledger.json"
        ledger = default_ledger()
        ledger["wallet"]["wallet_address_sha256"] = updater.sha256_text(address)
        ledger_path.write_text(json.dumps(ledger))
        with patch.object(updater, "LEDGER", ledger_path), patch.dict(os.environ, {"ARKEY": jwk}), patch.object(updater.time, "sleep"):
            for balance, expected in [(b"14115073154798", "14.115073154798"), (b"0", "0"), (b"1", "0.000000000001")]:
                with patch.object(updater, "urlopen", return_value=io.BytesIO(balance)) as query:
                    updater.refresh_balance(argparse.Namespace())
                    assert query.call_args.args[0] == f"https://arweave.net/wallet/{address}/balance"
                saved = json.loads(ledger_path.read_text())
                assert saved["wallet"]["last_known_balance_ar"] == expected
                assert saved["wallet"]["last_known_balance_at"]
                assert saved["wallet"]["wallet_address"] is None
                assert saved["entries"] == []
            before = ledger_path.read_bytes()
            for response in [b"-1", b"NaN", b"<html>error</html>"]:
                with patch.object(updater, "urlopen", side_effect=lambda *a, **k: io.BytesIO(response)):
                    try:
                        updater.refresh_balance(argparse.Namespace())
                        raise AssertionError("invalid response accepted")
                    except SystemExit:
                        pass
                assert ledger_path.read_bytes() == before
            with patch.object(updater, "urlopen", side_effect=TimeoutError):
                try:
                    updater.refresh_balance(argparse.Namespace())
                    raise AssertionError("network failure accepted")
                except SystemExit:
                    pass
            assert ledger_path.read_bytes() == before
            for key in ["invalid", json.dumps({"kty":"RSA","n":"b3RoZXI"})]:
                with patch.dict(os.environ, {"ARKEY":key}), patch.object(updater, "urlopen") as query:
                    try:
                        updater.refresh_balance(argparse.Namespace())
                        raise AssertionError("invalid or mismatched wallet accepted")
                    except SystemExit:
                        pass
                    query.assert_not_called()
                assert ledger_path.read_bytes() == before


def main() -> int:
    check_live_refresh()
    if not LEDGER.exists():
        raise SystemExit("missing record-chain/arweave-wallet-ledger.json")
    if not STATUS.exists():
        raise SystemExit("missing api/arweave-wallet-status.json")

    with tempfile.TemporaryDirectory() as tmp:
        backup_ledger = Path(tmp) / "arweave-wallet-ledger.json"
        backup_status = Path(tmp) / "arweave-wallet-status.json"
        shutil.copy2(LEDGER, backup_ledger)
        shutil.copy2(STATUS, backup_status)

        try:
            # Start from a clean ledger so pre-existing entries
            # (which may have real winston values) don't affect
            # the total_spent_ar assertion.
            LEDGER.write_text(
                json.dumps(default_ledger(), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            run([
                "python3", "scripts/update_arweave_wallet_ledger.py",
                "set-balance",
                "--balance-ar", "1.5",
                "--wallet-address-sha256", "0" * 64,
                "--low-balance-threshold-ar", "0.25",
                "--balance-at", "2026-06-10T08:00:00Z",
            ])
            run([
                "python3", "scripts/update_arweave_wallet_ledger.py",
                "append-upload",
                "--tx-id", "TEST_TX_ID_FOR_WALLET_LEDGER_CONTRACT",
                "--kind", "contract_test",
                "--source-path", "contract/test",
                "--amount-ar", "0.1",
                "--paid-at", "2026-06-10T08:01:00Z",
            ])
            run(["python3", "scripts/generate_arweave_wallet_status.py"])

            status = json.loads(STATUS.read_text(encoding="utf-8"))
            assert status["schema"] == "trinityaccord.arweave-wallet-status.v1"
            assert status["balance"]["balance_known"] is True
            assert status["balance"]["balance_ar"] == "1.5"
            assert status["balance"]["checked_at"] == "2026-06-10T08:00:00Z"
            assert status["balance"]["needs_recharge"] is False
            assert status["spending"]["total_spent_ar"] == "0.1"
            assert status["spending"]["total_paid_uploads"] >= 1
            assert status["wallet"]["wallet_address_sha256"] == "0" * 64
            assert status["boundary"]["wallet_status_is_operational_only"] is True

            print("PASS: arweave wallet ledger update contract")
        finally:
            shutil.copy2(backup_ledger, LEDGER)
            shutil.copy2(backup_status, STATUS)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

