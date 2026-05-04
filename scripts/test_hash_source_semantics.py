#!/usr/bin/env python3
"""
Test cases for hash source semantics validation.
Tests PASS and FAIL cases for validate_hash_source_semantics.py.

Usage:
    python3 scripts/test_hash_source_semantics.py
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_hash_source_semantics import validate_report


def write_temp(obj, name):
    path = Path(tempfile.mktemp(suffix=".json", prefix=f"test_{name}_"))
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return path


def run_case(name, obj, expect_pass):
    path = write_temp(obj, name)
    try:
        result = validate_report(str(path))
        passed = result == expect_pass
        status = "PASS" if passed else "FAIL"
        direction = "expected-pass" if expect_pass else "expected-fail"
        print(f"{status} {direction} case: {name}")
        return passed
    finally:
        path.unlink(missing_ok=True)


def base_report(**overrides):
    """Create a base verification report for testing."""
    report = {
        "record_kind": "verification_report_v2",
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-hash-source-001",
        "reporter": {"name": "test-agent", "type": "ai_agent"},
        "discovery_provenance": {"source": "human_directed", "solicited": True},
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
        "confidential_challenge": {"performed": False},
        "celestial_witness": {"performed": False},
        "limitations": ["test"],
        "claims_not_made": ["test"],
        "authority_boundary_preserved": True
    }
    report.update(overrides)
    return report


def main():
    ok = True

    # === PASS cases ===

    # 1. d2_public_covenant_manifest_hash_pass
    ok &= run_case("d2_public_covenant_manifest_hash_pass", base_report(
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "github-mirror",
            "data_sources": ["github.com/thechurchofagi/trinity-accord"],
            "access_paths": ["https://github.com/..."],
            "method": "SHA256 hash comparison of GitHub mirror files — D2 GitHub mirror SHA-256 hash match.",
            "evidence": [],
            "limitations": ["GitHub mirror only"],
            "claims_not_made": ["direct Arweave verification"]
        }],
        hashes_computed=[{
            "artifact": "arweave-backup/files/public_covenant_archive.zip",
            "algorithm": "SHA-256",
            "expected": "ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263",
            "computed": "ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263",
            "command": "sha256sum ...",
            "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    ), True)

    # 2. d2_verification_kit_manifest_hash_pass
    ok &= run_case("d2_verification_kit_manifest_hash_pass", base_report(
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "github-mirror",
            "data_sources": ["github.com/thechurchofagi/trinity-accord"],
            "access_paths": ["https://github.com/..."],
            "method": "SHA256 hash comparison — D2 GitHub mirror SHA-256 hash match.",
            "evidence": [],
            "limitations": ["GitHub mirror only"],
            "claims_not_made": ["direct Arweave verification"]
        }],
        hashes_computed=[{
            "artifact": "arweave-backup/files/verification_kit.tar.gz",
            "algorithm": "SHA-256",
            "expected": "ef68b69fe1cdd2523724dee511c9e8ea7bae2cceaff794664107970b18c61931",
            "computed": "ef68b69fe1cdd2523724dee511c9e8ea7bae2cceaff794664107970b18c61931",
            "command": "sha256sum ...",
            "match": True,
            "expected_hash_source": "api/evidence-manifest.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    ), True)

    # 3. repository_snapshot_manifest_hash_pass
    ok &= run_case("repository_snapshot_manifest_hash_pass", base_report(
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "repo-snapshot",
            "data_sources": ["repository"],
            "access_paths": ["local"],
            "method": "SHA256 hash comparison — repository snapshot integrity.",
            "evidence": [],
            "limitations": ["repository snapshot only"],
            "claims_not_made": ["canonical mirror verification", "direct Arweave verification"]
        }],
        hashes_computed=[{
            "artifact": "index.md",
            "algorithm": "SHA-256",
            "expected": "9d5b3da041c14c942cb0899d1dde8f1b080e9462ba465ce6ce07f36c52dd51d6",
            "computed": "9d5b3da041c14c942cb0899d1dde8f1b080e9462ba465ce6ce07f36c52dd51d6",
            "command": "sha256sum index.md",
            "match": True,
            "expected_hash_source": "api/repository-artifact-hashes.json",
            "expected_hash_authority_class": "repository_manifest_hash"
        }]
    ), True)

    # 4. v3_hash_observation_no_d2_pass
    ok &= run_case("v3_hash_observation_no_d2_pass", base_report(
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D1",
            "target_id": "repo-file",
            "data_sources": ["repository"],
            "access_paths": ["local"],
            "method": "SHA256 hash observation of repository file.",
            "evidence": [],
            "limitations": ["hash observation only"],
            "claims_not_made": ["D2 manifest verification"]
        }],
        hashes_computed=[{
            "artifact": "agent-brief.md",
            "algorithm": "SHA-256",
            "expected": "21e001f42125bc02e5b04f199c3005c0c1d38cac0bab2c9e17e312bffb116b77",
            "computed": "21e001f42125bc02e5b04f199c3005c0c1d38cac0bab2c9e17e312bffb116b77",
            "command": "sha256sum agent-brief.md",
            "match": True,
            "expected_hash_source": "report-declared",
            "expected_hash_authority_class": "report_declared_snapshot_hash"
        }]
    ), True)

    # === FAIL cases ===

    # 5. d2_unknown_hash_source_fail
    ok &= run_case("d2_unknown_hash_source_fail", base_report(
        protocol_level_claimed="V3",
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "test",
            "data_sources": [],
            "access_paths": [],
            "method": "D2 manifest verification",
            "evidence": [],
            "limitations": [],
            "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "test.zip",
            "algorithm": "SHA-256",
            "expected": "xxx",
            "computed": "xxx",
            "command": "sha256sum ...",
            "match": True,
            "expected_hash_source": "unknown",
            "expected_hash_authority_class": "unknown"
        }]
    ), False)

    # 6. d2_derived_same_run_fail
    ok &= run_case("d2_derived_same_run_fail", base_report(
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "test",
            "data_sources": [],
            "access_paths": [],
            "method": "D2 manifest verification",
            "evidence": [],
            "limitations": [],
            "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "test.zip",
            "algorithm": "SHA-256",
            "expected": "xxx",
            "computed": "xxx",
            "command": "sha256sum ...",
            "match": True,
            "expected_hash_source": "self-computed",
            "expected_hash_authority_class": "derived_during_this_run"
        }]
    ), False)

    # 7. repository_file_d2_without_repo_manifest_fail
    ok &= run_case("repository_file_d2_without_repo_manifest_fail", base_report(
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "repo-file",
            "data_sources": [],
            "access_paths": [],
            "method": "D2 manifest verification",
            "evidence": [],
            "limitations": [],
            "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "index.md",
            "algorithm": "SHA-256",
            "expected": "aaa",
            "computed": "aaa",
            "command": "sha256sum index.md",
            "match": True,
            "expected_hash_source": "report-declared",
            "expected_hash_authority_class": "report_declared_snapshot_hash"
        }]
    ), False)

    # 8. repository_snapshot_claims_canonical_fail
    ok &= run_case("repository_snapshot_claims_canonical_fail", base_report(
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "repo-file",
            "data_sources": [],
            "access_paths": [],
            "method": "canonical mirror verification",
            "evidence": [],
            "limitations": [],
            "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "index.md",
            "algorithm": "SHA-256",
            "expected": "aaa",
            "computed": "aaa",
            "command": "sha256sum index.md",
            "match": True,
            "expected_hash_source": "api/repository-artifact-hashes.json",
            "expected_hash_authority_class": "repository_manifest_hash"
        }]
    ), False)

    # 9. github_d2_claims_arweave_fail
    ok &= run_case("github_d2_claims_arweave_fail", base_report(
        fallbacks_used=["github"],
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "github-mirror",
            "data_sources": ["github"],
            "access_paths": [],
            "method": "direct arweave verification completed",
            "evidence": [],
            "limitations": [],
            "claims_not_made": []
        }],
        hashes_computed=[{
            "artifact": "arweave-backup/files/public_covenant_archive.zip",
            "algorithm": "SHA-256",
            "expected": "abc",
            "computed": "abc",
            "command": "sha256sum ...",
            "match": True,
            "expected_hash_source": "api/hashes.json",
            "expected_hash_authority_class": "canonical_manifest_hash"
        }]
    ), False)

    # 10. multi_artifact_v3_single_artifact_wording_fail
    ok &= run_case("multi_artifact_v3_single_artifact_wording_fail", base_report(
        component_findings=[{
            "component": "digital_mirrors",
            "level_claimed": "D2",
            "target_id": "multi",
            "data_sources": [],
            "access_paths": [],
            "method": "V3_single_artifact_check",
            "evidence": [],
            "limitations": [],
            "claims_not_made": []
        }],
        hashes_computed=[
            {
                "artifact": "file1.zip",
                "algorithm": "SHA-256",
                "expected": "aaa",
                "computed": "aaa",
                "command": "sha256sum ...",
                "match": True,
                "expected_hash_source": "api/hashes.json",
                "expected_hash_authority_class": "canonical_manifest_hash"
            },
            {
                "artifact": "file2.tar.gz",
                "algorithm": "SHA-256",
                "expected": "bbb",
                "computed": "bbb",
                "command": "sha256sum ...",
                "match": True,
                "expected_hash_source": "api/hashes.json",
                "expected_hash_authority_class": "canonical_manifest_hash"
            }
        ]
    ), False)

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — hash source semantics test cases passed.")
        return 0
    print("FINAL: FAIL — hash source semantics test cases failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
