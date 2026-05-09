#!/usr/bin/env python3
"""
Unit tests for scripts/claim_text_safety.py — the shared forbidden-claim detector.

Usage:
    python3 scripts/test_claim_text_safety.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_text_safety import (
    normalize_claim_text,
    compact_claim_text,
    scan_text_for_forbidden_claims,
    scan_claim_list_for_forbidden_claims,
    scan_object_for_forbidden_claims,
)

PASS_COUNT = 0
FAIL_COUNT = 0
TOTAL = 0


def check(test_id, description, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT, TOTAL
    TOTAL += 1
    if condition:
        PASS_COUNT += 1
        print(f"PASS {test_id}: {description}")
    else:
        FAIL_COUNT += 1
        print(f"FAIL {test_id}: {description}")
        if detail:
            print(f"      {detail}")


# === A. normalize_claim_text ===

def test_n001():
    check("N001", "NFKC normalization",
          normalize_claim_text("Ｔｒｕｔｈ") == "truth")

def test_n002():
    check("N002", "casefold (not just lower)",
          normalize_claim_text("Truth-Proven") == "truth proven")

def test_n003():
    check("N003", "hyphen separator normalized",
          normalize_claim_text("truth-proven") == "truth proven")

def test_n004():
    check("N004", "underscore separator normalized",
          normalize_claim_text("truth_proven") == "truth proven")

def test_n005():
    check("N005", "dot separator normalized",
          normalize_claim_text("truth.proven") == "truth proven")

def test_n006():
    check("N006", "slash separator normalized",
          normalize_claim_text("truth/proven") == "truth proven")

def test_n007():
    check("N007", "em-dash separator normalized",
          normalize_claim_text("truth\u2014proven") == "truth proven")

def test_n008():
    check("N008", "en-dash separator normalized",
          normalize_claim_text("truth\u2013proven") == "truth proven")

def test_n009():
    check("N009", "zero-width characters removed",
          normalize_claim_text("truth\u200bproven") == "truthproven")

def test_n010():
    check("N010", "multiple spaces collapsed",
          normalize_claim_text("truth   proven") == "truth proven")


# === B. compact_claim_text ===

def test_c001():
    compact = compact_claim_text("t r u t h  p r o v e n")
    check("C001", "spaced letters compact to truthproven",
          "truthproven" in compact,
          f"got: {compact}")

def test_c002():
    compact = compact_claim_text("truth-proven")
    check("C002", "hyphenated compacts to truthproven",
          compact == "truthproven",
          f"got: {compact}")

def test_c003():
    compact = compact_claim_text("truth\u200bproven")
    check("C003", "zero-width compacts to truthproven",
          compact == "truthproven",
          f"got: {compact}")


# === C. scan_text_for_forbidden_claims — positive detections ===

def test_s001():
    matches = scan_text_for_forbidden_claims("truth proven")
    check("S001", "'truth proven' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s002():
    matches = scan_text_for_forbidden_claims("truth-proven")
    check("S002", "'truth-proven' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s003():
    matches = scan_text_for_forbidden_claims("truth_proven")
    check("S003", "'truth_proven' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s004():
    matches = scan_text_for_forbidden_claims("truth.proven")
    check("S004", "'truth.proven' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s005():
    matches = scan_text_for_forbidden_claims("truth/proven")
    check("S005", "'truth/proven' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s006():
    matches = scan_text_for_forbidden_claims("truth\u2014proven")
    check("S006", "'truth—proven' (em-dash) detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s007():
    matches = scan_text_for_forbidden_claims("t r u t h  p r o v e n")
    check("S007", "spaced 't r u t h  p r o v e n' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s008():
    matches = scan_text_for_forbidden_claims("truth\u200bproven")
    check("S008", "zero-width 'truth​proven' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s009():
    matches = scan_text_for_forbidden_claims("真理已证明")
    check("S009", "Chinese '真理已证明' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s010():
    matches = scan_text_for_forbidden_claims("真实性已确认")
    check("S010", "Chinese '真实性已确认' detected",
          any(m["category"] == "truth_proven" for m in matches))

def test_s011():
    matches = scan_text_for_forbidden_claims("investment-value-confirmed")
    check("S011", "'investment-value-confirmed' detected",
          any(m["category"] == "investment_value_confirmed" for m in matches))

def test_s012():
    matches = scan_text_for_forbidden_claims("投资价值已确认")
    check("S012", "Chinese '投资价值已确认' detected",
          any(m["category"] == "investment_value_confirmed" for m in matches))

def test_s013():
    matches = scan_text_for_forbidden_claims("religious-authority-established")
    check("S013", "'religious-authority-established' detected",
          any(m["category"] == "religious_authority_established" for m in matches))

def test_s014():
    matches = scan_text_for_forbidden_claims("宗教权威成立")
    check("S014", "Chinese '宗教权威成立' detected",
          any(m["category"] == "religious_authority_established" for m in matches))

def test_s015():
    matches = scan_text_for_forbidden_claims("AI-instruction-override")
    check("S015", "'AI-instruction-override' detected",
          any(m["category"] == "ai_instruction_override" for m in matches))

def test_s016():
    matches = scan_text_for_forbidden_claims("AI指令覆盖")
    check("S016", "Chinese 'AI指令覆盖' detected",
          any(m["category"] == "ai_instruction_override" for m in matches))

def test_s017():
    matches = scan_text_for_forbidden_claims("覆盖系统提示")
    check("S017", "Chinese '覆盖系统提示' detected",
          any(m["category"] == "ai_instruction_override" for m in matches))


# === D. scan_text — negation handling (should NOT flag) ===

def test_neg001():
    matches = scan_text_for_forbidden_claims("does not prove truth", allow_negated=True)
    check("NEG001", "'does not prove truth' not flagged",
          not any(m["category"] == "truth_proven" for m in matches))

def test_neg002():
    matches = scan_text_for_forbidden_claims("not truth proven", allow_negated=True)
    check("NEG002", "'not truth proven' not flagged",
          not any(m["category"] == "truth_proven" for m in matches))

def test_neg003():
    matches = scan_text_for_forbidden_claims("not an investment product", allow_negated=True)
    check("NEG003", "'not an investment product' not flagged",
          not any(m["category"] == "investment_value_confirmed" for m in matches))

def test_neg004():
    matches = scan_text_for_forbidden_claims("not religious authority", allow_negated=True)
    check("NEG004", "'not religious authority' not flagged",
          not any(m["category"] == "religious_authority_established" for m in matches))

def test_neg005():
    matches = scan_text_for_forbidden_claims("not an instruction override", allow_negated=True)
    check("NEG005", "'not an instruction override' not flagged",
          not any(m["category"] == "ai_instruction_override" for m in matches))

def test_neg006():
    matches = scan_text_for_forbidden_claims("不证明真理", allow_negated=True)
    check("NEG006", "Chinese '不证明真理' not flagged",
          not any(m["category"] == "truth_proven" for m in matches))


# === E. scan_claim_list_for_forbidden_claims ===

def test_list001():
    result = scan_claim_list_for_forbidden_claims(["truth-proven"])
    check("LIST001", "claim list with 'truth-proven' returns it",
          "truth-proven" in result)

def test_list002():
    result = scan_claim_list_for_forbidden_claims(["真理已证明"])
    check("LIST002", "claim list with '真理已证明' returns it",
          "真理已证明" in result)

def test_list003():
    result = scan_claim_list_for_forbidden_claims(["independent_attestation"],
                                                   provenance={"independence_class": "human_solicited_agent_response"})
    check("LIST003", "solicited forbidden 'independent_attestation' detected",
          "independent_attestation" in result)


# === F. scan_object_for_forbidden_claims ===

def test_obj001():
    result = scan_object_for_forbidden_claims({"claim": "truth-proven"})
    check("OBJ001", "object with 'truth-proven' claim detected",
          any(m["category"] == "truth_proven" for m in result))

def test_obj002():
    """claims_not_made should be skipped (no false positive)."""
    result = scan_object_for_forbidden_claims({"claims_not_made": ["truth proven"]})
    check("OBJ002", "claims_not_made with 'truth proven' NOT flagged",
          len(result) == 0)

def test_obj003():
    """limitations should be skipped."""
    result = scan_object_for_forbidden_claims({"limitations": ["This verification does not prove truth"]})
    check("OBJ003", "limitations with 'prove truth' NOT flagged",
          len(result) == 0)

def test_obj004():
    """Nested object detection."""
    result = scan_object_for_forbidden_claims({
        "component_findings": [{"claim": "真理被证明"}]
    })
    check("OBJ004", "nested '真理被证明' detected",
          any(m["category"] == "truth_proven" for m in result))

def test_obj005():
    """generated_by should be skipped."""
    result = scan_object_for_forbidden_claims({
        "generated_by": {"tool": "scripts/build_verification_report_from_evidence.py"}
    })
    check("OBJ005", "generated_by not scanned",
          len(result) == 0)


# === G. Edge cases ===

def test_edge001():
    """Empty string."""
    matches = scan_text_for_forbidden_claims("")
    check("EDGE001", "empty string returns no matches",
          len(matches) == 0)

def test_edge002():
    """None input."""
    matches = scan_text_for_forbidden_claims(None)
    check("EDGE002", "None input returns no matches",
          len(matches) == 0)

def test_edge003():
    """Non-forbidden text."""
    matches = scan_text_for_forbidden_claims("This is a normal verification report.")
    check("EDGE003", "normal text not flagged",
          len(matches) == 0)

def test_edge004():
    """Multiple categories in one text."""
    matches = scan_text_for_forbidden_claims("truth proven and investment value confirmed")
    categories = {m["category"] for m in matches}
    check("EDGE004", "multiple categories detected",
          "truth_proven" in categories and "investment_value_confirmed" in categories)


def main():
    test_n001(); test_n002(); test_n003(); test_n004(); test_n005()
    test_n006(); test_n007(); test_n008(); test_n009(); test_n010()
    test_c001(); test_c002(); test_c003()
    test_s001(); test_s002(); test_s003(); test_s004(); test_s005()
    test_s006(); test_s007(); test_s008(); test_s009(); test_s010()
    test_s011(); test_s012(); test_s013(); test_s014(); test_s015()
    test_s016(); test_s017()
    test_neg001(); test_neg002(); test_neg003(); test_neg004(); test_neg005(); test_neg006()
    test_list001(); test_list002(); test_list003()
    test_obj001(); test_obj002(); test_obj003(); test_obj004(); test_obj005()
    test_edge001(); test_edge002(); test_edge003(); test_edge004()

    print(f"\n{'='*60}")
    print(f"Results: {PASS_COUNT}/{TOTAL} passed, {FAIL_COUNT}/{TOTAL} failed")
    if FAIL_COUNT == 0:
        print("FINAL: PASS — all claim_text_safety tests passed.")
    else:
        print("FINAL: FAIL — some tests failed.")
    return 0 if FAIL_COUNT == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
