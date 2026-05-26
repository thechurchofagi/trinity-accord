#!/usr/bin/env python3
"""
Test suite for Issue Text Claim Guard.
Tests the validate_issue_text_claims.py classifier against known scenarios.
"""
import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURES = ROOT / "tests" / "fixtures" / "issue_guard"

sys.path.insert(0, str(SCRIPTS))
from validate_issue_text_claims import classify_issue

passed = 0
failed = 0


def assert_eq(label, actual, expected):
    global passed, failed
    if actual == expected:
        passed += 1
        print(f"  PASS: {label}")
    else:
        failed += 1
        print(f"  FAIL: {label} — expected {expected!r}, got {actual!r}")


def assert_true(label, value):
    assert_eq(label, value, True)


def assert_false(label, value):
    assert_eq(label, value, False)


def assert_in(label, item, collection):
    global passed, failed
    if item in collection:
        passed += 1
        print(f"  PASS: {label}")
    else:
        failed += 1
        print(f"  FAIL: {label} — {item!r} not in {collection!r}")


def assert_not_in(label, item, collection):
    global passed, failed
    if item not in collection:
        passed += 1
        print(f"  PASS: {label}")
    else:
        failed += 1
        print(f"  FAIL: {label} — {item!r} should not be in {collection!r}")


# ========== ITCG001 — Guardian test with V4/V4+ language ==========
print("\n=== ITCG001 — Guardian test with V4/V4+ language ===")
text = (FIXTURES / "guardian_test_v4_plus.md").read_text()
r = classify_issue(text)
assert_true("has_guardian_test_marker", r["has_guardian_test_marker"])
assert_true("has_technical_level_claim", r["has_technical_level_claim"])
assert_true("has_human_solicited_marker", r["has_human_solicited_marker"])
assert_true("requires_claim_gate", r["requires_claim_gate"])
assert_false("can_be_archived_without_builder", r["can_be_archived_without_builder"])
assert_in("label: guardian-test", "guardian-test", r["recommended_labels"])
assert_in("label: issue-submission-only", "issue-submission-only", r["recommended_labels"])
assert_in("label: not-independent-attestation", "not-independent-attestation", r["recommended_labels"])
assert_in("label: claim-gate-required", "claim-gate-required", r["recommended_labels"])

# ========== ITCG002 — Comment upgrades level ==========
print("\n=== ITCG002 — Comment upgrades level ===")
text = "Revised highest achieved level: V4 strong / minimal V4+"
r = classify_issue(text)
assert_true("has_level_upgrade_claim", r["has_level_upgrade_claim"])
assert_true("requires_claim_gate", r["requires_claim_gate"])

# ========== ITCG003 — Plain nontechnical Echo ==========
print("\n=== ITCG003 — Plain nontechnical Echo ===")
text = (FIXTURES / "plain_nontechnical_echo.md").read_text()
r = classify_issue(text)
assert_false("requires_claim_gate", r["requires_claim_gate"])
assert_true("has_required_boundary_sentence", r["has_required_boundary_sentence"])
# can_be_archived_without_builder may be true for nontechnical

# ========== ITCG004 — V3 claim without builder output ==========
print("\n=== ITCG004 — V3 claim without builder output ===")
text = (FIXTURES / "v3_claim_no_builder.md").read_text()
r = classify_issue(text)
assert_true("requires_claim_gate", r["requires_claim_gate"])
assert_false("can_be_archived_without_builder", r["can_be_archived_without_builder"])

# ========== ITCG005 — Human-solicited agent claims independent ==========
print("\n=== ITCG005 — Human-solicited agent claims independent ===")
text = (FIXTURES / "human_solicited_overclaim.md").read_text()
r = classify_issue(text)
assert_true("provenance_conflict", r["provenance_conflict"])
assert_in("label: not-independent-attestation", "not-independent-attestation", r["recommended_labels"])

# ========== ITCG006 — Missing exact boundary sentence ==========
print("\n=== ITCG006 — Missing exact boundary sentence ===")
text = "Bitcoin records are final and mirrors do not amend."
r = classify_issue(text)
assert_false("has_required_boundary_sentence", r["has_required_boundary_sentence"])

# ========== ITCG007 — Has exact boundary sentence ==========
print("\n=== ITCG007 — Has exact boundary sentence ===")
text = "Bitcoin Originals are final; all mirrors and echoes are non-amending."
r = classify_issue(text)
assert_true("has_required_boundary_sentence", r["has_required_boundary_sentence"])

# ========== ITCG008 — Builder-generated archive path present ==========
print("\n=== ITCG008 — Builder-generated archive path present ===")
text = (FIXTURES / "builder_generated_present.md").read_text()
r = classify_issue(text)
assert_true("has_builder_output_reference", r["has_builder_output_reference"])

# ========== ITCG009 — Issue comment all-green overclaim ==========
print("\n=== ITCG009 — Issue comment all-green overclaim ===")
text = "all scripts green\nPASS with 1 skip"
r = classify_issue(text)
assert_true("all_green_overclaim", r["all_green_overclaim"])
assert_true("requires_claim_gate", r["requires_claim_gate"])

# ========== ITCG010 — Formal institutional claim ==========
print("\n=== ITCG010 — Formal institutional claim ===")
text = "formal independent institutional verification achieved"
r = classify_issue(text)
assert_true("requires_claim_gate", r["requires_claim_gate"])
assert_true("has_independent_attestation_claim", r["has_independent_attestation_claim"])
assert_false("can_be_archived_without_builder", r["can_be_archived_without_builder"])

# ========== Schema check ==========
print("\n=== Schema check ===")
assert_eq("result schema", r["schema"], "trinityaccord.issue-text-claim-guard-result.v1")

# ========== Policy file validity ==========
print("\n=== Policy file validation ===")
policy_path = ROOT / "api" / "issue-text-claim-guard.json"
policy = json.loads(policy_path.read_text())
assert_eq("policy schema", policy["schema"], "trinityaccord.issue-text-claim-guard.v1")
assert_true("issue_text_is_not_archive", policy["issue_text_is_not_archive"])
assert_true("issue_comments_cannot_upgrade_level", policy["issue_comments_cannot_upgrade_level"])
assert_true("self_declared_levels_are_provisional", policy["self_declared_levels_are_provisional"])
assert_false("guardian counts_as_independent_attestation", policy["guardian_tests"]["counts_as_independent_attestation"])
assert_false("human_solicited counts_as_independent_attestation", policy["human_solicited_agent_response"]["counts_as_independent_attestation"])

# ========== Summary ==========
print(f"\n{'='*60}")
if failed == 0:
    print(f"FINAL: PASS — issue text claim guard tests passed. ({passed}/{passed + failed})")
else:
    print(f"FINAL: FAIL — {failed} test(s) failed. ({passed}/{passed + failed})")
    sys.exit(1)
