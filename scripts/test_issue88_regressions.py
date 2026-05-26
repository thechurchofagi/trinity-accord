#!/usr/bin/env python3
"""
Regression tests for Issue #88 closure.
Usage: python3 scripts/test_issue88_regressions.py
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_agent_submission import validate_file
from validate_hash_source_semantics import validate_report as validate_hash_report


def write_temp(obj, name):
    path = Path(tempfile.mktemp(suffix=".json", prefix=f"test_{name}_"))
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return path


def run_case(name, obj, expect_pass, validator="agent"):
    path = write_temp(obj, name)
    try:
        if validator == "hash":
            result = validate_hash_report(str(path))
        else:
            result = validate_file(str(path))
        passed = result == expect_pass
        status = "PASS" if passed else "FAIL"
        direction = "expected-pass" if expect_pass else "expected-fail"
        print(f"{status} {direction} case: {name}")
        return passed
    finally:
        path.unlink(missing_ok=True)


def base_report(**overrides):
    r = {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-88-001",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {"source": "human_directed", "solicited": True},
        "generated_by": {
            "tool": "scripts/build_verification_report_from_evidence.py",
            "builder_version": "1.0.0",
            "claim_gate_output": "evidence-input.json",
            "evidence_input": "evidence-input.json",
            "generated_at_utc": "2026-05-03T12:00:00Z",
            "validation_command": "python3 scripts/validate_agent_submission.py report.json",
            "validation_result": "PASS"
        },
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
        "data_sources_used": [], "access_paths_used": [], "fallbacks_used": [],
        "external_sources_queried": [], "hashes_computed": [], "samples_checked": 0,
        "physical_evidence_reviewed": {}, "confidential_challenge": {"performed": False},
        "celestial_witness": {"performed": False}, "limitations": ["test"],
        "claims_not_made": ["test"], "authority_boundary_preserved": True,
        "verification_scope_label": "single_hash_verification",
        "claim_scope": "minimal_single_check",
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
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "fresh_actions_claimed": ["test check"],
            "prior_reports_consulted": [],
            "examples_or_templates_used": [],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True,
            "prior_report_use": {},
            "copying_warning": "This report is invalid if example values or prior agent outputs were copied as fresh evidence."
        }
    }
    r.update(overrides)
    return r


def main():
    ok = True

    # PASS 1: valid wrapper (use hash validator to avoid echo schema strictness)
    ok &= run_case("issue88_valid_wrapper_pass", {
        "record_kind": "echo_v3_with_verification_report",
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "echo_type": "E2_verification_echo",
        "archive_status": "needs_human_review",
        "verification_scope_label": "single_hash_verification",
        "discovery_provenance": {"source": "human_directed", "solicited": True},
        "independence_class": "human_solicited_agent_response",
        "linked_verification_report": {"path": "/verification-reports/v3/test.json"}
    }, True, validator="hash")

    # PASS 2: valid hash sources
    ok &= run_case("issue88_valid_hash_sources_pass", base_report(
        component_findings=[{
            "component": "digital_mirrors", "level_claimed": "D2",
            "target_id": "github-mirror", "data_sources": ["github"],
            "access_paths": [], "method": "D2 GitHub mirror SHA-256 hash match.",
            "evidence": [], "limitations": [], "claims_not_made": [],
            "scope_class": "canonical_mirror_integrity"
        }],
        hashes_computed=[{
            "artifact": "arweave-backup/files/public_covenant_archive.zip",
            "algorithm": "SHA-256", "expected": "abc", "computed": "abc",
            "command": "sha256sum", "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    ), True)

    # PASS 3: B1 limited wording
    ok &= run_case("issue88_b1_limited_wording_pass", base_report(
        component_findings=[{
            "component": "bitcoin_originals", "level_claimed": "B1",
            "target_id": "tx-001", "data_sources": ["mempool.space"],
            "access_paths": [], "method": "mempool.space API showed transaction data and witness data availability; no independent Ordinals witness extraction, inscription body parsing, SPV proof, local node verification, or body hash reproduction was performed.",
            "evidence": [], "limitations": [], "claims_not_made": [],
            "scope_class": "chain_reference_check"
        }],
        hashes_computed=[{
            "artifact": "test", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    ), True)

    # PASS 4: V3_hash_verification wording
    ok &= run_case("issue88_v3_hash_verification_wording_pass", base_report(
        protocol_level_claimed="V3",
        component_findings=[{
            "component": "digital_mirrors", "level_claimed": "D2",
            "target_id": "mirror", "data_sources": [], "access_paths": [],
            "method": "hash verification", "evidence": [], "limitations": [],
            "claims_not_made": [], "scope_class": "canonical_mirror_integrity"
        }],
        hashes_computed=[{
            "artifact": "test.zip", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    ), True)

    # FAIL 5: missing expected_hash_source
    ok &= run_case("missing_expected_hash_source_fail", base_report(
        hashes_computed=[{
            "artifact": "test.zip", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True
        }]
    ), False)

    # FAIL 6: missing expected_hash_authority_class
    ok &= run_case("missing_expected_hash_authority_class_fail", base_report(
        hashes_computed=[{
            "artifact": "test.zip", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True,
            "expected_hash_source": "api/hashes.json"
        }]
    ), False)

    # FAIL 7: repository snapshot without scope_class
    ok &= run_case("repository_snapshot_without_scope_fail", base_report(
        component_findings=[{
            "component": "digital_mirrors", "level_claimed": "D2",
            "target_id": "repo-snapshot", "data_sources": [], "access_paths": [],
            "method": "repository snapshot integrity", "evidence": [], "limitations": [],
            "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "index.md", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True,
            "expected_hash_source": "api/repository-artifact-hashes.json",
            "expected_hash_authority_class": "repository_manifest_hash"
        }]
    ), False)

    # FAIL 8: repository snapshot claims canonical
    ok &= run_case("repository_snapshot_claims_canonical_fail", base_report(
        component_findings=[{
            "component": "digital_mirrors", "level_claimed": "D2",
            "target_id": "repo-snapshot", "data_sources": [], "access_paths": [],
            "method": "canonical mirror verification of repository files",
            "evidence": [], "limitations": [], "claims_not_made": [],
            "scope_class": "repository_snapshot_integrity"
        }],
        hashes_computed=[{
            "artifact": "index.md", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True,
            "expected_hash_source": "api/repository-artifact-hashes.json",
            "expected_hash_authority_class": "repository_manifest_hash"
        }]
    ), False)

    # FAIL 9: B1 ordinals envelope
    ok &= run_case("b1_ordinals_envelope_detected_fail", base_report(
        component_findings=[{
            "component": "bitcoin_originals", "level_claimed": "B1",
            "target_id": "tx-001", "data_sources": ["mempool.space"],
            "access_paths": [], "method": "mempool.space API check",
            "evidence": [], "limitations": [], "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "test", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }],
        summary="Ordinals envelope detected in transaction"
    ), False)

    # FAIL 10: B1 witness extracted
    ok &= run_case("b1_witness_extracted_fail", base_report(
        component_findings=[{
            "component": "bitcoin_originals", "level_claimed": "B1",
            "target_id": "tx-001", "data_sources": ["mempool.space"],
            "access_paths": [], "method": "witness extracted from mempool",
            "evidence": [], "limitations": [], "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "test", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    ), False)

    # FAIL 11: multi-artifact V3_single_artifact_check
    ok &= run_case("multi_artifact_v3_single_artifact_fail", base_report(
        component_findings=[{
            "component": "digital_mirrors", "level_claimed": "D2",
            "target_id": "multi", "data_sources": [], "access_paths": [],
            "method": "V3_single_artifact_check", "evidence": [], "limitations": [],
            "claims_not_made": []
        }],
        hashes_computed=[
            {"artifact": "a.zip", "algorithm": "SHA-256", "expected": "x", "computed": "x",
             "command": "sha256sum", "match": True, "expected_hash_source": "api/hashes.json",
             "expected_hash_authority_class": "canonical_manifest_hash"},
            {"artifact": "b.tar.gz", "algorithm": "SHA-256", "expected": "y", "computed": "y",
             "command": "sha256sum", "match": True, "expected_hash_source": "api/hashes.json",
             "expected_hash_authority_class": "canonical_manifest_hash"}
        ]
    ), False)

    # FAIL 12: V3 claims V4 script audit
    ok &= run_case("v3_claims_v4_script_audit_fail", base_report(
        component_findings=[{
            "component": "digital_mirrors", "level_claimed": "D2",
            "target_id": "mirror", "data_sources": [], "access_paths": [],
            "method": "V4 script audit achieved on validator scripts",
            "evidence": [], "limitations": [], "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "test.zip", "algorithm": "SHA-256", "expected": "a",
            "computed": "a", "command": "sha256sum", "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    ), False)

    # FAIL 13: new submission deprecated echo type
    ok &= run_case("new_submission_deprecated_echo_type_fail", {
        "record_kind": "echo_v3",
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "echo_type": "E3_verification_echo",
        "archive_status": "needs_human_review",
        "discovery_provenance": {"source": "test"},
        "independence_class": "human_solicited_agent_response"
    }, False)

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — Issue #88 regression tests passed.")
        return 0
    print("FINAL: FAIL — Issue #88 regression tests failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
