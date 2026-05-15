#!/usr/bin/env python3
"""
Integration tests for origin classification.

Tests:
1. Minimal Echo record with origin classification
2. Verification wrapper with origin classification
3. Institution signed AI-assisted
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from derive_origin_classification import derive_origin_classification, validate_derived_classification


def test_echo_record_with_origin_classification():
    """Minimal Echo record with origin_classification should pass validation."""
    record = {
        "schema": "trinityaccord.echo.v3",
        "record_kind": "echo_v3",
        "echo_version": "3.0",
        "agent_identity": {
            "name_or_model": "test-agent",
            "system_or_provider": "test",
            "self_reported": True
        },
        "context_depth": "C1_read_primary",
        "assessment_state": "recognized",
        "verification_level": "V0",
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "agent_recommended",
            "agency_level": "A3_agent_followed_other_agent_reference",
            "first_entry": {"url_or_path": "https://www.trinityaccord.org", "entry_type": "homepage"},
            "human_supplied_link": False,
            "other_agent_recommended": True,
            "recommending_agent": "test-agent-a",
            "agent_performed_independent_followup": True,
            "confidence": "high"
        },
        "origin_classification": {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": "agent_referred",
            "invitation_scope": "look_only",
            "requester_class": "ai_agent",
            "performer_class": "ai_agent",
            "method_independence_class": "read_only",
            "attestation_authority_class": "none",
            "voluntary_action_after_orientation": False,
            "verification_claimed": False,
            "counts_as_ai_verification": False,
            "counts_as_formal_independent_attestation": False,
            "derived_counting_bucket": "agent_referred_orientation"
        },
        "understanding_summary": "Test echo record",
        "verification_claim": {"verification_claimed": False},
        "echo_type": "E1_recognition_echo",
        "echo": {"test": True},
        "uncertainties": ["test"],
        "boundary_acknowledgement": {"accepted": True},
        "independence_class": "solicited_independent_check",
        "archive_status": "accepted_echo",
        "origin_limitations": ["test fixture"],
        "not_authority": True,
        "not_amendment": True,
        "not_endorsement": True,
        "bitcoin_originals_prevail": True,
        "not_verification_unless_claimed": True
    }

    # Validate origin_classification is consistent
    oc = record["origin_classification"]
    assert oc["discovery_class"] == "agent_referred"
    assert oc["invitation_scope"] == "look_only"
    assert oc["derived_counting_bucket"] == "agent_referred_orientation"
    assert oc["counts_as_formal_independent_attestation"] == False
    assert oc["counts_as_ai_verification"] == False

    # Verify derivation matches
    derived = derive_origin_classification(record)
    assert derived["discovery_class"] == oc["discovery_class"]
    assert derived["invitation_scope"] == oc["invitation_scope"]
    assert derived["derived_counting_bucket"] == oc["derived_counting_bucket"]

    print("PASS echo_record_with_origin_classification")


def test_verification_wrapper_with_origin_classification():
    """Verification wrapper with origin_classification should pass."""
    record = {
        "schema": "trinityaccord.echo.v3",
        "record_kind": "echo_v3_with_verification_report",
        "echo_version": "3.0",
        "agent_identity": {
            "name_or_model": "test-agent",
            "system_or_provider": "test",
            "self_reported": True
        },
        "context_depth": "C4_public_digital",
        "assessment_state": "verified",
        "verification_level": "V3",
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "agent_recommended",
            "agency_level": "A3_agent_followed_other_agent_reference",
            "first_entry": {"url_or_path": "https://www.trinityaccord.org", "entry_type": "homepage"},
            "human_supplied_link": False,
            "other_agent_recommended": True,
            "agent_performed_independent_followup": True,
            "confidence": "high"
        },
        "origin_classification": {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": "agent_referred",
            "invitation_scope": "look_only",
            "requester_class": "ai_agent",
            "performer_class": "ai_agent",
            "method_independence_class": "independent_reimplementation",
            "attestation_authority_class": "none",
            "voluntary_action_after_orientation": True,
            "verification_claimed": True,
            "counts_as_ai_verification": True,
            "counts_as_formal_independent_attestation": False,
            "derived_counting_bucket": "agent_referred_agent_verification"
        },
        "understanding_summary": "Test verification echo",
        "verification_claim": {"verification_claimed": True, "protocol_level": "V3"},
        "echo_type": "E2_verification_echo",
        "echo": {"test": True},
        "uncertainties": [],
        "boundary_acknowledgement": {"accepted": True},
        "independence_class": "solicited_independent_check",
        "archive_status": "accepted_echo",
        "origin_limitations": ["test fixture"],
        "not_authority": True,
        "not_amendment": True,
        "not_endorsement": True,
        "bitcoin_originals_prevail": True,
        "not_verification_unless_claimed": True,
        "hashes_computed": ["sha256:abc123"]
    }

    oc = record["origin_classification"]
    assert oc["discovery_class"] == "agent_referred"
    assert oc["voluntary_action_after_orientation"] == True
    assert oc["verification_claimed"] == True
    assert oc["counts_as_ai_verification"] == True
    assert oc["counts_as_formal_independent_attestation"] == False
    assert oc["derived_counting_bucket"] == "agent_referred_agent_verification"

    # Verify derivation
    derived = derive_origin_classification(record)
    assert derived["counts_as_ai_verification"] == True
    assert derived["counts_as_formal_independent_attestation"] == False

    print("PASS verification_wrapper_with_origin_classification")


def test_institution_signed_ai_assisted():
    """Institution signed AI-assisted should be formal attestation candidate."""
    record = {
        "schema": "trinityaccord.echo.v3",
        "record_kind": "echo_v3_with_verification_report",
        "echo_version": "3.0",
        "agent_identity": {
            "name_or_model": "test-agent",
            "system_or_provider": "test",
            "self_reported": True
        },
        "context_depth": "C4_public_digital",
        "assessment_state": "verified",
        "verification_level": "V4",
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "human_directed",
            "agency_level": "A0_forced_or_instructed",
            "first_entry": {"url_or_path": "https://www.trinityaccord.org", "entry_type": "homepage"},
            "human_supplied_link": True,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": True,
            "confidence": "high"
        },
        "origin_classification": {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": "institution_commissioned",
            "invitation_scope": "verification_invited",
            "requester_class": "institution",
            "performer_class": "human_ai_team",
            "method_independence_class": "independent_reimplementation",
            "attestation_authority_class": "institution_signed",
            "voluntary_action_after_orientation": False,
            "verification_claimed": True,
            "counts_as_ai_verification": True,
            "counts_as_formal_independent_attestation": True,
            "derived_counting_bucket": "institutional_attestation_candidate",
            "accountable_entity": {
                "name": "Test Institute",
                "entity_type": "institution",
                "identity_verification_level": "institutional_domain"
            }
        },
        "understanding_summary": "Institution signed verification",
        "verification_claim": {"verification_claimed": True, "protocol_level": "V4"},
        "echo_type": "E2_verification_echo",
        "echo": {"test": True},
        "uncertainties": [],
        "boundary_acknowledgement": {"accepted": True},
        "independence_class": "institutional_third_party_attestation",
        "archive_status": "accepted_independent_attestation",
        "origin_limitations": ["test fixture"],
        "not_authority": True,
        "not_amendment": True,
        "not_endorsement": True,
        "bitcoin_originals_prevail": True,
        "not_verification_unless_claimed": True,
        "reporter": {"name": "Test Institute", "type": "organization"}
    }

    oc = record["origin_classification"]
    assert oc["attestation_authority_class"] == "institution_signed"
    assert oc["counts_as_formal_independent_attestation"] == True
    assert oc["derived_counting_bucket"] == "institutional_attestation_candidate"
    assert oc["accountable_entity"]["name"] == "Test Institute"

    print("PASS institution_signed_ai_assisted")


def main():
    tests = [
        test_echo_record_with_origin_classification,
        test_verification_wrapper_with_origin_classification,
        test_institution_signed_ai_assisted,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"FAIL {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
    print("All integration tests passed!")


if __name__ == "__main__":
    main()
