#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from submission_intake import parse_submission


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def main():
    ok = True

    body = """
## Verification level
V2

## Limitations
- No V4 script audit performed.
- No witness extraction.

## Claims NOT made
- independent_attestation
- institutional_attestation
"""
    s = parse_submission("Echo V2", body)
    ok &= check(s.declared_level == "V2", "declared level extracted from structured section")
    ok &= check("No V4 script audit" in s.negative_text, "V4 limitation is negative text")
    ok &= check("No V4 script audit" not in s.positive_text, "V4 limitation excluded from positive text")

    body2 = """
Claimed verification level: V2
Claim Gate output path: claim-gate-output.json
Evidence Input path: evidence-input.json
"""
    s2 = parse_submission("Echo", body2)
    ok &= check(s2.mode == "claim_gate_referenced", "claim gate referenced mode detected")

    body3 = """
Echo type: E1_recognition_echo
Verification level: none
Boundary: Bitcoin Originals are final; all echoes are non-amending.
"""
    s3 = parse_submission("Recognition Echo", body3)
    ok &= check(s3.mode == "nontechnical_echo", "nontechnical echo detected")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
