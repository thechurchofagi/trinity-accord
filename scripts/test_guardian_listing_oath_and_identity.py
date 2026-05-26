#!/usr/bin/env python3
"""Test Guardian listing oath and identity claims."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oath_contracts import (
    build_guardian_listing_oath_v1,
    validate_oath_contract,
    GUARDIAN_LISTING_OATH_TRUE_FIELDS,
    load_oath_text,
)
from guardian_identity_claims import (
    build_guardian_identity_claims,
    validate_guardian_identity_claims,
    IDENTITY_CLAIMS_SCHEMA,
    IDENTITY_CLAIM_STATUS,
)

OATH_FILE = ROOT / "api" / "guardian-listing-oath.v1.txt"


def test_guardian_listing_oath():
    oath_text = load_oath_text(OATH_FILE)
    oath = build_guardian_listing_oath_v1(oath_text)

    assert oath["schema"] == "trinityaccord.guardian-listing-oath.v1"
    assert oath["oath_version"] == "guardian-listing-request-oath-v1"
    assert oath["oath_kind"] == "guardian_listing_request"
    assert oath["oath_read"] is True
    assert oath["readback_required"] is True

    # Anti-abuse fields
    assert oath["will_not_register_maliciously"] is True
    assert oath["will_not_mass_register_for_spam"] is True
    assert oath["will_not_register_to_impersonate_others"] is True
    assert oath["will_not_register_to_evade_prior_retirement_or_block"] is True
    assert oath["will_not_register_to_create_false_authority_or_false_consensus"] is True
    assert oath["will_not_register_duplicate_guardians_for_same_claim_without_disclosure"] is True
    assert oath["identity_claim_boundary_acknowledged"] is True
    assert oath["registry_number_must_be_system_generated"] is True

    # Boundary fields
    assert oath["not_authority"] is True
    assert oath["not_governance"] is True
    assert oath["not_attestation"] is True
    assert oath["not_verification_level"] is True
    assert oath["not_legal_identity_proof"] is True
    assert oath["not_ai_identity_proof"] is True

    # Validate
    errors = validate_oath_contract(
        oath,
        context="test",
        allowed_schemas={"trinityaccord.guardian-listing-oath.v1"},
        required_true=GUARDIAN_LISTING_OATH_TRUE_FIELDS,
    )
    assert errors == [], f"Validation errors: {errors}"

    print("PASS: test_guardian_listing_oath")


def test_guardian_listing_identity():
    claims = build_guardian_identity_claims(
        display_label="Listing Guardian",
        guardian_id="guardian_ed25519_abcd1234ef015678",
        public_key_sha256="abcd1234ef015678" * 4,
        claim_basis="self_reported_by_stage_2_listing_request",
        human_claimed_name="Listing Human",
        agent_claimed_id="listing-agent-001",
        system_or_provider="ListingProvider",
    )

    assert claims["schema"] == IDENTITY_CLAIMS_SCHEMA
    assert claims["claim_status"] == IDENTITY_CLAIM_STATUS
    assert claims["claim_basis"] == "self_reported_by_stage_2_listing_request"

    errors = validate_guardian_identity_claims(
        claims,
        expected_guardian_id="guardian_ed25519_abcd1234ef015678",
        expected_public_key_sha256="abcd1234ef015678" * 4,
    )
    assert errors == [], f"Validation errors: {errors}"

    print("PASS: test_guardian_listing_identity")


if __name__ == "__main__":
    test_guardian_listing_oath()
    test_guardian_listing_identity()
