#!/usr/bin/env python3
"""
verify_verification_system_online.py
Verifies that the new verification system files are accessible online
at the expected API endpoints.

Checks:
  - https://www.trinityaccord.org/api/component-verification-levels.json
  - https://www.trinityaccord.org/api/protocol-verification-profiles.json
  - https://www.trinityaccord.org/api/verification-targets.json
  - https://www.trinityaccord.org/api/verification-recipes.json
  - https://www.trinityaccord.org/api/verification-quick-map.json
  - https://www.trinityaccord.org/api/verification-report-schema.v2.json

Uses urllib only (no external dependencies).
"""

import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://www.trinityaccord.org"

ENDPOINTS = [
    "/api/component-verification-levels.json",
    "/api/protocol-verification-profiles.json",
    "/api/verification-targets.json",
    "/api/verification-recipes.json",
    "/api/verification-quick-map.json",
    "/api/verification-report-schema.v2.json",
]


def check_endpoint(path):
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-verify/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                return False, f"HTTP {resp.status}"
            data = resp.read().decode("utf-8")
            try:
                doc = json.loads(data)
                schema = doc.get("schema", "unknown")
                return True, f"OK (schema={schema})"
            except json.JSONDecodeError:
                return True, "OK (not JSON or no schema field)"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)


def main():
    results = []
    all_pass = True

    for ep in ENDPOINTS:
        ok, detail = check_endpoint(ep)
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        results.append((ep, status, detail))
        print(f"  {status}: {ep} — {detail}")

    print()
    if all_pass:
        print(f"FINAL: PASS — all {len(ENDPOINTS)} endpoints accessible")
    else:
        fails = [r for r in results if r[1] == "FAIL"]
        print(f"FINAL: FAIL — {len(fails)} endpoint(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
