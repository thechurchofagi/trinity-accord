#!/usr/bin/env python3
"""Validate that required public API files have unified metadata fields.

Usage:
  python3 scripts/validate_public_api_metadata.py --self-test
  python3 scripts/validate_public_api_metadata.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_API_REQUIRED = [
    "api/authority.json",
    "api/agent-value.json",
    "api/verification-levels.json",
    "api/echo-types.json",
    "api/evidence-manifest.json",
    "api/hashes.json",
    "api/links.json",
    "api/echo-index.json",
    "api/independent-attestation-index.json",
]

REQUIRED_FIELDS = [
    "schema",
    "version",
    "source_digest",
    "source_digest_algorithm",
    "non_amending_boundary",
    "limitations",
    "does_not_prove",
]

# Schema files are exempt from metadata requirements
SCHEMA_EXEMPT_PATTERN = re.compile(r"schema", re.I)


def validate_file(path: Path) -> list[str]:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{path.name}: JSON parse error: {e}"]

    if not isinstance(data, dict):
        return [f"{path.name}: not a JSON object"]

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"{path.name}: missing required field '{field}'")

    # Validate field types
    if "version" in data and not data["version"]:
        errors.append(f"{path.name}: version is empty")

    if "source_digest" in data:
        digest = data["source_digest"]
        if not re.match(r"^[a-fA-F0-9]{16}$|^[a-fA-F0-9]{64}$", str(digest)):
            errors.append(f"{path.name}: source_digest must be 16 or 64 hex, got: {digest}")

    if "source_digest_algorithm" in data:
        algo = data["source_digest_algorithm"]
        if "sha256" not in algo.lower():
            errors.append(f"{path.name}: source_digest_algorithm must include sha256")

    if "non_amending_boundary" in data:
        if data["non_amending_boundary"] is not True:
            # Check fallback
            if "canonical_authority" not in data or "Bitcoin" not in str(data.get("canonical_authority", "")):
                errors.append(f"{path.name}: non_amending_boundary must be true or have canonical_authority")

    if "limitations" in data:
        if not isinstance(data["limitations"], list) or len(data["limitations"]) == 0:
            errors.append(f"{path.name}: limitations must be non-empty list")

    if "does_not_prove" in data:
        if not isinstance(data["does_not_prove"], list) or len(data["does_not_prove"]) == 0:
            errors.append(f"{path.name}: does_not_prove must be non-empty list")

    return errors


def validate_all() -> list[str]:
    errors = []
    for rel in PUBLIC_API_REQUIRED:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: file not found")
            continue
        errors.extend(validate_file(path))
    return errors


def self_test():
    """Run self-test cases."""
    import tempfile

    def make_api(overrides=None):
        base = {
            "schema": "trinity-accord.test.v1",
            "version": "v1",
            "source_digest": "a7e6f39d82549f46",
            "source_digest_algorithm": "sha256(canonical_json_without_source_digest)",
            "non_amending_boundary": True,
            "limitations": ["test limitation"],
            "does_not_prove": ["test"],
        }
        if overrides:
            base.update(overrides)
        return base

    def check(label, description, ok):
        status = "PASS" if ok else "FAIL"
        print(f"  {'✓' if ok else '✗'} {label}: {description}")
        return ok

    print("Public API metadata validator self-test")
    print("=" * 50)

    all_ok = True

    # Valid
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api()))
    errs = validate_file(p)
    all_ok &= check("META01", "valid metadata passes", len(errs) == 0)
    p.unlink()

    # Missing version
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api({"version": None})))
    errs = validate_file(p)
    # version=None means key exists but empty
    p.write_text(json.dumps(make_api()))
    d = json.loads(p.read_text())
    del d["version"]
    p.write_text(json.dumps(d))
    errs = validate_file(p)
    all_ok &= check("META02", "missing version rejected", any("version" in e for e in errs))
    p.unlink()

    # Missing source_digest
    p = Path(tempfile.mktemp(suffix=".json"))
    d = make_api()
    del d["source_digest"]
    p.write_text(json.dumps(d))
    errs = validate_file(p)
    all_ok &= check("META03", "missing source_digest rejected", any("source_digest" in e and "algorithm" not in e for e in errs))
    p.unlink()

    # Bad digest format
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api({"source_digest": "not-hex"})))
    errs = validate_file(p)
    all_ok &= check("META04", "bad digest format rejected", any("source_digest" in e for e in errs))
    p.unlink()

    # Missing limitations
    p = Path(tempfile.mktemp(suffix=".json"))
    d = make_api()
    del d["limitations"]
    p.write_text(json.dumps(d))
    errs = validate_file(p)
    all_ok &= check("META05", "missing limitations rejected", any("limitations" in e for e in errs))
    p.unlink()

    # Missing does_not_prove
    p = Path(tempfile.mktemp(suffix=".json"))
    d = make_api()
    del d["does_not_prove"]
    p.write_text(json.dumps(d))
    errs = validate_file(p)
    all_ok &= check("META06", "missing does_not_prove rejected", any("does_not_prove" in e for e in errs))
    p.unlink()

    # non_amending_boundary false
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api({"non_amending_boundary": False})))
    errs = validate_file(p)
    all_ok &= check("META07", "non_amending_boundary=false rejected", any("non_amending" in e for e in errs))
    p.unlink()

    print()
    if all_ok:
        print("VALIDATE_PUBLIC_API_METADATA_SELF_TEST_OK")
    else:
        print("VALIDATE_PUBLIC_API_METADATA_SELF_TEST_FAIL")
        sys.exit(1)


def main():
    if "--self-test" in sys.argv:
        self_test()
        return

    errors = validate_all()
    if errors:
        print("FAIL: public API metadata validation errors:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("VALIDATE_PUBLIC_API_METADATA_OK")


if __name__ == "__main__":
    main()
