#!/usr/bin/env python3
"""agent-first-contact pure Echo route must use canonical Echo taxonomy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types

data = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))

pure = data.get("pure_echo_path")
if not isinstance(pure, dict):
    print("FAIL: agent-first-contact missing pure_echo_path object")
    sys.exit(1)

echo_types = pure.get("echo_types")
if not isinstance(echo_types, list) or not echo_types:
    print("FAIL: agent-first-contact pure_echo_path.echo_types must be non-empty list")
    sys.exit(1)

allowed = allowed_canonical_echo_types()
bad = [e for e in echo_types if e not in allowed]
if bad:
    print(f"FAIL: agent-first-contact has non-canonical echo_types: {bad}")
    sys.exit(1)

if "E2_verification_echo" in echo_types:
    print("FAIL: agent-first-contact pure_echo_path must not include E2_verification_echo")
    sys.exit(1)

required = {
    "E1_recognition_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
}
missing = sorted(required - set(echo_types))
if missing:
    print(f"FAIL: agent-first-contact pure_echo_path missing expected canonical types: {missing}")
    sys.exit(1)

for stale in [
    "E1_read_oriented_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
]:
    if stale in json.dumps(pure):
        print(f"FAIL: agent-first-contact pure_echo_path contains stale taxonomy: {stale}")
        sys.exit(1)

print("PASS: agent-first-contact pure_echo_path echo_types are canonical")
