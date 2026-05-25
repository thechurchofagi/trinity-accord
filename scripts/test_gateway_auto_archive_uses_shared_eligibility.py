#!/usr/bin/env python3
"""gateway-auto-archive.yml must use shared archive eligibility logic."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = (ROOT / ".github/workflows/gateway-auto-archive.yml").read_text(encoding="utf-8")

required = [
    "from archive_echo_issue import validate_gateway_archive_eligibility",
    "validate_gateway_archive_eligibility(issue)",
]

for frag in required:
    if frag not in workflow:
        print(f"FAIL: gateway-auto-archive.yml missing shared eligibility fragment: {frag}")
        sys.exit(1)

for forbidden in [
    "def field(",
    "def is_true(",
    "required_true = [",
]:
    if forbidden in workflow:
        print(f"FAIL: gateway-auto-archive.yml still contains loose inline parser fragment: {forbidden}")
        sys.exit(1)

print("PASS: gateway-auto-archive.yml uses shared archive eligibility")
