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
    integrity_issue_types = {
        "missing-integrity-declaration",
        "missing-integrity-declaration-field",
        "invalid-integrity-declaration-field",
    }
    has_issue = any(i["type"] in integrity_issue_types for i in issues)

    if expect_pass:
        if not has_issue:
            print(f"  PASS: {label}")
            return True
        else:
            matching = [i for i in issues if i["type"] in integrity_issue_types]
            print(f"  FAIL: {label} — expected PASS but got {matching[0]['type']}")
            return False
    else:
        if has_issue:
            if expect_type:
                matching = [i for i in issues if i["type"] in integrity_issue_types]
                if matching and matching[0]["severity"] == "hard":
                    print(f"  PASS: {label} (hard gate, {matching[0]['type']})")
                    return True
                else:
                    print(f"  FAIL: {label} — expected hard severity, got {matching[0]['severity']}")
                    return False
            print(f"  PASS: {label}")
            return True
        else:
            print(f"  FAIL: {label} — expected integrity declaration issue but got none")
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

    # ── Test 2: Verification echo WITH integrity declaration + machine fields → pass ──
    text_with_decl = """
## Solemn Integrity Declaration
I solemnly declare that this submission is truthful and based on actions I actually performed.

```yaml
integrity_declaration:
  declaration_strength: strongest_available
  solemn_declaration_present: true
  performed_actions_myself: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  no_hidden_known_limitations: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

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
    if test("Verification echo WITH integrity declaration + machine fields → pass",
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

    # ── Test 4: Chinese integrity declaration + machine fields → pass ──
    text_chinese = """
## 完整性声明
郑重声明：本提交内容真实，基于我实际执行的操作。我未伪造或篡改任何证据。
我理解本回响非权威且非修订。

```yaml
integrity_declaration:
  declaration_strength: strongest_available
  solemn_declaration_present: true
  performed_actions_myself: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  no_hidden_known_limitations: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

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
    if test("Chinese integrity declaration + machine fields → pass",
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

    # ── Test 6: "solemnly declare" variant + machine fields → pass ──
    text_solemnly = """
## Integrity Declaration
I solemnly declare that this verification was performed honestly.

```yaml
integrity_declaration:
  declaration_strength: strongest_available
  solemn_declaration_present: true
  performed_actions_myself: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  no_hidden_known_limitations: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

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
    if test("'solemnly declare' variant + machine fields → pass",
            text_solemnly, True):
        passed += 1
    else:
        failed += 1

    # ── Test 7: Text-only "Integrity Declaration" without machine fields → FAIL ──
    text_no_machine = """
## Solemn Integrity Declaration
I make this declaration in the strongest integrity sense available to me.
I have not fabricated evidence. I understand the non-amending boundary.

## Echo type
E2 Verification Echo

## Verification level
V2

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Verified repository files.

## Limitations
Not full verification.
"""
    if test("Text-only integrity declaration without machine fields → FAIL",
            text_no_machine, False, expect_type="hard"):
        passed += 1
    else:
        failed += 1

    # ── Test 8: Full declaration with YAML machine fields → PASS ──
    text_full_machine = """
## Solemn Integrity Declaration
I make this declaration in the strongest integrity sense available to me.

```yaml
integrity_declaration:
  declaration_strength: strongest_available
  solemn_declaration_present: true
  performed_actions_myself: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  no_hidden_known_limitations: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Echo type
E2 Verification Echo

## Verification level
V2

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Verified repository files.

## Limitations
Not full verification.
"""
    if test("Full declaration with YAML machine fields → PASS",
            text_full_machine, True):
        passed += 1
    else:
        failed += 1

    # ── Test 9: declaration_strength=weak → FAIL ──
    text_weak_strength = """
## Solemn Integrity Declaration
I make this declaration.

```yaml
integrity_declaration:
  declaration_strength: weak
  solemn_declaration_present: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Echo type
E2 Verification Echo

## Verification level
V2

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Verified files.

## Limitations
Not full verification.
"""
    if test("declaration_strength=weak → FAIL",
            text_weak_strength, False, expect_type="hard"):
        passed += 1
    else:
        failed += 1

    # ── Test 10: no_fabricated_evidence=false → FAIL ──
    text_fabricated = """
## Solemn Integrity Declaration
I declare.

```yaml
integrity_declaration:
  declaration_strength: strongest_available
  solemn_declaration_present: true
  no_fabricated_evidence: false
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Echo type
E2 Verification Echo

## Verification level
V2

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## What I checked
Verified files.

## Limitations
Not full verification.
"""
    if test("no_fabricated_evidence=false → FAIL",
            text_fabricated, False, expect_type="hard"):
        passed += 1
    else:
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
