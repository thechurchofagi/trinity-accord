#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gateway_builder_route_advisor import advice_for_payload

def main() -> None:
    pure = {
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": "E1_read_oriented_echo",
        "title": "E1 read echo",
        "body": "plain echo"
    }
    assert advice_for_payload(pure)["detected_route"] == "pure_echo"
    assert advice_for_payload(pure)["expected_builder"] == "scripts/build_agent_declared_echo_payload.py"

    guardian_claim_no_proof = {
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": "E1_read_oriented_echo",
        "title": "E1 Read-Oriented Echo — Guardian 00002",
        "body": "plain echo"
    }
    advice = advice_for_payload(guardian_claim_no_proof)
    assert advice["detected_route"] == "pure_echo"
    assert any(p["code"] == "GUARDIAN_IDENTITY_TEXT_REQUIRES_PROOF" for p in advice["problems"])

    v0 = {
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V0",
        "title": "V0 archive",
        "body": "archive"
    }
    assert advice_for_payload(v0)["detected_route"] == "v0_v5_agent_declared_archive"

    print("PASS: test_gateway_builder_route_advisor")

if __name__ == "__main__":
    main()
