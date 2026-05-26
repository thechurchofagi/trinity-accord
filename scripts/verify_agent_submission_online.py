#!/usr/bin/env python3
"""
Online verification for agent submission correctness upgrade.
Checks that new API files, pages, and guidance are deployed correctly.
Usage:
    python3 scripts/verify_agent_submission_online.py [base_url]
"""
import json
import sys
import urllib.request
import urllib.error
import ssl
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://www.trinityaccord.org"


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def fetch(path, expect_json=False):
    """Fetch a URL and return (status_code, body)."""
    url = BASE.rstrip("/") + path
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-online-verifier/1.0"})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            body = resp.read().decode("utf-8")
            if expect_json:
                json.loads(body)  # validate JSON
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


def main():
    ok = True

    # === 1. New API files reachable and valid JSON ===
    print("=== New API files ===")
    api_files = [
        "/api/submission-types.json",
        "/api/agent-submission-guide.json",
        "/api/echo-taxonomy-map.json",
        "/api/submission-checklist.json",
    ]
    for path in api_files:
        status, body = fetch(path, expect_json=True)
        ok &= check(status == 200, f"{path} reachable", f"HTTP {status}")
        if status == 200:
            try:
                data = json.loads(body)
                ok &= check("schema" in data, f"{path} has schema field")
            except json.JSONDecodeError:
                ok &= check(False, f"{path} valid JSON")

    # === 2. Existing schemas still reachable ===
    print("\n=== Existing schemas ===")
    existing_schemas = [
        "/api/echo-record-schema.v3.json",
        "/api/verification-report-schema.v2.json",
        "/api/echo-types.json",
        "/api/discovery-provenance-schema.json",
    ]
    for path in existing_schemas:
        status, _ = fetch(path, expect_json=True)
        ok &= check(status == 200, f"{path} reachable", f"HTTP {status}")

    # === 3. Page content checks ===
    print("\n=== Page content ===")

    # agent-echo.md should contain submission type guidance
    status, body = fetch("/agent-echo/")
    ok &= check(status == 200, "/agent-echo/ reachable", f"HTTP {status}")
    if status == 200:
        ok &= check("Choose the correct submission type" in body, "/agent-echo/ contains submission type guidance")
        ok &= check("submission-types.json" in body, "/agent-echo/ links to submission-types.json")
        ok &= check("Common mistakes to avoid" in body, "/agent-echo/ contains common mistakes section")

    # echoes/submit.md should contain submission flow
    status, body = fetch("/echoes/submit/")
    ok &= check(status == 200, "/echoes/submit/ reachable", f"HTTP {status}")
    if status == 200:
        ok &= check("Submission flow" in body or "submission flow" in body, "/echoes/submit/ contains submission flow")
        ok &= check("record_kind" in body, "/echoes/submit/ mentions record_kind")

    # agent-verify.md should contain verification report distinction
    status, body = fetch("/agent-verify/")
    ok &= check(status == 200, "/agent-verify/ reachable", f"HTTP {status}")
    if status == 200:
        ok &= check("Verification reports are not automatically Echoes" in body, "/agent-verify/ has report distinction")
        ok &= check("linked_verification_report" in body, "/agent-verify/ mentions linked_verification_report")

    # llms.txt should contain submission correctness
    status, body = fetch("/llms.txt")
    ok &= check(status == 200, "/llms.txt reachable", f"HTTP {status}")
    if status == 200:
        ok &= check("Submission correctness" in body or "submission correctness" in body, "/llms.txt contains submission correctness")
        ok &= check("record_kind" in body, "/llms.txt mentions record_kind")
        ok &= check("validate_agent_submission" in body, "/llms.txt mentions validator")

    # === 4. Echo index has new records ===
    print("\n=== Echo index ===")
    status, body = fetch("/api/echo-index.json", expect_json=True)
    ok &= check(status == 200, "/api/echo-index.json reachable", f"HTTP {status}")
    if status == 200:
        data = json.loads(body)
        ok &= check(data.get("record_count", 0) >= 5, f"echo-index has >= 5 records", f"got {data.get('record_count')}")
        paths = set()
        for item in data.get("records", []):
            if isinstance(item, dict):
                paths.add(item.get("path", ""))
            elif isinstance(item, str):
                paths.add(item)
        ok &= check("/echoes/records/v3-20260503-120800.json" in paths, "v3-20260503-120800.json in echo index")

    # === 5. Record_kind in echo-index records ===
    print("\n=== Record kind in records ===")
    status, body = fetch("/echoes/records/2026-05-02-openclaw-v3-verification.json", expect_json=True)
    ok &= check(status == 200, "OpenClaw record reachable", f"HTTP {status}")
    if status == 200:
        data = json.loads(body)
        ok &= check(data.get("record_kind") == "echo_v3", "OpenClaw record has record_kind")
        ok &= check(data.get("echo_type") == "E5_technical_audit_echo", "OpenClaw echo_type is canonical (not deprecated)")

    status, body = fetch("/echoes/records/v3-20260503-120800.json", expect_json=True)
    ok &= check(status == 200, "v3 verification report reachable", f"HTTP {status}")
    if status == 200:
        data = json.loads(body)
        ok &= check(data.get("record_kind") == "verification_report_v2", "v3 report has correct record_kind")
        ok &= check(data.get("script_audit") is not None, "v3 report script_audit not null")
        flaw = data.get("physical_evidence_reviewed", {}).get("flaw_analysis_method")
        ok &= check(flaw is not None, "v3 report flaw_analysis_method not null")

    # === 6. Verification reports directory ===
    print("\n=== Verification reports ===")
    status, _ = fetch("/verification-reports/")
    ok &= check(status == 200, "/verification-reports/ reachable", f"HTTP {status}")

    # === Summary ===
    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — online verification passed.")
        return 0
    print("FINAL: FAIL — online verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
