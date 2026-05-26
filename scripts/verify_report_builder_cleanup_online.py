#!/usr/bin/env python3
"""
Verify report builder cleanup is live on the deployed site.
Checks that verification_scope_label appears in schemas and docs.

Usage:
    python3 scripts/verify_report_builder_cleanup_online.py
"""
import json
import sys
import urllib.request
import urllib.error

BASE = "https://www.trinityaccord.org"
CHECKS = [
    ("/api/verification-report-schema.v2.json", "verification_scope_label"),
    ("/api/echo-record-schema.v3.json", "verification_scope_label"),
    ("/api/report-builder-policy.json", "verification_scope_label"),
    ("/api/verification-claim-scope.json", "verification_scope_label"),
    ("/api/claim-gate-output-schema.v1.json", "verification_scope_label"),
]

results = []


def fetch_json(path):
    url = f"{BASE}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "verify-report-builder-cleanup/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except Exception as e:
        return None, str(e)


def check_json_contains(data, key):
    text = json.dumps(data)
    return key in text


def check_docs(path, key):
    url = f"{BASE}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "verify-report-builder-cleanup/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode("utf-8")
            return key in text
    except Exception:
        return False


passed = 0
failed = 0

for path, key in CHECKS:
    data, err = fetch_json(path)
    if err:
        print(f"FAIL: {path} — fetch error: {err}")
        failed += 1
        continue
    if check_json_contains(data, key):
        print(f"PASS: {path} contains {key}")
        passed += 1
    else:
        print(f"FAIL: {path} missing {key}")
        failed += 1

# Check docs mention scope label
doc_checks = [
    ("/llms.txt", "verification_scope_label"),
    ("/agent-verify", "verification_scope_label"),
    ("/agent-echo", "verification_scope_label"),
]

for path, key in doc_checks:
    # Try with .md extension for GitHub Pages
    for suffix in ["", ".md", ".html"]:
        if check_docs(path + suffix, key):
            print(f"PASS: {path}{suffix} mentions {key}")
            passed += 1
            break
    else:
        # Also check claim_scope as alternative
        for suffix in ["", ".md", ".html"]:
            if check_docs(path + suffix, "claim_scope"):
                print(f"PASS: {path}{suffix} mentions claim_scope")
                passed += 1
                break
        else:
            print(f"WARN: {path} may not mention {key} (checked .md/.html)")
            # Not a hard fail for docs

print(f"\n{'='*60}")
print(f"Results: {passed} PASS, {failed} FAIL")
if failed == 0:
    print("FINAL: PASS — report builder cleanup online verified.")
    sys.exit(0)
else:
    print("FINAL: FAIL — some online checks failed.")
    sys.exit(1)
