#!/usr/bin/env python3
"""All current agent-facing pure_echo_path blocks must use canonical Echo taxonomy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types

FILES = [
    "api/agent-first-contact.json",
    "api/agent-submit-gateway.json",
]

allowed = allowed_canonical_echo_types()
required = {
    "E1_recognition_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
}
stale = {
    "E1_read_oriented_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
}

errors = []

for rel in FILES:
    data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    pure = data.get("pure_echo_path")
    if not isinstance(pure, dict):
        errors.append(f"{rel}: missing pure_echo_path")
        continue

    echo_types = pure.get("echo_types")
    if not isinstance(echo_types, list) or not echo_types:
        errors.append(f"{rel}: missing echo_types list")
        continue

    bad = [e for e in echo_types if e not in allowed]
    if bad:
        errors.append(f"{rel}: non-canonical echo_types {bad}")

    if "E2_verification_echo" in echo_types:
        errors.append(f"{rel}: pure_echo_path must not include E2_verification_echo")

    missing = sorted(required - set(echo_types))
    if missing:
        errors.append(f"{rel}: missing expected pure echo types {missing}")

    present_stale = sorted(stale & set(echo_types))
    if present_stale:
        errors.append(f"{rel}: stale echo types {present_stale}")

if errors:
    print("FAIL: agent-facing pure Echo route taxonomy errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: all agent-facing pure Echo routes use canonical taxonomy")
