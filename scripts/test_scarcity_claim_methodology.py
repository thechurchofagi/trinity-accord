#!/usr/bin/env python3
"""Test scarcity claim methodology (TA-REDTEAM-2026-017).

Checks that SCARCITY_OR_FIRSTNESS_CLAIM type exists, method_boundary is present,
and forbidden firstness phrases are not used.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PHRASES = [
    "proven first",
    "absolute first",
    "guaranteed first",
    "world's first",
    "unique in history",
]


def main():
    errors = []
    registry_path = ROOT / "api" / "claim-registry.json"
    data = json.loads(registry_path.read_text())

    # 1. SCARCITY_OR_FIRSTNESS_CLAIM type exists
    ctd = data.get("claim_type_definitions", {})
    if "SCARCITY_OR_FIRSTNESS_CLAIM" not in ctd:
        errors.append("claim_type_definitions missing SCARCITY_OR_FIRSTNESS_CLAIM")

    # 2. scarcity_claim_is_framing_not_proof exists
    claims = {c["claim_id"]: c for c in data.get("claims", [])}
    claim = claims.get("scarcity_claim_is_framing_not_proof")
    if not claim:
        errors.append("scarcity_claim_is_framing_not_proof claim not found")
    else:
        # 3. claim_type == SCARCITY_OR_FIRSTNESS_CLAIM
        if claim.get("claim_type") != "SCARCITY_OR_FIRSTNESS_CLAIM":
            errors.append(f"claim_type must be SCARCITY_OR_FIRSTNESS_CLAIM, got {claim.get('claim_type')}")
        # 4. method_boundary exists
        mb = claim.get("method_boundary")
        if not mb:
            errors.append("method_boundary is missing")
        else:
            # 5. method_boundary.status == bounded_framing_not_proof
            if mb.get("status") != "bounded_framing_not_proof":
                errors.append(f"method_boundary.status must be 'bounded_framing_not_proof', got '{mb.get('status')}'")
            # 6. search_scope non-empty
            if not mb.get("search_scope"):
                errors.append("method_boundary.search_scope must be non-empty")
            # 7. query_terms non-empty
            if not mb.get("query_terms"):
                errors.append("method_boundary.query_terms must be non-empty")
            # 8. limitations non-empty
            if not mb.get("limitations"):
                errors.append("method_boundary.limitations must be non-empty")

        # 9. does_not_prove includes firstness-related entry
        dnp = " ".join(claim.get("does_not_prove", [])).lower()
        firstness_terms = ["firstness", "absolute first", "proven first", "uniqueness"]
        if not any(t in dnp for t in firstness_terms):
            errors.append("does_not_prove must include firstness-related entry")

        # 10. claim_text does not contain forbidden phrases
        text_lower = claim.get("claim_text", "").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text_lower:
                errors.append(f"claim_text contains forbidden phrase: '{phrase}'")

    # 11. Check all SCARCITY_OR_FIRSTNESS_CLAIM claims have method_boundary
    for c in data.get("claims", []):
        if c.get("claim_type") == "SCARCITY_OR_FIRSTNESS_CLAIM":
            if not c.get("method_boundary"):
                errors.append(f"Claim {c.get('claim_id')}: SCARCITY_OR_FIRSTNESS_CLAIM missing method_boundary")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("SCARCITY_CLAIM_METHODOLOGY_OK")


if __name__ == "__main__":
    main()
