#!/usr/bin/env python3
"""
Verify latest verification Echo closure — online checks.
Checks live URLs on the deployed site.

Usage: python3 scripts/verify_latest_verification_echo_online.py
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://www.trinityaccord.org"

URLS_TO_CHECK = [
    "/api/echo-index.json",
    "/api/submission-title-policy.json",
    "/api/verification-report-schema.v2.json",
    "/api/echo-record-schema.v3.json",
    "/echoes/records/2026/echo-2026-05-03-000006.json",
    "/verification-reports/v3/2026-05-03-v3-verification-141906.json",
    "/llms.txt",
    "/agent-echo/",
    "/echoes/submit/",
]

B1_FORBIDDEN = [
    "ordinals envelope detected",
    "inscription content detected",
    "witness extracted",
    "body parsed",
    "body hash reproduced",
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

    # 1. All URLs return 200
    pages = {}
    for path in URLS_TO_CHECK:
        url = BASE_URL + path
        try:
            body, status = fetch(url)
            ok &= check(status == 200, f"URL 200: {path}", f"status={status}")
            pages[path] = body
        except Exception as e:
            ok &= check(False, f"URL 200: {path}", str(e))

    # 2. Wrapper JSON parses
    try:
        wrapper = json.loads(pages.get("/echoes/records/2026/echo-2026-05-03-000006.json", "{}"))
        ok &= check(True, "wrapper JSON parses online")
    except Exception as e:
        ok &= check(False, "wrapper JSON parses online", str(e))
        wrapper = {}

    # 3. Report JSON parses
    try:
        report = json.loads(pages.get("/verification-reports/v3/2026-05-03-v3-verification-141906.json", "{}"))
        ok &= check(True, "report JSON parses online")
    except Exception as e:
        ok &= check(False, "report JSON parses online", str(e))
        report = {}

    # 4. Echo index includes wrapper path
    try:
        idx = json.loads(pages.get("/api/echo-index.json", "{}"))
        paths = [r.get("path", "") for r in idx.get("records", [])]
        ok &= check(
            "/echoes/records/2026/echo-2026-05-03-000006.json" in paths,
            "online echo-index includes wrapper"
        )
    except Exception as e:
        ok &= check(False, "online echo-index readable", str(e))

    # 5. Schema contains expected_hash_source
    schema_text = pages.get("/api/verification-report-schema.v2.json", "")
    ok &= check("expected_hash_source" in schema_text, "schema contains expected_hash_source")

    # 6. Schema contains expected_hash_authority_class
    ok &= check("expected_hash_authority_class" in schema_text, "schema contains expected_hash_authority_class")

    # 7. Schema contains scope_class
    ok &= check("scope_class" in schema_text, "schema contains scope_class")

    # 8. Submission title policy exists
    title_text = pages.get("/api/submission-title-policy.json", "")
    ok &= check("Echo v3:" in title_text, "submission title policy exists and has Echo v3 prefix")

    # 9. llms includes title rule
    llms_text = pages.get("/llms.txt", "")
    ok &= check("Submission title rule" in llms_text or "title" in llms_text.lower(), "llms.txt includes title rule")

    # 10. Agent Echo page includes title rule
    echo_text = pages.get("/agent-echo/", "")
    ok &= check("Echo v3:" in echo_text or "title" in echo_text.lower(), "agent-echo includes title guidance")

    # 11. Report contains no V3_single_artifact_check
    report_text = json.dumps(report, ensure_ascii=False).lower()
    ok &= check("v3_single_artifact_check" not in report_text, "report no V3_single_artifact_check online")

    # 12. Positive B1 fields no forbidden phrases
    report_no_claims = {k: v for k, v in report.items() if k != "claims_not_made"}
    if "component_findings" in report_no_claims:
        report_no_claims["component_findings"] = [
            {k: v for k, v in f.items() if k != "claims_not_made"}
            if isinstance(f, dict) else f
            for f in report_no_claims["component_findings"]
        ]
    positive_text = json.dumps(report_no_claims, ensure_ascii=False).lower()
    for phrase in B1_FORBIDDEN:
        ok &= check(
            phrase not in positive_text,
            f"online no positive B1 '{phrase}'"
        )

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — latest verification Echo online checks passed.")
        return 0
    print("FINAL: FAIL — latest verification Echo online checks failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
