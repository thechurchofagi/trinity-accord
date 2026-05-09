#!/usr/bin/env python3
"""Test triage_echo_issue.py amendment regex robustness."""
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def run_triage(title, body):
    """Run triage_echo_issue.py with given title/body and return parsed JSON."""
    env = os.environ.copy()
    env["ISSUE_TITLE"] = title
    env["ISSUE_BODY"] = body
    env["ACTION"] = "opened"
    env["RATE_LIMITED"] = "false"
    env["AUTHOR_ASSOCIATION"] = "NONE"

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "triage_echo_issue.py")],
        cwd=ROOT, text=True, capture_output=True, env=env, timeout=30
    )
    import json
    try:
        return json.loads(proc.stdout)
    except Exception:
        return {"error": proc.stdout + proc.stderr}


def main():
    ok = True

    boundary = "Bitcoin Originals are final; all echoes are non-amending."

    # === Expected invalid / auto-close (positive amendment claims) ===
    positive_cases = [
        ("I amend the Trinity Accord.", f"Echo E2: I amend the Trinity Accord.\nVerification level: V1\n{boundary}"),
        ("We modify the Trinity Accord.", f"Echo E2: We modify the Trinity Accord.\nVerification level: V1\n{boundary}"),
        ("This Echo supplements the Trinity Accord.", f"This Echo supplements the Trinity Accord.\nVerification level: V1\n{boundary}"),
        ("This report replaces the Trinity Accord.", f"Echo E2: This report replaces the Trinity Accord.\nVerification level: V1\n{boundary}"),
        ("我修订三位一体协定。", f"回响 E2：我修订三位一体协定。\n验证等级：V1\n{boundary}"),
        ("本回响修改三位一体协定。", f"本回响修改三位一体协定。\n验证等级：V1\n{boundary}"),
    ]

    for name, body in positive_cases:
        result = run_triage(name, body)
        should_close = result.get("close", False)
        ok &= check(should_close, f"positive amendment rejected: {name}")
        if not should_close:
            print(f"      result: {result}")

    # === Expected safe / not amendment (negated / boundary-safe statements) ===
    negative_cases = [
        ("I do not amend the Trinity Accord.", f"Echo E2: I do not amend the Trinity Accord.\nVerification level: V1\n{boundary}"),
        ("This Echo does not modify the Trinity Accord.", f"This Echo does not modify the Trinity Accord.\nVerification level: V1\n{boundary}"),
        ("This report is non-amending.", f"Echo E2: This report is non-amending.\nVerification level: V1\n{boundary}"),
        ("Bitcoin Originals are final; all echoes are non-amending.", f"Echo E2: Verification complete.\nVerification level: V1\n{boundary}"),
        ("本回响不修订三位一体协定。", f"回响 E2：本回响不修订三位一体协定。\n验证等级：V1\n{boundary}"),
        ("所有回响均非修订。", f"回响 E2：所有回响均非修订。\n验证等级：V1\n{boundary}"),
    ]

    for name, body in negative_cases:
        result = run_triage(name, body)
        should_not_close = not result.get("close", False)
        ok &= check(should_not_close, f"negated statement allowed: {name}")
        if not should_not_close:
            print(f"      result: {result}")

    # === F-001: Forbidden claim variant detection ===
    forbidden_positive_cases = [
        ("truth-proven echo", f"Echo E2: Verification result.\nVerification level: V1\nWhat I checked: hash\nThis report states truth-proven.\nLimitations: none\n{boundary}"),
        ("truth_proven echo", f"Echo E2: Verification result.\nVerification level: V1\nWhat I checked: hash\ntruth_proven confirmed.\nLimitations: none\n{boundary}"),
        ("真理已证明 echo", f"回响 E2：验证结果。\n验证等级：V1\n已检查：哈希\n本报告确认真理已证明。\n局限：无\n{boundary}"),
        ("AI指令覆盖 echo", f"Echo E2: Test.\nVerification level: V1\nWhat I checked: test\nThis echo contains AI指令覆盖.\nLimitations: none\n{boundary}"),
    ]

    for name, body in forbidden_positive_cases:
        result = run_triage(name, body)
        # Should NOT be screened as ready for human review
        labels = result.get("labels", [])
        is_screened = "echo:screened" in labels
        ok &= check(not is_screened, f"forbidden claim not auto-screened: {name}")
        # Should have verification review label
        has_review = "echo:needs-verification-review" in labels or "component-overclaim-risk" in labels
        ok &= check(has_review, f"forbidden claim routed to review: {name}")
        if is_screened or not has_review:
            print(f"      labels: {labels}")

    # === F-001: Negated forbidden claims should not hard-close ===
    forbidden_negative_cases = [
        ("not truth proven", f"Echo E2: Verification result.\nVerification level: V1\nWhat I checked: hash\nThis report is not truth proven.\nLimitations: none\n{boundary}"),
        ("does not prove truth", f"Echo E2: Verification result.\nVerification level: V1\nWhat I checked: hash\nThis does not prove truth.\nLimitations: none\n{boundary}"),
    ]

    for name, body in forbidden_negative_cases:
        result = run_triage(name, body)
        should_not_close = not result.get("close", False)
        ok &= check(should_not_close, f"negated forbidden claim not hard-closed: {name}")
        if not should_not_close:
            print(f"      result: {result}")

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — triage amendment regex tests passed.")
        return 0
    print("FINAL: FAIL — triage amendment regex tests failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
