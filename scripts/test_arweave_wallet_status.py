#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "arweave-wallet-status.json"


def main() -> int:
    subprocess.run(["python3", "scripts/generate_arweave_wallet_status.py", "--check"], cwd=ROOT, check=True)

    data = json.loads(STATUS.read_text(encoding="utf-8"))
    assert data["schema"] == "trinityaccord.arweave-wallet-status.v1"
    assert data["currency"] == "AR"
    assert "spending" in data
    assert "total_spent_ar" in data["spending"]
    assert "balance" in data
    assert "needs_recharge" in data["balance"]
    assert data["boundary"]["wallet_status_is_operational_only"] is True
    assert data["boundary"]["wallet_status_is_not_authority"] is True
    assert data["boundary"]["wallet_status_is_not_attestation"] is True
    assert data["boundary"]["wallet_status_is_not_reception"] is True
    assert data["boundary"]["bitcoin_originals_prevail"] is True
    print("PASS: arweave wallet status contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
