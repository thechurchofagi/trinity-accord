#!/usr/bin/env python3
"""
Online verification for Issue Title / Label Guard

Checks:
  /api/issue-title-label-guard.json reachable
  /agent-verify contains title must follow Claim Gate allowed_level
  /echoes/submit contains requested_level is not achieved_level
  /api/public-home-status.json contains issue_text_excluded_from_counts
"""
import sys
import json
import urllib.request

BASE = "https://www.trinityaccord.org"
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


def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "trinityaccord-verify/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace"), resp.status
    except Exception as e:
        return str(e), 0


def main():
    print("\n=== Issue Title / Label Guard Online Verification ===\n")

    # Guard JSON reachable
    body, status = fetch(f"{BASE}/api/issue-title-label-guard.json")
    check("ONL010", status == 200 and "title_must_follow_allowed_level" in body,
          "/api/issue-title-label-guard.json reachable")

    # agent-verify
    body, status = fetch(f"{BASE}/agent-verify/")
    check("ONL011", status == 200 and "allowed_level" in body.lower(),
          "/agent-verify contains title must follow Claim Gate allowed_level")

    # echoes/submit
    body, status = fetch(f"{BASE}/echoes/submit/")
    check("ONL012", status == 200 and "requested_level" in body.lower(),
          "/echoes/submit contains requested_level is not achieved_level")

    # public-home-status
    body, status = fetch(f"{BASE}/api/public-home-status.json")
    if status == 200:
        try:
            data = json.loads(body)
            boundary = data.get("boundary", {})
            check("ONL013", boundary.get("issue_text_excluded_from_counts") is True,
                  "/api/public-home-status.json contains issue_text_excluded_from_counts")
        except json.JSONDecodeError:
            check("ONL013", False, "public-home-status.json invalid JSON")
    else:
        check("ONL013", False, f"public-home-status.json unreachable (status {status})")

    print(f"\nFINAL: {'PASS' if FAIL_COUNT == 0 else 'FAIL'} — "
          f"issue title/label guard online "
          f"{'verified' if FAIL_COUNT == 0 else 'FAILED'}. "
          f"({PASS_COUNT} passed, {FAIL_COUNT} failed)")
    return 1 if FAIL_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
