#!/usr/bin/env python3
"""Run all public homepage artifact generators in the correct order.

Called by the Homepage Status Sync workflow before verification checks.
Each generator updates its output file(s) in-place; verification scripts
then confirm no drift remains.

Generators (order matters — public-home-status depends on the others):
  1. generate_waiting_heartbeat_status.py  → api/waiting-heartbeat-status.json + record-chain/heartbeat/index.json
  2. generate_arweave_wallet_status.py     → api/arweave-wallet-status.json
  3. generate_guardian_current_registry.py → api/guardian-state.json + api/guardian-current-registry.json
  4. generate_record_chain_status.py       → api/record-chain-status.json
  5. normalize_record_chain_integrity_status.py → deterministic verified-head integrity fields
  6. generate_public_home_status.py        → api/public-home-status.json + index.md
  7. patch_public_home_status_primary.py   → api/public-home-status.json + index.md (primary counters)
  8. generate_sitemap.py                   → sitemap.xml
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATORS = [
    ("waiting-heartbeat-status", [sys.executable, "scripts/generate_waiting_heartbeat_status.py"]),
    ("arweave-wallet-status", [sys.executable, "scripts/generate_arweave_wallet_status.py"]),
    ("guardian-current-registry", [sys.executable, "scripts/generate_guardian_current_registry.py"]),
    ("record-chain-status",   [sys.executable, "scripts/generate_record_chain_status.py"]),
    ("record-chain-integrity-status", [sys.executable, "scripts/normalize_record_chain_integrity_status.py"]),
    ("public-home-status",    [sys.executable, "scripts/generate_public_home_status.py"]),
    ("public-home-status-primary-patch", [sys.executable, "scripts/patch_public_home_status_primary.py"]),
    ("sitemap",               [sys.executable, "scripts/generate_sitemap.py"]),
]


def main() -> int:
    failures: list[str] = []
    for name, cmd in GENERATORS:
        print(f"Generating {name}...", flush=True)
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FAIL: {name} generation failed (exit {result.returncode})", file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            failures.append(name)
        else:
            if result.stdout:
                print(result.stdout, end="", flush=True)
            print(f"OK: {name}")

    if failures:
        print(f"\nFAIL: {len(failures)} generator(s) failed: {', '.join(failures)}", file=sys.stderr)
        return 1

    print("\nAll public homepage artifacts updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
