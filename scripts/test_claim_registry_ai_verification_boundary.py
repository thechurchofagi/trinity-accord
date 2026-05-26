#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR5: Claim registry AI verification boundary tests.

Verifies that:
1. AI_INDEPENDENT_VERIFICATION_CLAIM type exists in claim_type_definitions
2. AI verification claims have correct attestation flags
3. Schema requires the AI verification type
4. Public surfaces reference the correct boundary docs
5. All validators exist
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test(label, passed):
    if passed:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label}")
    return passed


def main():
    passed = 0
    failed = 0

    registry = load_json(ROOT / "api" / "claim-registry.json")
    schema = load_json(ROOT / "api" / "claim-registry-schema.v1.json")

    # ── Test 1: Type definition exists ──
    types = registry.get("claim_type_definitions", {})
    has_type = "AI_INDEPENDENT_VERIFICATION_CLAIM" in types
    if test("AI_INDEPENDENT_VERIFICATION_CLAIM type defined", has_type):
        passed += 1
    else:
        failed += 1

    # ── Test 2: Type has correct default ──
    if has_type:
        type_def = types["AI_INDEPENDENT_VERIFICATION_CLAIM"]
        correct_default = type_def.get("counts_as_independent_attestation_by_default") is False
        if test("Type has counts_as_independent_attestation_by_default=false", correct_default):
            passed += 1
        else:
            failed += 1
    else:
        print("  SKIP: Type not defined")
        failed += 1

    # ── Test 3: Schema requires the type ──
    required = schema.get("properties", {}).get("claim_type_definitions", {}).get("required", [])
    if test("Schema requires AI_INDEPENDENT_VERIFICATION_CLAIM",
            "AI_INDEPENDENT_VERIFICATION_CLAIM" in required):
        passed += 1
    else:
        failed += 1

    # ── Test 4: AI verification claims exist ──
    claims = {c["claim_id"]: c for c in registry.get("claims", [])}
    ai_claim = claims.get("ai_independent_verification_is_not_formal_attestation")
    auth_claim = claims.get("external_human_authorization_of_ai_does_not_produce_formal_attestation")

    if test("ai_independent_verification claim exists", ai_claim is not None):
        passed += 1
    else:
        failed += 1

    if test("external_human_authorization claim exists", auth_claim is not None):
        passed += 1
    else:
        failed += 1

    # ── Test 5: Claims have correct flags ──
    if ai_claim:
        flags_ok = (
            ai_claim.get("claim_type") == "AI_INDEPENDENT_VERIFICATION_CLAIM"
            and ai_claim.get("counts_as_independent_attestation") is False
            and ai_claim.get("formal_attestation_gate_required") is True
        )
        if test("AI verification claim has correct type and flags", flags_ok):
            passed += 1
        else:
            failed += 1
    else:
        print("  SKIP: AI claim not found")
        failed += 1

    if auth_claim:
        flags_ok = (
            auth_claim.get("claim_type") == "AI_INDEPENDENT_VERIFICATION_CLAIM"
            and auth_claim.get("counts_as_independent_attestation") is False
            and auth_claim.get("formal_attestation_gate_required") is True
        )
        if test("Authorization claim has correct type and flags", flags_ok):
            passed += 1
        else:
            failed += 1
    else:
        print("  SKIP: Authorization claim not found")
        failed += 1

    # ── Test 6: Claims reference public surfaces ──
    if ai_claim:
        surfaces = ai_claim.get("public_surfaces", [])
        has_surfaces = len(surfaces) > 0 and "llms.txt" in surfaces
        if test("AI verification claim has public_surfaces", has_surfaces):
            passed += 1
        else:
            failed += 1
    else:
        print("  SKIP: AI claim not found")
        failed += 1

    # ── Test 7: Validators reference existing test scripts ──
    if ai_claim:
        validators = ai_claim.get("validators", [])
        all_exist = all((ROOT / v).exists() for v in validators)
        if test("AI verification claim validators exist", all_exist):
            passed += 1
        else:
            for v in validators:
                if not (ROOT / v).exists():
                    print(f"    Missing validator: {v}")
            failed += 1
    else:
        print("  SKIP: AI claim not found")
        failed += 1

    # ── Test 8: claims do_not_prove includes formal attestation ──
    if ai_claim:
        dnp = ai_claim.get("does_not_prove", [])
        has_dnp = any("formal" in x.lower() or "attestation" in x.lower() for x in dnp)
        if test("AI claim does_not_prove includes formal attestation", has_dnp):
            passed += 1
        else:
            failed += 1
    else:
        print("  SKIP: AI claim not found")
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
