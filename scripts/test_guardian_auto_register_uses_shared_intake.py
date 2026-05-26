#!/usr/bin/env python3
"""Guardian auto-register must use shared Gateway intake parser/policy."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "auto_register_guardian_from_gateway_issues.py"
text = path.read_text(encoding="utf-8")

required = [
    "from gateway_intake import",
    "parse_intake_block",
    "parse_bool",
    "from gateway_v0_v5_policy import is_valid_gateway_receipt_block",
    "is_valid_gateway_receipt_block(fields)",
]

ok = True
for frag in required:
    if frag not in text:
        print(f"FAIL: auto-register missing shared parser/policy fragment: {frag}")
        ok = False

for pat in [
    r"def\s+extract_intake_block\s*\([^)]*\):\s*\n\s*m\s*=\s*re\.search",
    r"def\s+boolish\s*\([^)]*\):\s*\n\s*return\s+str\(value\)\.strip\(\)\.lower\(\)\s*==\s*[\"']true[\"']",
]:
    if re.search(pat, text):
        print(f"FAIL: auto-register still contains loose parser pattern: {pat}")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: Guardian auto-register uses shared intake parser/policy")
