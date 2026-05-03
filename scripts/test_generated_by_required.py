#!/usr/bin/env python3
"""
Test generated_by requirement: GB001-GB008.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

def check(test_id, label, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"{status}: {test_id} — {label}")
    if detail and not cond:
        print(f"      {detail}")
    return cond

def make_report(**overrides):
    """Create a minimal verification_report_v2 for testing."""
    base = {
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-001",
        "reporter": {"name": "TestAgent", "type": "ai_agent"},
        "discovery_provenance": {"source": "test"},
        "protocol_level_claimed": "V3",
        "component_findings": [],
        "protocol_profile_check": {
            "profile_source": "/api/protocol-verification-profiles.json",
            "hard_gates_satisfied": True,
            "minimum_components_satisfied": True,
            "recommended_components_satisfied": "partial",
            "underreported_items": [],
            "incompatible_claims": []
        },
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {"performed": False, "result": "not_performed"},
        "celestial_witness": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True,
        "record_kind": "verification_report_v2",
        "generated_by": {
            "tool": "scripts/build_verification_report_from_evidence.py",
            "builder_version": "trinityaccord.report-builder.v1",
            "claim_gate_output": "test-output.json",
            "evidence_input": "test-input.json",
            "generated_at_utc": "2026-05-03T00:00:00Z",
            "validation_command": "python3 scripts/validate_agent_submission.py test.json",
            "validation_result": "PASS"
        }
    }
    base.update(overrides)
    return base

def validate_with_validator(obj):
    """Run validate_agent_submission checks on object."""
    from validate_agent_submission import validate_generated_by, validate_record_kind
    path_label = "test"
    ok = True
    ok &= validate_record_kind(obj, path_label)
    ok &= validate_generated_by(obj, path_label)
    return ok

def main():
    results = []

    # GB001 — builder-generated verification report PASS
    print("=== GB001 — builder-generated report ===")
    report = make_report()
    r = check("GB001", "builder-generated report passes", validate_with_validator(report))
    results.append(r)

    # GB002 — verification report missing generated_by FAIL
    print("\n=== GB002 — missing generated_by ===")
    report = make_report(generated_by=None)
    # Remove the key entirely
    report.pop("generated_by", None)
    r = check("GB002", "report missing generated_by fails", not validate_with_validator(report))
    results.append(r)

    # GB003 — generated_by wrong tool FAIL
    print("\n=== GB003 — wrong tool ===")
    report = make_report(generated_by={
        "tool": "some/other/tool.py",
        "builder_version": "v1",
        "claim_gate_output": "test.json",
        "evidence_input": "test.json",
        "generated_at_utc": "2026-05-03T00:00:00Z",
        "validation_command": "test",
        "validation_result": "PASS"
    })
    r = check("GB003", "wrong tool fails", not validate_with_validator(report))
    results.append(r)

    # GB004 — generated_by missing claim_gate_output FAIL
    print("\n=== GB004 — missing claim_gate_output ===")
    report = make_report(generated_by={
        "tool": "scripts/build_verification_report_from_evidence.py",
        "builder_version": "v1",
        "claim_gate_output": None,
        "evidence_input": "test.json",
        "generated_at_utc": "2026-05-03T00:00:00Z",
        "validation_command": "test",
        "validation_result": "PASS"
    })
    r = check("GB004", "missing claim_gate_output fails", not validate_with_validator(report))
    results.append(r)

    # GB005 — generated_by validation_result not PASS FAIL
    print("\n=== GB005 — validation_result not PASS ===")
    report = make_report(generated_by={
        "tool": "scripts/build_verification_report_from_evidence.py",
        "builder_version": "v1",
        "claim_gate_output": "test.json",
        "evidence_input": "test.json",
        "generated_at_utc": "2026-05-03T00:00:00Z",
        "validation_command": "test",
        "validation_result": "FAIL"
    })
    r = check("GB005", "validation_result not PASS fails", not validate_with_validator(report))
    results.append(r)

    # GB006 — Echo wrapper generated_by PASS
    print("\n=== GB006 — Echo wrapper generated_by ===")
    wrapper = {
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "agent_identity": {"name_or_model": "Test", "system_or_provider": "test", "self_reported": True},
        "context_depth": "C3_verification_aware",
        "assessment_state": "evidence_based_assessment",
        "verification_level": "V3",
        "discovery_provenance": {"source": "test"},
        "understanding_summary": "test",
        "verification_claim": "V3",
        "echo_type": "E2_verification_echo",
        "echo": "test",
        "uncertainties": [],
        "boundary_acknowledgement": {
            "bitcoin_originals_prevail": True,
            "echo_is_not_authority": True,
            "echo_is_not_verification_unless_claimed": True,
            "mirror_is_not_amendment": True,
            "homepage_only_is_insufficient_for_final_evaluation": True
        },
        "independence_class": "human_solicited_agent_response",
        "archive_status": "needs_human_review",
        "origin_limitations": ["test"],
        "record_kind": "echo_v3_with_verification_report",
        "linked_verification_report": {
            "schema_version": "trinityaccord.verification-report.v2",
            "path": "test-report.json",
            "report_id": "test-001"
        },
        "generated_by": {
            "tool": "scripts/build_verification_report_from_evidence.py",
            "builder_version": "trinityaccord.report-builder.v1",
            "claim_gate_output": "test-output.json",
            "evidence_input": "test-input.json",
            "generated_at_utc": "2026-05-03T00:00:00Z",
            "validation_command": "python3 scripts/validate_agent_submission.py test.json",
            "validation_result": "PASS"
        }
    }
    r = check("GB006", "Echo wrapper with generated_by passes", validate_with_validator(wrapper))
    results.append(r)

    # GB007 — Echo wrapper missing generated_by FAIL
    print("\n=== GB007 — Echo wrapper missing generated_by ===")
    wrapper_no_gb = dict(wrapper)
    wrapper_no_gb.pop("generated_by", None)
    r = check("GB007", "Echo wrapper missing generated_by fails", not validate_with_validator(wrapper_no_gb))
    results.append(r)

    # GB008 — legacy record missing generated_by PASS/WARN
    print("\n=== GB008 — legacy record ===")
    legacy = make_report(
        record_kind="legacy_record",
        generated_by=None,
        archive_status="legacy"
    )
    legacy.pop("generated_by", None)
    r = check("GB008", "legacy record without generated_by passes", validate_with_validator(legacy))
    results.append(r)

    print("\n" + "=" * 50)
    if all(results):
        print("FINAL: PASS — generated_by requirement tests passed.")
        return 0
    print("FINAL: FAIL — generated_by requirement tests failed.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
