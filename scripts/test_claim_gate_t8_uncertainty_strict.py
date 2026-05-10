#!/usr/bin/env python3
"""
Test: T8 uncertainty must be structured numeric, not free-text guesses.
TA-REDTEAM-2026-001 regression tests.

Natural-language uncertainty strings must be rejected.
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


def assert_t8_rejected(name, time_check):
    """Assert that T8 path is NOT achieved (T8 component not granted)."""
    evidence = base_evidence({"time_anchor_checks": [time_check]})
    result = run_gate(base_input(evidence))
    t_level = result.get("allowed_component_levels", {}).get("time_anchors", "T0")
    # If T8 was rejected, time_anchors should be T0 (no other time anchors present)
    if t_level == "T8":
        print(json.dumps(result, indent=2))
        raise AssertionError(f"{name}: T8 incorrectly granted for free-text uncertainty")
    print(f"PASS: {name} -> time_anchors={t_level}")


def main():
    base_t8 = {
        "anchor_type": "star_moon_witness",
        "method_class": "astronomical_ephemeris_solver",
        "nonpublic_boundary": True,
        "authorized": True,
        "report_id": "celestial-report-001",
        "report_hash": "b" * 64,
        "signed_or_attributable_report": True,
        "verifier_identity_or_role": "qualified_external_witness"
    }

    # All these free-text uncertainty strings must be rejected
    bad_uncertainties = [
        "about 9 minutes by intuition",
        "approx 5 minutes",
        "approximately 5 min",
        "roughly 8m",
        "\u00b19 maybe",
        "not measured, probably 7 minutes",
        "estimated by eye at 6 minutes",
        "about 3 minutes",
        "guess of 4 minutes",
        "roughly 10m by eye",
    ]

    for bad_text in bad_uncertainties:
        check = {**base_t8, "uncertainty": bad_text}
        assert_t8_rejected(f"t8_bad_uncertainty_{bad_text[:20].strip()}", check)

    # Structured numeric uncertainty must still work (but not V8 without baseline)
    good_check = {
        **base_t8,
        "uncertainty_minutes": 9.0,
        "uncertainty_basis": "solver_output",
    }
    evidence = base_evidence({"time_anchor_checks": [good_check]})
    result = run_gate(base_input(evidence))
    t_level = result.get("allowed_component_levels", {}).get("time_anchors", "T0")
    if t_level != "T8":
        print(json.dumps(result, indent=2))
        raise AssertionError(f"structured numeric uncertainty should grant T8 component, got {t_level}")
    # But protocol must NOT be V8 without baseline
    if result.get("allowed_protocol_level") == "V8":
        print(json.dumps(result, indent=2))
        raise AssertionError("structured T8 should not produce V8 protocol without baseline")
    print(f"PASS: structured_numeric_t8 -> time_anchors={t_level}, protocol={result.get('allowed_protocol_level')}")

    print("CLAIM_GATE_T8_UNCERTAINTY_STRICT_OK")


if __name__ == "__main__":
    main()
