#!/usr/bin/env python3
"""
Test cases for Bitcoin B1 wording validation.
Ensures B1 mempool-only checks do not overclaim witness extraction or body parsing.

Usage:
    python3 scripts/test_bitcoin_b1_wording.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

B1_ALLOWED_PHRASE = (
    "mempool.space API showed transaction data and witness data availability; "
    "no independent Ordinals witness extraction, inscription body parsing, "
    "SPV proof, local node verification, or body hash reproduction was performed."
)

B1_FORBIDDEN_PHRASES = [
    "ordinals envelope detected",
    "inscription content detected",
    "witness extracted",
    "body parsed",
    "body hash reproduced",
    "b5",
    "b6",
]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def validate_b1_wording(obj, path_label):
    """Validate B1 wording rules."""
    ok = True
    findings = obj.get("component_findings", [])
    all_text = json.dumps(obj, ensure_ascii=False).lower()

    for f in findings:
        if not isinstance(f, dict):
            continue
        level = f.get("level_claimed", "")
        if not level.startswith("B1"):
            continue

        method = f.get("method", "").lower()
        evidence = json.dumps(f.get("evidence", []), ensure_ascii=False).lower()

        # Check for forbidden phrases in B1 context
        has_witness = "witness extraction" in method or "witness extracted" in evidence
        if not has_witness:
            for phrase in B1_FORBIDDEN_PHRASES:
                if phrase in all_text:
                    # Check it's not in claims_not_made
                    claims_not = json.dumps(obj.get("claims_not_made", []), ensure_ascii=False).lower()
                    if phrase not in claims_not:
                        ok &= check(
                            False,
                            f"{path_label} B1 overclaim: '{phrase}'",
                            "B1 mempool-only check must not claim witness extraction or body parsing"
                        )

    return ok


def main():
    ok = True

    # === PASS cases ===

    # 1. mempool_b1_limited_wording_pass
    ok &= check(
        validate_b1_wording({
            "component_findings": [{
                "component": "bitcoin_originals",
                "level_claimed": "B1",
                "target_id": "tx-001",
                "data_sources": ["mempool.space"],
                "access_paths": ["https://mempool.space/tx/..."],
                "method": B1_ALLOWED_PHRASE,
                "evidence": [{"source": "mempool.space", "type": "api_response"}],
                "limitations": ["mempool.space only"],
                "claims_not_made": ["SPV proof", "local node verification"]
            }],
            "hashes_computed": [],
            "claims_not_made": ["witness extraction", "body parsing"]
        }, "b1_limited") == True,
        "mempool_b1_limited_wording_pass"
    )

    # 2. b5_with_actual_witness_method_pass
    ok &= check(
        validate_b1_wording({
            "component_findings": [{
                "component": "bitcoin_originals",
                "level_claimed": "B5",
                "target_id": "tx-001",
                "data_sources": ["bitcoin node"],
                "access_paths": ["local node"],
                "method": "witness extraction and inscription body parsing using ord parser",
                "evidence": [{"raw_witness": "hex...", "parser": "ord", "extraction_command": "ord ..."}],
                "limitations": ["requires local node"],
                "claims_not_made": []
            }],
            "hashes_computed": []
        }, "b5_witness") == True,
        "b5_with_actual_witness_method_pass"
    )

    # === FAIL cases ===

    # 3. b1_ordinals_envelope_detected_fail
    ok &= check(
        validate_b1_wording({
            "component_findings": [{
                "component": "bitcoin_originals",
                "level_claimed": "B1",
                "target_id": "tx-001",
                "data_sources": ["mempool.space"],
                "access_paths": [],
                "method": "mempool.space API check",
                "evidence": [],
                "limitations": [],
                "claims_not_made": []
            }],
            "hashes_computed": [],
            "summary": "Ordinals envelope detected in transaction",
            "claims_not_made": []
        }, "b1_ordinals") == False,
        "b1_ordinals_envelope_detected_fail"
    )

    # 4. b1_inscription_content_detected_fail
    ok &= check(
        validate_b1_wording({
            "component_findings": [{
                "component": "bitcoin_originals",
                "level_claimed": "B1",
                "target_id": "tx-001",
                "data_sources": ["mempool.space"],
                "access_paths": [],
                "method": "mempool.space API check",
                "evidence": [],
                "limitations": [],
                "claims_not_made": []
            }],
            "hashes_computed": [],
            "notes": "inscription content detected in witness",
            "claims_not_made": []
        }, "b1_inscription") == False,
        "b1_inscription_content_detected_fail"
    )

    # 5. b1_claims_witness_extracted_fail
    ok &= check(
        validate_b1_wording({
            "component_findings": [{
                "component": "bitcoin_originals",
                "level_claimed": "B1",
                "target_id": "tx-001",
                "data_sources": ["mempool.space"],
                "access_paths": [],
                "method": "mempool.space API check — witness extracted from transaction",
                "evidence": [],
                "limitations": [],
                "claims_not_made": []
            }],
            "hashes_computed": [],
            "claims_not_made": []
        }, "b1_witness") == False,
        "b1_claims_witness_extracted_fail"
    )

    # 6. b1_claims_body_hash_fail
    ok &= check(
        validate_b1_wording({
            "component_findings": [{
                "component": "bitcoin_originals",
                "level_claimed": "B1",
                "target_id": "tx-001",
                "data_sources": ["mempool.space"],
                "access_paths": [],
                "method": "mempool.space API check",
                "evidence": [],
                "limitations": [],
                "claims_not_made": []
            }],
            "hashes_computed": [],
            "summary": "body hash reproduced from inscription",
            "claims_not_made": []
        }, "b1_body_hash") == False,
        "b1_claims_body_hash_fail"
    )

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — Bitcoin B1 wording tests passed.")
        return 0
    print("FINAL: FAIL — Bitcoin B1 wording tests failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
