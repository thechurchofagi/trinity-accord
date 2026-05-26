#!/usr/bin/env python3
"""
Test cases for verification_scope_label consistency.
Covers VSL001–VSL012 scenarios.

Usage:
    python3 scripts/test_verification_scope_label.py
"""
import json
import sys
import tempfile
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_agent_submission import validate_file

PASS_COUNT = 0
FAIL_COUNT = 0
TOTAL = 0


def make_base_report(protocol_level, scope_label, record_kind="verification_report_v2"):
    """Create a minimal valid report with given protocol level and scope label."""
    base = {
        "record_kind": record_kind,
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": f"test-vsl-{protocol_level}",
        "reporter": {"name": "test-agent", "type": "ai_agent"},
        "discovery_provenance": {"source": "human_directed", "solicited": True},
        "protocol_level_claimed": protocol_level,
        "generated_by": {
            "tool": "scripts/build_verification_report_from_evidence.py",
            "builder_version": "1.0.0",
            "claim_gate_output": "test.json",
            "evidence_input": "test.json",
            "generated_at_utc": "2026-05-04T00:00:00Z",
            "validation_command": "python3 scripts/validate_agent_submission.py test.json",
            "validation_result": "PASS"
        },
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
        "physical_evidence_reviewed": {"flaw_analysis_method": "not_performed"},
        "confidential_challenge": {"performed": False},
        "celestial_witness": {"performed": False},
        "limitations": ["test"],
        "claims_not_made": ["test"],
        "authority_boundary_preserved": True,
        "origin_classification": {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": "human_directed",
            "invitation_scope": "verification_invited",
            "requester_class": "ai_agent",
            "performer_class": "ai_agent",
            "method_independence_class": "official_script_run",
            "attestation_authority_class": "none",
            "derived_counting_bucket": "human_directed_agent_verification",
            "counts_as_formal_independent_attestation": False,
        },
        "integrity_boundary": {
            "agent_integrity_declaration_present": True,
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_actions_claimed": ["test"],
            "fresh_outputs_attached": True
        }
    }
    if scope_label is not None:
        base["verification_scope_label"] = scope_label
    return base


def make_base_wrapper(verification_level, scope_label):
    """Create a minimal valid echo wrapper with given level and scope label."""
    base = {
        "record_kind": "echo_v3_with_verification_report",
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "echo_type": "E2_verification_echo",
        "agent_identity": {"name_or_model": "test-agent", "system_or_provider": "test", "self_reported": True},
        "context_depth": "C3_verification_aware",
        "assessment_state": "qualified_assessment",
        "verification_level": verification_level,
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "human_directed",
            "agency_level": "A1_human_gave_exact_url",
            "first_entry": {"url_or_path": "https://github.com/test", "entry_type": "github_repository"},
            "human_supplied_link": True,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": True,
            "confidence": "high"
        },
        "understanding_summary": "Test verification echo.",
        "verification_claim": f"Protocol level {verification_level} achieved.",
        "echo": "Test echo content.",
        "uncertainties": ["test"],
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
        "linked_verification_report": {
            "schema_version": "trinityaccord.verification-report.v2",
            "path": "test.json",
            "report_id": "test-vsl"
        },
        "not_authority": True,
        "not_amendment": True,
        "not_endorsement": True,
        "bitcoin_originals_prevail": True,
        "not_verification_unless_claimed": True,
        "generated_by": {
            "tool": "scripts/build_verification_report_from_evidence.py",
            "builder_version": "1.0.0",
            "claim_gate_output": "test.json",
            "evidence_input": "test.json",
            "generated_at_utc": "2026-05-04T00:00:00Z",
            "validation_command": "python3 scripts/validate_agent_submission.py test.json",
            "validation_result": "PASS"
        },
        "verification_integrity": {
            "integrity_declaration_present": True,
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_actions_claimed": ["test"]
        }
    }
    if scope_label is not None:
        base["verification_scope_label"] = scope_label
    return base


def write_temp(obj, name):
    path = Path(tempfile.mktemp(suffix=".json", prefix=f"vsl_{name}_"))
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return path


def run_case(test_id, description, obj, expect_pass):
    global PASS_COUNT, FAIL_COUNT, TOTAL
    TOTAL += 1

    path = write_temp(obj, test_id)
    try:
        result = validate_file(str(path))
        passed = result == expect_pass
        if passed:
            PASS_COUNT += 1
            print(f"PASS {test_id}: {description}")
        else:
            FAIL_COUNT += 1
            print(f"FAIL {test_id}: {description}")
            print(f"      Expected {'PASS' if expect_pass else 'FAIL'}, got {'PASS' if result else 'FAIL'}")
    except Exception as e:
        FAIL_COUNT += 1
        print(f"FAIL {test_id}: {description} — Exception: {e}")
    finally:
        path.unlink(missing_ok=True)


def main():
    # VSL001 V0 + read_only_orientation PASS
    run_case("VSL001", "V0 + read_only_orientation PASS",
             make_base_report("V0", "read_only_orientation"), True)

    # VSL002 V0 + single_hash_verification FAIL
    run_case("VSL002", "V0 + single_hash_verification FAIL",
             make_base_report("V0", "single_hash_verification"), False)

    # VSL003 V1 + authority_boundary_recognition PASS
    run_case("VSL003", "V1 + authority_boundary_recognition PASS",
             make_base_report("V1", "authority_boundary_recognition"), True)

    # VSL004 V3 one hash + single_hash_verification PASS
    report = make_base_report("V3", "single_hash_verification")
    report["hashes_computed"] = [{"artifact": "test", "algorithm": "SHA256", "expected": "a"*64, "computed": "a"*64, "command": "sha256sum", "match": True, "expected_hash_source": "api/hashes.json", "expected_hash_authority_class": "canonical_manifest_hash"}]
    run_case("VSL004", "V3 one hash + single_hash_verification PASS", report, True)

    # VSL005 V3 one hash + full_public_digital_verification FAIL
    report = make_base_report("V3", "full_public_digital_verification")
    report["hashes_computed"] = [{"artifact": "test", "algorithm": "SHA256", "expected": "a"*64, "computed": "a"*64, "command": "sha256sum", "match": True, "expected_hash_source": "api/hashes.json", "expected_hash_authority_class": "canonical_manifest_hash"}]
    run_case("VSL005", "V3 one hash + full_public_digital_verification FAIL", report, False)

    # VSL006 V4 official scripts + official_script_audit PASS
    report = make_base_report("V4", "official_script_audit")
    report["script_audit"] = {"scope_class": "profile_required_script_audit", "scripts_reviewed": ["test.py"], "command": ["python3 test.py"], "environment": {"test.py": {"python": "3.x"}}, "exit_code": 0, "output_summary": ["PASS"], "scripts_executed": 1, "all_scripts_green": True, "all_validators_green": True, "scripts": [{"path": "test.py", "executed": True, "exists": True, "exit_code": 0, "result": "PASS"}], "non_blocking_failures": []}
    run_case("VSL006", "V4 + official_script_audit PASS", report, True)

    # VSL007 V4 official scripts + independent_single_artifact_reproduction FAIL
    report = make_base_report("V4", "independent_single_artifact_reproduction")
    report["script_audit"] = {"scope_class": "profile_required_script_audit", "scripts_reviewed": ["test.py"], "command": ["python3 test.py"], "environment": {"test.py": {"python": "3.x"}}, "exit_code": 0, "output_summary": ["PASS"], "scripts_executed": 1, "all_scripts_green": True, "all_validators_green": True, "scripts": [{"path": "test.py", "executed": True, "exists": True, "exit_code": 0, "result": "PASS"}], "non_blocking_failures": []}
    run_case("VSL007", "V4 + independent_single_artifact_reproduction FAIL", report, False)

    # VSL008 V4 with non-blocking failure + official_script_audit_with_limitations PASS
    report = make_base_report("V4", "official_script_audit_with_limitations")
    report["script_audit"] = {"scope_class": "profile_required_script_audit", "scripts_reviewed": ["test.py"], "command": ["python3 test.py"], "environment": {"test.py": {"python": "3.x"}}, "exit_code": 0, "output_summary": ["PASS"], "scripts_executed": 1, "all_scripts_green": False, "all_validators_green": False, "scripts": [{"path": "test.py", "executed": True, "exists": True, "exit_code": 0, "result": "PASS"}], "non_blocking_failures": [{"path": "link_check.py", "result": "FAIL"}]}
    run_case("VSL008", "V4 with non-blocking + official_script_audit_with_limitations PASS", report, True)

    # VSL009 V4 with non-blocking failure + official_script_audit FAIL (overclaim)
    report = make_base_report("V4", "official_script_audit")
    report["script_audit"] = {"scope_class": "profile_required_script_audit", "scripts_reviewed": ["test.py"], "command": ["python3 test.py"], "environment": {"test.py": {"python": "3.x"}}, "exit_code": 0, "output_summary": ["PASS"], "scripts_executed": 1, "all_scripts_green": False, "all_validators_green": False, "scripts": [{"path": "test.py", "executed": True, "exists": True, "exit_code": 0, "result": "PASS"}], "non_blocking_failures": [{"path": "link_check.py", "result": "FAIL"}]}
    run_case("VSL009", "V4 with non-blocking + official_script_audit FAIL (overclaim)", report, False)

    # VSL010 V4+ one artifact + independent_single_artifact_reproduction PASS
    report = make_base_report("V4+", "independent_single_artifact_reproduction")
    report["script_audit"] = {"scope_class": "independent_reproduction", "scripts_reviewed": ["test.py"], "command": ["python3 test.py"], "environment": {"test.py": {"python": "3.x"}}, "exit_code": 0, "output_summary": ["PASS"], "scripts_executed": 1, "all_scripts_green": True, "all_validators_green": True, "scripts": [{"path": "test.py", "executed": True, "exists": True, "exit_code": 0, "result": "PASS", "independent": True}], "non_blocking_failures": []}
    run_case("VSL010", "V4+ one artifact + independent_single_artifact_reproduction PASS", report, True)

    # VSL011 V4+ one artifact + full_public_digital_verification FAIL
    report = make_base_report("V4+", "full_public_digital_verification")
    report["script_audit"] = {"scope_class": "independent_reproduction", "scripts_reviewed": ["test.py"], "command": ["python3 test.py"], "environment": {"test.py": {"python": "3.x"}}, "exit_code": 0, "output_summary": ["PASS"], "scripts_executed": 1, "all_scripts_green": True, "all_validators_green": True, "scripts": [{"path": "test.py", "executed": True, "exists": True, "exit_code": 0, "result": "PASS", "independent": True}], "non_blocking_failures": []}
    run_case("VSL011", "V4+ one artifact + full_public_digital_verification FAIL", report, False)

    # VSL012 legacy record missing label PASS/WARN
    legacy = make_base_report("V0", None)
    legacy["record_kind"] = "legacy_record"
    legacy["archive_status"] = "legacy"
    run_case("VSL012", "legacy record missing label PASS/WARN", legacy, True)

    print(f"\n{'='*60}")
    print(f"Results: {PASS_COUNT}/{TOTAL} passed, {FAIL_COUNT}/{TOTAL} failed")
    if FAIL_COUNT == 0:
        print("FINAL: PASS — verification_scope_label tests passed.")
    else:
        print("FINAL: FAIL — some verification_scope_label tests failed.")
    return 0 if FAIL_COUNT == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
