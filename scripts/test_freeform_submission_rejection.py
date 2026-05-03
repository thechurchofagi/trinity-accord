#!/usr/bin/env python3
"""
Test freeform submission rejection: FF001-FF008.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

def check(test_id, label, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"{status}: {test_id} — {label}")
    if detail and not cond:
        print(f"      {detail}")
    return cond

def validate_report(obj):
    """Run validate_agent_submission checks."""
    from validate_agent_submission import validate_generated_by, validate_record_kind
    ok = True
    ok &= validate_record_kind(obj, "test")
    ok &= validate_generated_by(obj, "test")
    return ok

def make_builder_report():
    """A properly builder-generated report."""
    return {
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-builder-001",
        "reporter": {"name": "TestAgent", "type": "ai_agent"},
        "discovery_provenance": {"source": "test"},
        "protocol_level_claimed": "V4",
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
        "script_audit": {
            "scope_class": "profile_required_script_audit",
            "scripts_reviewed": 0,
            "scripts_executed": 0,
            "scripts": [],
            "missing_scripts": [],
            "blocking_failures": [],
            "non_blocking_failures": [],
            "all_validators_green": False
        },
        "generated_by": {
            "tool": "scripts/build_verification_report_from_evidence.py",
            "builder_version": "trinityaccord.report-builder.v1",
            "claim_gate_output": "test-claim-gate-output.json",
            "evidence_input": "test-evidence-input.json",
            "generated_at_utc": "2026-05-03T00:00:00Z",
            "validation_command": "python3 scripts/validate_agent_submission.py test.json",
            "validation_result": "PASS"
        }
    }

def make_builder_wrapper():
    """A properly builder-generated echo wrapper."""
    return {
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "agent_identity": {"name_or_model": "Test", "system_or_provider": "test", "self_reported": True},
        "context_depth": "C3_verification_aware",
        "assessment_state": "evidence_based_assessment",
        "verification_level": "V4",
        "discovery_provenance": {"source": "test"},
        "understanding_summary": "test",
        "verification_claim": "V4",
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
            "claim_gate_output": "test-claim-gate-output.json",
            "evidence_input": "test-evidence-input.json",
            "generated_at_utc": "2026-05-03T00:00:00Z",
            "validation_command": "python3 scripts/validate_agent_submission.py test.json",
            "validation_result": "PASS"
        }
    }

def main():
    results = []

    # FF001 — freeform V4 report FAIL
    print("=== FF001 — freeform V4 report ===")
    freeform_v4 = {
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "freeform-001",
        "reporter": {"name": "FreeformAgent", "type": "ai_agent"},
        "discovery_provenance": {"source": "test"},
        "protocol_level_claimed": "V4",
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
    }
    r = check("FF001", "freeform V4 report rejected", not validate_report(freeform_v4))
    results.append(r)

    # FF002 — freeform D2 report FAIL
    print("\n=== FF002 — freeform D2 report ===")
    freeform_d2 = dict(freeform_v4)
    freeform_d2["report_id"] = "freeform-002"
    freeform_d2["protocol_level_claimed"] = "V3"
    r = check("FF002", "freeform D2 report rejected", not validate_report(freeform_d2))
    results.append(r)

    # FF003 — freeform Echo wrapper FAIL
    print("\n=== FF003 — freeform Echo wrapper ===")
    freeform_wrapper = {
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
    }
    r = check("FF003", "freeform Echo wrapper rejected", not validate_report(freeform_wrapper))
    results.append(r)

    # FF004 — freeform Issue-style Echo JSON FAIL
    print("\n=== FF004 — freeform Issue-style Echo ===")
    freeform_issue = dict(freeform_wrapper)
    freeform_issue.pop("generated_by", None)
    freeform_issue.pop("linked_verification_report", None)
    freeform_issue["record_kind"] = "echo_v3_with_verification_report"
    r = check("FF004", "freeform Issue-style Echo rejected", not validate_report(freeform_issue))
    results.append(r)

    # FF005 — builder-generated V4 report PASS
    print("\n=== FF005 — builder-generated V4 report ===")
    r = check("FF005", "builder-generated V4 report passes", validate_report(make_builder_report()))
    results.append(r)

    # FF006 — builder-generated wrapper PASS
    print("\n=== FF006 — builder-generated wrapper ===")
    r = check("FF006", "builder-generated wrapper passes", validate_report(make_builder_wrapper()))
    results.append(r)

    # FF007 — freeform non-technical recognition Echo PASS
    print("\n=== FF007 — non-technical recognition Echo ===")
    non_tech_echo = {
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "agent_identity": {"name_or_model": "Test", "system_or_provider": "test", "self_reported": True},
        "context_depth": "C1_orientation",
        "assessment_state": "preliminary_orientation",
        "verification_level": "none",
        "discovery_provenance": {"source": "test"},
        "understanding_summary": "test",
        "verification_claim": "none",
        "echo_type": "E1_recognition_echo",
        "echo": "Interesting project",
        "uncertainties": ["not verified"],
        "boundary_acknowledgement": {
            "bitcoin_originals_prevail": True,
            "echo_is_not_authority": True,
            "echo_is_not_verification_unless_claimed": True,
            "mirror_is_not_amendment": True,
            "homepage_only_is_insufficient_for_final_evaluation": True
        },
        "independence_class": "unsolicited_independent",
        "archive_status": "needs_human_review",
        "origin_limitations": ["no verification performed"],
        "record_kind": "echo_v3",
    }
    r = check("FF007", "non-technical Echo passes without generated_by",
              validate_report(non_tech_echo))
    results.append(r)

    # FF008 — non-technical Echo tries to claim V4 FAIL
    print("\n=== FF008 — non-technical Echo claims V4 ===")
    overclaim_echo = dict(non_tech_echo)
    overclaim_echo["verification_level"] = "V4"
    overclaim_echo["verification_claim"] = "V4 achieved"
    overclaim_echo["echo_type"] = "E2_verification_echo"
    overclaim_echo["record_kind"] = "echo_v3_with_verification_report"
    overclaim_echo["linked_verification_report"] = {
        "schema_version": "trinityaccord.verification-report.v2",
        "path": "nonexistent.json",
        "report_id": "fake"
    }
    r = check("FF008", "non-technical Echo claiming V4 rejected",
              not validate_report(overclaim_echo))
    results.append(r)

    print("\n" + "=" * 50)
    if all(results):
        print("FINAL: PASS — freeform submission rejection tests passed.")
        return 0
    print("FINAL: FAIL — freeform submission rejection tests failed.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
