#!/usr/bin/env python3
"""
Online verification of Issue #88 closure.
Usage: python3 scripts/verify_issue88_closure_online.py
"""
import json
import sys
import urllib.request
import urllib.error

BASE = "https://www.trinityaccord.org"

URLS = [
    "/api/echo-index.json",
    "/api/verification-report-schema.v2.json",
    "/api/echo-record-schema.v3.json",
    "/verification-reports/v3/2026-05-03-v3-verification-openclaw.json",
    "/echoes/records/2026/echo-2026-05-03-000005.json",
    "/api/repository-artifact-hashes.json",
    "/api/hash-source-classes.json",
]

B1_FORBIDDEN = ["ordinals envelope detected", "inscription content detected",
                "witness extracted", "body parsed", "body hash reproduced"]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def fetch_json(path):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8")), resp.status


def main():
    ok = True

    # 1. All URLs return 200
    for path in URLS:
        try:
            _, status = fetch_json(path)
            ok &= check(status == 200, f"{path} HTTP {status}")
        except Exception as e:
            ok &= check(False, f"{path} reachable", str(e)[:80])

    # 2. Report JSON parses and has scope_class
    try:
        report, _ = fetch_json("/verification-reports/v3/2026-05-03-v3-verification-openclaw.json")
        ok &= check(True, "report JSON parses")
        report_text = json.dumps(report, ensure_ascii=False).lower()

        # scope_class present
        has_scope = any("scope_class" in json.dumps(f) for f in report.get("component_findings", []))
        ok &= check(has_scope, "report contains scope_class")

        # No V3_single_artifact_check
        ok &= check("v3_single_artifact_check" not in report_text, "report no V3_single_artifact_check")

        # No B1 forbidden
        for phrase in B1_FORBIDDEN:
            ok &= check(phrase not in report_text, f"report no '{phrase}'")

        # expected_hash_source in schema
        schema, _ = fetch_json("/api/verification-report-schema.v2.json")
        props = schema["properties"]["hashes_computed"]["items"]["properties"]
        ok &= check("expected_hash_source" in props, "schema requires expected_hash_source")
        ok &= check("expected_hash_authority_class" in props, "schema requires expected_hash_authority_class")
    except Exception as e:
        ok &= check(False, "report validation", str(e)[:80])

    # 3. Wrapper has E2_verification_echo
    try:
        wrapper, _ = fetch_json("/echoes/records/2026/echo-2026-05-03-000005.json")
        ok &= check(wrapper.get("echo_type") == "E2_verification_echo", "wrapper E2_verification_echo")
    except Exception as e:
        ok &= check(False, "wrapper validation", str(e)[:80])

    # 4. Echo index includes wrapper
    try:
        idx, _ = fetch_json("/api/echo-index.json")
        paths = [r.get("path", "") for r in idx.get("records", [])]
        ok &= check(
            "/echoes/records/2026/echo-2026-05-03-000005.json" in paths,
            "echo-index includes wrapper 000005"
        )
    except Exception as e:
        ok &= check(False, "echo-index validation", str(e)[:80])

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — Issue #88 online closure verified.")
        return 0
    print("FINAL: FAIL — Issue #88 online closure verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
