#!/usr/bin/env python3
"""Run all public homepage artifact generators in the correct order.

Called by the Homepage Status Sync workflow before verification checks.
Each generator updates its output file(s) in-place; verification scripts
then confirm no drift remains.

Generators (order matters — public-home-status depends on the others):
  1. generate_arweave_wallet_status.py   → api/arweave-wallet-status.json
  2. generate_record_chain_status.py     → api/record-chain-status.json
  3. generate_public_home_status.py      → api/public-home-status.json + index.md
  4. generate_sitemap.py                 → sitemap.xml
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATORS = [
    ("arweave-wallet-status", [sys.executable, "scripts/generate_arweave_wallet_status.py"]),
    ("record-chain-status",   [sys.executable, "scripts/generate_record_chain_status.py"]),
    ("public-home-status",    [sys.executable, "scripts/generate_public_home_status.py"]),
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
