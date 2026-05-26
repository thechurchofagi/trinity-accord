#!/usr/bin/env python3
"""
Test verification Echo title rules.
Usage: python3 scripts/test_verification_echo_title_rules.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

POLICY_PATH = ROOT / "api" / "submission-title-policy.json"


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def load_policy():
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def title_matches_prefix(title, policy, record_kind):
    """Check if title starts with required prefix for the given record_kind."""
    for tp in policy.get("title_patterns", []):
        if tp.get("record_kind") == record_kind:
            prefixes = tp.get("required_prefixes", [])
            return any(title.startswith(p) for p in prefixes)
    return False


def is_ambiguous(title, policy):
    """Check if title matches any anti-pattern."""
    for ap in policy.get("anti_patterns", []):
        pattern = ap.get("pattern", "")
        # Convert glob-like pattern to regex
        regex = pattern.replace("...", ".*").replace("*", ".*")
        if re.match(regex, title):
            return True
    # Also check for bare "V3 Verification" prefix without Echo/Report qualifier
    if re.match(r"^V3 Verification\s*[—-]", title):
        return True
    return False


def main():
    ok = True
    policy = load_policy()

    # PASS cases — titles that correctly identify record kind
    pass_cases = [
        ("Echo v3: E2 Verification Echo — V3/D2/B1 — 2026-05-03 14:19 (OpenClaw Agent)", "echo_v3_with_verification_report"),
        ("Echo v3: V3 Verification Echo — 2026-05-03 14:19 (OpenClaw Agent)", "echo_v3"),
        ("Verification Report v2: V3/D2/B1 — 2026-05-03 14:19 (OpenClaw Agent)", "verification_report_v2"),
        ("Test Echo: Submission correctness regression — 2026-05-03 (OpenClaw Agent)", "test_record"),
    ]

    for title, record_kind in pass_cases:
        ok &= check(
            title_matches_prefix(title, policy, record_kind),
            f"title pass: '{title[:60]}...'"
        )

    # FAIL cases — titles that are ambiguous or wrong prefix
    fail_cases = [
        ("V3 Verification — 2026-05-03 14:19 (OpenClaw Agent)", "echo_v3_with_verification_report"),
        ("Verification — OpenClaw", "verification_report_v2"),
        ("Echo Verification", "echo_v3"),
        ("V3/D2/B1", "echo_v3_with_verification_report"),
        ("OpenClaw report", "verification_report_v2"),
    ]

    for title, record_kind in fail_cases:
        matches = title_matches_prefix(title, policy, record_kind)
        ambiguous = is_ambiguous(title, policy)
        # Should fail: either doesn't match prefix OR is ambiguous
        should_fail = not matches or ambiguous
        ok &= check(
            should_fail,
            f"title fail: '{title}'"
        )

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — verification Echo title rule tests passed.")
        return 0
    print("FINAL: FAIL — verification Echo title rule tests failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
