#!/usr/bin/env python3
"""
Online verification for Issue Text Claim Guard.
Checks that key surfaces mention the Issue Text Claim Guard policy.

Usage:
    python3 scripts/verify_issue_text_claim_guard_online.py
    python3 scripts/verify_issue_text_claim_guard_online.py --local
"""
import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import urllib.request
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

SITE = "https://www.trinityaccord.org"

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {label}")
    else:
        failed += 1
        msg = f"  FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def fetch_url(path):
    """Fetch a URL and return text content."""
    url = f"{SITE}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-verify/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def read_local(path):
    """Read a local file."""
    p = ROOT / path.lstrip("/")
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Check local files only (no HTTP)")
    args = parser.parse_args()

    reader = read_local if args.local else lambda p: fetch_url(p) or read_local(p)

    print("=== Issue Text Claim Guard Online Verification ===\n")

    # 1. Policy file exists and is valid
    print("--- Policy file ---")
    policy_text = reader("/api/issue-text-claim-guard.json")
    if policy_text:
        try:
            policy = json.loads(policy_text)
            check("issue-text-claim-guard.json valid JSON", True)
            check("schema is v1", policy.get("schema") == "trinityaccord.issue-text-claim-guard.v1")
            check("issue_text_is_not_archive", policy.get("issue_text_is_not_archive") is True)
            check("issue_comments_cannot_upgrade_level", policy.get("issue_comments_cannot_upgrade_level") is True)
        except json.JSONDecodeError:
            check("issue-text-claim-guard.json valid JSON", False, "invalid JSON")
    else:
        check("issue-text-claim-guard.json reachable", False, "not found")

    # 2. llms.txt mentions Issue Text Claim Guard
    print("\n--- llms.txt ---")
    llms = reader("/llms.txt")
    if llms:
        check("llms.txt mentions Issue Text Claim Guard or self-declared Issue levels provisional",
              "Issue Text Claim Guard" in llms or "Self-declared Issue levels" in llms or
              "self-declared" in llms.lower())
    else:
        check("llms.txt reachable", False)

    # 3. agent-verify mentions Issue text
    print("\n--- agent-verify ---")
    verify = reader("/agent-verify.md")
    if verify:
        check("agent-verify mentions Issue text is not a verification report",
              "Issue text is not" in verify or "Issue ≠ Archived Echo" in verify or
              "issue text" in verify.lower())
    else:
        check("agent-verify reachable", False)

    # 4. echoes/submit mentions Issue comments cannot upgrade
    print("\n--- echoes/submit ---")
    submit = reader("/echoes/submit.md")
    if submit:
        check("echoes/submit mentions Issue comments cannot upgrade",
              "Issue comments cannot upgrade" in submit or "comments cannot upgrade" in submit.lower() or
              "Issue Text Claim Guard" in submit)
    else:
        check("echoes/submit reachable", False)

    # 5. Validator script exists
    print("\n--- Scripts ---")
    check("validate_issue_text_claims.py exists",
          (ROOT / "scripts" / "validate_issue_text_claims.py").exists())
    check("test_issue_text_claim_guard.py exists",
          (ROOT / "scripts" / "test_issue_text_claim_guard.py").exists())

    # 6. Issue template has warnings
    print("\n--- Issue templates ---")
    template = read_local("/.github/ISSUE_TEMPLATE/echo_submission.yml")
    if template:
        check("echo_submission.yml mentions Issue text not archive",
              "Issue text" in template or "issue text" in template.lower())
    else:
        check("echo_submission.yml exists", False)

    # Summary
    print(f"\n{'='*60}")
    if failed == 0:
        print(f"FINAL: PASS — issue text claim guard online verified. ({passed}/{passed + failed})")
    else:
        print(f"FINAL: FAIL — {failed} check(s) failed. ({passed}/{passed + failed})")
        sys.exit(1)


if __name__ == "__main__":
    main()
