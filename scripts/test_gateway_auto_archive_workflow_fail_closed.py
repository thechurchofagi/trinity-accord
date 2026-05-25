#!/usr/bin/env python3
"""Verify gateway-auto-archive.yml has a fail-closed eligibility gate before archive."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
wf = ROOT / ".github/workflows/gateway-auto-archive.yml"
text = wf.read_text(encoding="utf-8")

required = [
    "created_by_gateway",
    "server_validated",
    "server_rendered",
    "archive_ready",
    "gateway_receipt_id",
    "Refusing archive",
]

missing = [s for s in required if s not in text]
if missing:
    print(f"Missing fail-closed archive gate terms in {wf}: {missing}")
    sys.exit(1)

if "python3 scripts/archive_echo_issue.py" not in text:
    print("Expected archive_echo_issue.py call not found.")
    sys.exit(1)

gate_pos = text.find("Refusing archive")
archive_pos = text.find("python3 scripts/archive_echo_issue.py")
if gate_pos == -1 or archive_pos == -1 or gate_pos > archive_pos:
    print("Fail-closed gate must appear before archive_echo_issue.py call.")
    sys.exit(1)

print("PASS: gateway-auto-archive has fail-closed eligibility gate before archive.")
