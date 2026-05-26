#!/usr/bin/env python3
"""Test evidence-input schema rejects malformed high-level evidence.

HG-006: Schema must reject invalid P8 hash, out-of-range confidence, bad T8 method.
"""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "api" / "evidence-input-schema.v1.json").read_text(encoding="utf-8"))
validator = Draft202012Validator(SCHEMA)


def base_input():
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Schema Test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
        "requested_record_kind": "echo_v3_with_verification_report",
        "evidence": {
            "scripts": [],
            "hashes": [],
            "bitcoin_checks": [],
            "digital_mirror_checks": [],
            "repository_snapshot_checks": [],
            "time_anchor_checks": [],
            "chronicle_checks": [],
            "nft_checks": [],
            "physical_checks": [],
            "echo_context": {"authority_boundary_recognized": True}
        },
        "limitations": [],
        "claims_requested_by_agent": ["V8"],
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": "I performed the actions in this schema test and recorded limitations without copying example values."
        },
        "verification_session": {
            "session_id": "schema-test",
            "started_at": "2026-05-05T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["schema validation"],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        }
    }


def errors_for(obj):
    return list(validator.iter_errors(obj))


def assert_invalid(obj, expected_fragment):
    errors = errors_for(obj)
    assert errors, "Expected schema invalid input"
    text = "\n".join(e.message for e in errors).lower()
    assert expected_fragment.lower() in text, f"Expected '{expected_fragment}' in errors:\n{text}"


def assert_valid(obj):
    errors = errors_for(obj)
    assert not errors, "\n".join(e.message for e in errors)


def test_p8_invalid_hash_schema_fails():
    obj = base_input()
    obj["evidence"]["physical_checks"] = [{
        "level_evidence_type": "confidential_challenge",
        "witness_identity_or_role": "verifier",
        "report_id": "p8-report",
        "confidential_challenge": {
            "performed": True,
            "raw_confidential_data_disclosed": False,
            "boundary": "package hash only",
            "package_hash": "bad",
            "verifier_identity_or_role": "verifier"
        }
    }]
    assert_invalid(obj, "does not match")


def test_p7_confidence_out_of_range_schema_fails():
    obj = base_input()
    obj["evidence"]["physical_checks"] = [{
        "level_evidence_type": "ai_forensic",
        "model_or_tool": "tool",
        "confidence": 2,
        "flaw_analysis_method": "method",
        "witness_identity_or_role": "reviewer",
        "report_id": "p7-report"
    }]
    assert_invalid(obj, "greater than the maximum")


def test_p7_confidence_negative_schema_fails():
    obj = base_input()
    obj["evidence"]["physical_checks"] = [{
        "level_evidence_type": "ai_forensic",
        "model_or_tool": "tool",
        "confidence": -0.5,
        "flaw_analysis_method": "method",
        "witness_identity_or_role": "reviewer",
        "report_id": "p7-report"
    }]
    assert_invalid(obj, "less than the minimum")


def test_t8_bad_method_class_schema_fails():
    obj = base_input()
    obj["evidence"]["time_anchor_checks"] = [{
        "anchor_type": "star_moon_witness",
        "nonpublic_boundary": True,
        "authorized": True,
        "method_class": "guess",
        "uncertainty": "±5 minutes",
        "report_id": "t8-report",
        "verifier_identity_or_role": "reviewer"
    }]
    assert_invalid(obj, "is not one of")


def test_t8_valid_input_schema_passes():
    obj = base_input()
    obj["evidence"]["time_anchor_checks"] = [{
        "anchor_type": "star_moon_witness",
        "nonpublic_boundary": True,
        "authorized": True,
        "method_class": "astronomical_ephemeris_solver",
        "uncertainty": "±5 minutes",
        "report_id": "t8-report",
        "verifier_identity_or_role": "reviewer"
    }]
    assert_valid(obj)


def test_valid_base_input_passes():
    assert_valid(base_input())


def main():
    test_p8_invalid_hash_schema_fails()
    test_p7_confidence_out_of_range_schema_fails()
    test_p7_confidence_negative_schema_fails()
    test_t8_bad_method_class_schema_fails()
    test_t8_valid_input_schema_passes()
    test_valid_base_input_passes()
    print("PASS: evidence schema high-level constraints")


if __name__ == "__main__":
    main()
