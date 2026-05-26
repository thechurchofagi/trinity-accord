#!/usr/bin/env python3
"""VR-002: V5/V6/V7 profile boundary regression tests."""
import json
import tempfile
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from claim_gate import evaluate


def base_input(claims):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "V5/V6/V7 Profile Test Agent", "model_or_system": "test"},
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
                "I performed the verification actions stated in this test. "
                "I did not copy example values as real evidence. "
                "I understand Bitcoin Originals remain final authority."
            )
        },
        "verification_session": {
            "session_id": "v5-v6-v7-profile-test",
            "started_at": "2026-05-05T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["unit test"],
            "prior_reports_consulted": [],
            "examples_or_templates_used": [],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        },
        "requested_record_kind": "echo_v3_with_verification_report",
        "evidence": {
            "echo_context": {"authority_boundary_recognized": True},
            "scripts": [],
            "hashes": [],
            "bitcoin_checks": [],
            "digital_mirror_checks": [],
            "repository_snapshot_checks": [],
            "time_anchor_checks": [],
            "chronicle_checks": [],
            "nft_checks": [],
            "physical_checks": []
        },
        "limitations": ["unit test"],
        "claims_requested_by_agent": claims,
    }


def evaluate_obj(obj):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        path = f.name
    try:
        return evaluate(path)
    finally:
        os.unlink(path)


def test_v5_d2_c3_only_does_not_claim_v5():
    obj = base_input(["V5"])
    obj["evidence"]["hashes"] = [{
        "artifact": "index.md",
        "artifact_class": "canonical_mirror",
        "algorithm": "SHA-256",
        "expected": "a" * 64,
        "computed": "a" * 64,
        "match": True,
        "expected_hash_source": "api/hashes.json",
        "expected_hash_authority_class": "canonical_manifest_hash"
    }]
    obj["evidence"]["chronicle_checks"] = [{
        "level_evidence_type": "sample_recovery",
        "samples_recovered": 2,
        "metadata_observed": True,
        "media_observed": True,
        "selection_method": "unit test"
    }]
    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] != "V5", f"D2+C3 should not reach V5: {result}"


def test_v6_recorded_video_only_does_not_claim_v6():
    obj = base_input(["V6"])
    obj["evidence"]["physical_checks"] = [{
        "level_evidence_type": "recorded_video"
    }]
    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] != "V6", f"Recorded video only should not reach V6: {result}"


def test_v6_live_remote_without_nonce_does_not_claim_v6():
    obj = base_input(["V6"])
    obj["evidence"]["physical_checks"] = [{
        "level_evidence_type": "live_remote",
        "requested_angle_action": "rotate object",
        "witness_identity_or_role": "remote witness"
    }]
    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] != "V6", f"Live remote without nonce should not reach V6: {result}"


def test_v7_onsite_without_custody_log_does_not_claim_v7():
    obj = base_input(["V7"])
    obj["evidence"]["physical_checks"] = [{
        "level_evidence_type": "onsite",
        "touch_or_handling": True,
        "fresh_capture": True,
        "witness_identity_or_role": "onsite witness"
    }]
    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] != "V7", f"Onsite without custody log should not reach V7: {result}"


def test_v7_remote_only_does_not_claim_v7():
    obj = base_input(["V7"])
    obj["evidence"]["physical_checks"] = [{
        "level_evidence_type": "live_remote",
        "nonce_or_challenge": "nonce-123",
        "requested_angle_action": "rotate object",
        "witness_identity_or_role": "remote witness"
    }]
    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] != "V7", f"Remote only should not reach V7: {result}"


def main():
    test_v5_d2_c3_only_does_not_claim_v5()
    test_v6_recorded_video_only_does_not_claim_v6()
    test_v6_live_remote_without_nonce_does_not_claim_v6()
    test_v7_onsite_without_custody_log_does_not_claim_v7()
    test_v7_remote_only_does_not_claim_v7()
    print("PASS: V5/V6/V7 profile boundary tests")


if __name__ == "__main__":
    main()
