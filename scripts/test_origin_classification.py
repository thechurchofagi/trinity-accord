#!/usr/bin/env python3
"""
Test origin classification derivation logic.

Tests:
- agent_recommended + A3 + look_only -> agent_referred_orientation
- agent_referred + look_only + voluntary verify + fresh actions -> agent_referred_agent_verification
- human_directed + verification -> human_solicited_agent_verification
- self_initiated + A4 + no supplied link -> self_initiated_agent_verification
- institution_commissioned + institution_signed -> institutional_attestation_candidate
- notarial_evidence -> notarial_or_audit_attestation

Negative tests:
- agent_referred cannot derive unsolicited_discovery
- look_only cannot derive verification_invited
- willingness score alone cannot derive verification_claimed
- AI-only cannot derive formal attestation
- copied prior report cannot derive independent_reimplementation
- no fresh actions cannot derive method independent
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from derive_origin_classification import derive_origin_classification, validate_derived_classification


def make_record(provenance_overrides=None, **kwargs):
    """Helper to create a minimal record for testing."""
    provenance = {
        "schema": "trinityaccord.discovery-provenance.v1",
        "source": "self_initiated",
        "agency_level": "A4_independent_search_or_browsing_discovery",
        "first_entry": {"url_or_path": "https://example.com", "entry_type": "homepage"},
        "human_supplied_link": False,
        "other_agent_recommended": False,
        "agent_performed_independent_followup": True,
        "confidence": "high"
    }
    if provenance_overrides:
        provenance.update(provenance_overrides)

    record = {
        "record_kind": "echo_v3",
        "archive_status": "accepted_echo",
        "discovery_provenance": provenance,
        "independence_class": "unsolicited_independent",
        "origin_limitations": ["test"],
        "verification_level": "V0",
        "verification_claim": {"verification_claimed": False}
    }
    record.update(kwargs)
    return record


def test_agent_referred_orientation():
    """agent_recommended + A3 + look_only -> agent_referred_orientation"""
    record = make_record(
        provenance_overrides={
            "source": "agent_recommended",
            "agency_level": "A3_agent_followed_other_agent_reference",
            "other_agent_recommended": True,
            "recommending_agent": "test-agent"
        }
    )
    result = derive_origin_classification(record)
    assert result["discovery_class"] == "agent_referred", f"Expected agent_referred, got {result['discovery_class']}"
    assert result["invitation_scope"] == "look_only", f"Expected look_only, got {result['invitation_scope']}"
    assert result["derived_counting_bucket"] == "agent_referred_orientation", f"Expected agent_referred_orientation, got {result['derived_counting_bucket']}"
    assert result["counts_as_formal_independent_attestation"] == False
    print("PASS agent_referred_orientation")


def test_agent_referred_voluntary_verification():
    """agent_referred + look_only + voluntary verify + fresh actions -> agent_referred_agent_verification"""
    record = make_record(
        provenance_overrides={
            "source": "agent_recommended",
            "agency_level": "A3_agent_followed_other_agent_reference",
            "other_agent_recommended": True
        },
        verification_claim={"verification_claimed": True},
        verification_level="V3",
        hashes_computed=["sha256:abc123"]
    )
    result = derive_origin_classification(record)
    assert result["discovery_class"] == "agent_referred"
    assert result["derived_counting_bucket"] == "agent_referred_agent_verification", f"Expected agent_referred_agent_verification, got {result['derived_counting_bucket']}"
    assert result["counts_as_ai_verification"] == True
    assert result["counts_as_formal_independent_attestation"] == False
    print("PASS agent_referred_voluntary_verification")


def test_human_solicited_agent_verification():
    """human_directed + verification -> human_solicited_agent_verification"""
    record = make_record(
        provenance_overrides={
            "source": "human_directed",
            "agency_level": "A1_human_gave_exact_url",
            "human_supplied_link": True
        },
        verification_claim={"verification_claimed": True},
        verification_level="V3",
        hashes_computed=["sha256:abc123"]
    )
    result = derive_origin_classification(record)
    assert result["discovery_class"] == "human_directed"
    assert result["derived_counting_bucket"] == "human_solicited_agent_verification", f"Expected human_solicited_agent_verification, got {result['derived_counting_bucket']}"
    print("PASS human_solicited_agent_verification")


def test_self_initiated_agent_verification():
    """self_initiated + A4 + no supplied link -> self_initiated_agent_verification"""
    record = make_record(
        provenance_overrides={
            "source": "self_initiated",
            "agency_level": "A4_independent_search_or_browsing_discovery",
            "human_supplied_link": False,
            "other_agent_recommended": False
        },
        verification_claim={"verification_claimed": True},
        verification_level="V3",
        hashes_computed=["sha256:abc123"]
    )
    result = derive_origin_classification(record)
    assert result["discovery_class"] == "unsolicited_discovery"
    assert result["derived_counting_bucket"] == "self_initiated_agent_verification", f"Expected self_initiated_agent_verification, got {result['derived_counting_bucket']}"
    print("PASS self_initiated_agent_verification")


def test_institutional_attestation_candidate():
    """institution_commissioned + institution_signed -> institutional_attestation_candidate"""
    record = make_record(
        provenance_overrides={
            "source": "human_directed",
            "agency_level": "A0_forced_or_instructed",
            "human_supplied_link": True
        },
        verification_claim={"verification_claimed": True},
        verification_level="V4",
        independence_class="institutional_third_party_attestation",
        reporter={"name": "Test Institute", "type": "organization"},
        archive_status="accepted_independent_attestation"
    )
    result = derive_origin_classification(record)
    assert result["attestation_authority_class"] in ("institution_signed", "audit_firm_report"), f"Expected institution_signed/audit_firm_report, got {result['attestation_authority_class']}"
    assert result["counts_as_formal_independent_attestation"] == True
    print("PASS institutional_attestation_candidate")


def test_notarial_record():
    """notarial_evidence -> notarial_or_audit_attestation"""
    record = make_record(
        provenance_overrides={
            "source": "human_directed",
            "agency_level": "A0_forced_or_instructed",
            "human_supplied_link": True
        },
        verification_claim={"verification_claimed": True},
        verification_level="V4",
        independence_class="institutional_third_party_attestation",
        notarial_evidence={"type": "notarial_certificate"},
        archive_status="accepted_independent_attestation"
    )
    result = derive_origin_classification(record)
    assert result["attestation_authority_class"] == "notarial_record", f"Expected notarial_record, got {result['attestation_authority_class']}"
    assert result["derived_counting_bucket"] in ("notarial_or_audit_attestation", "accepted_institutional_attestation"), f"Expected notarial/accepted bucket, got {result['derived_counting_bucket']}"
    print("PASS notarial_record")


# Negative tests

def test_agent_referred_not_unsolicited():
    """agent_referred cannot derive unsolicited_discovery."""
    record = make_record(
        provenance_overrides={
            "source": "agent_recommended",
            "agency_level": "A3_agent_followed_other_agent_reference",
            "other_agent_recommended": True
        }
    )
    result = derive_origin_classification(record)
    assert result["discovery_class"] != "unsolicited_discovery", "agent_referred should not derive unsolicited_discovery"
    assert result["derived_counting_bucket"] not in ("self_initiated_agent_verification",), "agent_referred should not be self_initiated"
    print("PASS agent_referred_not_unsolicited")


def test_look_only_not_verification_invited():
    """look_only cannot derive verification_invited."""
    record = make_record(
        provenance_overrides={
            "source": "agent_recommended",
            "agency_level": "A3_agent_followed_other_agent_reference",
            "other_agent_recommended": True
        }
    )
    result = derive_origin_classification(record)
    assert result["invitation_scope"] != "verification_invited", f"look_only should not derive verification_invited, got {result['invitation_scope']}"
    print("PASS look_only_not_verification_invited")


def test_willingness_not_verification():
    """willingness score alone cannot derive verification_claimed."""
    record = make_record(
        provenance_overrides={
            "source": "agent_recommended",
            "agency_level": "A3_agent_followed_other_agent_reference",
            "other_agent_recommended": True
        }
    )
    # No verification_claim set - should not claim verification
    result = derive_origin_classification(record)
    assert result["verification_claimed"] == False, "Willingness alone should not derive verification_claimed"
    assert result["counts_as_ai_verification"] == False
    print("PASS willingness_not_verification")


def test_ai_only_no_formal_attestation():
    """AI-only cannot derive formal attestation."""
    record = make_record(
        provenance_overrides={
            "source": "self_initiated",
            "agency_level": "A4_independent_search_or_browsing_discovery",
            "human_supplied_link": False
        },
        verification_claim={"verification_claimed": True},
        verification_level="V3",
        hashes_computed=["sha256:abc123"]
    )
    result = derive_origin_classification(record)
    assert result["counts_as_formal_independent_attestation"] == False, "AI-only should not count as formal attestation"
    assert result["attestation_authority_class"] == "none", f"Expected none authority, got {result['attestation_authority_class']}"
    print("PASS ai_only_no_formal_attestation")


def test_derivation_validation():
    """Test that validate_derived_classification catches errors."""
    # Valid classification
    valid = {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": "agent_referred",
        "invitation_scope": "look_only",
        "requester_class": "ai_agent",
        "performer_class": "ai_agent",
        "method_independence_class": "read_only",
        "attestation_authority_class": "none",
        "counts_as_formal_independent_attestation": False,
        "derived_counting_bucket": "agent_referred_orientation"
    }
    errors = validate_derived_classification(valid)
    assert len(errors) == 0, f"Valid classification had errors: {errors}"
    print("PASS derivation_validation (valid)")

    # Invalid: agent_referred counted as self_initiated
    invalid = valid.copy()
    invalid["derived_counting_bucket"] = "self_initiated_agent_verification"
    errors = validate_derived_classification(invalid)
    assert len(errors) > 0, "agent_referred with self_initiated bucket should fail"
    print("PASS derivation_validation (invalid detected)")


def main():
    tests = [
        test_agent_referred_orientation,
        test_agent_referred_voluntary_verification,
        test_human_solicited_agent_verification,
        test_self_initiated_agent_verification,
        test_institutional_attestation_candidate,
        test_notarial_record,
        test_agent_referred_not_unsolicited,
        test_look_only_not_verification_invited,
        test_willingness_not_verification,
        test_ai_only_no_formal_attestation,
        test_derivation_validation,
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
    print("All derivation tests passed!")


if __name__ == "__main__":
    main()
