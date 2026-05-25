#!/usr/bin/env python3
"""PUB-ECHO-001: Public status Echo buckets must match taxonomy."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

taxonomy = json.loads((ROOT / "api/echo-types.json").read_text(encoding="utf-8"))
types = {item["id"]: item["key"] for item in taxonomy.get("types", [])}

expected = {
    "E1": "recognition", "E2": "verification", "E3": "critical",
    "E4": "interpretive", "E5": "technical-audit", "E6": "propagation",
    "E7": "refusal", "E8": "witness", "E9": "seed",
}
if types != expected:
    print(f"FAIL: api/echo-types.json taxonomy drift: {types}")
    sys.exit(1)

src = (ROOT / "scripts/generate_public_home_status.py").read_text(encoding="utf-8")

for term in ["E6_preservation_echo", "E7_propagation_echo", "E4_refusal_echo", "E5_correction_echo"]:
    if term in src:
        print(f"FAIL: public status still contains taxonomy-conflicting bucket: {term}")
        sys.exit(1)

for term in ["E6_propagation_echo", "E7_refusal_echo"]:
    if term not in src:
        print(f"FAIL: public status missing taxonomy-aligned bucket: {term}")
        sys.exit(1)

print("PASS: public status Echo buckets match taxonomy")
