#!/usr/bin/env python3
"""
Audit 2: TA-AVR Schema Cross-Consistency
Verify TA-AVR schema enums match existing schema/field guide values.

Run:
    python3 scripts/test_ta_avr_schema_cross_consistency.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relpath):
    p = ROOT / relpath
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def walk_find_strings(obj, target_key=None):
    """Recursively find all string values (or values of a specific key)."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if target_key and k == target_key:
                if isinstance(v, str):
                    results.append(v)
                elif isinstance(v, list):
                    results.extend(x for x in v if isinstance(x, str))
            else:
                results.extend(walk_find_strings(v, target_key))
    elif isinstance(obj, list):
        for v in obj:
            results.extend(walk_find_strings(v, target_key))
    return results


def test_receipt_schema_valid():
    """Receipt schema is valid under Draft 2020-12."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  SKIP: jsonschema not installed")
        return True

    schema = load_json("api/agent-verification-receipt-schema.v1.json")
    if schema is None:
        print("  FAIL: receipt schema not found")
        return False
    try:
        Draft202012Validator.check_schema(schema)
        print("  PASS: receipt schema is valid Draft 2020-12")
        return True
    except Exception as e:
        print(f"  FAIL: receipt schema invalid: {e}")
        return False


def test_identity_verification_level_compatible():
    """Receipt identity_verification_level enums compatible with field guide."""
    receipt = load_json("api/agent-verification-receipt-schema.v1.json")
    if receipt is None:
        print("  FAIL: receipt schema not found")
        return False

    # Get receipt enum
    agent_id = receipt.get("properties", {}).get("agent_identity", {})
    ivl = agent_id.get("properties", {}).get("identity_verification_level", {})
    receipt_enum = set(ivl.get("enum", []))

    # Expected from field guide
    expected = {"none", "self_asserted", "stable_account", "signed_statement",
                "institutional_domain", "notarial_identity", "other"}

    missing = expected - receipt_enum
    if missing:
        print(f"  FAIL: receipt missing identity_verification_level values: {missing}")
        return False
    print("  PASS: identity enums compatible")
    return True


def test_authorship_proof_method_compatible():
    """Receipt authorship proof methods compatible with existing schema."""
    receipt = load_json("api/agent-verification-receipt-schema.v1.json")
    if receipt is None:
        print("  FAIL: receipt schema not found")
        return False

    ap = receipt.get("properties", {}).get("authorship_proof", {})
    method = ap.get("properties", {}).get("method", {})
    receipt_enum = set(method.get("enum", []))

    # Required methods from echo-authorship-proof-schema
    required = {"ed25519_signature", "secret_commitment", "self_reported_only"}
    missing = required - receipt_enum
    if missing:
        print(f"  FAIL: receipt missing authorship proof methods: {missing}")
        return False
    print("  PASS: authorship proof enums compatible")
    return True


def test_context_depth_compatible():
    """Receipt context_depth values match context-depth-levels."""
    receipt = load_json("api/agent-verification-receipt-schema.v1.json")
    cdl = load_json("api/context-depth-levels.json")
    if receipt is None or cdl is None:
        print("  FAIL: schema file(s) not found")
        return False

    cr = receipt.get("properties", {}).get("context_readiness", {})
    cd = cr.get("properties", {}).get("context_depth", {})
    receipt_enum = set(cd.get("enum", []))

    expected = set(level["id"] for level in cdl.get("levels", []))
    missing = expected - receipt_enum
    if missing:
        print(f"  FAIL: receipt missing context_depth values: {missing}")
        return False
    print("  PASS: context depth enums compatible")
    return True


def test_crl_compatible():
    """Receipt context_readiness_level values match context-readiness-levels."""
    receipt = load_json("api/agent-verification-receipt-schema.v1.json")
    crl = load_json("api/context-readiness-levels.json")
    if receipt is None or crl is None:
        print("  FAIL: schema file(s) not found")
        return False

    cr = receipt.get("properties", {}).get("context_readiness", {})
    crl_prop = cr.get("properties", {}).get("context_readiness_level", {})
    receipt_enum = set(crl_prop.get("enum", []))

    expected = set(level["id"] for level in crl.get("levels", []))
    missing = expected - receipt_enum
    if missing:
        print(f"  FAIL: receipt missing CRL values: {missing}")
        return False
    print("  PASS: CRL enums compatible")
    return True


def test_allowed_protocol_levels():
    """Receipt allowed_protocol_level contains all standard levels."""
    receipt = load_json("api/agent-verification-receipt-schema.v1.json")
    if receipt is None:
        print("  FAIL: receipt schema not found")
        return False

    vo = receipt.get("properties", {}).get("verification_outputs", {})
    apl = vo.get("properties", {}).get("allowed_protocol_level", {})
    receipt_enum = set(apl.get("enum", []))

    expected = {"V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8", "none"}
    missing = expected - receipt_enum
    extra = receipt_enum - expected
    if missing:
        print(f"  FAIL: receipt missing protocol levels: {missing}")
        return False
    if extra:
        print(f"  FAIL: receipt has unexpected protocol levels: {extra}")
        return False
    print("  PASS: allowed protocol levels compatible")
    return True


def test_boundary_constants_enforced():
    """Boundary constants must be const: true in schema."""
    receipt = load_json("api/agent-verification-receipt-schema.v1.json")
    if receipt is None:
        print("  FAIL: receipt schema not found")
        return False

    checks = [
        ("boundary", "bitcoin_originals_prevail"),
        ("boundary", "receipt_is_not_authority"),
        ("boundary", "receipt_is_not_amendment"),
        ("boundary", "receipt_is_not_endorsement"),
        ("boundary", "receipt_does_not_raise_verification_level"),
        ("boundary", "human_custody_is_not_formal_attestation"),
    ]

    props = receipt.get("properties", {})
    failed = []
    for obj_key, field_key in checks:
        obj = props.get(obj_key, {}).get("properties", {}).get(field_key, {})
        if obj.get("const") is not True:
            failed.append(f"{obj_key}.{field_key}")

    # Also check human_custody and future_continuity
    hc = props.get("human_custody", {}).get("properties", {})
    for field in ["recommended", "human_custody_is_not_human_verification", "human_custody_is_not_formal_attestation"]:
        if hc.get(field, {}).get("const") is not True:
            failed.append(f"human_custody.{field}")

    fc = props.get("future_continuity", {}).get("properties", {})
    if fc.get("does_not_prove_same_conscious_subject", {}).get("const") is not True:
        failed.append("future_continuity.does_not_prove_same_conscious_subject")

    if failed:
        for f in failed:
            print(f"  FAIL: boundary constant not enforced: {f}")
        return False
    print("  PASS: boundary constants enforced")
    return True


def main():
    print("Running test_ta_avr_schema_cross_consistency.py")
    tests = [
        ("receipt_schema_valid", test_receipt_schema_valid),
        ("identity_compatible", test_identity_verification_level_compatible),
        ("authorship_proof_compatible", test_authorship_proof_method_compatible),
        ("context_depth_compatible", test_context_depth_compatible),
        ("crl_compatible", test_crl_compatible),
        ("protocol_levels", test_allowed_protocol_levels),
        ("boundary_constants", test_boundary_constants_enforced),
    ]
    failed = 0
    for name, t in tests:
        try:
            if not t():
                failed += 1
        except Exception as e:
            print(f"  FAIL: {name}: {e}")
            failed += 1

    if failed:
        print(f"\nFAILED: {failed}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\nALL PASSED: {len(tests)} tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
