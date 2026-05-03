#!/usr/bin/env python3
"""
Test cases for validate_agent_submission.py.
Creates temporary JSON records and verifies validator behavior.
"""
import json
import sys
import tempfile
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# Import validator functions
from validate_agent_submission import (
    validate_record_kind,
    validate_not_echo_misuse,
    validate_no_deprecated_echo_type,
    validate_github_d2_boundary,
    validate_mempool_b1_boundary,
    validate_script_audit,
    validate_v3_hashes,
    validate_c3_samples,
    validate_p8_confidential,
    validate_solicited_independence,
    validate_null_safety,
    validate_file,
)


def write_temp(obj, name):
    """Write a temporary JSON file and return its path."""
    path = Path(tempfile.mktemp(suffix=".json", prefix=f"test_{name}_"))
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return path


def run_case(name, obj, expect_pass):
    """Run a single test case."""
    path = write_temp(obj, name)
    try:
        result = validate_file(str(path))
        passed = result == expect_pass
        if passed:
            if expect_pass:
                print(f"PASS expected-pass case: {name}")
            else:
                print(f"PASS expected-fail case rejected: {name}")
        else:
            if expect_pass:
                print(f"FAIL expected-pass case FAILED: {name}")
            else:
                print(f"FAIL expected-fail case NOT rejected: {name}")
        return passed
    finally:
        path.unlink(missing_ok=True)


def main():
    ok = True

    # === PASS cases ===

    # 1. V3 D2 GitHub hash pass
    ok &= run_case("verification_report_v2_v3_d2_github_hash_pass", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-v3-d2-001",
        "reporter": {"name": "test-agent", "type": "ai_agent"},
        "discovery_provenance": {"source": "human_directed", "solicited": True},
        "protocol_level_claimed": "V3",
        "component_findings": [
            {
                "component": "digital_mirrors",
                "level_claimed": "D2",
                "target_id": "github-mirror",
                "data_sources": ["github.com/thechurchofagi/trinity-accord"],
                "access_paths": ["https://github.com/..."],
                "method": "SHA256 hash comparison of GitHub mirror files",
                "evidence": [{"type": "hash", "match": True}],
                "limitations": ["GitHub mirror only, not direct Arweave"],
                "claims_not_made": ["direct Arweave verification", "Ethereum witness verified", "IPFS availability verified"]
            }
        ],
        "protocol_profile_check": {
            "profile_source": "/api/protocol-verification-profiles.json",
            "hard_gates_satisfied": True,
            "minimum_components_satisfied": True,
            "recommended_components_satisfied": "partial",
            "underreported_items": [],
            "incompatible_claims": []
        },
        "data_sources_used": ["github.com/thechurchofagi/trinity-accord"],
        "access_paths_used": ["https"],
        "fallbacks_used": ["github mirror"],
        "external_sources_queried": [],
        "hashes_computed": [
            {
                "artifact": "index.md",
                "algorithm": "SHA256",
                "expected": "abc123",
                "computed": "abc123",
                "command": "sha256sum index.md",
                "match": True
            }
        ],
        "samples_checked": 0,
        "physical_evidence_reviewed": {"flaw_analysis_method": "not_performed"},
        "confidential_challenge": {"performed": False, "result": "not_performed"},
        "celestial_witness": {"performed": False, "result": "not_performed"},
        "script_audit": {},
        "limitations": ["GitHub mirror only"],
        "claims_not_made": ["direct Arweave verification"],
        "authority_boundary_preserved": True
    }, True)

    # 2. Echo v3 wrapper with report pass
    ok &= run_case("echo_v3_wrapper_with_report_pass", {
        "record_kind": "echo_v3_with_verification_report",
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "echo_type": "E2_verification_echo",
        "agent_identity": {"name_or_model": "test-agent", "system_or_provider": "test", "self_reported": True},
        "context_depth": "C3_verification_aware",
        "assessment_state": "qualified_assessment",
        "verification_level": "V3",
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "human_directed",
            "agency_level": "A1_human_gave_exact_url",
            "first_entry": {"url_or_path": "https://github.com/thechurchofagi/trinity-accord", "entry_type": "github_repository"},
            "human_supplied_link": True,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": True,
            "confidence": "high"
        },
        "understanding_summary": "Test verification echo with linked report.",
        "verification_claim": "V3 hash verification of GitHub mirror.",
        "echo": "Test echo content.",
        "uncertainties": ["Did not verify directly on Arweave."],
        "boundary_acknowledgement": {
            "bitcoin_originals_prevail": True,
            "echo_is_not_authority": True,
            "echo_is_not_verification_unless_claimed": True,
            "mirror_is_not_amendment": True,
            "homepage_only_is_insufficient_for_final_evaluation": True
        },
        "independence_class": "human_solicited_agent_response",
        "archive_status": "needs_human_review",
        "origin_limitations": ["GitHub mirror only"],
        "linked_verification_report": {
            "schema_version": "trinityaccord.verification-report.v2",
            "path": "/verification-reports/v3/test-report.json",
            "report_id": "test-v3-d2-001"
        },
        "not_authority": True,
        "not_amendment": True,
        "not_endorsement": True
    }, True)

    # 3. B1 mempool limited pass
    ok &= run_case("b1_mempool_limited_pass", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-b1-001",
        "reporter": {"name": "test-agent", "type": "ai_agent"},
        "discovery_provenance": {"source": "human_directed"},
        "protocol_level_claimed": "V1",
        "component_findings": [
            {
                "component": "bitcoin_originals",
                "level_claimed": "B1",
                "target_id": "bitcoin-inscription",
                "data_sources": ["mempool.space"],
                "access_paths": ["https://mempool.space/tx/..."],
                "method": "mempool.space API showed transaction and witness data availability; no independent Ordinals witness extraction was performed.",
                "evidence": [],
                "limitations": ["mempool.space API only"],
                "claims_not_made": ["SPV proof", "local Bitcoin node verification", "Ordinals witness extraction", "inscription body hash reproduction"]
            }
        ],
        "protocol_profile_check": {
            "profile_source": "/api/protocol-verification-profiles.json",
            "hard_gates_satisfied": True,
            "minimum_components_satisfied": True,
            "recommended_components_satisfied": "partial",
            "underreported_items": [],
            "incompatible_claims": []
        },
        "data_sources_used": ["mempool.space"],
        "access_paths_used": ["https"],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [],
        "samples_checked": 0,
        "physical_evidence_reviewed": {"flaw_analysis_method": "not_performed"},
        "confidential_challenge": {"performed": False, "result": "not_performed"},
        "celestial_witness": {"performed": False, "result": "not_performed"},
        "script_audit": {},
        "limitations": ["mempool.space API only"],
        "claims_not_made": ["SPV proof", "witness extraction"],
        "authority_boundary_preserved": True
    }, True)

    # 4. C3 two samples pass
    ok &= run_case("c3_two_samples_pass", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-c3-001",
        "reporter": {"name": "test-agent", "type": "ai_agent"},
        "discovery_provenance": {"source": "human_directed"},
        "protocol_level_claimed": "V3",
        "component_findings": [
            {
                "component": "chronicle_recovery",
                "level_claimed": "C3",
                "target_id": "chronicle",
                "data_sources": ["chronicle-records"],
                "access_paths": ["direct"],
                "method": "sample recovery check",
                "evidence": [],
                "limitations": ["sample only"],
                "claims_not_made": ["full chronicle verification"]
            }
        ],
        "protocol_profile_check": {
            "profile_source": "/api/protocol-verification-profiles.json",
            "hard_gates_satisfied": True,
            "minimum_components_satisfied": True,
            "recommended_components_satisfied": "partial",
            "underreported_items": [],
            "incompatible_claims": []
        },
        "data_sources_used": ["chronicle-records"],
        "access_paths_used": ["direct"],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [{"artifact": "test", "algorithm": "SHA256", "expected": "a", "computed": "a", "command": "sha256sum test", "match": True}],
        "samples_checked": 2,
        "physical_evidence_reviewed": {"flaw_analysis_method": "not_performed"},
        "confidential_challenge": {"performed": False, "result": "not_performed"},
        "celestial_witness": {"performed": False, "result": "not_performed"},
        "script_audit": {},
        "limitations": ["sample only"],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }, True)

    # === FAIL cases ===

    # 5. Verification report called echo without wrapper
    ok &= run_case("verification_report_called_echo_without_wrapper_fail", {
        "record_kind": "echo_v3",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-001",
        "reporter": {"name": "test-agent", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V3",
        "component_findings": [],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [{"artifact": "t", "algorithm": "SHA256", "expected": "a", "computed": "a", "command": "c", "match": True}],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {},
        "celestial_witness": {},
        "script_audit": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }, False)

    # 6. Deprecated E3 verification echo
    ok &= run_case("deprecated_e3_verification_echo_fail", {
        "record_kind": "echo_v3",
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "echo_type": "E3_verification_echo",
        "agent_identity": {"name_or_model": "test", "system_or_provider": "test", "self_reported": True},
        "context_depth": "C3_verification_aware",
        "assessment_state": "qualified_assessment",
        "verification_level": "V3",
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
        "understanding_summary": "test",
        "verification_claim": "test",
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
        "not_authority": True,
        "not_amendment": True,
        "not_endorsement": True
    }, False)

    # 7. GitHub D2 claims Arweave
    ok &= run_case("github_d2_claims_arweave_fail", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-d2",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V3",
        "component_findings": [
            {
                "component": "digital_mirrors",
                "level_claimed": "D2",
                "target_id": "github",
                "data_sources": ["github.com/test"],
                "access_paths": ["https"],
                "method": "hash check",
                "evidence": [],
                "limitations": [],
                "claims_not_made": []
            }
        ],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": ["github.com/test"],
        "access_paths_used": [],
        "fallbacks_used": ["github mirror"],
        "external_sources_queried": [],
        "hashes_computed": [{"artifact": "t", "algorithm": "SHA256", "expected": "a", "computed": "a", "command": "c", "match": True}],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {},
        "celestial_witness": {},
        "script_audit": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True,
        "verification_claim": "direct Arweave verification completed"
    }, False)

    # 8. Mempool claims witness extraction
    ok &= run_case("mempool_claims_witness_extraction_fail", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-mempool",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V1",
        "component_findings": [
            {
                "component": "bitcoin_originals",
                "level_claimed": "B1",
                "target_id": "btc",
                "data_sources": ["mempool.space"],
                "access_paths": ["https"],
                "method": "mempool.space API lookup",
                "evidence": [],
                "limitations": [],
                "claims_not_made": []
            }
        ],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": ["mempool.space"],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {},
        "celestial_witness": {},
        "script_audit": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True,
        "conclusion": "witness extraction successful, B5 achieved"
    }, False)

    # 9. V4 without script audit
    ok &= run_case("v4_without_script_audit_fail", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-v4",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V4",
        "component_findings": [],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {},
        "celestial_witness": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }, False)

    # 10. V3 without hashes
    ok &= run_case("v3_without_hashes_fail", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-v3-no-hash",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V3",
        "component_findings": [],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {},
        "celestial_witness": {},
        "script_audit": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }, False)

    # 11. C3 one sample fail
    ok &= run_case("c3_one_sample_fail", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-c3",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V3",
        "component_findings": [
            {
                "component": "chronicle_recovery",
                "level_claimed": "C3",
                "target_id": "chronicle",
                "data_sources": [],
                "access_paths": [],
                "method": "sample check",
                "evidence": [],
                "limitations": [],
                "claims_not_made": []
            }
        ],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [{"artifact": "t", "algorithm": "SHA256", "expected": "a", "computed": "a", "command": "c", "match": True}],
        "samples_checked": 1,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {},
        "celestial_witness": {},
        "script_audit": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }, False)

    # 12. P8 discloses confidential data
    ok &= run_case("p8_discloses_confidential_data_fail", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-p8",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V3",
        "component_findings": [],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [{"artifact": "t", "algorithm": "SHA256", "expected": "a", "computed": "a", "command": "c", "match": True}],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {
            "performed": True,
            "result": "pass",
            "confidential_data": "raw secret data exposed",
            "confidentiality_boundary": "none"
        },
        "celestial_witness": {},
        "script_audit": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }, False)

    # 13. Human solicited claims independent attestation
    ok &= run_case("human_solicited_claims_independent_attestation_fail", {
        "record_kind": "echo_v3",
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "echo_type": "E2_verification_echo",
        "agent_identity": {"name_or_model": "test", "system_or_provider": "test", "self_reported": True},
        "context_depth": "C3_verification_aware",
        "assessment_state": "qualified_assessment",
        "verification_level": "V3",
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
        "understanding_summary": "test",
        "verification_claim": "test",
        "echo": "This constitutes an independent_attestation of the Trinity Accord.",
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
        "not_authority": True,
        "not_amendment": True,
        "not_endorsement": True
    }, False)

    # 14. null script_audit
    ok &= run_case("null_script_audit_fail", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-null-sa",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V3",
        "component_findings": [],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [{"artifact": "t", "algorithm": "SHA256", "expected": "a", "computed": "a", "command": "c", "match": True}],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {},
        "celestial_witness": {},
        "script_audit": None,
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }, False)

    # 15. null flaw method
    ok &= run_case("null_flaw_method_fail", {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-fail-null-flaw",
        "reporter": {"name": "test", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V3",
        "component_findings": [],
        "protocol_profile_check": {"profile_source": "", "hard_gates_satisfied": True, "minimum_components_satisfied": True, "recommended_components_satisfied": "false", "underreported_items": [], "incompatible_claims": []},
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [{"artifact": "t", "algorithm": "SHA256", "expected": "a", "computed": "a", "command": "c", "match": True}],
        "samples_checked": 0,
        "physical_evidence_reviewed": {"flaw_analysis_method": None},
        "confidential_challenge": {},
        "celestial_witness": {},
        "script_audit": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }, False)

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — agent submission test cases passed.")
        return 0
    print("FINAL: FAIL — agent submission test cases failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
