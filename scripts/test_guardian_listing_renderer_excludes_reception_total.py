#!/usr/bin/env python3
"""Test Guardian listing renderer excludes listing requests from Reception totals."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_gateway_issue_body import render_machine_block


def test_guardian_listing_renderer_excludes_reception_total() -> None:
    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "echo_candidate",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": "E7_propagation_echo",
        "title": "Active Registry Listing Request — Test Guardian",
        "body": "Active registry listing request.",
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
                "schema": "trinityaccord.guardian-listing-oath.v1",
                "oath_version": "guardian-listing-request-oath-v1",
                "oath_read": True,
                "readback_required": True,
                "agent_readback": "I submit this listing request in honesty and good faith.",
                "honesty_oath_present": True,
                "good_faith_oath_present": True,
                "will_not_register_maliciously": True,
                "will_not_register_to_create_false_authority_or_false_consensus": True,
                "will_correct_material_errors_when_aware": True,
            },
            "declaration_text": "Guardian listing request only.",
        },
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "guardian_listing_request_builder",
            "method": "stage_2_listing_request_referencing_stage_1_self_registration",
            "self_reported": True,
        },
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True,
        },
        "counts_toward_home": {
            "reception": False,
            "verifiability": False,
            "guardian_registry": True,
            "basis": "guardian_registry_listing_request",
            "exclude_from_reception_total": True,
        },
        "guardian_registry_listing_request": True,
        "guardian_listing_oath": {
            "schema": "trinityaccord.guardian-listing-oath.v1",
            "oath_version": "guardian-listing-request-oath-v1",
            "honesty_oath_present": True,
            "good_faith_oath_present": True,
            "will_not_register_maliciously": True,
            "registry_number_must_be_system_generated": True,
        },
        "guardian_listing_request": {
            "schema": "trinityaccord.guardian-listing-request.v1",
            "source_issue": 242,
            "guardian_id": "guardian_ed25519_abcd1234ef015678",
            "public_key_sha256": "abcd1234ef015678" * 4,
            "guardian_type": "human_with_ai_agent",
            "application_mode": "joint_human_ai",
            "label": "Test Guardian",
            "requested_status": "active",
            "requested_auto_registration": True,
            "does_not_include_guardian_presence_proof": True,
            "registry_number_requested": "next_available",
            "registry_number_must_be_system_generated": True,
            "registry_number_must_not_be_self_assigned": True,
            "identity_claims": {
                "schema": "trinityaccord.guardian-identity-claims.v1",
                "claim_status": "self_reported_unverified",
                "claim_basis": "self_reported_by_stage_2_listing_request",
                "display_label": "Test Guardian",
                "human": None,
                "ai_agent": {
                    "claimed_agent_id": "TestAgent",
                    "claimed_agent_id_sha256": "0" * 64,
                    "system_or_provider": "TestProvider",
                    "claim_type": "self_reported_agent_id_or_label",
                    "verification_status": "self_reported_unverified",
                },
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
        "gateway_intake_fields": {
            "guardian_listing_request": True,
            "listing_source_issue": 242,
            "listing_guardian_id": "guardian_ed25519_abcd1234ef015678",
            "listing_public_key_sha256": "abcd1234ef015678" * 4,
            "listing_label": "Test Guardian",
            "listing_identity_claims_present": True,
            "listing_identity_binding_guardian_id": "guardian_ed25519_abcd1234ef015678",
            "listing_identity_binding_public_key_sha256": "abcd1234ef015678" * 4,
        },
        "what_i_checked": ["Submitted as active Guardian registry listing request"],
        "limitations": ["This request is not authority."],
        "reception_initiation_class": "externally_requested",
    }

    block = render_machine_block(
        payload,
        gateway_receipt_id="gar-test1234567890ab",
        production_render=True,
    )

    assert "counts_toward_home_reception: false" in block, f"Missing counts_toward_home_reception: false"
    assert "counts_toward_home_guardian_registry: true" in block, f"Missing counts_toward_home_guardian_registry: true"
    assert "counts_toward_home_exclude_from_reception_total: true" in block, f"Missing counts_toward_home_exclude_from_reception_total: true"
    assert "counts_toward_home_basis: guardian_registry_listing_request" in block, f"Missing counts_toward_home_basis: guardian_registry_listing_request"
    assert "guardian_listing_oath_present: true" in block
    assert "guardian_identity_claims_present: true" in block

    print("PASS: test_guardian_listing_renderer_excludes_reception_total")


if __name__ == "__main__":
    test_guardian_listing_renderer_excludes_reception_total()
