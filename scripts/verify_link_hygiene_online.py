#!/usr/bin/env python3
import re
import sys
import urllib.request
from urllib.error import HTTPError, URLError

BASE = "https://www.trinityaccord.org"

REQUIRED_ROUTES = [
    "/echoes/digests/2026-q2",
    "/EVIDENCE-RELATIONSHIP-MAP",
    "/EVIDENCE-BACKUP-COVERAGE",
    "/archive_legacy_index_2025_09",
    "/downloads/arweave-bundle-verification",
    "/echoes/examples/critical-echo-template/",
]

PAGES_TO_SCAN = [
    "/echoes/digests",
    "/agent-echo",
    "/start",
    "/status",
    "/echoes/high-value-criteria",
    "/echoes/types",
]

FORBIDDEN_ONLINE_PATTERNS = [
    "/echoes/digests/-",
    "/EVIDENCE-RELATIONSHIP-MAP.md",
    "/EVIDENCE-BACKUP-COVERAGE.md",
    "/archive_legacy_index_2025_09.md",
    "/downloads/arweave-bundle-verification.md",
    "/echoes/examples/critical-echo-template.md",
]

def fetch(path, required=True):
    sep = "&" if "?" in path else "?"
    url = BASE + path + sep + "cb=link-hygiene"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrinityLinkHygieneVerifier/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        if required:
            print(f"FAIL: fetch {path}: HTTP {e.code}")
        else:
            print(f"SKIP/EXPECTED: fetch {path}: HTTP {e.code}")
        return e.code, ""
    except Exception as e:
        if required:
            print(f"FAIL: fetch {path}: {e}")
        else:
            print(f"SKIP: fetch {path}: {e}")
        return None, ""

def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False

def main():
    ok = True

    print("=== Required routes reachable ===")
    for route in REQUIRED_ROUTES:
        status, body = fetch(route)
        ok &= check(status in {200, 301, 302}, f"{route} reachable", f"status {status}")

    print("\n=== Online pages have no forbidden links ===")
    for page in PAGES_TO_SCAN:
        status, body = fetch(page, required=False)
        if status not in {200, 301, 302}:
            print(f"SKIP: {page} not reachable; status {status}")
            continue
        for pattern in FORBIDDEN_ONLINE_PATTERNS:
            ok &= check(pattern not in body, f"{page} does not contain {pattern}")

    print("\n=== Digest index has real digest link ===")
    status, body = fetch("/echoes/digests", required=False)
    if status in {200, 301, 302}:
        ok &= check("/echoes/digests/2026-q2" in body, "digest index links 2026-q2")
        ok &= check("/echoes/digests/-" not in body, "digest index has no placeholder")
    else:
        print(f"SKIP: /echoes/digests not reachable; status {status}")

    print("\n=== Sitemap digest source ===")
    status, sitemap = fetch("/sitemap.xml", required=False)
    if status in {200, 301, 302}:
        ok &= check("/echoes/digests/-" not in sitemap, "sitemap has no digest placeholder")
        if "https://www.trinityaccord.org/echoes/digests/2026-q2" in sitemap:
            status2, _ = fetch("/echoes/digests/2026-q2", required=False)
            ok &= check(status2 in {200, 301, 302}, "sitemap 2026-q2 route reachable")
    else:
        print(f"SKIP: sitemap not reachable; status {status}")

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — online link hygiene validation passed.")
        return 0
    print("FINAL: FAIL — online link hygiene validation failed.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
