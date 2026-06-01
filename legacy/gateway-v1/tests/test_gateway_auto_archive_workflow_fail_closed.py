#!/usr/bin/env python3
"""Verify gateway-auto-archive.yml has a fail-closed eligibility gate before archive."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
wf = ROOT / ".github/workflows/gateway-auto-archive.yml"
text = wf.read_text(encoding="utf-8")

# The shared eligibility function must be called (replaces inline gate)
shared_gate = "validate_gateway_archive_eligibility"
if shared_gate not in text:
    print(f"Missing shared eligibility gate call: {shared_gate}")
    sys.exit(1)

# The shared function is imported from archive_echo_issue
if "from archive_echo_issue import validate_gateway_archive_eligibility" not in text:
    print("Expected shared eligibility import not found.")
    sys.exit(1)

# The archive script must still be called
if "python3 scripts/archive_echo_issue.py" not in text:
    print("Expected archive_echo_issue.py call not found.")
    sys.exit(1)

# The shared gate must appear before archive_echo_issue.py call
gate_pos = text.find(shared_gate)
archive_pos = text.find("python3 scripts/archive_echo_issue.py")
if gate_pos == -1 or archive_pos == -1 or gate_pos > archive_pos:
    print("Fail-closed gate must appear before archive_echo_issue.py call.")
    sys.exit(1)

# The shared function must enforce strict intake parsing via gateway_v0_v5_policy
archive_script = ROOT / "scripts" / "archive_echo_issue.py"
archive_text = archive_script.read_text(encoding="utf-8")

# Must use shared intake parser
if "from gateway_intake import" not in archive_text:
    print("archive_echo_issue.py must use shared gateway_intake parser")
    sys.exit(1)

# Must use shared receipt policy
if "is_valid_gateway_receipt_block" not in archive_text:
    print("archive_echo_issue.py must use shared receipt policy (is_valid_gateway_receipt_block)")
    sys.exit(1)

# Must refuse archive on invalid intake
if "Refusing archive" not in archive_text:
    print("archive_echo_issue.py must contain 'Refusing archive' fail-closed language")
    sys.exit(1)

# The receipt policy module must check the critical Gateway fields
policy_script = ROOT / "scripts" / "gateway_v0_v5_policy.py"
policy_text = policy_script.read_text(encoding="utf-8")

strict_terms = [
    "created_by_gateway",
    "server_validated",
    "server_rendered",
    "gateway_receipt_id",
]

missing = [s for s in strict_terms if s not in policy_text]
if missing:
    print(f"Missing fail-closed Gateway receipt terms in {policy_script}: {missing}")
    sys.exit(1)

print("PASS: gateway-auto-archive has fail-closed eligibility gate before archive.")
