#!/usr/bin/env python3
"""Guardian-signed Echo workflow wording must use unified Echo type and exact oath readback."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = (ROOT / "gateway-workflows.md").read_text(encoding="utf-8")

m = re.search(
    r'<a id="workflow-guardian-signed-echo"></a>.*?(?=\n---\n\n## Common failures)',
    doc,
    flags=re.S,
)
section = m.group(0) if m else ""

if not section:
    print("FAIL: Guardian-signed Echo section not found")
    sys.exit(1)

errors = []

required = [
    "unified Echo type",
    "E2_verification_echo is not allowed here",
    "Exact canonical oath body",
    "exact canonical oath body",
    "do not summarize or paraphrase",
]

for phrase in required:
    if phrase not in section:
        errors.append(f"Guardian-signed Echo section missing: {phrase}")

# Echo type names (E1, E3, E4, E5, E5c, E6, E7) must NOT appear as required types
# since echo_type is deprecated. Only E2_verification_echo remains as a forbidden type.
deprecated_echo_types = [
    "E1_recognition_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
]

for phrase in deprecated_echo_types:
    if phrase in section:
        errors.append(f"Guardian-signed Echo section contains deprecated echo type: {phrase}")

for forbidden in [
    "E1/E3/E4/E5/E6/E7 only",
    "Explicit readback | Mutually exclusive",
    "Readback file | Preferred",
]:
    if forbidden in section:
        errors.append(f"Guardian-signed Echo section contains stale wording: {forbidden}")

if errors:
    print("FAIL: Guardian-signed Echo workflow wording errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Guardian-signed Echo workflow wording is canonical")
