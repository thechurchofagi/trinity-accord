#!/usr/bin/env python3
"""Repair at most one current Record-Chain archive without bypassing daily limits."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "record-chain" / "arweave-backlog.json"
ACTIONABLE = {"pending_upload", "upload_failed", "readback_failed", "waiting_for_key"}


def main() -> int:
    try:
        doc = json.loads(BACKLOG.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"cannot read Record-Chain Arweave backlog: {exc}") from exc
    candidates = [
        item
        for item in doc.get("items", [])
        if isinstance(item, dict) and item.get("archive_status") in ACTIONABLE
    ]
    if not candidates:
        print("Record-Chain Arweave repair backlog is empty; no paid action.")
        return 0
    result = subprocess.run(
        ["python3", "scripts/run_record_chain_arweave_incremental.py", "--mode", "live"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode == 75:
        print("Record-Chain repair deferred: daily paid-upload limit already reached.")
        return 0
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
