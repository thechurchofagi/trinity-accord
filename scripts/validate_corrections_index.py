#!/usr/bin/env python3
"""Validate api/corrections-index.json (TA-REDTEAM-2026-012).

Usage:
  python3 scripts/validate_corrections_index.py
  python3 scripts/validate_corrections_index.py --self-test
  python3 scripts/validate_corrections_index.py --index path/to/index.json
"""
import json
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "api" / "corrections-index.json"

REQUIRED_SCHEMA = "trinity-accord.corrections-index.v1"
REQUIRED_VERSION = "v1"

CURRENT_STATUSES = {"current", "accepted_current"}
NON_CURRENT_STATUSES = {"superseded", "revoked", "invalidated", "withdrawn", "historical_only", "closed_test_record"}


def _stable_json(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate(index_path: str | Path) -> list[str]:
    """Validate corrections-index.json. Returns list of errors."""
    errors = []
    data = json.loads(Path(index_path).read_text(encoding="utf-8"))

    # Schema
    if data.get("schema") != REQUIRED_SCHEMA:
        errors.append(f"schema must be {REQUIRED_SCHEMA}, got: {data.get('schema')}")

    # Version
    if data.get("version") != REQUIRED_VERSION:
        errors.append(f"version must be {REQUIRED_VERSION}, got: {data.get('version')}")

    # source_digest: recompute and verify
    stored_digest = data.get("source_digest")
    if not stored_digest:
        errors.append("source_digest is missing")
    else:
        recomputed = {k: v for k, v in data.items() if k != "source_digest"}
        expected_digest = hashlib.sha256(_stable_json(recomputed).encode()).hexdigest()[:16]
        if stored_digest != expected_digest:
            errors.append(f"source_digest mismatch: stored={stored_digest}, expected={expected_digest}")

    # limitations and does_not_prove non-empty
    limitations = data.get("limitations", [])
    if not isinstance(limitations, list) or len(limitations) == 0:
        errors.append("limitations must be non-empty list")

    does_not_prove = data.get("does_not_prove", [])
    if not isinstance(does_not_prove, list) or len(does_not_prove) == 0:
        errors.append("does_not_prove must be non-empty list")

    # Validate records
    records = data.get("records", [])
    if not isinstance(records, list):
        errors.append("records must be a list")
    else:
        for i, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"records[{i}] must be object")
                continue
            errors.extend(_validate_record(record, f"records[{i}]"))

    # Validate known_non_current_records
    known = data.get("known_non_current_records", [])
    if not isinstance(known, list):
        errors.append("known_non_current_records must be a list")
    else:
        for i, record in enumerate(known):
            if not isinstance(record, dict):
                errors.append(f"known_non_current_records[{i}] must be object")
                continue
            errors.extend(_validate_record(record, f"known_non_current_records[{i}]"))

    # no_hard_delete_policy
    policy = data.get("no_hard_delete_policy", {})
    if not isinstance(policy, dict) or not policy.get("enabled"):
        errors.append("no_hard_delete_policy.enabled must be true")

    return errors


def _validate_record(record: dict, prefix: str) -> list[str]:
    """Validate a single correction/known-non-current record."""
    errors = []

    # Required fields for all records
    for field in ["id", "record_type", "status", "is_current", "historical_record_only", "reason"]:
        if field not in record:
            errors.append(f"{prefix}: missing required field '{field}'")

    if errors:
        return errors

    status = record.get("status")
    is_current = record.get("is_current")
    historical = record.get("historical_record_only")

    # Non-current records
    if status in NON_CURRENT_STATUSES:
        if is_current is not False:
            errors.append(f"{prefix}: non-current status '{status}' requires is_current=false")
        if historical is not True:
            errors.append(f"{prefix}: non-current status '{status}' requires historical_record_only=true")

    # Superseded requires superseded_by or explicit reason
    if status == "superseded":
        if record.get("superseded_by") is None and not record.get("reason"):
            errors.append(f"{prefix}: superseded requires superseded_by or reason")

    return errors


def run_self_test() -> bool:
    """Run self-tests for the corrections index validator."""
    import tempfile
    import copy

    passed = 0
    failed = 0

    # Valid empty index template
    valid_template = {
        "schema": "trinity-accord.corrections-index.v1",
        "version": "v1",
        "source_digest": "PLACEHOLDER",
        "source_digest_algorithm": "sha256(canonical_json_without_source_digest)",
        "non_amending_boundary": True,
        "canonical_authority": "Bitcoin Originals only",
        "not_instruction_override": True,
        "current_status": {"formal_corrections": 0},
        "records": [],
        "known_non_current_records": [],
        "no_hard_delete_policy": {"enabled": True},
        "limitations": ["test"],
        "does_not_prove": ["test"],
    }

    def write_temp_with_digest(data):
        """Write temp file with correct source_digest computed from data."""
        d = copy.deepcopy(data)
        d.pop("source_digest", None)
        digest = hashlib.sha256(_stable_json(d).encode()).hexdigest()[:16]
        out = copy.deepcopy(data)
        out["source_digest"] = digest
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(out, f)
        f.close()
        return f.name

    def write_temp_raw(data):
        """Write temp file as-is, without computing digest."""
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, f)
        f.close()
        return f.name

    # 1. Valid empty index accepted
    path = write_temp_with_digest(copy.deepcopy(valid_template))
    errs = validate(path)
    os.unlink(path)
    if not errs:
        print("  PASS: valid empty index accepted")
        passed += 1
    else:
        print(f"  FAIL: valid empty index accepted — {errs}")
        failed += 1

    # 2. Missing source_digest rejected
    bad = copy.deepcopy(valid_template)
    bad.pop("source_digest", None)
    path = write_temp_raw(bad)
    errs = validate(path)
    os.unlink(path)
    if any("source_digest" in e for e in errs):
        print("  PASS: missing source_digest rejected")
        passed += 1
    else:
        print(f"  FAIL: missing source_digest rejected — {errs}")
        failed += 1

    # 3. Digest mismatch rejected
    bad = copy.deepcopy(valid_template)
    bad["source_digest"] = "0000000000000000"
    path = write_temp_raw(bad)
    errs = validate(path)
    os.unlink(path)
    if any("mismatch" in e for e in errs):
        print("  PASS: digest mismatch rejected")
        passed += 1
    else:
        print(f"  FAIL: digest mismatch rejected — {errs}")
        failed += 1

    # 4. Revoked current=true rejected
    bad = copy.deepcopy(valid_template)
    bad["records"] = [{
        "id": "test", "record_type": "revocation", "status": "revoked",
        "is_current": True, "historical_record_only": True, "reason": "test"
    }]
    path = write_temp_with_digest(bad)
    errs = validate(path)
    os.unlink(path)
    if any("is_current" in e for e in errs):
        print("  PASS: revoked current=true rejected")
        passed += 1
    else:
        print(f"  FAIL: revoked current=true rejected — {errs}")
        failed += 1

    # 5. Superseded without reason rejected
    bad = copy.deepcopy(valid_template)
    bad["records"] = [{
        "id": "test", "record_type": "supersession", "status": "superseded",
        "is_current": False, "historical_record_only": True, "reason": ""
    }]
    path = write_temp_with_digest(bad)
    errs = validate(path)
    os.unlink(path)
    if any("superseded" in e.lower() and ("reason" in e.lower() or "superseded_by" in e.lower()) for e in errs):
        print("  PASS: superseded without reason rejected")
        passed += 1
    else:
        print(f"  FAIL: superseded without reason rejected — {errs}")
        failed += 1

    # 6. Non-current without historical_record_only rejected
    bad = copy.deepcopy(valid_template)
    bad["records"] = [{
        "id": "test", "record_type": "revocation", "status": "revoked",
        "is_current": False, "historical_record_only": False, "reason": "test"
    }]
    path = write_temp_with_digest(bad)
    errs = validate(path)
    os.unlink(path)
    if any("historical_record_only" in e for e in errs):
        print("  PASS: non-current without historical_record_only rejected")
        passed += 1
    else:
        print(f"  FAIL: non-current without historical_record_only rejected — {errs}")
        failed += 1

    print(f"\nSelf-test: {passed} passed, {failed} failed")
    return failed == 0


def main() -> int:
    if "--self-test" in sys.argv:
        return 0 if run_self_test() else 1

    index_path = DEFAULT_INDEX
    if "--index" in sys.argv:
        idx = sys.argv.index("--index")
        if idx + 1 < len(sys.argv):
            index_path = sys.argv[idx + 1]

    if not Path(index_path).exists():
        print(f"FAIL: file not found: {index_path}")
        return 1

    errors = validate(index_path)
    if errors:
        print("CORRECTIONS_INDEX_INVALID")
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    print("CORRECTIONS_INDEX_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
