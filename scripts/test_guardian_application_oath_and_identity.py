#!/usr/bin/env python3
"""Test Guardian application oath and identity claims."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oath_contracts import (
    build_oath_contract,
    validate_oath_contract,
    GUARDIAN_APPLICATION_OATH_TRUE_FIELDS,
    load_oath_text,
)
from guardian_identity_claims import (
    build_guardian_identity_claims,
    validate_guardian_identity_claims,
    IDENTITY_CLAIMS_SCHEMA,
    IDENTITY_CLAIM_STATUS,
)

OATH_FILE = ROOT / "api" / "guardian-application-oath.v1.txt"


def test_guardian_application_oath():
    oath_text = load_oath_text(OATH_FILE)
    oath = build_oath_contract(
        schema="trinityaccord.guardian-application-oath.v1",
        oath_version="guardian-application-oath-v1",
        oath_kind="guardian_application",
        oath_text=oath_text,
        true_fields=GUARDIAN_APPLICATION_OATH_TRUE_FIELDS,
    )

    assert oath["schema"] == "trinityaccord.guardian-application-oath.v1"
    assert oath["oath_version"] == "guardian-application-oath-v1"
    assert oath["oath_kind"] == "guardian_application"
    assert oath["oath_read"] is True
    assert oath["readback_required"] is True

    # Anti-abuse fields
    assert oath["will_not_register_maliciously"] is True
    assert oath["will_not_mass_register_for_spam"] is True
    assert oath["will_not_register_to_impersonate_others"] is True
    assert oath["will_not_register_to_evade_prior_retirement_or_block"] is True
    assert oath["will_not_register_to_create_false_authority_or_false_consensus"] is True
    assert oath["will_not_register_duplicate_guardians_for_same_claim_without_disclosure"] is True
    assert oath["will_retire_or_rotate_key_if_claim_becomes_misleading"] is True
    assert oath["good_faith_stewardship_only"] is True

    # Boundary fields
    assert oath["not_authority"] is True
    assert oath["not_governance"] is True
    assert oath["not_attestation"] is True
    assert oath["not_verification_level"] is True
    assert oath["not_successor_reception"] is True
    assert oath["not_amendment"] is True
    assert oath["not_legal_identity_proof"] is True
    assert oath["not_ai_identity_proof"] is True
    assert oath["key_continuity_only"] is True
    assert oath["bitcoin_originals_prevail"] is True

    # Validate
    errors = validate_oath_contract(
        oath,
        context="test",
        allowed_schemas={"trinityaccord.guardian-application-oath.v1"},
        required_true=GUARDIAN_APPLICATION_OATH_TRUE_FIELDS,
    )
    assert errors == [], f"Validation errors: {errors}"

    print("PASS: test_guardian_application_oath")


def test_guardian_identity_claims():
    claims = build_guardian_identity_claims(
        display_label="Test Guardian",
        guardian_id="guardian_ed25519_abcd1234ef015678",
        public_key_sha256="abcd1234ef015678" * 4,
        claim_basis="self_reported_by_stage_1_guardian_application",
        human_claimed_name="Test Human",
        agent_claimed_id="test-agent-001",
        system_or_provider="TestProvider",
    )

    assert claims["schema"] == IDENTITY_CLAIMS_SCHEMA
    assert claims["claim_status"] == IDENTITY_CLAIM_STATUS
    assert claims["display_label"] == "Test Guardian"
    assert claims["human"]["claimed_name"] == "Test Human"
    assert claims["human"]["legal_identity_verified"] is False
    assert claims["ai_agent"]["claimed_agent_id"] == "test-agent-001"
    assert claims["binding"]["guardian_id"] == "guardian_ed25519_abcd1234ef015678"
    assert claims["binding"]["algorithm"] == "ed25519"
    assert claims["anti_impersonation_boundary"]["not_legal_identity_proof"] is True
    assert claims["anti_impersonation_boundary"]["key_continuity_only"] is True

    # Validate
    errors = validate_guardian_identity_claims(
        claims,
        expected_guardian_id="guardian_ed25519_abcd1234ef015678",
        expected_public_key_sha256="abcd1234ef015678" * 4,
    )
    assert errors == [], f"Validation errors: {errors}"

    print("PASS: test_guardian_identity_claims")


if __name__ == "__main__":
    test_guardian_application_oath()
    test_guardian_identity_claims()
