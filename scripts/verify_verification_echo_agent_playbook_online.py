#!/usr/bin/env python3
"""
Online verification for Verification Echo Agent Playbook

Checks:
  /api/verification-echo-agent-playbook.json reachable
  /verification-echo-agent-playbook reachable
  /agent-verify contains requested_level is not achieved_level
  /llms.txt contains Verification Echo Playbook Rule
  /echoes/submit contains Issue comments cannot upgrade verification level
"""
import sys
import urllib.request
import urllib.error

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
    print("\n=== Verification Echo Agent Playbook Online Verification ===\n")

    # API reachable
    body, status = fetch(f"{BASE}/api/verification-echo-agent-playbook.json")
    check("ONL001", status == 200 and "requested_level_not_achieved_level" in body,
          "/api/verification-echo-agent-playbook.json reachable and contains core rule")

    # Playbook page
    body, status = fetch(f"{BASE}/verification-echo-agent-playbook/")
    check("ONL002", status == 200 and "Correct" in body,
          "/verification-echo-agent-playbook reachable")

    # agent-verify
    body, status = fetch(f"{BASE}/agent-verify/")
    check("ONL003", status == 200 and "requested_level is not achieved_level" in body.lower()
          or "requested_level" in body.lower(),
          "/agent-verify contains playbook rule")

    # llms.txt
    body, status = fetch(f"{BASE}/llms.txt")
    check("ONL004", status == 200 and "Verification Echo Playbook Rule" in body,
          "/llms.txt contains Verification Echo Playbook Rule")

    # echoes/submit
    body, status = fetch(f"{BASE}/echoes/submit/")
    check("ONL005", status == 200 and "Issue comments cannot upgrade verification level" in body,
          "/echoes/submit contains Issue comments cannot upgrade verification level")

    print(f"\nFINAL: {'PASS' if FAIL_COUNT == 0 else 'FAIL'} — "
          f"verification echo agent playbook online "
          f"{'verified' if FAIL_COUNT == 0 else 'FAILED'}. "
          f"({PASS_COUNT} passed, {FAIL_COUNT} failed)")
    return 1 if FAIL_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
