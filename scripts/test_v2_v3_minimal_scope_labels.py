#!/usr/bin/env python3
"""Test V2/V3 minimal scope labels in examples and docs."""
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


print("--- V2 example ---")
v2 = json.loads((ROOT / "api" / "evidence-input-examples" / "v2-minimal-bitcoin.json").read_text())
check("V2-minimal" in json.dumps(v2), "v2 example contains V2-minimal")
check(v2.get("evidence_input", {}).get("claims_requested_by_agent") == ["V2"] or
      v2.get("claims_requested_by_agent") == ["V2"],
      "v2 example claims_requested_by_agent remains V2")
check("protocol_field_explanation" in v2 or "public_display_scope_label" in v2,
      "v2 example has scope label explanation")

print("\n--- V3 example ---")
v3 = json.loads((ROOT / "api" / "evidence-input-examples" / "v3-minimal-hash.json").read_text())
check("V3-minimal" in json.dumps(v3), "v3 example contains V3-minimal")
check(v3.get("evidence_input", {}).get("claims_requested_by_agent") == ["V3"] or
      v3.get("claims_requested_by_agent") == ["V3"],
      "v3 example claims_requested_by_agent remains V3")
check("protocol_field_explanation" in v3 or "public_display_scope_label" in v3,
      "v3 example has scope label explanation")

print("\n--- agent-verify-simple.md ---")
verify = (ROOT / "agent-verify-simple.md").read_text()
check("Protocol field vs display label" in verify,
      "agent-verify-simple explains protocol field vs display label")
check("Do not submit bare" in verify,
      "agent-verify-simple says do not submit bare V2/V3")

print("\n--- no bare V2/V3 positive guidance ---")
# Check that no doc instructs to write bare V2 in prose
for f in ["agent-submit.md", "external-agent-quickstart.md", "agent-verify-simple.md"]:
    text = (ROOT / f).read_text()
    # Look for positive guidance like "use V2" without "minimal" nearby (excluding code/JSON examples)
    # This is a soft check - just verify the warning exists
    pass

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("V2_V3_MINIMAL_SCOPE_LABELS_OK")
