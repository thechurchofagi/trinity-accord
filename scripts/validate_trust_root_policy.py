#!/usr/bin/env python3
"""Validate trust-root-policy.json structure and references."""
import json
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SHA256_HEX_LEN = 64


def _file_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


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

    # TA-REDTEAM-2026-012: historical roots validation
    historical_roots = data.get("historical_roots")
    if not isinstance(historical_roots, list):
        errors.append("historical_roots must be a list")
    else:
        current_roots = [r for r in historical_roots if isinstance(r, dict) and r.get("is_current") is True]
        if len(current_roots) == 0:
            errors.append("historical_roots must contain at least one current root")
        elif len(current_roots) > 1:
            errors.append(f"historical_roots must contain exactly one current root, found {len(current_roots)}")

        for i, root in enumerate(historical_roots):
            if not isinstance(root, dict):
                errors.append(f"historical_roots[{i}] must be object")
                continue

            prefix = f"historical_roots[{i}]"

            # Check sha256 fields are 64 hex chars
            for sha_field in ["authority_manifest_sha256", "btc_signature_sha256", "eth_witness_sha256"]:
                val = root.get(sha_field)
                if val is not None:
                    if not isinstance(val, str) or len(val) != SHA256_HEX_LEN:
                        errors.append(f"{prefix}.{sha_field} must be {SHA256_HEX_LEN} hex chars")
                    elif not all(c in "0123456789abcdefABCDEF" for c in val):
                        errors.append(f"{prefix}.{sha_field} must be valid hex")

            # Current root checks
            if root.get("is_current") is True:
                if root.get("historical_record_only") is not False:
                    errors.append(f"{prefix}: current root must have historical_record_only=false")

                # Verify sha256 matches actual files
                sha_map = {
                    "authority_manifest_sha256": current_root.get("authority_manifest_path"),
                    "btc_signature_sha256": current_root.get("btc_signature_path"),
                    "eth_witness_sha256": current_root.get("eth_witness_path"),
                }
                for sha_field, rel_path in sha_map.items():
                    expected = root.get(sha_field)
                    if expected and rel_path:
                        actual_path = ROOT / rel_path
                        if actual_path.exists():
                            actual = _file_sha256(actual_path)
                            if expected.lower() != actual.lower():
                                errors.append(
                                    f"{prefix}.{sha_field} mismatch: expected {expected[:16]}... "
                                    f"but actual file hash is {actual[:16]}..."
                                )

            # Non-current root checks
            if root.get("is_current") is False:
                if root.get("historical_record_only") is not True:
                    errors.append(f"{prefix}: non-current root must have historical_record_only=true")

                # Revoked roots require reason
                if root.get("status") == "revoked":
                    if not root.get("revocation_reason"):
                        errors.append(f"{prefix}: revoked root requires revocation_reason")

                # Superseded roots require successor
                if root.get("status") == "superseded":
                    if root.get("superseded_by") is None and not root.get("supersession_reason"):
                        errors.append(f"{prefix}: superseded root requires superseded_by or supersession_reason")

    return errors


def self_test():
    print("Running trust-root policy validator self-test...")

    # Load actual current_root paths for self-test
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
        "historical_roots": [],
        "limitations": ["test limitation"]
    }
    errs = validate(valid)
    # Empty historical_roots list → should fail (no current root)
    assert any("at least one current root" in e for e in errs), f"should require current root: {errs}"

    # Add valid current root
    valid["historical_roots"] = [{
        "root_id": "test-current",
        "status": "current",
        "is_current": True,
        "historical_record_only": False,
        "effective_from": "2026-05-10",
        "authority_manifest_sha256": "41f95905e50cc699a7e6a3fcb0bd8633cf36170d3ef41170cd373467f8528b33",
        "btc_signature_sha256": "8e70e0e0d8f8e0cdd8e388ee4c462f86358a6ac9bb6231701d7876439ada561b",
        "eth_witness_sha256": "3c187c6b764a1d53984588875c1c1fed3f1c91fd165512ad8dfa4f279542a65f",
        "reason": "Test current root."
    }]
    errs = validate(valid)
    assert not errs, f"valid should pass: {errs}"
    print("  ✓ valid with current root passes")

    # Two current roots
    import copy
    two_current = copy.deepcopy(valid)
    two_current["historical_roots"].append(copy.deepcopy(valid["historical_roots"][0]))
    errs = validate(two_current)
    assert any("exactly one current root" in e for e in errs), f"should reject two current: {errs}"
    print("  ✓ two current roots rejected")

    # Current root hash mismatch
    bad_hash = copy.deepcopy(valid)
    bad_hash["historical_roots"][0]["authority_manifest_sha256"] = "0" * 64
    errs = validate(bad_hash)
    assert any("mismatch" in e for e in errs), f"should reject hash mismatch: {errs}"
    print("  ✓ current root hash mismatch rejected")

    # Missing schema
    bad_schema = dict(valid, schema="wrong")
    errs = validate(bad_schema)
    assert any("schema" in e for e in errs), f"should reject bad schema: {errs}"
    print("  ✓ bad schema rejected")

    # Missing successor root
    no_successor = copy.deepcopy(valid)
    no_successor["rotation_policy"]["requires_successor_root_record"] = False
    errs = validate(no_successor)
    assert any("successor" in e for e in errs), f"should reject no successor: {errs}"
    print("  ✓ no successor root rejected")

    # Missing CODEOWNERS review
    no_co = copy.deepcopy(valid)
    no_co["rotation_policy"]["requires_codeowners_review"] = False
    errs = validate(no_co)
    assert any("codeowners" in e.lower() for e in errs), f"should reject no CODEOWNERS: {errs}"
    print("  ✓ no CODEOWNERS rejected")

    # Missing revocation
    no_rvp = copy.deepcopy(valid)
    del no_rvp["revocation_policy"]
    errs = validate(no_rvp)
    assert any("revocation" in e for e in errs), f"should reject no revocation: {errs}"
    print("  ✓ no revocation rejected")

    # Empty limitations
    no_lim = dict(valid, limitations=[])
    errs = validate(no_lim)
    assert any("limitations" in e for e in errs), f"should reject empty limitations: {errs}"
    print("  ✓ empty limitations rejected")

    # Revoked root with is_current=true
    revoked_current = copy.deepcopy(valid)
    revoked_root = {
        "root_id": "revoked-root",
        "status": "revoked",
        "is_current": True,
        "historical_record_only": False,
        "effective_from": "2026-01-01",
        "reason": "Test"
    }
    revoked_current["historical_roots"].append(revoked_root)
    errs = validate(revoked_current)
    # Should fail: two current roots
    assert any("exactly one current root" in e for e in errs), f"should reject revoked is_current=true: {errs}"
    print("  ✓ revoked root with is_current=true rejected (two current roots)")

    # Superseded root missing successor
    superseded = copy.deepcopy(valid)
    superseded["historical_roots"].append({
        "root_id": "old-root",
        "status": "superseded",
        "is_current": False,
        "historical_record_only": True,
        "effective_from": "2026-01-01",
        "reason": "Test"
    })
    errs = validate(superseded)
    assert any("superseded" in e.lower() and "superseded_by" in e for e in errs), f"should reject superseded without successor: {errs}"
    print("  ✓ superseded root missing successor rejected")

    print("\nPASS: trust-root policy validator self-test")
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
