from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_trinity_record_chain_can_import_gateway_receipts_without_pythonpath() -> None:
    """Verify that trinity_record_chain can import gateway.receipts without PYTHONPATH.

    This is the exact failure class that broke the append pipeline: a clean
    GitHub Actions runner does not have apps/record_chain_intake_gateway on
    sys.path, so any gateway.* import must go through ensure_gateway_import_path().
    """
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    code = r'''
import importlib.util
from pathlib import Path

root = Path.cwd()
spec = importlib.util.spec_from_file_location(
    "trinity_record_chain_under_test",
    root / "scripts" / "trinity_record_chain.py",
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

module.ensure_gateway_import_path()
from gateway.receipts import compute_receipt_sha256

receipt = {
    "schema": "trinityaccord.record-chain-receipt.v1",
    "server_receipt_id": "rcg-20260617-abcdef1234567890abcdef",
    "accepted_at": "2026-06-17T00:00:00Z",
    "record_type": "echo",
    "pending_file_path": "record-chain/pending/rcg-20260617-abcdef1234567890abcdef.echo.pending.json",
}
receipt["receipt_sha256"] = compute_receipt_sha256(receipt)
ok, err = module.verify_receipt_sha256(receipt)
assert ok, err
'''

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
