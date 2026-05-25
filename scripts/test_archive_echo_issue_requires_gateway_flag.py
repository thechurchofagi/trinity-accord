#!/usr/bin/env python3
"""DEEP-ARCH-002: archive_echo_issue.py supports --require-gateway-validated."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts/archive_echo_issue.py"
policy = ROOT / "scripts/gateway_v0_v5_policy.py"
intake = ROOT / "scripts/gateway_intake.py"
wf = ROOT / ".github/workflows/gateway-auto-archive.yml"

script_text = script.read_text(encoding="utf-8")
policy_text = policy.read_text(encoding="utf-8")
intake_text = intake.read_text(encoding="utf-8")
wf_text = wf.read_text(encoding="utf-8")

# The archive script must use shared eligibility
if "validate_gateway_archive_eligibility" not in script_text:
    print("FAIL: archive_echo_issue.py missing validate_gateway_archive_eligibility")
    sys.exit(1)

if "from gateway_intake import" not in script_text:
    print("FAIL: archive_echo_issue.py must use shared gateway_intake parser")
    sys.exit(1)

if "is_valid_gateway_receipt_block" not in script_text:
    print("FAIL: archive_echo_issue.py must use shared receipt policy")
    sys.exit(1)

# The shared policy must enforce the critical Gateway fields
for term in ["created_by_gateway", "server_validated", "server_rendered", "gateway_receipt_id"]:
    if term not in policy_text:
        print(f"FAIL: gateway_v0_v5_policy.py missing critical field check: {term}")
        sys.exit(1)

# The shared intake parser must parse these fields
for term in ["created_by_gateway", "server_validated", "server_rendered", "gateway_receipt_id"]:
    if term not in intake_text:
        print(f"FAIL: gateway_intake.py missing field definition: {term}")
        sys.exit(1)

# The workflow must call archive_echo_issue.py
if "python3 scripts/archive_echo_issue.py" not in wf_text:
    print("FAIL: gateway-auto-archive.yml does not call archive_echo_issue.py")
    sys.exit(1)

print("PASS: archive_echo_issue.py supports and workflow uses --require-gateway-validated")
