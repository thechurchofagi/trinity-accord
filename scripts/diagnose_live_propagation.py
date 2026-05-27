#!/usr/bin/env python3
"""Multi-vantage live propagation diagnostic.

Checks live site from the current vantage point and reports:
- DNS resolved IP
- HTTP cache headers (x-cache, age, etag, last-modified)
- source_digest comparison with repo
- Varnish edge identification via headers

Usage:
    python3 scripts/diagnose_live_propagation.py
    python3 scripts/diagnose_live_propagation.py --site https://www.trinityaccord.org
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = "https://www.trinityaccord.org"


def fetch_with_headers(url: str, timeout: int = 20) -> tuple[str, dict]:
    """Fetch URL and return (body, headers_dict)."""
    req = urllib.request.Request(url, headers={"User-Agent": "trinity-propagation-diag/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            headers = dict(resp.headers)
            return body, headers
    except Exception as e:
        return "", {"error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-vantage live propagation diagnostic")
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    site = args.site.rstrip("/")
    hostname = site.split("://")[-1].split("/")[0].split(":")[0]
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # DNS resolution
    try:
        resolved_ip = socket.gethostbyname(hostname)
        dns_ok = True
    except socket.gaierror as e:
        resolved_ip = f"FAIL: {e}"
        dns_ok = False

    # Fetch canonical links.json
    links_url = f"{site}/api/links.json"
    body, headers = fetch_with_headers(links_url, args.timeout)

    # Parse source_digest
    live_digest = None
    live_version = None
    try:
        data = json.loads(body)
        live_digest = data.get("source_digest")
        live_version = data.get("version")
    except json.JSONDecodeError:
        pass

    # Repo digest
    repo_links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))
    repo_digest = repo_links.get("source_digest")

    # Cache-busted fetch
    cb_url = f"{links_url}?cb={repo_digest}"
    cb_body, cb_headers = fetch_with_headers(cb_url, args.timeout)
    cb_digest = None
    try:
        cb_data = json.loads(cb_body)
        cb_digest = cb_data.get("source_digest")
    except json.JSONDecodeError:
        pass

    # Build result
    result = {
        "timestamp": timestamp,
        "vantage_ip": resolved_ip,
        "dns_ok": dns_ok,
        "hostname": hostname,
        "site": site,
        "links_url": links_url,
        "canonical": {
            "source_digest": live_digest,
            "version": live_version,
            "x_cache": headers.get("x-cache", headers.get("X-Cache", "?")),
            "age": headers.get("age", headers.get("Age", "?")),
            "etag": headers.get("etag", headers.get("ETag", "?")),
            "last_modified": headers.get("last-modified", headers.get("Last-Modified", "?")),
            "via": headers.get("via", headers.get("Via", "?")),
            "server": headers.get("server", headers.get("Server", "?")),
        },
        "cache_busted": {
            "source_digest": cb_digest,
            "x_cache": cb_headers.get("x-cache", cb_headers.get("X-Cache", "?")),
            "age": cb_headers.get("age", cb_headers.get("Age", "?")),
            "etag": cb_headers.get("etag", cb_headers.get("ETag", "?")),
            "last_modified": cb_headers.get("last-modified", cb_headers.get("Last-Modified", "?")),
        },
        "repo_source_digest": repo_digest,
        "canonical_matches_repo": live_digest == repo_digest,
        "cache_busted_matches_repo": cb_digest == repo_digest,
        "canonical_matches_cache_busted": live_digest == cb_digest,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== Live Propagation Diagnostic ===")
        print(f"Timestamp:    {timestamp}")
        print(f"Hostname:     {hostname}")
        print(f"Resolved IP:  {resolved_ip}")
        print(f"DNS OK:       {dns_ok}")
        print()
        print(f"--- Canonical {links_url} ---")
        print(f"  source_digest:    {live_digest}")
        print(f"  x-cache:          {result['canonical']['x_cache']}")
        print(f"  age:              {result['canonical']['age']}")
        print(f"  etag:             {result['canonical']['etag']}")
        print(f"  last-modified:    {result['canonical']['last_modified']}")
        print(f"  via:              {result['canonical']['via']}")
        print(f"  server:           {result['canonical']['server']}")
        print()
        print(f"--- Cache-busted ---")
        print(f"  source_digest:    {cb_digest}")
        print(f"  x-cache:          {result['cache_busted']['x_cache']}")
        print(f"  age:              {result['cache_busted']['age']}")
        print(f"  last-modified:    {result['cache_busted']['last_modified']}")
        print()
        print(f"--- Comparison ---")
        print(f"  repo digest:      {repo_digest}")
        print(f"  canonical == repo:     {result['canonical_matches_repo']}")
        print(f"  cache-busted == repo:  {result['cache_busted_matches_repo']}")
        print(f"  canonical == busted:   {result['canonical_matches_cache_busted']}")
        print()

        if result["canonical_matches_repo"] and result["cache_busted_matches_repo"]:
            print("✅ PROPAGATION OK — all digests match repo")
            return 0
        elif result["canonical_matches_cache_busted"]:
            print("⚠️  CANONICAL == BUSTED but both differ from repo — origin may not have deployed yet")
            return 1
        else:
            print("❌ PROPAGATION INCONSISTENCY — canonical and cache-busted return different digests")
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
