#!/usr/bin/env python3
"""Update all public generated artifacts.

Runs generate_sitemap.py unconditionally, and if generate_public_home_status.py
exists, runs that too.  Exit code is non-zero if any sub-script fails.

Usage:
    python3 scripts/update_public_generated_artifacts.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = [
    "scripts/generate_sitemap.py",
]

# Optional: only run if the file exists
OPTIONAL_SCRIPTS = [
    "scripts/generate_public_home_status.py",
]


def run_script(script: str) -> int:
    """Run a Python script and return its exit code."""
    print(f"--- Running {script} ---")
    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print(f"FAILED: {script} (exit {result.returncode})")
    else:
        print(f"OK: {script}")
    return result.returncode


def main() -> int:
    failures = 0

    for script in SCRIPTS:
        if not (ROOT / script).exists():
            print(f"SKIP (not found): {script}")
            continue
        failures += run_script(script)

    for script in OPTIONAL_SCRIPTS:
        if not (ROOT / script).exists():
            print(f"SKIP (optional, not found): {script}")
            continue
        failures += run_script(script)

    if failures:
        print(f"\n{failures} script(s) failed.")
        return 1

    print("\nAll public generated artifacts updated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
