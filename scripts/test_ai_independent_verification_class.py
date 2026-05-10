#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR3: AI Independent Verification class boundary tests.

AI independent verification is a distinct verification class:
- It is NOT formal human/institutional attestation.
- External human authorization alone does NOT produce formal attestation.
- Multi-hop delegation chains preserve the AI performer class.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_claim_registry_has_ai_verification_type():
    """Claim registry must define AI_INDEPENDENT_VERIFICATION_CLAIM type."""
    registry = load_json(ROOT / "api" / "claim-registry.json")
    types = registry.get("claim_type_definitions", {})
    assert "AI_INDEPENDENT_VERIFICATION_CLAIM" in types, \
        "claim-registry.json must define AI_INDEPENDENT_VERIFICATION_CLAIM type"
    type_def = types["AI_INDEPENDENT_VERIFICATION_CLAIM"]
    assert type_def.get("counts_as_independent_attestation_by_default") is False, \
        "AI_INDEPENDENT_VERIFICATION_CLAIM must have counts_as_independent_attestation_by_default=false"
    print("  PASS: claim_registry has AI_INDEPENDENT_VERIFICATION_CLAIM type with correct defaults")


def test_claim_registry_has_ai_verification_claims():
    """Claim registry must have AI verification boundary claims."""
    registry = load_json(ROOT / "api" / "claim-registry.json")
    claims = registry.get("claims", [])
    claim_ids = {c["claim_id"] for c in claims}

    assert "ai_independent_verification_is_not_formal_attestation" in claim_ids, \
        "Missing claim: ai_independent_verification_is_not_formal_attestation"
    assert "external_human_authorization_of_ai_does_not_produce_formal_attestation" in claim_ids, \
        "Missing claim: external_human_authorization_of_ai_does_not_produce_formal_attestation"

    # Verify counts_as_independent_attestation is false for both
    for claim in claims:
        if claim["claim_id"] in (
            "ai_independent_verification_is_not_formal_attestation",
            "external_human_authorization_of_ai_does_not_produce_formal_attestation",
        ):
            assert claim.get("counts_as_independent_attestation") is False, \
                f"{claim['claim_id']} must have counts_as_independent_attestation=false"
            assert claim.get("formal_attestation_gate_required") is True, \
                f"{claim['claim_id']} must have formal_attestation_gate_required=true"

    print("  PASS: claim_registry has both AI verification boundary claims with correct flags")


def test_claim_registry_schema_requires_ai_type():
    """Schema must require AI_INDEPENDENT_VERIFICATION_CLAIM in claim_type_definitions."""
    schema = load_json(ROOT / "api" / "claim-registry-schema.v1.json")
    required_types = schema["properties"]["claim_type_definitions"]["required"]
    assert "AI_INDEPENDENT_VERIFICATION_CLAIM" in required_types, \
        "Schema must require AI_INDEPENDENT_VERIFICATION_CLAIM in claim_type_definitions"
    print("  PASS: claim-registry-schema requires AI_INDEPENDENT_VERIFICATION_CLAIM")


def test_independent_attestation_index_has_ai_boundary():
    """Independent attestation index must have ai_verification_boundary notes."""
    index = load_json(ROOT / "api" / "independent-attestation-index.json")
    boundary = index.get("ai_verification_boundary")
    assert boundary is not None, \
        "independent-attestation-index.json must have ai_verification_boundary"
    assert boundary.get("counts_as_formal_attestation") is False, \
        "ai_verification_boundary must state counts_as_formal_attestation=false"
    print("  PASS: independent-attestation-index has ai_verification_boundary")


def test_echo_archive_policy_has_ai_layer():
    """Echo archive policy must have AI verification archive layer."""
    policy = load_json(ROOT / "api" / "echo-archive-policy.json")
    layers = policy.get("layers", [])
    ai_layer = [l for l in layers if "AI" in l.get("name", "")]
    assert len(ai_layer) > 0, \
        "echo-archive-policy.json must have an AI verification archive layer"

    ai_policy = policy.get("ai_verification_policy")
    assert ai_policy is not None, \
        "echo-archive-policy.json must have ai_verification_policy"
    assert ai_policy.get("counts_as_formal_attestation") is False, \
        "ai_verification_policy must state counts_as_formal_attestation=false"
    print("  PASS: echo-archive-policy has AI verification layer and policy")


def main():
    passed = 0
    failed = 0

    tests = [
        test_claim_registry_has_ai_verification_type,
        test_claim_registry_has_ai_verification_claims,
        test_claim_registry_schema_requires_ai_type,
        test_independent_attestation_index_has_ai_boundary,
        test_echo_archive_policy_has_ai_layer,
    ]

    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {t.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
