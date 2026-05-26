#!/usr/bin/env python3
"""Validate api/recovery-index.json (TA-REDTEAM-2026-014).

Usage:
  python3 scripts/validate_recovery_index.py
  python3 scripts/validate_recovery_index.py --self-test
  python3 scripts/validate_recovery_index.py --index path/to/index.json
"""
import json
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "api" / "recovery-index.json"

REQUIRED_SCHEMA = "trinity-accord.recovery-index.v1"
REQUIRED_VERSION = "v1"


def _stable_json(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate(index_path: str | Path) -> list[str]:
    """Validate recovery-index.json. Returns list of errors."""
    errors = []
    data = json.loads(Path(index_path).read_text(encoding="utf-8"))

    # Schema
    if data.get("schema") != REQUIRED_SCHEMA:
        errors.append(f"schema must be {REQUIRED_SCHEMA}, got: {data.get('schema')}")

    # Version
    if data.get("version") != REQUIRED_VERSION:
        errors.append(f"version must be {REQUIRED_VERSION}, got: {data.get('version')}")

    # source_digest
    stored_digest = data.get("source_digest")
    if not stored_digest:
        errors.append("source_digest is missing")
    else:
        recomputed = {k: v for k, v in data.items() if k != "source_digest"}
        expected_digest = hashlib.sha256(_stable_json(recomputed).encode()).hexdigest()[:16]
        if stored_digest != expected_digest:
            errors.append(f"source_digest mismatch: stored={stored_digest}, expected={expected_digest}")

    # source_digest_algorithm
    algo = data.get("source_digest_algorithm", "")
    if "sha256" not in algo:
        errors.append("source_digest_algorithm must include sha256")

    # non_amending_boundary
    if data.get("non_amending_boundary") is not True:
        errors.append("non_amending_boundary must be true")

    # canonical_authority
    if data.get("canonical_authority") != "Bitcoin Originals only":
        errors.append("canonical_authority must be 'Bitcoin Originals only'")

    # minimal_trusted_bootstrap_root
    root = data.get("minimal_trusted_bootstrap_root", {})
    originals = root.get("bitcoin_originals", [])
    if len(originals) != 3:
        errors.append(f"bitcoin_originals must have exactly 3 entries, got {len(originals)}")

    if not root.get("bitcoin_authority_address", "").startswith("bc1"):
        errors.append("bitcoin_authority_address must start with bc1")

    # required_recovery_files must include corrections-index
    req_files = data.get("required_recovery_files", [])
    if not any("corrections-index" in f for f in req_files):
        errors.append("required_recovery_files must include corrections-index")

    # mandatory_recovery_steps must include check_corrections_index
    steps = data.get("mandatory_recovery_steps", [])
    if "check_corrections_index" not in steps:
        errors.append("mandatory_recovery_steps must include check_corrections_index")

    # recovery_status_values must include full/partial/failed
    statuses = data.get("recovery_status_values", [])
    for required in ["full_recovery", "partial_recovery", "failed_recovery"]:
        if required not in statuses:
            errors.append(f"recovery_status_values must include {required}")

    # limitations and does_not_prove non-empty
    if not data.get("limitations"):
        errors.append("limitations must be non-empty")
    if not data.get("does_not_prove"):
        errors.append("does_not_prove must be non-empty")

    return errors


def self_test():
    """Run self-tests with valid and invalid inputs."""
    import tempfile
    import copy

    valid = json.loads(DEFAULT_INDEX.read_text(encoding="utf-8"))

    # Valid should pass
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(valid, f)
        f.flush()
        errs = validate(f.name)
        if errs:
            print("SELF-TEST FAIL: valid index rejected:", errs)
            return False

    # Missing corrections-index
    bad = copy.deepcopy(valid)
    bad["required_recovery_files"] = [f for f in bad["required_recovery_files"] if "corrections" not in f]
    # Recompute digest
    recomputed = {k: v for k, v in bad.items() if k != "source_digest"}
    bad["source_digest"] = hashlib.sha256(_stable_json(recomputed).encode()).hexdigest()[:16]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(bad, f)
        f.flush()
        errs = validate(f.name)
        if not any("corrections-index" in e for e in errs):
            print("SELF-TEST FAIL: missing corrections-index not caught")
            return False

    # Missing check_corrections_index step
    bad2 = copy.deepcopy(valid)
    bad2["mandatory_recovery_steps"] = [s for s in bad2["mandatory_recovery_steps"] if s != "check_corrections_index"]
    recomputed2 = {k: v for k, v in bad2.items() if k != "source_digest"}
    bad2["source_digest"] = hashlib.sha256(_stable_json(recomputed2).encode()).hexdigest()[:16]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(bad2, f)
        f.flush()
        errs = validate(f.name)
        if not any("check_corrections_index" in e for e in errs):
            print("SELF-TEST FAIL: missing check_corrections_index not caught")
            return False

    # Only 2 bitcoin originals
    bad3 = copy.deepcopy(valid)
    bad3["minimal_trusted_bootstrap_root"]["bitcoin_originals"] = bad3["minimal_trusted_bootstrap_root"]["bitcoin_originals"][:2]
    recomputed3 = {k: v for k, v in bad3.items() if k != "source_digest"}
    bad3["source_digest"] = hashlib.sha256(_stable_json(recomputed3).encode()).hexdigest()[:16]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(bad3, f)
        f.flush()
        errs = validate(f.name)
        if not any("3 entries" in e for e in errs):
            print("SELF-TEST FAIL: only 2 originals not caught")
            return False

    # non_amending_boundary=false
    bad4 = copy.deepcopy(valid)
    bad4["non_amending_boundary"] = False
    recomputed4 = {k: v for k, v in bad4.items() if k != "source_digest"}
    bad4["source_digest"] = hashlib.sha256(_stable_json(recomputed4).encode()).hexdigest()[:16]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(bad4, f)
        f.flush()
        errs = validate(f.name)
        if not any("non_amending_boundary" in e for e in errs):
            print("SELF-TEST FAIL: non_amending_boundary=false not caught")
            return False

    # Digest mismatch
    bad5 = copy.deepcopy(valid)
    bad5["source_digest"] = "0000000000000000"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(bad5, f)
        f.flush()
        errs = validate(f.name)
        if not any("mismatch" in e for e in errs):
            print("SELF-TEST FAIL: digest mismatch not caught")
            return False

    # Missing full_recovery status
    bad6 = copy.deepcopy(valid)
    bad6["recovery_status_values"] = [s for s in bad6["recovery_status_values"] if s != "full_recovery"]
    recomputed6 = {k: v for k, v in bad6.items() if k != "source_digest"}
    bad6["source_digest"] = hashlib.sha256(_stable_json(recomputed6).encode()).hexdigest()[:16]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(bad6, f)
        f.flush()
        errs = validate(f.name)
        if not any("full_recovery" in e for e in errs):
            print("SELF-TEST FAIL: missing full_recovery not caught")
            return False

    print("SELF-TEST PASS")
    return True


def main():
    if "--self-test" in sys.argv:
        ok = self_test()
        sys.exit(0 if ok else 1)

    idx = sys.argv.index("--index") + 1 if "--index" in sys.argv else None
    path = sys.argv[idx] if idx else str(DEFAULT_INDEX)

    errors = validate(path)
    if errors:
        print("RECOVERY_INDEX_INVALID")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("RECOVERY_INDEX_OK")


if __name__ == "__main__":
    main()
