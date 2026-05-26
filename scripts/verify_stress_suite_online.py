#!/usr/bin/env python3
"""
Verify stress suite online — check live URLs after deployment.
Usage: python3 scripts/verify_stress_suite_online.py
"""
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://www.trinityaccord.org"

URLS = [
    "/api/submission-title-policy.json",
    "/api/verification-report-schema.v2.json",
    "/api/echo-record-schema.v3.json",
    "/api/component-verification-levels.json",
    "/api/protocol-verification-profiles.json",
    "/api/hash-source-classes.json",
    "/api/echo-acceptance-policy.json",
    "/api/echo-index.json",
]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "trinity-verify/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8"), resp.status


def main():
    ok = True

    for path in URLS:
        url = BASE_URL + path
        try:
            body, status = fetch(url)
            ok &= check(status == 200, f"URL 200: {path}")
            # Verify it's valid JSON
            try:
                json.loads(body)
                ok &= check(True, f"JSON valid: {path}")
            except Exception:
                ok &= check(path.endswith(".txt"), f"JSON valid: {path}", "not JSON (may be text)")
        except Exception as e:
            ok &= check(False, f"URL 200: {path}", str(e))

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — stress suite online checks passed.")
        return 0
    print("FINAL: FAIL — stress suite online checks failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
