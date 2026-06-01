#!/usr/bin/env python3
"""echo-triage rate classifier must reject ambiguous Gateway intake shapes."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = (ROOT / ".github" / "workflows" / "echo-triage.yml").read_text(encoding="utf-8")

required_fragments = [
    "function parseIntakeFields",
    "duplicate_intake_keys",
    "Object.prototype.hasOwnProperty.call",
    "missing_or_multiple_intake_blocks",
    '["true", "false"].includes(got)',
]

ok = True
for frag in required_fragments:
    if frag not in workflow:
        print(f"FAIL: echo-triage rate classifier missing ambiguity guard fragment: {frag}")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: echo-triage rate classifier has ambiguity guards")
