#!/usr/bin/env python3
"""Part C: Contract test — runs the native record hash semantics verifier."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_native_record_hash_semantics.py"),
         "--base-dir", str(ROOT)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("FAIL: native record hash semantics verification failed:")
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return 1
    print("PASS: native record hash semantics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
