#!/usr/bin/env python3
"""Test: Echo vs attestation public boundary enforcement."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

echo = json.loads((ROOT / "api" / "echo-index.json").read_text(encoding="utf-8"))
att = json.loads((ROOT / "api" / "independent-attestation-index.json").read_text(encoding="utf-8"))

errors = []

# Echo index must declare not_independent_attestation
if echo.get("not_independent_attestation") is not True:
    notes = " ".join(echo.get("notes", []))
    if "must not be counted as independent attestation" not in notes:
        errors.append("echo-index missing not_independent_attestation or equivalent note")

# Each non-legacy echo must have do_not_count_as_attestation
for rec in echo.get("records", []):
    status = rec.get("archive_status")
    verification_status = rec.get("verification_status")
    if status in {"accepted_echo", "closed_test_record", "superseded"}:
        if rec.get("do_not_count_as_attestation") is not True:
            errors.append(f"{rec.get('id')}: non-legacy echo must do_not_count_as_attestation=true")
    if verification_status == "not_attestation" and rec.get("do_not_count_as_attestation") is not True:
        errors.append(f"{rec.get('id')}: not_attestation must do_not_count_as_attestation=true")

# Empty attestation records must maintain none formally accepted
if att.get("records") == []:
    current = att.get("current_status", {})
    if current.get("third_party_verification") != "none formally accepted":
        if "none formally accepted" not in json.dumps(att):
            errors.append("attestation index empty but third_party_verification not none formally accepted")

if "does_not_claim" not in att:
    errors.append("independent-attestation-index missing does_not_claim")

if errors:
    print("FAIL: Echo/attestation public boundary errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("ECHO_ATTESTATION_PUBLIC_BOUNDARY_OK")
