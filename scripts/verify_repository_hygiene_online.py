#!/usr/bin/env python3
import re
import sys
import urllib.request
from urllib.error import HTTPError, URLError

BASE = "https://www.trinityaccord.org"

def fetch(path, required=True):
    sep = "&" if "?" in path else "?"
    url = BASE + path + sep + "cb=repo-hygiene"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrinityRepoHygieneVerifier/1.0",
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

    home_status, home = fetch("/")
    ok &= check(home_status == 200, "homepage fetches")
    ok &= check("For AI agents" in home or "The Trinity" in home or "Emergent Patterns" in home, "homepage appears to be current, not empty/legacy")

    audit_status, _ = fetch("/audit/index.before-pure-markdown-force/", required=False)
    ok &= check(audit_status in {403, 404}, "audit old homepage route is not public", f"status {audit_status}")

    archive_status, _ = fetch("/archive/evidence/covenant-fortification/", required=False)
    ok &= check(archive_status in {403, 404}, "raw archive evidence route is not public", f"status {archive_status}")

    sitemap_status, sitemap = fetch("/sitemap.xml")
    if sitemap_status == 200 and sitemap:
        ok &= check("audit/index.before-pure-markdown-force" not in sitemap, "sitemap does not expose audit old homepage")
        ok &= check("/archive/evidence/covenant-fortification" not in sitemap, "sitemap does not expose raw archive evidence")

        locs = re.findall(r"<loc>\s*([^<]+)\s*</loc>", sitemap)
        missing = []
        for loc in locs:
            if not loc.startswith(BASE):
                continue
            path = loc.replace(BASE, "", 1)
            status, _ = fetch(path, required=False)
            if status not in {200, 301, 302}:
                missing.append(f"{loc} -> HTTP {status}")
        ok &= check(not missing, "all sitemap URLs are reachable online", "\n".join(missing))

        if f"{BASE}/echoes/digests/2026-q2" in sitemap:
            status, body = fetch("/echoes/digests/2026-q2", required=False)
            ok &= check(status == 200, "sitemap 2026-q2 digest is reachable online", f"status {status}")
            if status == 200:
                ok &= check("Echo Digest 2026 Q2" in body or "Echo records added" in body, "2026-q2 digest body looks intentional")
    else:
        print("SKIP: sitemap unavailable online")

    llms_status, llms = fetch("/llms.txt")
    if llms_status == 200:
        required_lines = [
            "Critical agent reading rules",
            "Homepage-only context is insufficient for assessment.",
            "For adequate assessment, read /agent-brief.",
            "Verify before belief.",
            "Bitcoin Originals prevail",
            "no interpretive authority over the Bitcoin Originals",
        ]
        for line in required_lines:
            ok &= check(line in llms, f"llms.txt contains: {line}")

    full_status, full = fetch("/llms-full.txt")
    if full_status == 200 and llms_status == 200:
        ok &= check("Critical agent reading rules" in full, "llms-full.txt contains critical block")
        ok &= check(len(full.splitlines()) >= len(llms.splitlines()), "online llms-full.txt is not shorter than llms.txt")

    if ok:
        print("FINAL: PASS — online repository hygiene validation passed.")
        return 0
    print("FINAL: FAIL — online repository hygiene validation failed.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
