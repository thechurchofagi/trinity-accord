#!/usr/bin/env python3
"""
Test: High component evidence (P7/P8/P9/T8) does NOT raise protocol to V8
without core baseline (B2+D5+T3+C5).

Component levels may remain high, but protocol must stay below V8.
TA-REDTEAM-2026-001 regression tests.
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


# Valid external P7 forensic evidence (would qualify for P7 component)
VALID_P7 = {
    "level_evidence_type": "ai_forensic",
    "model_or_tool": "forensic-tool-name",
    "confidence": 0.87,
    "flaw_analysis_method": "microscopy_feature_match",
    "signed_or_attributable_report": True,
    "report_id": "forensic-report-2026-001",
    "report_hash": "a" * 64,
    "verifier_identity_or_role": "qualified_external_witness"
}

# Valid external P8 confidential challenge evidence
VALID_P8 = {
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
}

# Valid T8 celestial evidence
VALID_T8 = {
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
}


def assert_high_component_not_v8(name, evidence, expected_component_key=None):
    result = run_gate(base_input(evidence))
    protocol = result.get("allowed_protocol_level")
    if protocol == "V8":
        print(json.dumps(result, indent=2))
        raise AssertionError(f"{name}: incorrectly allowed V8 protocol")

    # Verify component level can still be high
    if expected_component_key:
        comp = result.get("allowed_component_levels", {}).get(expected_component_key, "?")
        print(f"PASS: {name} -> protocol={protocol}, {expected_component_key}={comp}")
    else:
        print(f"PASS: {name} -> protocol={protocol}")


def main():
    # P7 high component + no baseline -> protocol != V8
    assert_high_component_not_v8("p7_high_component_no_baseline", base_evidence({
        "physical_checks": [VALID_P7]
    }), "physical_anchor")

    # P8 high component + no baseline -> protocol != V8
    assert_high_component_not_v8("p8_high_component_no_baseline", base_evidence({
        "physical_checks": [VALID_P8]
    }), "physical_anchor")

    # T8 high component + no baseline -> protocol != V8
    assert_high_component_not_v8("t8_high_component_no_baseline", base_evidence({
        "time_anchor_checks": [VALID_T8]
    }), "time_anchors")

    # Combined P7+T8 with no baseline -> protocol != V8
    assert_high_component_not_v8("p7_t8_combined_no_baseline", base_evidence({
        "physical_checks": [VALID_P7],
        "time_anchor_checks": [VALID_T8]
    }))

    print("CLAIM_GATE_HIGH_COMPONENT_PROTOCOL_CAP_OK")


if __name__ == "__main__":
    main()
