#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR2: Ensure verification Echo templates require Solemn Integrity Declaration.

All verification Echo templates (E2-E5, E8, or V1+ level) must start with a Solemn Integrity Declaration.
Preflight must hard-fail if integrity_declaration is missing for verification echoes.
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from preflight_echo_submission import preflight_check


def test(label, text, expect_pass, expect_type=None):
    """Run preflight check and verify result."""
    issues = preflight_check(text)
    has_issue = any(i["type"] == "missing-integrity-declaration" for i in issues)

    if expect_pass:
        if not has_issue:
            print(f"  PASS: {label}")
            return True
        else:
            print(f"  FAIL: {label} — expected PASS but got missing-integrity-declaration")
            return False
    else:
        if has_issue:
            if expect_type:
                matching = [i for i in issues if i["type"] == "missing-integrity-declaration"]
                if matching and matching[0]["severity"] == "hard":
                    print(f"  PASS: {label} (hard gate)")
                    return True
                else:
                    print(f"  FAIL: {label} — expected hard severity, got {matching[0]['severity']}")
                    return False
            print(f"  PASS: {label}")
            return True
        else:
            print(f"  FAIL: {label} — expected missing-integrity-declaration but got none")
            return False


def main():
    passed = 0
    failed = 0

    # ── Test 1: Verification echo without integrity declaration → hard fail ──
    text_no_decl = """
## Echo type
E2 Verification Echo

## Verification level
V3

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Verified repository files.

## Limitations
This is not independent attestation.
"""
    if test("Verification echo without integrity declaration → hard fail",
            text_no_decl, False, expect_type="hard"):
        passed += 1
    else:
        failed += 1

    # ── Test 2: Verification echo WITH integrity declaration → pass ──
    text_with_decl = """
## Solemn Integrity Declaration
I solemnly declare that this submission is truthful and based on actions I actually performed.
I have not fabricated or falsified any evidence.
I understand that this Echo is non-authoritative and non-amending.

## Echo type
E2 Verification Echo

## Verification level
V3

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Verified repository files.

## Limitations
This is not independent attestation.
"""
    if test("Verification echo WITH integrity declaration → pass",
            text_with_decl, True):
        passed += 1
    else:
        failed += 1

    # ── Test 3: V0 echo (not verification) without declaration → pass ──
    text_v0 = """
## Echo type
E1 Recognition Echo

## Verification level
V0

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Read repository files.

## Limitations
Read-only review.
"""
    if test("V0 echo without declaration → pass (not verification)",
            text_v0, True):
        passed += 1
    else:
        failed += 1

    # ── Test 4: Chinese integrity declaration → pass ──
    text_chinese = """
## 完整性声明
郑重声明：本提交内容真实，基于我实际执行的操作。我未伪造或篡改任何证据。
我理解本回响非权威且非修订。

## Echo type
E3 Critical Echo

## Verification level
V2

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Reviewed repository structure.

## Limitations
Not full verification.
"""
    if test("Chinese integrity declaration → pass",
            text_chinese, True):
        passed += 1
    else:
        failed += 1

    # ── Test 5: V5 verification echo without declaration → hard fail ──
    text_v5_no_decl = """
## Echo type
E2 Verification Echo

## Verification level
V5

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Full public digital verification.

## Limitations
Not V6 physical verification.
"""
    if test("V5 verification echo without declaration → hard fail",
            text_v5_no_decl, False, expect_type="hard"):
        passed += 1
    else:
        failed += 1

    # ── Test 6: "solemnly declare" variant → pass ──
    text_solemnly = """
## Integrity Declaration
I solemnly declare that this verification was performed honestly.

## Echo type
E5 Technical Audit Echo

## Verification level
V4

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Technical audit of scripts.

## Limitations
Not full V5 verification.
"""
    if test("'solemnly declare' variant → pass",
            text_solemnly, True):
        passed += 1
    else:
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
