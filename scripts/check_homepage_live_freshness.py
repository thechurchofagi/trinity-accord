#!/usr/bin/env python3
"""Check that live homepage status surfaces match repository state.

This script verifies that the deployed site is not serving a stale generated
homepage/API status after bot-generated commits.

Checks:
  1. live /api/public-home-status.json exactly matches repo copy
  2. live /api/record-chain-status.json exactly matches repo copy
  3. live homepage generated block has the same Source data digest as repo index.md
  4. live homepage generated block mentions the repo latest_record_id
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"
DEFAULT_SITE = "https://www.trinityaccord.org"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_repo_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def read_repo_bytes(rel: str) -> bytes:
    return (ROOT / rel).read_bytes()


def cache_busted_url(site: str, path: str, token: str) -> str:
    url = site.rstrip("/") + path
    parsed = urllib.parse.urlsplit(url)
    q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    q.append(("freshness", token))
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib.parse.urlencode(q),
            parsed.fragment,
        )
    )


def fetch(site: str, path: str, token: str, timeout: int) -> bytes:
    req = urllib.request.Request(
        cache_busted_url(site, path, token),
        headers={
            "User-Agent": "trinity-homepage-live-freshness/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def extract_block(text: str) -> str:
    match = re.search(re.escape(BEGIN) + r".*?" + re.escape(END), text, re.S)
    if not match:
        raise ValueError("generated public status block markers missing")
    return match.group(0)


def extract_digest(text: str) -> str | None:
    match = re.search(r"Source data digest\s*<code>([0-9a-f]{16})</code>", text)
    return match.group(1) if match else None


def load_json_bytes(data: bytes) -> Any:
    return json.loads(data.decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-sleep", type=int, default=30)
    args = parser.parse_args()

    token_material = (
        read_repo_bytes("api/public-home-status.json")
        + read_repo_bytes("api/record-chain-status.json")
        + read_repo_bytes("index.md")
    )
    token = sha256(token_material)[:16]

    repo_public = read_repo_bytes("api/public-home-status.json")
    repo_record_status = read_repo_bytes("api/record-chain-status.json")
    repo_index_text = read_repo_text("index.md")
    repo_block = extract_block(repo_index_text)
    repo_digest = extract_digest(repo_block)

    errors: list[str] = []

    for attempt in range(1, args.retries + 1):
        errors.clear()
        print(f"Homepage live freshness attempt {attempt}/{args.retries}: {args.site}")

        try:
            live_public = fetch(args.site, "/api/public-home-status.json", token, args.timeout)
            live_record_status = fetch(args.site, "/api/record-chain-status.json", token, args.timeout)
            live_home = fetch(args.site, "/", token, args.timeout).decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to fetch live surfaces: {exc}")
            if attempt < args.retries:
                time.sleep(args.retry_sleep)
                continue
            break

        if sha256(live_public) != sha256(repo_public):
            errors.append(
                "live /api/public-home-status.json differs from repo "
                f"repo={sha256(repo_public)} live={sha256(live_public)}"
            )

        if sha256(live_record_status) != sha256(repo_record_status):
            errors.append(
                "live /api/record-chain-status.json differs from repo "
                f"repo={sha256(repo_record_status)} live={sha256(live_record_status)}"
            )

        try:
            live_block = extract_block(live_home)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"live homepage generated block missing/unreadable: {exc}")
            live_block = ""

        live_digest = extract_digest(live_block)
        if repo_digest and live_digest != repo_digest:
            errors.append(f"live homepage source digest mismatch: repo={repo_digest} live={live_digest}")

        try:
            repo_public_json = load_json_bytes(repo_public)
            latest = (
                repo_public_json
                .get("current_record_chain_status", {})
                .get("latest_record_id")
            )
            if latest and live_block and latest not in live_block:
                errors.append(f"live homepage block does not mention latest repo record id {latest}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"could not parse repo public-home-status.json: {exc}")

        if not errors:
            print("PASS: live homepage status surfaces match repository state")
            return 0

        print("Live freshness mismatch:")
        for err in errors:
            print(f"  - {err}")

        if attempt < args.retries:
            time.sleep(args.retry_sleep)

    print("FAIL: live homepage status surfaces are stale or unavailable")
    return 1


if __name__ == "__main__":
    sys.exit(main())
