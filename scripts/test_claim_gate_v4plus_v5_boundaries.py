#!/usr/bin/env python3
"""VR-006: V4/V4+/V5 boundary regression tests."""
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
        "agent": {"name": "V4+/V5 Boundary Test Agent", "model_or_system": "test"},
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
            "declaration_text": "Unit test declaration with authority boundary preserved."
        },
        "verification_session": {
            "session_id": "v4plus-v5-boundary-test",
            "started_at": "2026-05-05T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["unit test"],
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


def add_official_script_pass(obj):
    obj["evidence"]["scripts"] = [{
        "path": "downloads/verify.py",
        "official": True,
        "source_reviewed": True,
        "executed": True,
        "exit_code": 0,
        "command": "python3 downloads/verify.py",
        "environment": "unit-test",
        "output_summary": "pass",
        "result": "PASS"
    }]


def test_official_scripts_only_do_not_claim_v4plus():
    obj = base_input(["V4+"])
    add_official_script_pass(obj)
    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] != "V4+", f"Official scripts only should not reach V4+: {result}"


def test_official_script_pass_does_not_claim_v5():
    obj = base_input(["V5"])
    add_official_script_pass(obj)
    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] != "V5", f"Official script pass should not reach V5: {result}"


def test_one_valid_hash_does_not_claim_v5():
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
    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] != "V5", f"One valid hash should not reach V5: {result}"


def main():
    test_official_scripts_only_do_not_claim_v4plus()
    test_official_script_pass_does_not_claim_v5()
    test_one_valid_hash_does_not_claim_v5()
    print("PASS: V4+/V5 boundary tests")


if __name__ == "__main__":
    main()
