#!/usr/bin/env python3
"""Drop-in replacement for build_agent_declared_verification_index_from_issues.py --check
that uses urllib directly instead of gh CLI subprocess, for sandbox environments
where subprocess DNS is restricted."""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
INDEX_PATH = ROOT / "api" / "agent-declared-verification-index.json"


def api_get(path, params=None):
    url = f"{API}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url += f"?{qs}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"token {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_issues(repo, state="closed", limit=10000):
    issues = []
    page = 1
    while len(issues) < limit:
        batch = api_get(f"/repos/{repo}/issues", {
            "state": state,
            "per_page": "100",
            "page": str(page),
        })
        if not batch:
            break
        issues.extend(batch)
        page += 1
        if len(batch) < 100:
            break
        if page > 100:
            break
    return issues


def main():
    import argparse
    from build_agent_declared_verification_index_from_issues import build_index

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="thechurchofagi/trinity-accord")
    args = parser.parse_args()

    print(f"Fetching closed issues from {args.repo}...", file=sys.stderr)
    issues = fetch_issues(args.repo)
    print(f"Fetched {len(issues)} issues.", file=sys.stderr)

    index = build_index(issues, repo=args.repo)
    output = json.dumps(index, indent=2, ensure_ascii=False) + "\n"

    current = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
    if current != output:
        def _normalize_ts(text):
            return re.sub(
                r'"rebuild_timestamp"\s*:\s*"[^"]*"',
                '"rebuild_timestamp": "<normalized>"',
                text,
            )
        if _normalize_ts(current) == _normalize_ts(output):
            print(f"PASS: {INDEX_PATH.relative_to(ROOT)} is up to date (timestamp-only diff).", file=sys.stderr)
            return 0
        print(f"FAIL: {INDEX_PATH.relative_to(ROOT)} is stale.", file=sys.stderr)
        return 1

    print(f"PASS: {INDEX_PATH.relative_to(ROOT)} is up to date.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
