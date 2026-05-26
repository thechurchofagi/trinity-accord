#!/usr/bin/env python3
"""
Online verification of submission semantics upgrade.
Checks that new API files and guide updates are deployed and reachable.

Usage:
    python3 scripts/verify_submission_semantics_online.py
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BASE_URL = "https://www.trinityaccord.org"


def check_url(path, label):
    """Check that a URL is reachable."""
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as resp:
            ok = resp.status == 200
            status = f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        # Try GET for pages that reject HEAD
        try:
            req2 = urllib.request.Request(url)
            with urllib.request.urlopen(req2, timeout=15) as resp2:
                ok = resp2.status == 200
                status = f"HTTP {resp2.status} (GET fallback)"
        except Exception:
            ok = False
            status = f"HTTP {e.code}"
    except Exception as e:
        ok = False
        status = str(e)[:80]

    if ok:
        print(f"PASS: {label} — {status}")
    else:
        print(f"FAIL: {label} — {status}")
    return ok


def check_page_contains(path, needle, label):
    """Check that a page contains specific text."""
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        if needle.lower() in body.lower():
            print(f"PASS: {label}")
            return True
        print(f"FAIL: {label} — text not found: '{needle[:60]}'")
        return False
    except Exception as e:
        print(f"FAIL: {label} — {str(e)[:80]}")
        return False


def main():
    ok = True

    # New API files reachable
    ok &= check_url("/api/hash-source-classes.json", "api/hash-source-classes.json reachable")
    ok &= check_url("/api/echo-acceptance-policy.json", "api/echo-acceptance-policy.json reachable")
    ok &= check_url("/api/repository-artifact-hashes.json", "api/repository-artifact-hashes.json reachable")

    # Guide updates contain new content
    ok &= check_page_contains(
        "/agent-verify",
        "Expected hash source is required",
        "/agent-verify contains expected hash source rule"
    )
    ok &= check_page_contains(
        "/agent-echo",
        "GitHub Issue is not automatically an indexed Echo",
        "/agent-echo contains Issue vs Echo rule"
    )
    ok &= check_page_contains(
        "/echoes/submit",
        "Before submitting a verification Echo",
        "/echoes/submit contains pre-submit checklist"
    )
    ok &= check_page_contains(
        "/llms.txt",
        "Hash-source rule",
        "/llms.txt contains Hash-source rule"
    )

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — online submission semantics verification passed.")
        return 0
    print("FINAL: FAIL — online submission semantics verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
