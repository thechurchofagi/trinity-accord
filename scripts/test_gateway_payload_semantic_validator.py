#!/usr/bin/env python3
"""Unit tests for validate_gateway_payload_semantics.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_gateway_payload_semantics import validate

verification = {
    "requested_archive_kind": "agent_declared_verification_archive",
    "agent_declared_protocol_level": "V5",
    "level_selection_acknowledgement": {
        "declared_template_level": "V1",
    },
}

errors = validate(verification)
if not any("agent_declared_protocol_level must equal" in e for e in errors):
    print("FAIL: mismatched declared level was not rejected")
    sys.exit(1)

echo = {
    "requested_archive_kind": "agent_declared_echo_archive",
    "agent_declared_protocol_level": "V4",
    "counts_toward_home": {
        "verifiability": True,
        "reception": True,
    },
}

errors = validate(echo)
required_fragments = [
    "must not claim agent_declared_protocol_level",
    "verifiability must be false",
]
for frag in required_fragments:
    if not any(frag in e for e in errors):
        print(f"FAIL: expected semantic error missing: {frag}")
        print(errors)
        sys.exit(1)

guardian = {
    "guardian_registry_listing_request": True,
    "requested_archive_kind": "agent_declared_echo_archive",
    "echo_type": "E5_technical_audit_echo",
    "guardian_presence_proof": {"proof": "bad"},
}

errors = validate(guardian)
required_fragments = [
    "requires requested_archive_kind=guardian_active_registry_listing_request",
    "requires echo_type=E6_propagation_echo",
    "must not include guardian_presence_proof",
]
for frag in required_fragments:
    if not any(frag in e for e in errors):
        print(f"FAIL: expected guardian semantic error missing: {frag}")
        print(errors)
        sys.exit(1)

print("PASS: Gateway semantic validator catches combination errors")
