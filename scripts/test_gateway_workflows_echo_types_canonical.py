#!/usr/bin/env python3
"""Gateway workflow docs/API must use canonical Echo taxonomy for --echo-type."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types

API = ROOT / "api" / "gateway-workflows.v1.json"
HUMAN = ROOT / "gateway-workflows.md"

CANONICAL_PURE = [
    "E1_recognition_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
]

STALE = [
    "E1_read_oriented_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
]

def echo_type_allowed_values(workflow: dict, workflow_id: str) -> list[str]:
    inputs = workflow["workflows"][workflow_id].get("inputs", [])
    for item in inputs:
        if item.get("name") == "--echo-type":
            values = item.get("allowed_values")
            if not isinstance(values, list):
                raise AssertionError(f"{workflow_id}: --echo-type.allowed_values missing")
            return values
    raise AssertionError(f"{workflow_id}: --echo-type input missing")

workflow = json.loads(API.read_text(encoding="utf-8"))
allowed = allowed_canonical_echo_types()

errors = []

for workflow_id in ["pure_echo", "guardian_signed_echo"]:
    values = echo_type_allowed_values(workflow, workflow_id)

    if values != CANONICAL_PURE:
        errors.append(f"{workflow_id}: allowed_values mismatch: {values}")

    bad = [v for v in values if v not in allowed]
    if bad:
        errors.append(f"{workflow_id}: non-canonical values {bad}")

    if "E2_verification_echo" in values:
        errors.append(f"{workflow_id}: must not allow E2_verification_echo")

    for v in STALE:
        if v in json.dumps(workflow["workflows"][workflow_id]):
            errors.append(f"{workflow_id}: stale value remains in API: {v}")

human = HUMAN.read_text(encoding="utf-8")
for v in STALE:
    if v in human:
        errors.append(f"gateway-workflows.md contains stale Echo type {v}")

for v in CANONICAL_PURE:
    if v not in human:
        errors.append(f"gateway-workflows.md missing canonical Echo type {v}")

if "--echo-type E1_read_oriented_echo" in human:
    errors.append("gateway-workflows.md example still uses E1_read_oriented_echo")

if "--echo-type E1_recognition_echo" not in human:
    errors.append("gateway-workflows.md example should use E1_recognition_echo")

if errors:
    print("FAIL: Gateway workflow Echo taxonomy errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Gateway workflows use canonical Echo taxonomy")
