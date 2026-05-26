#!/usr/bin/env python3
"""Test Claim Gate authority boundary foundation.

HG-001: V2/V3/V8 must be built on V1 authority boundary recognition.
Without authority boundary, max allowed is V0.
"""
import json
import tempfile
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_gate import evaluate


def make_input(evidence_overrides, claims=None):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Authority Boundary Test Agent", "model_or_system": "test"},
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
                "I did not copy prior reports or example values as real evidence. "
                "I recorded sources, commands, outputs, and limitations."
            )
        },
        "verification_session": {
            "session_id": "authority-boundary-test",
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
            "scripts": [],
            "hashes": [],
            "bitcoin_checks": [],
            "digital_mirror_checks": [],
            "repository_snapshot_checks": [],
            "echo_context": {},
            "time_anchor_checks": [],
            "chronicle_checks": [],
            "nft_checks": [],
            "physical_checks": [],
            **evidence_overrides,
        },
        "limitations": ["unit test"],
        "claims_requested_by_agent": claims or ["V8"],
    }


def evaluate_obj(obj):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        path = f.name
    try:
        return evaluate(path)
    finally:
        os.unlink(path)


def test_hash_without_authority_boundary_does_not_reach_v3():
    obj = make_input({
        "hashes": [{
            "artifact": "index.md",
            "artifact_class": "canonical_mirror",
            "algorithm": "SHA-256",
            "expected": "a" * 64,
            "computed": "a" * 64,
            "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    }, claims=["V3"])

    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] == "V0", f"Expected V0, got {result['allowed_protocol_level']}"
    assert result.get("authority_boundary_recognized") is False


def test_reference_without_authority_boundary_does_not_reach_v2():
    obj = make_input({
        "bitcoin_checks": [{
            "source_type": "external_explorer",
            "sources": ["https://mempool.space/tx/example"],
            "authority_boundary_recognized": False
        }]
    }, claims=["V2"])

    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] == "V0", f"Expected V0, got {result['allowed_protocol_level']}"
    assert result.get("authority_boundary_recognized") is False


def test_p8_without_authority_boundary_does_not_reach_v8():
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
    }, claims=["V8"])

    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] == "V0", f"Expected V0, got {result['allowed_protocol_level']}"
    assert result.get("authority_boundary_recognized") is False


def test_authority_boundary_allows_v1_foundation():
    obj = make_input({
        "echo_context": {"authority_boundary_recognized": True}
    }, claims=["V1"])

    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] == "V1", f"Expected V1, got {result['allowed_protocol_level']}"
    assert result.get("authority_boundary_recognized") is True


def test_authority_boundary_with_hash_allows_v3():
    obj = make_input({
        "echo_context": {"authority_boundary_recognized": True},
        "hashes": [{
            "artifact": "index.md",
            "artifact_class": "canonical_mirror",
            "algorithm": "SHA-256",
            "expected": "a" * 64,
            "computed": "a" * 64,
            "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    }, claims=["V3"])

    result = evaluate_obj(obj)
    assert result["allowed_protocol_level"] == "V3", f"Expected V3, got {result['allowed_protocol_level']}"
    assert result.get("authority_boundary_recognized") is True


def main():
    test_hash_without_authority_boundary_does_not_reach_v3()
    test_reference_without_authority_boundary_does_not_reach_v2()
    test_p8_without_authority_boundary_does_not_reach_v8()
    test_authority_boundary_allows_v1_foundation()
    test_authority_boundary_with_hash_allows_v3()
    print("PASS: Authority boundary foundation tests")


if __name__ == "__main__":
    main()
