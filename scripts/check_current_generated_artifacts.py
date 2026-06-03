#!/usr/bin/env python3
"""Unified drift check for generated artifacts: sitemap and public-home-status.

Usage:
    python3 scripts/check_current_generated_artifacts.py          # check both
    python3 scripts/check_current_generated_artifacts.py --check  # same (CI compat)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    ("sitemap", [sys.executable, "scripts/generate_sitemap.py", "--check"]),
    ("public-home-status", [sys.executable, "scripts/generate_public_home_status.py", "--check"]),
]


def main() -> int:
    failures = []
    for name, cmd in CHECKS:
        print(f"Checking {name}...", flush=True)
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FAIL: {name} drift detected", file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            failures.append(name)
        else:
            print(f"PASS: {name} up to date")

    if failures:
        print(f"\nFAIL: {len(failures)} artifact(s) have drift: {', '.join(failures)}", file=sys.stderr)
        return 1

    print("\nPASS: All generated artifacts up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
