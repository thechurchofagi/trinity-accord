#!/usr/bin/env python3
"""Test that P8 confidential challenge validator requires complete metadata.

RF-002: No weak high-level evidence may produce high-level labels.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_validator(obj):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        path = f.name

    try:
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_agent_submission.py"), path],
            text=True,
            capture_output=True,
        )
    finally:
        Path(path).unlink(missing_ok=True)


def base_report():
    return {
        "schema_version": "trinityaccord.verification-report.v2",
        "record_kind": "verification_report_v2",
        "report_id": "p8-test-report",
        "reporter": {"name": "Test", "type": "ai_agent"},
        "discovery_provenance": {"solicited": True},
        "protocol_level_claimed": "V8",
        "component_findings": [
            {
                "component": "physical_anchor",
                "level_claimed": "P8",
                "target_id": "p8-physical-target",
                "data_sources": ["confidential forensic package"],
                "access_paths": ["package_hash_only"],
                "method": "confidential forensic analysis",
                "evidence": [{"type": "confidential_package", "verified": True}],
                "limitations": ["test only"],
                "claims_not_made": ["not an endorsement"]
            }
        ],
        "protocol_profile_check": {
            "profile_source": "/api/protocol-verification-profiles.json",
            "hard_gates_satisfied": True,
            "minimum_components_satisfied": True,
            "recommended_components_satisfied": "true",
            "underreported_items": [],
            "incompatible_claims": []
        },
        "data_sources_used": ["confidential forensic package"],
        "access_paths_used": ["package_hash_only"],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [],
        "samples_checked": 1,
        "physical_evidence_reviewed": {"confidential_package": True},
        "confidential_challenge": {
            "performed": True,
            "confidentiality_boundary": "public report exposes only package hash",
            "raw_confidential_data_disclosed": False,
            "package_hash": "a" * 64,
            "verifier_identity_or_role": "named forensic verifier",
            "report_id": "p8-report-001",
            "public_disclosure": "package_hash_only"
        },
        "celestial_witness": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True,
        "integrity_boundary": {
            "agent_integrity_declaration_present": True,
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_actions_claimed": ["confidential forensic verification"],
            "fresh_outputs_attached": True,
        },
        "script_audit": {},
        "all_scripts_green": False,
        "generated_by": {
            "tool": "scripts/build_verification_report_from_evidence.py",
            "builder_version": "test-0.1",
            "validation_result": "PASS",
            "claim_gate_output": "{}",
            "evidence_input": "{}",
            "generated_at_utc": "2026-05-05T00:00:00Z",
            "validation_command": "python3 scripts/validate_agent_submission.py",
        },
    }


def assert_fails_when(mutator, expected_text):
    obj = base_report()
    mutator(obj)
    proc = run_validator(obj)
    assert proc.returncode != 0, f"Expected failure but got returncode 0\nstdout: {proc.stdout}\nstderr: {proc.stderr}"
    combined = (proc.stdout + proc.stderr).lower()
    assert expected_text.lower() in combined, f"Expected '{expected_text}' in output:\n{combined}"


def test_p8_valid_fields_pass():
    proc = run_validator(base_report())
    assert proc.returncode == 0, f"Expected pass but got:\nstdout: {proc.stdout}\nstderr: {proc.stderr}"


def test_p8_missing_boundary_fails():
    assert_fails_when(
        lambda o: o["confidential_challenge"].update({"confidentiality_boundary": ""}),
        "confidentiality_boundary"
    )


def test_p8_raw_data_disclosed_fails():
    assert_fails_when(
        lambda o: o["confidential_challenge"].update({"raw_confidential_data_disclosed": True}),
        "raw_confidential_data_disclosed"
    )


def test_p8_invalid_package_hash_fails():
    assert_fails_when(
        lambda o: o["confidential_challenge"].update({"package_hash": "not-a-hash"}),
        "package_hash"
    )


def test_p8_missing_verifier_fails():
    assert_fails_when(
        lambda o: o["confidential_challenge"].update({"verifier_identity_or_role": ""}),
        "verifier_identity_or_role"
    )


def test_p8_missing_report_reference_fails():
    def mutate(o):
        o["confidential_challenge"]["report_id"] = ""
        o["confidential_challenge"]["report_path"] = ""
    assert_fails_when(mutate, "report_id or report_path")


def main():
    test_p8_valid_fields_pass()
    test_p8_missing_boundary_fails()
    test_p8_raw_data_disclosed_fails()
    test_p8_invalid_package_hash_fails()
    test_p8_missing_verifier_fails()
    test_p8_missing_report_reference_fails()
    print("PASS: confidential challenge validator field tests")


if __name__ == "__main__":
    main()
