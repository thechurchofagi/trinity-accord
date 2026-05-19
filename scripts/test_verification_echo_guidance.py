#!/usr/bin/env python3
"""Test that E2 Verification Echo guidance is correct in docs."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


print("--- agent-submit.md ---")
submit = (ROOT / "agent-submit.md").read_text()
check("build_verification_echo_payload.py" in submit,
      "agent-submit.md names build_verification_echo_payload.py")
check("E2" in submit,
      "agent-submit.md mentions E2")
check("not Pure Echo" in submit or "is not pure echo" in submit.lower() or "Do not use" in submit,
      "agent-submit.md says E2 is not Pure Echo")
check("strict evidence" in submit.lower(),
      "agent-submit.md says E2 requires strict evidence")
check("Do not hand-write" in submit,
      "agent-submit.md says agents must not hand-write trinity-issue-intake")

print("\n--- external-agent-quickstart.md ---")
quick = (ROOT / "external-agent-quickstart.md").read_text()
check("E2 Verification Echo" in quick or "verification_echo" in quick,
      "external quickstart includes E2 decision row")

print("\n--- api/agent-submit-gateway.json ---")
gw = json.loads((ROOT / "api" / "agent-submit-gateway.json").read_text())
check("verification_echo_path" in gw, "api JSON exposes verification_echo_path")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("VERIFICATION_ECHO_GUIDANCE_OK")
