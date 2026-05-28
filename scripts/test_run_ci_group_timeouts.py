#!/usr/bin/env python3
"""run_ci_group.py must enforce timeouts for every command."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "run_ci_group.py"

text = path.read_text(encoding="utf-8")
errors: list[str] = []

required = [
    "DEFAULT_TEST_TIMEOUT_SECONDS",
    "timeout_for_command",
    "subprocess.TimeoutExpired",
    "timeout=",
    "command timed out",
]

for item in required:
    if item not in text:
        errors.append(f"run_ci_group.py missing timeout guard: {item}")

if "subprocess.check_call(" in text:
    errors.append("run_ci_group.py must not use subprocess.check_call without timeout wrapper")

if "subprocess.check_output(" in text:
    errors.append("run_ci_group.py must not use subprocess.check_output without timeout wrapper")

if errors:
    print("FAIL: run_ci_group timeout guard errors:")
    for error in errors:
        print("  -", error)
    sys.exit(1)

print("PASS: run_ci_group enforces bounded command execution")
