#!/usr/bin/env python3
"""Validate VERIFY-RELEASE-REPORT.json against schema and invariants.

Usage:
  python3 scripts/validate_verify_release_report.py --report VERIFY-RELEASE-REPORT.json
  python3 scripts/validate_verify_release_report.py --self-test
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "api" / "verify-release-report-schema.v1.json"

REQUIRED_FIELDS = [
    "schema", "release_tag", "verification_scope", "cid_check_enabled",
    "status", "assets_expected", "assets_verified",
    "car_files_expected", "car_files_checked",
    "sha256_pass", "size_pass", "errors", "does_not_prove", "limitations",
    "report_status", "is_current", "historical_report_only",
    "current_status_url", "corrections_index_url",
]

VALID_SCOPES = [
    "hash_size_only", "hash_size_and_metadata_cid",
    "hash_size_and_full_dag", "full_evidence_chain",
]

VALID_REPORT_STATUSES = {"current", "historical", "superseded", "revoked", "invalidated"}
NON_CURRENT_REPORT_STATUSES = {"historical", "superseded", "revoked", "invalidated"}


def validate_report(report):
    errors = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in report:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors

    # Schema version
    if report.get("schema") != "verify-release-report-v3":
        errors.append(f"Unexpected schema: {report.get('schema')}")

    # Status
    if report["status"] not in ("PASS", "FAIL"):
        errors.append(f"Invalid status: {report['status']}")

    # Scope
    if report["verification_scope"] not in VALID_SCOPES:
        errors.append(f"Invalid verification_scope: {report['verification_scope']}")

    # does_not_prove
    dnp = report.get("does_not_prove", [])
    if not isinstance(dnp, list) or len(dnp) == 0:
        errors.append("does_not_prove must be non-empty array")

    # limitations
    lim = report.get("limitations", [])
    if not isinstance(lim, list) or len(lim) == 0:
        errors.append("limitations must be non-empty array")

    # PASS invariants
    if report["status"] == "PASS":
        if len(report.get("errors", [])) > 0:
            errors.append("PASS but errors non-empty")

        if report["assets_verified"] != report["assets_expected"]:
            errors.append(f"PASS but assets_verified ({report['assets_verified']}) != assets_expected ({report['assets_expected']})")

        if report["car_files_checked"] != report["car_files_expected"]:
            errors.append(f"PASS but car_files_checked ({report['car_files_checked']}) != car_files_expected ({report['car_files_expected']})")

        if report["sha256_pass"] != report["car_files_expected"]:
            errors.append(f"PASS but sha256_pass ({report['sha256_pass']}) != car_files_expected ({report['car_files_expected']})")

        if report["size_pass"] != report["car_files_expected"]:
            errors.append(f"PASS but size_pass ({report['size_pass']}) != car_files_expected ({report['car_files_expected']})")

        if report.get("cid_check_enabled") and report.get("metadata_cid_fail", 0) != 0:
            errors.append(f"PASS with cid_check_enabled but metadata_cid_fail={report.get('metadata_cid_fail')}")

    # Scope boundary
    if report["verification_scope"] == "hash_size_only":
        dnp_text = " ".join(dnp).lower()
        if "cid" not in dnp_text and "dag" not in dnp_text:
            errors.append("hash_size_only scope but does_not_prove does not mention CID/DAG")

    # TA-REDTEAM-2026-012: report lifecycle validation (mandatory)
    report_status = report.get("report_status")
    is_current_val = report.get("is_current")
    historical_report_only = report.get("historical_report_only")

    if report_status not in VALID_REPORT_STATUSES:
        errors.append(f"report_status must be one of {sorted(VALID_REPORT_STATUSES)}, got: {report_status}")

    # PASS reports must be current
    if report["status"] == "PASS":
        if report_status != "current":
            errors.append(f"PASS report must have report_status='current', got: '{report_status}'")
        if is_current_val is not True:
            errors.append("PASS report must have is_current=true")
        if historical_report_only is not False:
            errors.append("PASS current report must have historical_report_only=false")

    # Non-current reports
    if report_status in NON_CURRENT_REPORT_STATUSES:
        if is_current_val is not False:
            errors.append(f"non-current report_status '{report_status}' requires is_current=false")
        if historical_report_only is not True:
            errors.append(f"non-current report_status '{report_status}' requires historical_report_only=true")

    # URL check
    for field in ["current_status_url", "corrections_index_url"]:
        value = report.get(field)
        if not isinstance(value, str) or not value.startswith("https://www.trinityaccord.org/api/corrections-index.json"):
            errors.append(f"{field} must point to corrections-index.json")

    # Revoked requires revocation_reason
    if report_status == "revoked":
        if not report.get("revocation_reason"):
            errors.append("revoked report requires revocation_reason")

    # Superseded requires superseded_by + supersession_reason
    if report_status == "superseded":
        if report.get("superseded_by") is None and not report.get("supersession_reason"):
            errors.append("superseded report requires superseded_by or supersession_reason")
        if not report.get("supersession_reason"):
            errors.append("superseded report requires supersession_reason")

    # Invalidated requires invalidation_reason
    if report_status == "invalidated":
        if not report.get("invalidation_reason"):
            errors.append("invalidated report requires invalidation_reason")

    return errors


def self_test():
    print("Running report invariant self-tests...")

    # Test 1: PASS with errors -> FAIL
    r = make_valid_report()
    r["errors"] = [{"type": "test_error"}]
    errs = validate_report(r)
    assert any("errors non-empty" in e for e in errs), f"Expected errors non-empty: {errs}"
    print("  ✓ PASS with errors rejected")

    # Test 2: PASS with count mismatch -> FAIL
    r = make_valid_report()
    r["assets_verified"] = 174
    errs = validate_report(r)
    assert any("assets_verified" in e for e in errs), f"Expected count mismatch: {errs}"
    print("  ✓ PASS with asset count mismatch rejected")

    # Test 3: PASS with sha256 mismatch -> FAIL
    r = make_valid_report()
    r["sha256_pass"] = 349
    errs = validate_report(r)
    assert any("sha256_pass" in e for e in errs), f"Expected sha256 mismatch: {errs}"
    print("  ✓ PASS with sha256 count mismatch rejected")

    # Test 4: hash_size_only without CID/DAG in does_not_prove -> FAIL
    r = make_valid_report()
    r["does_not_prove"] = ["independent attestation"]
    errs = validate_report(r)
    assert any("CID/DAG" in e for e in errs), f"Expected CID/DAG boundary: {errs}"
    print("  ✓ hash_size_only without CID/DAG boundary rejected")

    # Test 5: Valid report passes
    r = make_valid_report()
    errs = validate_report(r)
    assert len(errs) == 0, f"Expected no errors: {errs}"
    print("  ✓ Valid report passes")

    # Test 6: FAIL status with errors is OK
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    errs = validate_report(r)
    assert len(errs) == 0, f"Expected no errors for FAIL: {errs}"
    print("  ✓ FAIL with errors accepted")

    # Test 7: Missing required field
    r = make_valid_report()
    del r["verification_scope"]
    errs = validate_report(r)
    assert any("verification_scope" in e for e in errs), f"Expected missing field: {errs}"
    print("  ✓ Missing required field rejected")

    # Test 8: cid_check + metadata_cid_fail != 0 with PASS
    r = make_valid_report()
    r["cid_check_enabled"] = True
    r["metadata_cid_fail"] = 1
    r["optional_checks"] = ["metadata root CID strict"]
    errs = validate_report(r)
    assert any("metadata_cid_fail" in e for e in errs), f"Expected CID fail: {errs}"
    print("  ✓ PASS with CID check + CID fail rejected")

    # TA-REDTEAM-2026-012: lifecycle self-tests
    # Test 9: PASS current report accepted
    r = make_valid_report()
    r["report_status"] = "current"
    r["is_current"] = True
    r["historical_report_only"] = False
    errs = validate_report(r)
    assert len(errs) == 0, f"Expected no errors: {errs}"
    print("  ✓ PASS current report accepted")

    # Test 10: PASS report missing report_status (lifecycle required = rejected)
    r = make_valid_report()
    del r["report_status"]
    errs = validate_report(r)
    assert any("report_status" in e for e in errs), f"Expected missing report_status: {errs}"
    print("  ✓ PASS report missing lifecycle fields rejected")

    # Test 11: revoked PASS report with is_current=true rejected
    r = make_valid_report()
    r["report_status"] = "revoked"
    r["is_current"] = True
    r["historical_report_only"] = True
    r["revocation_reason"] = "Compromised."
    errs = validate_report(r)
    assert any("PASS" in e and "current" in e for e in errs), f"Expected PASS current rejection: {errs}"
    print("  ✓ revoked PASS report with is_current=true rejected")

    # Test 12: revoked report missing revocation_reason
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    r["report_status"] = "revoked"
    r["is_current"] = False
    r["historical_report_only"] = True
    errs = validate_report(r)
    assert any("revocation_reason" in e for e in errs), f"Expected revocation_reason: {errs}"
    print("  ✓ revoked report missing revocation_reason rejected")

    # Test 13: superseded report missing superseded_by
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    r["report_status"] = "superseded"
    r["is_current"] = False
    r["historical_report_only"] = True
    errs = validate_report(r)
    assert any("superseded" in e.lower() for e in errs), f"Expected superseded rejection: {errs}"
    print("  ✓ superseded report missing superseded_by rejected")

    # Test 14: invalidated report missing invalidation_reason
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    r["report_status"] = "invalidated"
    r["is_current"] = False
    r["historical_report_only"] = True
    errs = validate_report(r)
    assert any("invalidation_reason" in e for e in errs), f"Expected invalidation_reason: {errs}"
    print("  ✓ invalidated report missing invalidation_reason rejected")

    # Test 15: historical_report_only must be true for non-current
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    r["report_status"] = "historical"
    r["is_current"] = False
    r["historical_report_only"] = False
    errs = validate_report(r)
    assert any("historical_report_only" in e for e in errs), f"Expected historical_report_only: {errs}"
    print("  ✓ historical_report_only=false for non-current rejected")

    print("\nVALIDATE_VERIFY_RELEASE_REPORT_SELF_TEST_OK")


def make_valid_report():
    return {
        "schema": "verify-release-report-v3",
        "release_tag": "nft-arweave-mirror-175-v1",
        "generated_at": "2026-05-10T00:00:00Z",
        "verification_scope": "hash_size_only",
        "cid_check_enabled": False,
        "full_dag_check_enabled": False,
        "supported_manifest_schema": "trinity-release-manifest-v1",
        "status": "PASS",
        "assets_expected": 175,
        "assets_verified": 175,
        "car_files_expected": 350,
        "car_files_checked": 350,
        "sha256_pass": 350,
        "size_pass": 350,
        "metadata_cid_pass": None,
        "metadata_cid_fail": None,
        "media_cid_audit_pass": None,
        "media_cid_audit_warning": None,
        "required_checks": ["test"],
        "optional_checks": [],
        "does_not_prove": [
            "independent attestation",
            "CID/root/DAG correctness",
            "on-chain evidence or full evidence chain",
        ],
        "limitations": [
            "GitHub Release asset availability is checked through GitHub API at verification time.",
        ],
        "errors": [],
        "report_status": "current",
        "is_current": True,
        "historical_report_only": False,
        "current_status_url": "https://www.trinityaccord.org/api/corrections-index.json",
        "corrections_index_url": "https://www.trinityaccord.org/api/corrections-index.json",
    }


def main():
    if "--self-test" in sys.argv:
        self_test()
        return

    if "--report" not in sys.argv:
        print("Usage: python3 scripts/validate_verify_release_report.py --report <path>")
        print("       python3 scripts/validate_verify_release_report.py --self-test")
        sys.exit(1)

    idx = sys.argv.index("--report")
    if idx + 1 >= len(sys.argv):
        print("Missing --report path")
        sys.exit(1)

    report_path = Path(sys.argv[idx + 1])
    if not report_path.exists():
        print(f"FAIL: Report not found: {report_path}")
        sys.exit(1)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    errors = validate_report(report)

    if errors:
        print("FAIL: Report validation errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("VERIFY_RELEASE_REPORT_VALID_OK")


if __name__ == "__main__":
    main()
