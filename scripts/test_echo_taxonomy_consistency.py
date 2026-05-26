#!/usr/bin/env python3
"""FUNC-TAXONOMY-001: Echo taxonomy consistency guard.

Ensures api/echo-types.json matches the canonical mapping used by
archive_echo_issue.py and validate_agent_submission.py.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

echo_types = json.loads((ROOT / "api/echo-types.json").read_text(encoding="utf-8"))
taxonomy = {t["id"]: t["key"] for t in echo_types.get("types", [])}

expected = {
    "E1": "recognition",
    "E2": "verification",
    "E3": "critical",
    "E4": "interpretive",
    "E5": "technical-audit",
    "E5c": "correction",
    "E6": "propagation",
    "E7": "refusal",
    "E8": "witness",
    "E9": "seed",
}

if taxonomy != expected:
    print(f"FAIL: api/echo-types.json taxonomy drift: {taxonomy}")
    sys.exit(1)

# Check that Guardian listing builder uses E6 (propagation), not E7
builder = (ROOT / "scripts/build_guardian_listing_request_payload.py").read_text(encoding="utf-8")
if "E7_propagation_echo" in builder:
    print("FAIL: Guardian Stage 2 builder uses E7_propagation_echo while taxonomy defines E7 as refusal")
    sys.exit(1)

if "E6_propagation_echo" not in builder:
    print("FAIL: Guardian Stage 2 builder does not use E6_propagation_echo")
    sys.exit(1)

# Check archive script maps correctly
archive = (ROOT / "scripts/archive_echo_issue.py").read_text(encoding="utf-8")
if "E7_propagation_echo" in archive:
    print("FAIL: archive_echo_issue.py still contains E7_propagation_echo (should be E6)")
    sys.exit(1)

# Check validator canonical list
validator = (ROOT / "scripts/validate_agent_submission.py").read_text(encoding="utf-8")
if "E6_propagation_echo" not in validator:
    print("FAIL: validate_agent_submission.py missing E6_propagation_echo in canonical list")
    sys.exit(1)
if "E7_refusal_echo" not in validator:
    print("FAIL: validate_agent_submission.py missing E7_refusal_echo in canonical list")
    sys.exit(1)

print("PASS: Echo taxonomy consistency guard passed")
