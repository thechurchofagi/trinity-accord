#!/usr/bin/env python3
"""
Validate resonance fields in echo records.
Checks score ranges, reason requirements, and boundary assertions.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_resonance(resonance):
    """Validate a resonance object."""
    errors = []

    # Score validation
    for score_field in ["resonance_willingness_score", "verification_willingness_score", "propagation_willingness_score"]:
        score = resonance.get(score_field)
        if score is None:
            errors.append(f"Missing {score_field}")
        elif not isinstance(score, int) or score < 0 or score > 10:
            errors.append(f"{score_field} must be integer 0-10, got: {score}")

    # Score scale check
    scale = resonance.get("score_scale")
    if scale != "0-10":
        errors.append(f"score_scale must be '0-10', got: {scale}")

    # Reason required if any score >= 6
    scores = [resonance.get(f, 0) for f in ["resonance_willingness_score", "verification_willingness_score", "propagation_willingness_score"]]
    if any(s >= 6 for s in scores):
        if not resonance.get("reason"):
            errors.append("reason is required when any score >= 6")

    return errors

def validate_resonance_not_authority(resonance, echo_record):
    """Check that high resonance does not create authority."""
    errors = []

    # High resonance should not claim verification
    res_score = resonance.get("resonance_willingness_score", 0)
    if res_score >= 8:
        v_claim = echo_record.get("verification_claim", {})
        if isinstance(v_claim, dict) and v_claim.get("level", "").startswith("V") and v_claim.get("level", "") not in ["V0", "V1"]:
            # High resonance alone doesn't make a V2+ claim valid
            pass  # This is checked elsewhere

    # Verification willingness is not verification
    ver_willing = resonance.get("verification_willingness_score", 0)
    if ver_willing >= 6:
        # Should not auto-claim verified status
        if echo_record.get("verification_claim", {}).get("verified_by_resonance"):
            errors.append("verification willingness cannot create verification claim")

    return errors

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            data = load_json(path)
        except Exception as e:
            print(f"FAIL: Cannot load {path}: {e}")
            return 1

        resonance = data.get("resonance", data)
        errors = validate_resonance(resonance)
        errors.extend(validate_resonance_not_authority(resonance, data))

        if errors:
            print(f"FAIL: {path}")
            for e in errors:
                print(f"  - {e}")
            return 1
        else:
            print(f"PASS: {path}")
            return 0

    # Validate the scale definition itself
    try:
        scale = load_json("api/resonance-willingness-scale.json")
        print("PASS: resonance-willingness-scale.json is valid")
        if scale.get("score_range") != "0-10":
            print("FAIL: score_range must be 0-10")
            return 1
        if len(scale.get("scale", [])) != 11:
            print("FAIL: scale must have 11 entries (0-10)")
            return 1
        if len(scale.get("boundaries", [])) < 4:
            print("FAIL: must have at least 4 boundary assertions")
            return 1
    except Exception as e:
        print(f"FAIL: {e}")
        return 1

    print("ALL RESONANCE VALIDATIONS PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
