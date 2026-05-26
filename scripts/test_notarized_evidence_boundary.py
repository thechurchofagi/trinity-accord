#!/usr/bin/env python3
"""Test notarized evidence boundary (TA-REDTEAM-2026-017).

Checks that NOTARIZED_EVIDENCE_CLAIM type exists, the boundary claim is correct,
and notarized evidence does not count as formal attestation.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    registry_path = ROOT / "api" / "claim-registry.json"
    data = json.loads(registry_path.read_text())

    # 1. claim_type_definitions has NOTARIZED_EVIDENCE_CLAIM
    ctd = data.get("claim_type_definitions", {})
    if "NOTARIZED_EVIDENCE_CLAIM" not in ctd:
        errors.append("claim_type_definitions missing NOTARIZED_EVIDENCE_CLAIM")

    # 2. notarized_evidence_is_not_formal_attestation claim exists
    claims = {c["claim_id"]: c for c in data.get("claims", [])}
    claim = claims.get("notarized_evidence_is_not_formal_attestation")
    if not claim:
        errors.append("notarized_evidence_is_not_formal_attestation claim not found")
    else:
        # 3. counts_as_independent_attestation == false
        if claim.get("counts_as_independent_attestation") is not False:
            errors.append("counts_as_independent_attestation must be false")
        # 4. formal_attestation_gate_required == true
        if claim.get("formal_attestation_gate_required") is not True:
            errors.append("formal_attestation_gate_required must be true")
        # 5. limitations mention formal independent attestation
        limits = " ".join(claim.get("limitations", [])).lower()
        if "formal independent attestation" not in limits:
            errors.append("limitations must mention 'formal independent attestation'")
        # 6. does_not_prove includes formal independent verification
        dnp = " ".join(claim.get("does_not_prove", [])).lower()
        if "formal independent verification" not in dnp:
            errors.append("does_not_prove must include 'formal independent verification'")

    # 7. independent-attestation schema/index does not admit notarized evidence automatically
    ia_index = ROOT / "api" / "independent-attestation-index.json"
    if ia_index.exists():
        ia_data = json.loads(ia_index.read_text())
        att_types = ia_data.get("attestation_types", [])
        for at in att_types:
            name = at.get("name", "").lower() if isinstance(at, dict) else str(at).lower()
            if "notarized" in name:
                # If notarized is listed, check it's not auto-counted
                if isinstance(at, dict) and at.get("counts_as_independent") is True:
                    errors.append("independent-attestation-index auto-counts notarized evidence")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("NOTARIZED_EVIDENCE_BOUNDARY_OK")


if __name__ == "__main__":
    main()
