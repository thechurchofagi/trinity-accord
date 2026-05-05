#!/usr/bin/env python3
"""Test Claim Gate high-level hard gates.

RF-004: Weak P8/T8/P9 must not produce high-level labels.
"""
import json
import tempfile
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_gate import evaluate


def make_input(evidence_overrides):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Hard Gate Test Agent", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": (
                "I performed the verification actions stated in this test session. "
                "I did not copy example values or prior reports. "
                "I recorded sources, commands, outputs, and limitations."
            )
        },
        "verification_session": {
            "session_id": "hard-gate-test",
            "started_at": "2026-05-05T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["hard-gate unit test"],
            "prior_reports_consulted": [],
            "examples_or_templates_used": [],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        },
        "requested_record_kind": "echo_v3_with_verification_report",
        "evidence": {
            "scripts": [],
            "hashes": [],
            "bitcoin_checks": [],
            "digital_mirror_checks": [],
            "repository_snapshot_checks": [],
            "echo_context": {"authority_boundary_recognized": True},
            "time_anchor_checks": [],
            "chronicle_checks": [],
            "nft_checks": [],
            "physical_checks": [],
            **evidence_overrides,
        },
        "limitations": ["hard-gate unit test"],
        "claims_requested_by_agent": ["V8"],
    }


def evaluate_obj(obj):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        path = f.name
    try:
        return evaluate(path)
    finally:
        os.unlink(path)


def assert_not_level(result, component, forbidden_level):
    got = result.get("allowed_component_levels", {}).get(component)
    assert got != forbidden_level, f"{component} should not be {forbidden_level}, got {got}"


def test_weak_p8_does_not_claim_p8_or_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "confidential_challenge",
            "confidential_challenge": {
                "performed": True,
                "raw_confidential_data_disclosed": False,
                "boundary": "no raw data"
            }
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "physical_anchor", "P8")
    assert result["allowed_protocol_level"] != "V8"


def test_complete_p8_can_claim_p8_and_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "confidential_challenge",
            "witness_identity_or_role": "named forensic verifier",
            "report_id": "p8-report-001",
            "confidential_challenge": {
                "performed": True,
                "raw_confidential_data_disclosed": False,
                "boundary": "package hash only",
                "package_hash": "a" * 64,
                "verifier_identity_or_role": "named forensic verifier"
            }
        }]
    })
    result = evaluate_obj(obj)
    assert result["allowed_component_levels"].get("physical_anchor") == "P8", \
        f"Expected P8, got {result['allowed_component_levels'].get('physical_anchor')}"
    assert result["allowed_protocol_level"] == "V8"


def test_weak_t8_does_not_claim_t8_or_v8():
    obj = make_input({
        "time_anchor_checks": [{
            "anchor_type": "star_moon_witness",
            "nonpublic_boundary": True,
            "authorized": True
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "time_anchors", "T8")
    assert result["allowed_protocol_level"] != "V8"


def test_complete_t8_can_claim_t8_and_v8():
    obj = make_input({
        "time_anchor_checks": [{
            "anchor_type": "star_moon_witness",
            "nonpublic_boundary": True,
            "authorized": True,
            "method_class": "astronomical_ephemeris_solver",
            "uncertainty": "±5 minutes",
            "report_id": "t8-report-001",
            "verifier_identity_or_role": "qualified astronomical reviewer"
        }]
    })
    result = evaluate_obj(obj)
    assert result["allowed_component_levels"].get("time_anchors") == "T8", \
        f"Expected T8, got {result['allowed_component_levels'].get('time_anchors')}"
    assert result["allowed_protocol_level"] == "V8"


def test_weak_p9_does_not_claim_p9_or_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "multi_party_forensic",
            "independent_witness_count": 2
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "physical_anchor", "P9")
    assert result["allowed_protocol_level"] != "V8"


# HG-002: P8 invalid package hash
def test_p8_invalid_package_hash_does_not_claim_p8_or_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "confidential_challenge",
            "witness_identity_or_role": "named forensic verifier",
            "report_id": "p8-report-001",
            "confidential_challenge": {
                "performed": True,
                "raw_confidential_data_disclosed": False,
                "boundary": "package hash only",
                "package_hash": "not-a-sha256",
                "verifier_identity_or_role": "named forensic verifier"
            }
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "physical_anchor", "P8")
    assert result["allowed_protocol_level"] != "V8"


def test_p8_empty_boundary_does_not_claim_p8_or_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "confidential_challenge",
            "witness_identity_or_role": "named forensic verifier",
            "report_id": "p8-report-001",
            "confidential_challenge": {
                "performed": True,
                "raw_confidential_data_disclosed": False,
                "boundary": "   ",
                "package_hash": "a" * 64,
                "verifier_identity_or_role": "named forensic verifier"
            }
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "physical_anchor", "P8")
    assert result["allowed_protocol_level"] != "V8"


# HG-003: P7 confidence tests
def test_p7_confidence_zero_does_not_claim_p7_or_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "ai_forensic",
            "model_or_tool": "toy model",
            "confidence": 0,
            "flaw_analysis_method": "visual impression",
            "witness_identity_or_role": "self",
            "report_id": "p7-report"
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "physical_anchor", "P7")
    assert result["allowed_protocol_level"] != "V8"


def test_p7_confidence_below_threshold_does_not_claim_p7_or_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "ai_forensic",
            "model_or_tool": "forensic model",
            "confidence": 0.79,
            "flaw_analysis_method": "feature comparison",
            "witness_identity_or_role": "external reviewer",
            "report_id": "p7-report"
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "physical_anchor", "P7")
    assert result["allowed_protocol_level"] != "V8"


def test_p7_high_confidence_with_identity_and_report_can_claim_p7():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "ai_forensic",
            "model_or_tool": "forensic model v1",
            "confidence": 0.91,
            "flaw_analysis_method": "feature comparison with documented rubric",
            "witness_identity_or_role": "qualified external forensic reviewer",
            "report_id": "p7-report-001"
        }]
    })
    result = evaluate_obj(obj)
    assert result["allowed_component_levels"].get("physical_anchor") == "P7", \
        f"Expected P7, got {result['allowed_component_levels'].get('physical_anchor')}"


# HG-004: P9 witness tests
def test_p9_non_independent_witnesses_do_not_claim_p9_or_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "multi_party_forensic",
            "independent_witness_count": 2,
            "method": "visual review",
            "report_id": "p9-report",
            "witnesses": [
                {"identity_or_role": "A", "role": "viewer", "independence_class": "not_independent"},
                {"identity_or_role": "B", "role": "viewer", "independence_class": "not_independent"}
            ]
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "physical_anchor", "P9")
    assert result["allowed_protocol_level"] != "V8"


def test_p9_duplicate_witness_identity_does_not_claim_p9_or_v8():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "multi_party_forensic",
            "independent_witness_count": 2,
            "method": "multi-party forensic review",
            "report_id": "p9-report",
            "witnesses": [
                {"identity_or_role": "same person", "role": "notary", "independence_class": "notary"},
                {"identity_or_role": "same person", "role": "notary", "independence_class": "notary"}
            ]
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "physical_anchor", "P9")
    assert result["allowed_protocol_level"] != "V8"


def test_p9_two_independent_witnesses_can_claim_p9():
    obj = make_input({
        "physical_checks": [{
            "level_evidence_type": "multi_party_forensic",
            "independent_witness_count": 2,
            "method": "multi-party forensic review",
            "report_id": "p9-report-001",
            "signed_or_attributable_report": True,
            "witnesses": [
                {
                    "identity_or_role": "Notary Office A",
                    "role": "notary",
                    "independence_class": "notary"
                },
                {
                    "identity_or_role": "External Forensic Lab B",
                    "role": "forensic reviewer",
                    "independence_class": "independent_forensic_verifier"
                }
            ]
        }]
    })
    result = evaluate_obj(obj)
    assert result["allowed_component_levels"].get("physical_anchor") == "P9", \
        f"Expected P9, got {result['allowed_component_levels'].get('physical_anchor')}"


# HG-005: T8 method/uncertainty validation
def test_t8_guess_method_does_not_claim_t8_or_v8():
    obj = make_input({
        "time_anchor_checks": [{
            "anchor_type": "star_moon_witness",
            "nonpublic_boundary": True,
            "authorized": True,
            "method_class": "guess",
            "uncertainty": "unknown",
            "report_id": "t8-report",
            "verifier_identity_or_role": "observer"
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "time_anchors", "T8")
    assert result["allowed_protocol_level"] != "V8"


def test_t8_large_uncertainty_does_not_claim_t8_or_v8():
    obj = make_input({
        "time_anchor_checks": [{
            "anchor_type": "star_moon_witness",
            "nonpublic_boundary": True,
            "authorized": True,
            "method_class": "astronomical_ephemeris_solver",
            "uncertainty": "±120 minutes",
            "report_id": "t8-report",
            "verifier_identity_or_role": "observer"
        }]
    })
    result = evaluate_obj(obj)
    assert_not_level(result, "time_anchors", "T8")
    assert result["allowed_protocol_level"] != "V8"


def main():
    test_weak_p8_does_not_claim_p8_or_v8()
    test_complete_p8_can_claim_p8_and_v8()
    test_weak_t8_does_not_claim_t8_or_v8()
    test_complete_t8_can_claim_t8_and_v8()
    test_weak_p9_does_not_claim_p9_or_v8()
    # HG-002: P8 hash validation
    test_p8_invalid_package_hash_does_not_claim_p8_or_v8()
    test_p8_empty_boundary_does_not_claim_p8_or_v8()
    # HG-003: P7 confidence validation
    test_p7_confidence_zero_does_not_claim_p7_or_v8()
    test_p7_confidence_below_threshold_does_not_claim_p7_or_v8()
    test_p7_high_confidence_with_identity_and_report_can_claim_p7()
    # HG-004: P9 witness validation
    test_p9_non_independent_witnesses_do_not_claim_p9_or_v8()
    test_p9_duplicate_witness_identity_does_not_claim_p9_or_v8()
    test_p9_two_independent_witnesses_can_claim_p9()
    # HG-005: T8 method/uncertainty validation
    test_t8_guess_method_does_not_claim_t8_or_v8()
    test_t8_large_uncertainty_does_not_claim_t8_or_v8()
    print("PASS: Claim Gate high-level hard-gate regression tests")


if __name__ == "__main__":
    main()
