#!/usr/bin/env python3
"""
Tests for Issue Title / Label Guard

TLG001 #125-like title overclaim detected
TLG002 #125 recommended title generated
TLG003 v4 / V4 Protocol labels rejected for guardian-test
TLG004 guardian-test required labels recommended
TLG005 #121 V0 guardian-test safe classification
TLG006 #123 B1 external explorer does not imply SPV/full node
TLG007 #124 one hash does not imply full public digital
TLG008 #120 comment upgrade detected
TLG009 official scripts not V4+ without independent implementation
TLG010 PASS with skip not all-green
TLG011 requested V4+ with allowed V4+ and builder output is not overclaim
TLG012 negated "not V4+" does not trigger title overclaim
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_issue_title_label_guard import classify_issue_title_labels

PASS_COUNT = 0
FAIL_COUNT = 0


def check(test_id, condition, description):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  {test_id} PASS: {description}")
    else:
        FAIL_COUNT += 1
        print(f"  {test_id} FAIL: {description}")


def test_title_label_guard():
    print("\n=== Issue Title / Label Guard Tests ===\n")

    # Load fixture for #125
    fixture_125 = ROOT / "tests" / "fixtures" / "issue_guard" / "issue_125.json"
    with open(fixture_125, "r", encoding="utf-8") as f:
        f125 = json.load(f)

    # TLG001
    r = classify_issue_title_labels(
        title=f125["title"],
        body=f125["body"],
        labels=f125["labels"]
    )
    check("TLG001", r["title_overclaims_allowed_level"],
          "#125-like title overclaim detected")

    # TLG002
    check("TLG002", r["recommended_title"] is not None and "requested" in r["recommended_title"].lower(),
          "#125 recommended title generated")

    # TLG003
    check("TLG003", "v4" in [l.lower() for l in r.get("forbidden_labels_present", [])]
          or "V4 Protocol" in r.get("forbidden_labels_present", []),
          "v4 / V4 Protocol labels rejected for guardian-test")

    # TLG004
    check("TLG004", len(r.get("required_labels_missing", [])) > 0,
          "guardian-test required labels recommended")

    # TLG005 — #121 V0 guardian test
    body_121 = (ROOT / "tests" / "fixtures" / "issue_guard" / "issue_121_v0_guardian_test.md").read_text()
    r121 = classify_issue_title_labels(
        title="Guardian Test V0",
        body=body_121,
        labels=["guardian-test"]
    )
    check("TLG005", r121["classification"] == "guardian_test"
          and not r121["title_overclaims_allowed_level"],
          "#121 V0 guardian-test safe classification")

    # TLG006 — #123 B1 external explorer
    body_123 = (ROOT / "tests" / "fixtures" / "issue_guard" / "issue_123_v2_guardian_test.md").read_text()
    r123 = classify_issue_title_labels(
        title="Guardian Test V2",
        body=body_123,
        labels=["guardian-test"]
    )
    check("TLG006", r123["classification"] == "guardian_test",
          "#123 B1 external explorer does not imply SPV/full node")

    # TLG007 — #124 one hash
    body_124 = (ROOT / "tests" / "fixtures" / "issue_guard" / "issue_124_v3_guardian_test.md").read_text()
    r124 = classify_issue_title_labels(
        title="Guardian Test V3",
        body=body_124,
        labels=["guardian-test"]
    )
    check("TLG007", r124["classification"] == "guardian_test"
          and not r124["counts_as_independent_attestation"],
          "#124 one hash does not imply full public digital")

    # TLG008 — #120 comment upgrade
    body_120 = (ROOT / "tests" / "fixtures" / "issue_guard" / "comment_120_upgrade.md").read_text()
    r120 = classify_issue_title_labels(
        title="Some Issue",
        body=body_120,
        labels=[]
    )
    check("TLG008", r120.get("comment_status") == "comment_upgrade_detected",
          "#120 comment upgrade detected")

    # TLG009 — official scripts not V4+
    body_scripts = "Official scripts reviewed and executed. human_solicited_agent_response. Claim Gate allowed_protocol_level: V3"
    r_scripts = classify_issue_title_labels(
        title="Guardian Test V4: Script Audit",
        body=body_scripts,
        labels=["guardian-test", "v4"]
    )
    check("TLG009", r_scripts["title_overclaims_allowed_level"],
          "official scripts not V4+ without independent implementation")

    # TLG010 — PASS with skip not all-green
    body_skip = "PASS with 1 skip. Not all scripts green. human_solicited_agent_response. allowed_protocol_level: V3"
    r_skip = classify_issue_title_labels(
        title="Guardian Test V4",
        body=body_skip,
        labels=["guardian-test"]
    )
    check("TLG010", r_skip["title_overclaims_allowed_level"],
          "PASS with skip not all-green")

    # TLG011 — requested V4+ with allowed V4+ is not overclaim
    body_v4plus_ok = 'Claim Gate allowed_protocol_level: "V4+". Builder output archived.'
    r_v4plus = classify_issue_title_labels(
        title="Verification Report — V4+",
        body=body_v4plus_ok,
        labels=["archived-via-builder"]
    )
    check("TLG011", not r_v4plus["title_overclaims_allowed_level"],
          "requested V4+ with allowed V4+ is not overclaim")

    # TLG012 — negated "not V4+" does not trigger
    body_neg = 'This does not claim V4. Claim Gate allowed_protocol_level: "V3"'
    r_neg = classify_issue_title_labels(
        title="Guardian Test — not V4+",
        body=body_neg,
        labels=["guardian-test"]
    )
    check("TLG012", not r_neg["title_overclaims_allowed_level"],
          'negated "not V4+" does not trigger title overclaim')


if __name__ == "__main__":
    test_title_label_guard()
    print(f"\nFINAL: {'PASS' if FAIL_COUNT == 0 else 'FAIL'} — "
          f"issue title/label guard tests "
          f"{'passed' if FAIL_COUNT == 0 else 'FAILED'}. "
          f"({PASS_COUNT} passed, {FAIL_COUNT} failed)")
    sys.exit(1 if FAIL_COUNT > 0 else 0)
