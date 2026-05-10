#!/usr/bin/env python3
"""Validate trust-root-policy.json structure and references."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    errors = []

    # Schema
    if data.get("schema") != "trinity-accord.trust-root-policy.v1":
        errors.append(f"invalid schema: {data.get('schema')}")

    # current_root paths should exist
    current_root = data.get("current_root", {})
    for key, rel_path in current_root.items():
        full = ROOT / rel_path
        if not full.exists():
            errors.append(f"current_root.{key} path does not exist: {rel_path}")

    # rotation_policy checks
    rp = data.get("rotation_policy", {})
    for field in ("requires_successor_root_record", "requires_old_root_reference",
                  "requires_human_review", "requires_codeowners_review",
                  "requires_ci_validators"):
        if not rp.get(field):
            errors.append(f"rotation_policy.{field} must be true")

    # revocation_policy
    rvp = data.get("revocation_policy", {})
    if not rvp:
        errors.append("revocation_policy is missing")
    else:
        for field in ("compromise_response_required", "revoked_roots_must_remain_auditable", "revocation_record_required"):
            if not rvp.get(field):
                errors.append(f"revocation_policy.{field} must be true")

    # non_amending_boundary
    nab = data.get("non_amending_boundary", {})
    if not nab.get("btc_originals_prevail"):
        errors.append("non_amending_boundary.btc_originals_prevail must be true")

    # limitations non-empty
    limitations = data.get("limitations", [])
    if not limitations:
        errors.append("limitations is empty")

    return errors


def self_test():
    print("Running trust-root policy validator self-test...")

    valid = {
        "schema": "trinity-accord.trust-root-policy.v1",
        "status": "active",
        "current_root": {
            "authority_manifest_path": "archive/authority-manifest/authority.jcs.json"
        },
        "rotation_policy": {
            "requires_successor_root_record": True,
            "requires_old_root_reference": True,
            "requires_human_review": True,
            "requires_codeowners_review": True,
            "requires_ci_validators": True
        },
        "revocation_policy": {
            "compromise_response_required": True,
            "revoked_roots_must_remain_auditable": True,
            "revocation_record_required": True
        },
        "non_amending_boundary": {"btc_originals_prevail": True},
        "limitations": ["test limitation"]
    }
    errs = validate(valid)
    assert not errs, f"valid should pass: {errs}"

    # Missing schema
    bad_schema = dict(valid, schema="wrong")
    errs = validate(bad_schema)
    assert any("schema" in e for e in errs), f"should reject bad schema: {errs}"

    # Missing successor root
    import copy
    no_successor = copy.deepcopy(valid)
    no_successor["rotation_policy"]["requires_successor_root_record"] = False
    errs = validate(no_successor)
    assert any("successor" in e for e in errs), f"should reject no successor: {errs}"

    # Missing CODEOWNERS review
    no_co = copy.deepcopy(valid)
    no_co["rotation_policy"]["requires_codeowners_review"] = False
    errs = validate(no_co)
    assert any("codeowners" in e.lower() for e in errs), f"should reject no CODEOWNERS: {errs}"

    # Missing revocation
    no_rvp = copy.deepcopy(valid)
    del no_rvp["revocation_policy"]
    errs = validate(no_rvp)
    assert any("revocation" in e for e in errs), f"should reject no revocation: {errs}"

    # Empty limitations
    no_lim = dict(valid, limitations=[])
    errs = validate(no_lim)
    assert any("limitations" in e for e in errs), f"should reject empty limitations: {errs}"

    print("PASS: trust-root policy validator self-test")
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_trust_root_policy.py [--self-test|<path>]")
        return 1

    if sys.argv[1] == "--self-test":
        return self_test()

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"FAIL: file not found: {path}")
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data)

    if errors:
        print(f"FAIL: {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
