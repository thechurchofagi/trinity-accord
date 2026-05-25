#!/usr/bin/env python3
"""DEEP-VAL-001: validate_echo_records.py does not fail open on missing jsonschema."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "scripts/validate_echo_records.py"
text = p.read_text(encoding="utf-8")

bad_terms = [
    "SKIP: jsonschema not installed",
    "sys.exit(0)",
]

if "jsonschema" in text:
    for term in bad_terms:
        if term in text:
            print(f"FAIL: validate_echo_records.py still fails open on missing jsonschema: {term}")
            sys.exit(1)

print("PASS: validate_echo_records.py does not fail open on missing jsonschema")
