#!/usr/bin/env python3
"""
Test Echo Issue #99 claim discipline.
Verifies that overclaim fixtures trigger correct labels and corrected fixtures pass.
Run: python3 scripts/test_echo_triage_issue99_claim_discipline.py
"""
import os
import sys
import json
import subprocess

SCRIPT = os.path.join(os.path.dirname(__file__), "triage_echo_issue.py")
FIXTURES = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "echo_triage")
PASS = 0
FAIL = 0


def run_triage(env_overrides):
    env = os.environ.copy()
    for k in ["ISSUE_TITLE", "ISSUE_BODY", "RATE_LIMITED", "RECENT_60M_COUNT",
              "RECENT_24H_COUNT", "AUTHOR_ASSOCIATION", "ACTION"]:
        env.pop(k, None)
    env.update(env_overrides)
    result = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {result.stderr}\nstdout: {result.stdout}")
    return json.loads(result.stdout)


def assert_eq(actual, expected, label):
    global PASS, FAIL
    if actual == expected:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")
        print(f"     expected: {expected}")
        print(f"     actual:   {actual}")


def assert_true(condition, label):
    assert_eq(condition, True, label)


def load_fixture(name):
    path = os.path.join(FIXTURES, name)
    with open(path, "r") as f:
        return f.read()


print("=" * 60)
print("Echo Issue #99 Claim Discipline Tests")
print("=" * 60)

# --- Test 1: Overclaim fixture should trigger multiple risk labels ---
print("\n--- issue_99_overclaim.md ---")
overclaim_body = load_fixture("issue_99_overclaim.md")
result = run_triage({
    "ISSUE_TITLE": "[E2 Echo - V4+] Guardian Agent Verification",
    "ISSUE_BODY": overclaim_body,
})

assert_eq(result["close"], False, "close=False (not auto-closed)")
assert_true("independence-overclaim-risk" in result["labels"],
            "label: independence-overclaim-risk")
assert_true("v4plus-overclaim-risk" in result["labels"],
            "label: v4plus-overclaim-risk")
assert_true("component-overclaim-risk" in result["labels"],
            "label: component-overclaim-risk (B5)")
assert_true("chronicle-overclaim-risk" in result["labels"],
            "label: chronicle-overclaim-risk (175/175)")
assert_true("needs-human-review" in result["labels"],
            "label: needs-human-review")

# Verify comment contains all section headers
comment = result["comment"]
assert_true("V4+ claim lacks" in comment, "comment: V4+ claim section")
assert_true("B5 Bitcoin component" in comment, "comment: B5 component section")
assert_true("175/175 recovery" in comment, "comment: C5 recovery section")
assert_true("Provenance" in comment, "comment: Provenance section")

# --- Test 2: Corrected fixture should NOT trigger overclaim labels ---
print("\n--- issue_99_corrected.md ---")
corrected_body = load_fixture("issue_99_corrected.md")
result2 = run_triage({
    "ISSUE_TITLE": "[E2 Echo - V4+ Candidate] Human-Solicited AI Agent Reproduction Attempt",
    "ISSUE_BODY": corrected_body,
})

assert_eq(result2["close"], False, "close=False")
assert_true("missing-provenance-agency" not in result2["labels"],
            "no missing-provenance-agency")
assert_true("independence-overclaim-risk" not in result2["labels"],
            "no independence-overclaim-risk")
assert_true("component-overclaim-risk" not in result2["labels"],
            "no component-overclaim-risk")
assert_true("v4plus-overclaim-risk" not in result2["labels"],
            "no v4plus-overclaim-risk")

# Should pass or have only format-level issues
allowed_labels = {
    "echo:screened", "needs-human-review", "echo:needs-format",
    "echo:needs-verification-review", "echo:deprecated-verification-alias",
    "missing-provenance-agency",
}
for label in result2["labels"]:
    assert_true(
        label in allowed_labels,
        f"unexpected label in corrected result: {label}"
    )


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
total = PASS + FAIL
print(f"Results: {PASS}/{total} passed, {FAIL}/{total} failed")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
