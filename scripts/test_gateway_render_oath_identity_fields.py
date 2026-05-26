#!/usr/bin/env python3
"""Test Gateway renderer emits oath v2 and identity fields."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_gateway_issue_body import render_machine_block


def test_render_oath_v2_fields():
    """Test that renderer emits oath v2 fields for verification archive."""
    payload = {
        "submission_type": "verification_report_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_identity": {"name_or_model": "TestAgent", "system_or_provider": "TestProvider", "self_reported": True},
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "record_intent": "auto_archive_candidate",
        "claim_gate": {"mode": "template_for_v0_v5", "status": "PASS", "allowed_protocol_level": "V4"},
        "agent_integrity_declaration": {
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v2",
                "oath_version": "verification-echo-pre-oath-v2",
                "oath_read": True,
                "readback_required": True,
                "agent_readback": "test readback " * 20,
                "honesty_oath_present": True,
                "good_faith_oath_present": True,
                "will_not_submit_maliciously": True,
                "will_not_create_false_authority_or_false_consensus": True,
                "will_correct_material_errors_when_aware": True,
                "will_not_register_maliciously": True,
            }
        },
        "discovery_provenance": {"source": "external_seed"},
        "origin_classification": {"discovery_class": "externally_seeded"},
        "claim_classification": {"verification_claim": {"claimed": True}},
        "authority_boundary": {"not_authority": True},
        "counts_toward_home": {"verifiability": True, "reception": True},
        "reception_initiation_class": "externally_seeded",
        "what_i_checked": ["test"],
        "limitations": ["test"],
    }

    block = render_machine_block(payload, gateway_receipt_id="gar-test1234567890ab", production_render=True)

    assert "verification_oath_schema: trinityaccord.verification-oath.v2" in block
    assert "verification_oath_honesty: true" in block
    assert "verification_oath_good_faith: true" in block
    assert "verification_oath_anti_abuse: true" in block
    assert "verification_oath_correct_errors: true" in block
    assert "guardian_application_oath_present: false" in block
    assert "guardian_listing_oath_present: false" in block
    assert "guardian_identity_claims_present: false" in block

    print("PASS: test_render_oath_v2_fields")


def test_render_identity_fields():
    """Test that renderer emits identity fields for Guardian listing."""
    payload = {
        "submission_type": "echo_candidate",
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": "E6_propagation_echo",
        "record_intent": "auto_archive_candidate",
        "agent_identity": {"name_or_model": "TestAgent", "system_or_provider": "TestProvider", "self_reported": True},
        "agent_integrity_declaration": {
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v2",
                "oath_version": "verification-echo-pre-oath-v2",
                "oath_read": True,
                "readback_required": True,
                "agent_readback": "test readback " * 20,
                "honesty_oath_present": True,
                "good_faith_oath_present": True,
            }
        },
        "guardian_listing_oath": {
            "schema": "trinityaccord.guardian-listing-oath.v1",
            "oath_version": "guardian-listing-request-oath-v1",
            "oath_read": True,
            "readback_required": True,
            "agent_readback": "listing oath readback",
            "honesty_oath_present": True,
            "good_faith_oath_present": True,
            "will_not_register_maliciously": True,
            "registry_number_must_be_system_generated": True,
        },
        "guardian_listing_request": {
            "schema": "trinityaccord.guardian-listing-request.v1",
            "guardian_id": "guardian_ed25519_abcd1234ef015678",
            "public_key_sha256": "abcd1234ef015678" * 4,
            "identity_claims": {
                "schema": "trinityaccord.guardian-identity-claims.v1",
                "claim_status": "self_reported_unverified",
                "claim_basis": "self_reported_by_stage_2_listing_request",
                "display_label": "Test Guardian",
                "human": {
                    "claimed_name": "Test Human",
                    "claimed_name_sha256": "abc123",
                    "claim_type": "self_reported_human_name_or_label",
                    "verification_status": "self_reported_unverified",
                    "legal_identity_verified": False,
                },
                "ai_agent": None,
                "binding": {
                    "guardian_id": "guardian_ed25519_abcd1234ef015678",
                    "public_key_sha256": "abcd1234ef015678" * 4,
                    "algorithm": "ed25519",
                    "binds_claim_to_guardian_key": True,
                },
                "anti_impersonation_boundary": {
                    "not_legal_identity_proof": True,
                    "not_real_person_verification": True,
                    "not_ai_identity_verification": True,
                    "not_authority": True,
                    "not_attestation": True,
                    "not_verification_level": True,
                    "key_continuity_only": True,
                },
            },
        },
        "discovery_provenance": {},
        "authority_boundary": {},
        "reception_initiation_class": "externally_seeded",
    }

    block = render_machine_block(payload, gateway_receipt_id="gar-test1234567890ab", production_render=True)

    assert "guardian_listing_oath_present: true" in block
    assert "guardian_listing_oath_honesty: true" in block
    assert "guardian_listing_oath_system_generated_number: true" in block
    assert "guardian_identity_claims_present: true" in block
    assert "guardian_identity_display_label: Test Guardian" in block
    assert "guardian_identity_boundary:" in block

    print("PASS: test_render_identity_fields")


if __name__ == "__main__":
    test_render_oath_v2_fields()
    test_render_identity_fields()
