#!/usr/bin/env python3
"""Test ordinary agent-declared echo archives still count toward Reception."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_gateway_issue_body import render_machine_block


def test_echo_archive_renderer_counts_reception() -> None:
    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "echo_candidate",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": "E6_preservation_echo",
        "title": "Ordinary Echo Archive",
        "body": "Ordinary echo archive.",
        "agent_identity": {
            "name_or_model": "TestAgent",
            "system_or_provider": "TestProvider",
            "self_reported": True,
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True,
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v2",
                "oath_version": "verification-echo-pre-oath-v2",
                "oath_read": True,
                "readback_required": True,
                "agent_readback": "I submit this echo in honesty and good faith.",
                "honesty_oath_present": True,
                "good_faith_oath_present": True,
                "will_not_submit_maliciously": True,
                "will_not_create_false_authority_or_false_consensus": True,
                "will_correct_material_errors_when_aware": True,
            },
            "declaration_text": "Ordinary echo archive.",
        },
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "test",
            "method": "test",
            "self_reported": True,
        },
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True,
        },
        "counts_toward_home": {
            "reception": True,
            "verifiability": False,
            "basis": "agent_declared_echo_template_pass",
        },
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "reception_initiation_class": "externally_requested",
    }

    block = render_machine_block(
        payload,
        gateway_receipt_id="gar-test1234567890ab",
        production_render=True,
    )

    assert "counts_toward_home_reception: true" in block, f"Missing counts_toward_home_reception: true"
    assert "counts_toward_home_verifiability: false" in block
    assert "counts_toward_home_basis: agent_declared_echo_template_pass" in block

    print("PASS: test_echo_archive_renderer_counts_reception")


if __name__ == "__main__":
    test_echo_archive_renderer_counts_reception()
