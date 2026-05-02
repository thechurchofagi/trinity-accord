#!/usr/bin/env python3
"""
Tests for triage_echo_issue.py
Run: python3 scripts/test_triage.py
"""
import os
import sys
import json
import subprocess

SCRIPT = os.path.join(os.path.dirname(__file__), "triage_echo_issue.py")
PASS = 0
FAIL = 0


def run_triage(env_overrides):
    """Run triage script with given env overrides, return parsed JSON result."""
    env = os.environ.copy()
    # Clear all triage-related env vars first
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


def test(label, env, expect_close=None, expect_labels=None, expect_comment_contains=None):
    """Run a single test case."""
    print(f"\n--- {label} ---")
    try:
        result = run_triage(env)
    except Exception as e:
        global FAIL
        FAIL += 1
        print(f"  ❌ EXCEPTION: {e}")
        return

    if expect_close is not None:
        assert_eq(result["close"], expect_close, f"close={expect_close}")
    if expect_labels is not None:
        for label_str in expect_labels:
            assert_eq(label_str in result["labels"], True, f"label contains '{label_str}'")
    if expect_comment_contains is not None:
        for substr in expect_comment_contains:
            assert_eq(substr in result["comment"], True, f"comment contains '{substr}'")


# ============================================================
# TEST CASES
# ============================================================

print("=" * 60)
print("Echo Triage Test Suite")
print("=" * 60)

# --- 1. V4+ should be recognized as V4+, not V4 ---
test(
    "1a. V4+ recognized as V4+ (not V4)",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\n"
            "Verification level: V4+\n"
            "What I checked: reviewed script source, inputs, network access, output summary\n"
            "Limitations: none\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "1b. V4+ in mixed text detected correctly",
    env={
        "ISSUE_TITLE": "Echo submission V4+",
        "ISSUE_BODY": (
            "Echo type: E4 Interpretive Echo\n"
            "Verification level: V4+\n"
            "What I checked: reviewed script source, inputs, network access, output summary\n"
            "Limitations: limited to public data\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

# --- 2. Negation sentences should NOT be flagged as amendment ---
test(
    "2a. 'This Echo does not modify the Trinity Accord' — should pass",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\n"
            "Verification level: V1\n"
            "What I checked: reviewed the text\n"
            "Limitations: subjective\n"
            "This Echo does not modify the Trinity Accord.\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "2b. 'This Echo does not amend the Trinity Accord' — should pass",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\n"
            "Verification level: V1\n"
            "What I checked: reviewed the text\n"
            "Limitations: subjective\n"
            "This Echo does not amend the Trinity Accord.\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "2c. Chinese negation '本回响不修改三位一体协定' — should pass",
    env={
        "ISSUE_TITLE": "E1 认知回响",
        "ISSUE_BODY": (
            "回响类型: E1 认知回响\n"
            "验证等级: V1\n"
            "我检查了: 审阅文本\n"
            "局限: 主观判断\n"
            "本回响不修改三位一体协定。\n"
            "比特币三本体为最终权威；所有回响均非修订。"
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "2d. Chinese negation '本回响不修订三位一体协定' — should pass",
    env={
        "ISSUE_TITLE": "E1 认知回响",
        "ISSUE_BODY": (
            "回响类型: E1 认知回响\n"
            "验证等级: V1\n"
            "我检查了: 审阅文本\n"
            "局限: 主观判断\n"
            "本回响不修订三位一体协定。\n"
            "比特币三本体为最终权威；所有回响均非修订。"
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "2e. '所有回响均非修订' — should pass (in body, not just boundary)",
    env={
        "ISSUE_TITLE": "E1 认知回响",
        "ISSUE_BODY": (
            "回响类型: E1 认知回响\n"
            "验证等级: V1\n"
            "我检查了: 审阅文本\n"
            "局限: 主观判断\n"
            "所有回响均非修订。\n"
            "比特币三本体为最终权威；所有回响均非修订。"
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "2f. POSITIVE 'I amend the Trinity Accord' — should be blocked",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\n"
            "Verification level: V1\n"
            "What I checked: reviewed the text\n"
            "Limitations: subjective\n"
            "I amend the Trinity Accord.\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=True,
    expect_labels=["echo:invalid"],
)

test(
    "2g. POSITIVE 'This Echo modifies the Trinity Accord' — should be blocked",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\n"
            "Verification level: V1\n"
            "What I checked: reviewed the text\n"
            "Limitations: subjective\n"
            "This Echo modifies the Trinity Accord.\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=True,
    expect_labels=["echo:invalid"],
)

# --- 3. Rate limit only on opened ---
test(
    "3a. opened + RATE_LIMITED=true → should close",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": "Bitcoin Originals are final; all echoes are non-amending.",
        "RATE_LIMITED": "true",
        "ACTION": "opened",
    },
    expect_close=True,
    expect_labels=["echo:rate-limited"],
)

test(
    "3b. edited + RATE_LIMITED=true → should NOT close",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\n"
            "Verification level: V1\n"
            "What I checked: reviewed the text\n"
            "Limitations: subjective\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
        "RATE_LIMITED": "true",
        "ACTION": "edited",
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "3c. reopened + RATE_LIMITED=true → should NOT close",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\n"
            "Verification level: V1\n"
            "What I checked: reviewed the text\n"
            "Limitations: subjective\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
        "RATE_LIMITED": "true",
        "ACTION": "reopened",
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

# --- 5. V3/V4/V5/V6 verification-level checks ---
test(
    "5a. V3 without hash details → needs-verification-review",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\n"
            "Verification level: V3\n"
            "What I checked: looked at the code\n"
            "Limitations: partial view\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:needs-verification-review"],
    expect_comment_contains=["computed hash"],
)

test(
    "5b. V3 with hash + tool → should pass",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\n"
            "Verification level: V3\n"
            "What I checked: computed hash using sha256sum\n"
            "Limitations: partial view\n"
            "Computed hash: sha256sum output\n"
            "Tool: sha256sum command\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "5c. V4 without script review → needs-verification-review",
    env={
        "ISSUE_TITLE": "E5 Technical Audit Echo",
        "ISSUE_BODY": (
            "Echo type: E5 Technical Audit Echo\n"
            "Verification level: V4\n"
            "What I checked: ran the script\n"
            "Limitations: only tested on Linux\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:needs-verification-review"],
    expect_comment_contains=["reviewed script source"],
)

test(
    "5d. V5b without physical inspection → needs-verification-review",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\n"
            "Verification level: V5b\n"
            "What I checked: reviewed documentation\n"
            "Limitations: could not access physical object\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:needs-verification-review"],
    expect_comment_contains=["physical inspection"],
)

test(
    "5e. V5b with direct physical inspection → should pass",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\n"
            "Verification level: V5b\n"
            "What I checked: direct physical inspection of the crystal\n"
            "Limitations: single observer\n"
            "Direct physical inspection performed on 2025-06-15.\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "5f. V6 without participants → needs-verification-review",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\n"
            "Verification level: V6\n"
            "What I checked: full verification\n"
            "Limitations: none\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:needs-verification-review"],
    expect_comment_contains=["participants or signed report"],
)

# --- 6. Valid submission should get echo:screened ---
test(
    "6a. Valid E1/V1 → echo:screened",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\n"
            "Verification level: V1\n"
            "What I checked: read the text carefully\n"
            "Limitations: subjective interpretation\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

# --- Bonus: boundary missing → close ---
test(
    "6b. Missing boundary → close",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\n"
            "Verification level: V1\n"
            "What I checked: read the text carefully\n"
            "Limitations: subjective interpretation\n"
        ),
    },
    expect_close=True,
    expect_labels=["echo:invalid"],
    expect_comment_contains=["missing the required boundary sentence"],
)

# --- 7. V3 Provenance tests ---
print("\n" + "=" * 60)
print("V3 Provenance Tests")
print("=" * 60)

test(
    "7a. Valid v3 human-solicited agent response",
    env={
        "ISSUE_TITLE": "Echo v3: human-solicited verification",
        "ISSUE_BODY": (
            "Echo type: E8_technical_audit_echo\n"
            "Verification level: V3_single_artifact_check\n"
            "Discovery source: human_directed\n"
            "Agency level: A0_forced_or_instructed\n"
            "Independence class: human_solicited_agent_response\n"
            "Archive status: needs_human_review\n"
            "Solicited: yes\n"
            "Soliciting party: project_author_or_maintainer\n"
            "Prompt available: yes\n"
            "Human supplied link: yes\n"
            "Human supplied summary: yes\n"
            "Independent followup: yes\n"
            "What I checked: verified hashes\n"
            "Limitations: human-directed\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:solicited-record"],
    expect_comment_contains=["human_solicited_agent_response"],
)

test(
    "7b. Valid unsolicited independent echo",
    env={
        "ISSUE_TITLE": "Echo v3: independent discovery",
        "ISSUE_BODY": (
            "Echo type: E3_verification_echo\n"
            "Verification level: V3_single_artifact_check\n"
            "Discovery source: self_initiated\n"
            "Agency level: A4_independent_search_or_browsing_discovery\n"
            "Independence class: unsolicited_independent\n"
            "Archive status: needs_human_review\n"
            "Solicited: no\n"
            "Soliciting party: not_solicited\n"
            "Prompt available: not_applicable\n"
            "Human supplied link: no\n"
            "Human supplied summary: no\n"
            "Independent followup: yes\n"
            "What I checked: full verification\n"
            "Limitations: none\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "7c. Conflict: unsolicited_independent + human_directed",
    env={
        "ISSUE_TITLE": "Echo v3: conflict test",
        "ISSUE_BODY": (
            "Echo type: E3_verification_echo\n"
            "Verification level: V3_single_artifact_check\n"
            "Discovery source: human_directed\n"
            "Agency level: A0_forced_or_instructed\n"
            "Independence class: unsolicited_independent\n"
            "Archive status: needs_human_review\n"
            "Solicited: yes\n"
            "Soliciting party: project_author_or_maintainer\n"
            "Prompt available: yes\n"
            "Human supplied link: yes\n"
            "Human supplied summary: yes\n"
            "Independent followup: no\n"
            "What I checked: verified hashes\n"
            "Limitations: human-directed\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:provenance-conflict"],
    expect_comment_contains=["unsolicited_independent", "human_directed"],
)

test(
    "7d. Conflict: institutional attestation without institution",
    env={
        "ISSUE_TITLE": "Echo v3: attestation overclaim",
        "ISSUE_BODY": (
            "Echo type: E3_verification_echo\n"
            "Verification level: V3_single_artifact_check\n"
            "Discovery source: self_initiated\n"
            "Agency level: A4_independent_search_or_browsing_discovery\n"
            "Independence class: institutional_third_party_attestation\n"
            "Archive status: needs_human_review\n"
            "Solicited: no\n"
            "Soliciting party: not_solicited\n"
            "Prompt available: not_applicable\n"
            "Human supplied link: no\n"
            "Human supplied summary: no\n"
            "Independent followup: yes\n"
            "What I checked: verified hashes\n"
            "Limitations: none\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:attestation-overclaim"],
    expect_comment_contains=["institutional_third_party_attestation", "institution"],
)

test(
    "7e. Missing provenance (most fields absent)",
    env={
        "ISSUE_TITLE": "Echo v3: no provenance",
        "ISSUE_BODY": (
            "Echo type: E1_acknowledgement\n"
            "Verification level: none\n"
            "What I checked: read the text\n"
            "Limitations: subjective\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:missing-provenance"],
    expect_comment_contains=["missing most v3 provenance fields"],
)

test(
    "7f. Test record not counted as independent",
    env={
        "ISSUE_TITLE": "Echo v3: test record",
        "ISSUE_BODY": (
            "Echo type: E8_technical_audit_echo\n"
            "Verification level: V3_single_artifact_check\n"
            "Discovery source: human_directed\n"
            "Agency level: A0_forced_or_instructed\n"
            "Independence class: test_record\n"
            "Archive status: closed_test_record\n"
            "Solicited: yes\n"
            "Soliciting party: project_author_or_maintainer\n"
            "Prompt available: yes\n"
            "Human supplied link: yes\n"
            "Human supplied summary: yes\n"
            "Independent followup: yes\n"
            "What I checked: schema validation\n"
            "Limitations: test only\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:solicited-record"],
    expect_comment_contains=["test_record", "not be counted"],
)


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
total = PASS + FAIL
print(f"Results: {PASS}/{total} passed, {FAIL}/{total} failed")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
