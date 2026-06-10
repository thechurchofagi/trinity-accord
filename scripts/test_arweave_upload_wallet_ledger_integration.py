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


def status_json() -> dict:
    return json.loads(STATUS.read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        backup_ledger = tmpdir / "ledger.json"
        backup_status = tmpdir / "status.json"
        shutil.copy2(LEDGER, backup_ledger)
        shutil.copy2(STATUS, backup_status)

        try:
            uploaded_result = tmpdir / "uploaded-result.json"
            uploaded_result.write_text(json.dumps({
                "schema": "trinityaccord.arweave-upload-result.v1",
                "result": "uploaded",
                "tx_id": "TEST_ARWEAVE_WALLET_LEDGER_TX_UPLOADED",
                "uploaded_at": "2026-06-10T09:00:00Z",
                "wallet_address_sha256": "1" * 64,
                "upload_cost_winston": "123000000000",
                "upload_cost_ar": "0.123",
                "wallet_balance_after_ar": "1.2345",
                "hash_match": True
            }, indent=2) + "\n", encoding="utf-8")

            run([
                "python3", "scripts/record_arweave_upload_result.py",
                "--upload-result-json", str(uploaded_result),
                "--kind", "contract_test_archive",
                "--source-path", "contract/test.json",
            ])
            run(["python3", "scripts/generate_arweave_wallet_status.py"])

            status = status_json()
            assert status["balance"]["balance_known"] is True
            assert status["balance"]["balance_ar"] == "1.2345"
            assert status["wallet"]["wallet_address_sha256"] == "1" * 64
            assert status["spending"]["last_upload_tx_id"] == "TEST_ARWEAVE_WALLET_LEDGER_TX_UPLOADED"

            readback_failed_result = tmpdir / "readback-failed-result.json"
            readback_failed_result.write_text(json.dumps({
                "schema": "trinityaccord.arweave-upload-result.v1",
                "result": "readback_failed",
                "tx_id": "TEST_ARWEAVE_WALLET_LEDGER_TX_READBACK_FAILED",
                "uploaded_at": "2026-06-10T09:05:00Z",
                "wallet_address_sha256": "1" * 64,
                "upload_cost_winston": "100000000000",
                "upload_cost_ar": "0.1",
                "wallet_balance_after_ar": "1.1345",
                "hash_match": False
            }, indent=2) + "\n", encoding="utf-8")

            run([
                "python3", "scripts/record_arweave_upload_result.py",
                "--upload-result-json", str(readback_failed_result),
                "--kind", "contract_test_archive",
                "--source-path", "contract/test-readback-failed.json",
            ])
            run(["python3", "scripts/generate_arweave_wallet_status.py"])

            status = status_json()
            assert status["balance"]["balance_ar"] == "1.1345"
            assert status["spending"]["last_upload_tx_id"] == "TEST_ARWEAVE_WALLET_LEDGER_TX_READBACK_FAILED"
            assert status["spending"]["total_paid_uploads"] >= 2
            print("PASS: arweave upload result -> wallet ledger integration")
        finally:
            shutil.copy2(backup_ledger, LEDGER)
            shutil.copy2(backup_status, STATUS)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
