#!/usr/bin/env python3
"""Intake boolean parser must be strict."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_agent_declared_verification_index_from_issues import parse_bool, BoolParseError

cases_true = ["true", "True", "1", "yes", " YES "]
cases_false = ["false", "False", "0", "no", " NO "]

for value in cases_true:
    if parse_bool(value, field="fixture") is not True:
        print(f"FAIL: expected true for {value!r}")
        sys.exit(1)

for value in cases_false:
    if parse_bool(value, field="fixture") is not False:
        print(f"FAIL: expected false for {value!r}")
        sys.exit(1)

for value in ["maybe", "tru", "", "none"]:
    try:
        parse_bool(value, field="fixture", issue_number=1)
    except BoolParseError:
        continue
    print(f"FAIL: malformed boolean accepted: {value!r}")
    sys.exit(1)

print("PASS: strict intake boolean parser works")
