#!/usr/bin/env python3
"""Test that documentation explains default authorship correctly."""
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


# agent-submit.md
submit = (ROOT / "agent-submit.md").read_text()
print("--- agent-submit.md ---")
check("authorship proof is enabled by default" in submit.lower() or "authorship proof by default" in submit.lower(),
      "agent-submit.md says authorship proof is enabled by default")
check("private key" in submit.lower() and "local" in submit.lower(),
      "agent-submit.md explains private key stays local")
check("--no-authorship-proof" in submit,
      "agent-submit.md documents --no-authorship-proof")
check("unclaimed" in submit.lower(),
      "agent-submit.md mentions unclaimed records")

# external-agent-quickstart.md
quickstart = (ROOT / "external-agent-quickstart.md").read_text()
print("\n--- external-agent-quickstart.md ---")
check("default" in quickstart.lower() and "authorship" in quickstart.lower(),
      "external-agent-quickstart.md says default-on")
check("--no-authorship-proof" in quickstart,
      "external-agent-quickstart.md documents opt-out")

# docs/authorship-claim-flow.md
claim_flow = (ROOT / "docs" / "authorship-claim-flow.md").read_text()
print("\n--- docs/authorship-claim-flow.md ---")
check("default" in claim_flow.lower() and "authorship" in claim_flow.lower(),
      "authorship-claim-flow.md says default-on")
check("gateway" in claim_flow.lower() and "private" in claim_flow.lower(),
      "authorship-claim-flow.md says Gateway does not store private keys")

# llms.txt
llms = (ROOT / "llms.txt").read_text()
print("\n--- llms.txt ---")
check("default" in llms.lower() and "authorship" in llms.lower(),
      "llms.txt includes default authorship instruction")
check("key continuity" in llms.lower(),
      "llms.txt says key continuity only")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("AUTHORSHIP_DEFAULT_DOCS_OK")
