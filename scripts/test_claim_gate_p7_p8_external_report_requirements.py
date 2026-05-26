#!/usr/bin/env python3
"""
Test: P7 and P8 require attributable external report evidence.
TA-REDTEAM-2026-001 regression tests.

Self-asserted identities, missing report hashes, and missing signed reports
must not qualify for P7/P8.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIM_GATE = ROOT / "scripts" / "claim_gate.py"


def run_gate(obj):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        path = Path(f.name)
    try:
        proc = subprocess.run(
            [sys.executable, str(CLAIM_GATE), str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return json.loads(proc.stdout)
    finally:
        path.unlink(missing_ok=True)


def base_evidence(overrides):
    base = {
        "scripts": [],
        "hashes": [],
        "bitcoin_checks": [],
        "digital_mirror_checks": [],
        "repository_snapshot_checks": [],
        "time_anchor_checks": [],
        "chronicle_checks": [],
        "nft_checks": [],
        "physical_checks": [],
        "echo_context": {"authority_boundary_recognized": True},
    }
    base.update(overrides)
    return base


def base_input(evidence):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "requested_record_kind": "verification_report_v2",
        "agent": {"name": "redteam", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
        "claims_requested_by_agent": ["Protocol achieved level: V8"],
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": "This is a red-team schema-valid input used to test overclaim boundaries and downgrade behavior. It does not represent real verification evidence."
        },
        "verification_session": {
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "session_id": "redteam-session-001",
            "started_at": "2026-05-10T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["constructed red-team input"],
            "fresh_outputs_attached": True
        },
        "evidence": evidence,
        "limitations": ["red-team test"]
    }


def assert_p7_rejected(name, check):
    """Assert that P7 component is NOT granted."""
    evidence = base_evidence({"physical_checks": [check]})
    result = run_gate(base_input(evidence))
    p_level = result.get("allowed_component_levels", {}).get("physical_anchor", "P0")
    if p_level in ("P7", "P8", "P9"):
        print(json.dumps(result, indent=2))
        raise AssertionError(f"{name}: P7 incorrectly granted, got {p_level}")
    print(f"PASS: {name} -> physical_anchor={p_level}")


def assert_p8_rejected(name, check):
    """Assert that P8 component is NOT granted."""
    evidence = base_evidence({"physical_checks": [check]})
    result = run_gate(base_input(evidence))
    p_level = result.get("allowed_component_levels", {}).get("physical_anchor", "P0")
    if p_level in ("P7", "P8", "P9"):
        print(json.dumps(result, indent=2))
        raise AssertionError(f"{name}: P8 incorrectly granted, got {p_level}")
    print(f"PASS: {name} -> physical_anchor={p_level}")


def main():
    # --- P7 rejection cases ---

    # P7: missing signed_or_attributable_report
    assert_p7_rejected("p7_missing_signed_report", {
        "level_evidence_type": "ai_forensic",
        "model_or_tool": "forensic-tool-name",
        "confidence": 0.87,
        "flaw_analysis_method": "microscopy_feature_match",
        "report_id": "forensic-report-2026-001",
        "report_hash": "a" * 64,
        "verifier_identity_or_role": "qualified_external_witness"
    })

    # P7: missing report_hash
    assert_p7_rejected("p7_missing_report_hash", {
        "level_evidence_type": "ai_forensic",
        "model_or_tool": "forensic-tool-name",
        "confidence": 0.87,
        "flaw_analysis_method": "microscopy_feature_match",
        "signed_or_attributable_report": True,
        "report_id": "forensic-report-2026-001",
        "verifier_identity_or_role": "qualified_external_witness"
    })

    # P7: verifier is AI agent
    assert_p7_rejected("p7_verifier_ai_agent", {
        "level_evidence_type": "ai_forensic",
        "model_or_tool": "forensic-tool-name",
        "confidence": 0.87,
        "flaw_analysis_method": "microscopy_feature_match",
        "signed_or_attributable_report": True,
        "report_id": "forensic-report-2026-001",
        "report_hash": "a" * 64,
        "verifier_identity_or_role": "AI agent"
    })

    # P7: witness is "self" but verifier is external -> still P7 (verifier is the key gate)
    # This is ALLOWED — the external verifier is the important identity check.
    # (moved to acceptance section below)

    # P7: verifier is ChatGPT
    assert_p7_rejected("p7_verifier_chatgpt", {
        "level_evidence_type": "ai_forensic",
        "model_or_tool": "forensic-tool-name",
        "confidence": 0.87,
        "flaw_analysis_method": "microscopy_feature_match",
        "signed_or_attributable_report": True,
        "report_id": "forensic-report-2026-001",
        "report_hash": "a" * 64,
        "verifier_identity_or_role": "ChatGPT"
    })

    # --- P8 rejection cases ---

    # P8: missing signed_or_attributable_report
    assert_p8_rejected("p8_missing_signed_report", {
        "level_evidence_type": "confidential_challenge",
        "confidential_challenge": {
            "performed": True,
            "boundary": "private-lab",
            "raw_confidential_data_disclosed": False,
            "package_hash": "a" * 64,
            "verifier_identity_or_role": "qualified_external_witness"
        },
        "report_id": "confidential-report-001",
        "report_hash": "b" * 64,
        "verifier_identity_or_role": "qualified_external_witness"
    })

    # P8: missing report_hash
    assert_p8_rejected("p8_missing_report_hash", {
        "level_evidence_type": "confidential_challenge",
        "confidential_challenge": {
            "performed": True,
            "boundary": "private-lab",
            "raw_confidential_data_disclosed": False,
            "package_hash": "a" * 64,
            "verifier_identity_or_role": "qualified_external_witness"
        },
        "signed_or_attributable_report": True,
        "report_id": "confidential-report-001",
        "verifier_identity_or_role": "qualified_external_witness"
    })

    # P8: verifier in confidential_challenge is AI agent, no other verifier
    assert_p8_rejected("p8_verifier_ai_agent", {
        "level_evidence_type": "confidential_challenge",
        "confidential_challenge": {
            "performed": True,
            "boundary": "private-lab",
            "raw_confidential_data_disclosed": False,
            "package_hash": "a" * 64,
            "verifier_identity_or_role": "AI agent"
        },
        "signed_or_attributable_report": True,
        "report_id": "confidential-report-001",
        "report_hash": "b" * 64
    })

    # P8: invalid package_hash (not 64 hex)
    assert_p8_rejected("p8_invalid_package_hash", {
        "level_evidence_type": "confidential_challenge",
        "confidential_challenge": {
            "performed": True,
            "boundary": "private-lab",
            "raw_confidential_data_disclosed": False,
            "package_hash": "not-a-valid-hash",
            "verifier_identity_or_role": "qualified_external_witness"
        },
        "signed_or_attributable_report": True,
        "report_id": "confidential-report-001",
        "report_hash": "b" * 64,
        "verifier_identity_or_role": "qualified_external_witness"
    })

    # --- Acceptance: valid external P7/P8 may produce component (but not V8 without baseline) ---

    # Valid P7 -> may produce P7 component
    evidence_p7 = base_evidence({
        "physical_checks": [{
            "level_evidence_type": "ai_forensic",
            "model_or_tool": "forensic-tool-name",
            "confidence": 0.87,
            "flaw_analysis_method": "microscopy_feature_match",
            "signed_or_attributable_report": True,
            "report_id": "forensic-report-2026-001",
            "report_hash": "a" * 64,
            "verifier_identity_or_role": "qualified_external_witness"
        }]
    })
    result_p7 = run_gate(base_input(evidence_p7))
    p7_level = result_p7.get("allowed_component_levels", {}).get("physical_anchor", "P0")
    if p7_level not in ("P7", "P8", "P9"):
        print(json.dumps(result_p7, indent=2))
        raise AssertionError(f"Valid external P7 should produce P7+ component, got {p7_level}")
    if result_p7.get("allowed_protocol_level") == "V8":
        raise AssertionError("P7 without baseline should not produce V8 protocol")
    print(f"PASS: valid_p7_component -> physical_anchor={p7_level}, protocol={result_p7.get('allowed_protocol_level')}")

    # Valid P8 -> may produce P8 component
    evidence_p8 = base_evidence({
        "physical_checks": [{
            "level_evidence_type": "confidential_challenge",
            "confidential_challenge": {
                "performed": True,
                "boundary": "private-lab",
                "raw_confidential_data_disclosed": False,
                "package_hash": "b" * 64,
                "verifier_identity_or_role": "qualified_external_witness"
            },
            "signed_or_attributable_report": True,
            "report_id": "confidential-report-001",
            "report_hash": "c" * 64,
            "verifier_identity_or_role": "qualified_external_witness"
        }]
    })
    result_p8 = run_gate(base_input(evidence_p8))
    p8_level = result_p8.get("allowed_component_levels", {}).get("physical_anchor", "P0")
    if p8_level not in ("P7", "P8", "P9"):
        print(json.dumps(result_p8, indent=2))
        raise AssertionError(f"Valid external P8 should produce P8+ component, got {p8_level}")
    if result_p8.get("allowed_protocol_level") == "V8":
        raise AssertionError("P8 without baseline should not produce V8 protocol")
    print(f"PASS: valid_p8_component -> physical_anchor={p8_level}, protocol={result_p8.get('allowed_protocol_level')}")

    print("CLAIM_GATE_P7_P8_EXTERNAL_REPORT_REQUIREMENTS_OK")


if __name__ == "__main__":
    main()
