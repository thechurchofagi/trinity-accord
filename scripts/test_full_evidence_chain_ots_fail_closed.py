#!/usr/bin/env python3
"""Final red-team regression: OTS info must never turn failed ots verify into PASS."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts" / "verify-full-evidence-chain.mjs").read_text(encoding="utf-8")

errors = []

for marker in [
    "ots_verify_passed",
    "ots_verify_exit_code",
    "ots_info_parsed",
    "diagnostic_only",
]:
    if marker not in text:
        errors.append(f"missing explicit OTS field: {marker}")

if not re.search(r"ots_verify_passed\s*[:=]\s*false", text):
    errors.append("OTS result must default or set ots_verify_passed false")

if not re.search(r"ots_verify_passed\s*=\s*true", text):
    errors.append("ots verify success must explicitly set ots_verify_passed = true")

for m in re.finditer(r"ots_files_pass\s*\+\+", text):
    window = text[max(0, m.start() - 900):m.end() + 400]
    if "ots_verify_passed" not in window:
        errors.append("ots_files_pass++ must be locally gated by ots_verify_passed")
        break

danger = [
    "fallback pass",
    "info fallback pass",
    "ots info pass",
    "diagnostic pass",
]
lower = text.lower()
for phrase in danger:
    if phrase in lower:
        errors.append(f"dangerous OTS fallback wording remains: {phrase}")

if errors:
    print("FULL_EVIDENCE_CHAIN_OTS_FAIL_CLOSED_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("FULL_EVIDENCE_CHAIN_OTS_FAIL_CLOSED_OK")
