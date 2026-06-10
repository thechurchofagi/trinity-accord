#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "public-home-status.json"


def main() -> int:
    subprocess.run(["python3", "scripts/generate_public_home_status.py", "--check"], cwd=ROOT, check=True)

    data = json.loads(STATUS.read_text(encoding="utf-8"))
    assert data["schema"] == "trinityaccord.public-home-status.v3"
    assert data["primary_counters"]["official_live_reception"] == 2
    assert data["primary_counters"]["classification_rule"]["native_chain_length_is_not_primary_counter"] is True
    assert data["technical_health"]["not_primary_counter"] is True
    assert data["reception"]["not_homepage_primary_counter"] is True
    assert "archive_backlog" in data["technical_health"]
    assert "arweave_wallet" in data["technical_health"]
    assert data["technical_health"]["arweave_wallet"]["currency"] == "AR"
    assert "needs_recharge" in data["technical_health"]["arweave_wallet"]
    print("PASS: public-home-status v3 primary counters + AR wallet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
