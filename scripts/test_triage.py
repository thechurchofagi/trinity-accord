#!/usr/bin/env python3
"""Compatibility entrypoint for the Repository Full Integrity echo triage step."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_TESTS = [
    ROOT / "scripts" / "test_echo_archive_metrics_contract.py",
    ROOT / "scripts" / "test_echo_index_contract.py",
    ROOT / "scripts" / "test_external_witness_index_contract.py",
]


def main() -> int:
    tests = [path for path in CANDIDATE_TESTS if path.exists()]
    if not tests:
        print("PASS: no active echo triage subtests are present")
        return 0
    for test in tests:
        print(f"[triage] running {test.relative_to(ROOT)}", flush=True)
        result = subprocess.run([sys.executable, str(test)], cwd=ROOT)
        if result.returncode:
            return result.returncode
    print("PASS: echo triage tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
