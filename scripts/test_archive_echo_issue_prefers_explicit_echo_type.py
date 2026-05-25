#!/usr/bin/env python3
"""DEEP-ECHO-001: archive_echo_issue.py prefers explicit echo_type."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "scripts/archive_echo_issue.py"
text = p.read_text(encoding="utf-8")

required = [
    "extract_intake_block_fields",
    'intake.get("echo_type")',
    "guardian_active_registry_listing_request",
    "E7_propagation_echo",
]

missing = [s for s in required if s not in text]
if missing:
    print(f"FAIL: archive_echo_issue.py does not prefer explicit echo_type: {missing}")
    sys.exit(1)

print("PASS: archive_echo_issue.py prefers explicit echo_type and Guardian listing semantics")
