#!/usr/bin/env python3
"""DEEP-ARCH-002: archive_echo_issue.py supports --require-gateway-validated."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts/archive_echo_issue.py"
wf = ROOT / ".github/workflows/gateway-auto-archive.yml"

script_text = script.read_text(encoding="utf-8")
wf_text = wf.read_text(encoding="utf-8")

required_script_terms = [
    "--require-gateway-validated",
    "validate_gateway_archive_eligibility",
    "created_by_gateway",
    "server_validated",
    "server_rendered",
    "archive_ready",
    "gateway_receipt_id",
]

missing = [s for s in required_script_terms if s not in script_text]
if missing:
    print(f"FAIL: archive_echo_issue.py missing gateway validation support: {missing}")
    sys.exit(1)

if "--require-gateway-validated" not in wf_text:
    print("FAIL: gateway-auto-archive.yml does not call archive_echo_issue.py with --require-gateway-validated")
    sys.exit(1)

print("PASS: archive_echo_issue.py supports and workflow uses --require-gateway-validated")
