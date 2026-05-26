#!/usr/bin/env python3
"""Test: Public indexes record sub-V6 level source."""
import json
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


# Check agent-declared-verification-index.json
print("\n=== agent-declared-verification-index.json ===")
idx = json.loads((ROOT / "api" / "agent-declared-verification-index.json").read_text())

records = idx if isinstance(idx, list) else idx.get("records", idx.get("entries", []))
if isinstance(records, list) and records:
    agent_declared = [r for r in records if r.get("basis") == "agent_declared_template_pass"]
    if agent_declared:
        for rec in agent_declared[:3]:  # Check first 3
            check(rec.get("level_source") is not None,
                  f"record has level_source")
            check(rec.get("route_id") is not None,
                  f"record has route_id")
            check(rec.get("strict_evidence_used_for_level") is False,
                  f"record says strict_evidence_used_for_level false")
    else:
        print("  (no agent_declared_template_pass records found)")
else:
    print("  (no records to check)")

# Check public-home-status.json does not describe V0-V5 as strict evidence
print("\n=== public-home-status.json ===")
status = json.loads((ROOT / "api" / "public-home-status.json").read_text())
status_text = json.dumps(status)
check("strict evidence determined" not in status_text.lower(),
      "public-home-status does not describe V0-V5 as strict evidence determined")

print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
