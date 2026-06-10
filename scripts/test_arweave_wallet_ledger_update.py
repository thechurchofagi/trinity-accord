#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "record-chain/arweave-wallet-ledger.json"
STATUS = ROOT / "api/arweave-wallet-status.json"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
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
