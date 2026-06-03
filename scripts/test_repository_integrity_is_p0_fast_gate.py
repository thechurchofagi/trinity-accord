#!/usr/bin/env python3
"""repository-integrity.yml should remain a compact P0 fast gate."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / ".github" / "workflows" / "repository-integrity.yml"
text = path.read_text(encoding="utf-8")

required = [
    "python3 scripts/run_ci_group.py p0-current",
    "workflow_dispatch:",
    "permissions:",
    "contents: read",
]

ok = True
for frag in required:
    if frag not in text:
        print(f"FAIL: repository-integrity.yml missing required fast-gate fragment: {frag}")
        ok = False

explicit_py_tests = [
    line for line in text.splitlines()
    if "run: python3 scripts/test_" in line
]

MAX_EXPLICIT_TESTS = 8
if len(explicit_py_tests) > MAX_EXPLICIT_TESTS:
    print(
        f"FAIL: repository-integrity.yml has too many inline test steps "
        f"({len(explicit_py_tests)} > {MAX_EXPLICIT_TESTS}). Move them to run_ci_group.py or deep-integrity.yml."
    )
    ok = False

for forbidden_group in [
    "python3 scripts/run_ci_group.py guardian",
    "python3 scripts/run_ci_group.py claim-gate",
    "python3 scripts/run_ci_group.py supply-chain",
    "python3 scripts/run_ci_group.py trust-root",
    "python3 scripts/run_ci_group.py chronicle",
]:
    if forbidden_group in text:
        print(f"FAIL: deep group should not run in repository-integrity fast gate: {forbidden_group}")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: repository-integrity.yml is a compact P0 fast gate")
