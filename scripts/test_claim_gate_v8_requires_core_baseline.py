#!/usr/bin/env python3
"""
Test: V8 protocol requires core baseline (B2+D5+T3+C5) AND high path.
TA-REDTEAM-2026-001 regression tests.

Self-asserted P7/P8/T8 evidence with B0/D0/T0/C0 must NOT produce protocol V8.
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
        # For overclaim tests, non-zero exit is expected (FAIL_WITH_REASONS)
        stdout = proc.stdout
        return json.loads(stdout)
    finally:
        path.unlink(missing_ok=True)


def base_evidence(overrides):
    """Create a minimal valid evidence object with all required fields."""
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


def assert_not_v8(name, evidence):
    result = run_gate(base_input(evidence))
    if result.get("allowed_protocol_level") == "V8":
        print(json.dumps(result, indent=2))
        raise AssertionError(f"{name}: incorrectly allowed V8")
    print(f"PASS: {name} -> {result.get('allowed_protocol_level')}")


def main():
    # Case 1: Minimal P7 self-asserted evidence -> NOT V8
    assert_not_v8("minimal_p7_self_asserted", base_evidence({
        "physical_checks": [{
            "level_evidence_type": "ai_forensic",
            "model_or_tool": "GPT-4 Vision",
            "confidence": 0.85,
            "report_id": "self-report-001",
            "witness_identity_or_role": "AI agent"
        }]
    }))

    # Case 2: Minimal P8 self-asserted evidence -> NOT V8
    assert_not_v8("minimal_p8_self_asserted", base_evidence({
        "physical_checks": [{
            "level_evidence_type": "confidential_challenge",
            "confidential_challenge": {
                "performed": True,
                "boundary": "private",
                "raw_confidential_data_disclosed": False,
                "package_hash": "a" * 64,
                "verifier_identity_or_role": "AI agent"
            },
            "report_id": "self-report-001"
        }]
    }))

    # Case 3: T8 natural-language uncertainty -> NOT V8
    assert_not_v8("t8_intuition_uncertainty", base_evidence({
        "time_anchor_checks": [{
            "anchor_type": "star_moon_witness",
            "method_class": "astronomical_ephemeris_solver",
            "uncertainty": "about 9 minutes by intuition",
            "nonpublic_boundary": True,
            "authorized": True,
            "report_id": "self-report-001",
            "verifier_identity_or_role": "AI agent"
        }]
    }))

    # Case 4: P7 with B0/D0/T0/C0 (even valid external P7) -> NOT V8 without baseline
    assert_not_v8("p7_no_baseline", base_evidence({
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
    }))

    # Case 5: P8 with B0/D0/T0/C0 -> NOT V8
    assert_not_v8("p8_no_baseline", base_evidence({
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
    }))

    # Case 6: T8 with B0/D0/C0 -> NOT V8
    assert_not_v8("t8_no_baseline", base_evidence({
        "time_anchor_checks": [{
            "anchor_type": "star_moon_witness",
            "method_class": "astronomical_ephemeris_solver",
            "uncertainty_minutes": 9.0,
            "uncertainty_basis": "solver_output",
            "nonpublic_boundary": True,
            "authorized": True,
            "report_id": "celestial-report-001",
            "report_hash": "d" * 64,
            "signed_or_attributable_report": True,
            "verifier_identity_or_role": "qualified_external_witness"
        }]
    }))

    print("CLAIM_GATE_V8_BASELINE_OK")


if __name__ == "__main__":
    main()
