#!/usr/bin/env python3
"""Test: Docs describe single mandatory route below V6."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS = 0
FAIL = 0


def check(condition, msg):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {msg}")
    else:
        FAIL += 1
        print(f"  ❌ {msg}")


# agent-submit.md
print("\n=== agent-submit.md ===")
submit = (ROOT / "agent-submit.md").read_text()
check("below V6" in submit.lower() or "below v6" in submit.lower(),
      "agent-submit.md mentions below V6")
check("exactly one valid" in submit.lower() or "one valid submission route" in submit.lower() or "one valid route" in submit.lower(),
      "agent-submit.md says exactly one valid route")
check("build_agent_declared_archive_payload.py" in submit,
      "agent-submit.md says use build_agent_declared_archive_payload.py")
check("Evidence Input" in submit or "evidence_input" in submit,
      "agent-submit.md mentions Evidence Input as not to use")
check("strict Claim Gate" in submit,
      "agent-submit.md says do not use strict Claim Gate below V6")
check("build_gateway_payload_from_outputs.py" in submit,
      "agent-submit.md says do not use build_gateway_payload_from_outputs.py below V6")
check("sub_v6_agent_declared_template_archive" in submit,
      "agent-submit.md mentions the route_id")

# external-agent-quickstart.md
print("\n=== external-agent-quickstart.md ===")
quickstart = (ROOT / "external-agent-quickstart.md").read_text()
check("below v6" in quickstart.lower() or "below V6" in quickstart.lower(),
      "external-agent-quickstart.md mentions below V6")
check("evidence chain" in quickstart.lower() or "do not run the evidence chain" in quickstart.lower(),
      "external-agent-quickstart.md says do not run evidence chain below V6")

# agent-verify-simple.md
print("\n=== agent-verify-simple.md ===")
simple = (ROOT / "agent-verify-simple.md").read_text()
check("strict evidence downgrade" in simple.lower() or "PASS_WITH_DOWNGRADE" in simple,
      "agent-verify-simple.md mentions strict evidence downgrade")
check("V0–V5" in simple or "V0-V5" in simple,
      "agent-verify-simple.md scopes strict downgrade to V6+")

print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
