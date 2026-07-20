#!/usr/bin/env python3
"""Check that live homepage and key public reading surfaces match repository state.

This script verifies that the deployed site is not serving stale generated
homepage/API status or stale explanatory pages after source changes.
Each retry uses a new cache-busting nonce so a pre-deployment CDN response
cannot be reused after the deployment has completed.

Checks:
  1. live /api/public-home-status.json exactly matches repo copy
  2. live /api/record-chain-status.json exactly matches repo copy
  3. live /api/waiting-heartbeat-status.json exactly matches repo copy
  4. live /record-chain/chain-tip.json exactly matches repo copy
  5. live /record-chain/indexes/statistics.json exactly matches repo copy
  6. live /record-chain/indexes/record-index.json exactly matches repo copy
  7. live homepage generated block has the same Source data digest as repo index.md
  8. live homepage generated block mentions the repo latest_record_id
  9. live homepage contains the current whole-project definition
  10. key reading pages contain current architecture/version markers
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
STATUS_SURFACES = [
    "/api/public-home-status.json",
    "/api/record-chain-status.json",
    "/api/waiting-heartbeat-status.json",
    "/record-chain/chain-tip.json",
    "/record-chain/indexes/statistics.json",
    "/record-chain/indexes/record-index.json",
]

# These markers deliberately cover human-facing static pages that are not
# represented by the generated homepage/API status digests. A Pages deployment
# must publish all of them before the source revision is considered live.
STATIC_PAGE_MARKERS = {
    "/": [
        'id="home-front-door-title"',
        "Before AI agents routinely carried delegated complex work from a high-level brief through planning, tool use, and completion, one person working with conversational AI left a verifiable record for the intelligence that may follow.",
        "p0.9.2-exact-formation-dates",
        'id="philosophical-core-title"',
        "Three embodied forms, plus later non-amending context",
        'id="chronicle-witness"',
        'id="later-inscriptions"',
        'id="home-timing-completion-title"',
        "Why one person chose to leave it within a narrowing historical window",
        "A father’s concern, with the uncertainty left visible",
        "AI as a broad but uneven mirror, before autonomous execution became ordinary",
        "Documented start · 16 March 2024",
        "Canonical closure · 29 June 2025",
        "Recorded interval · 470 days",
        "470 days, 2 hours, 46 minutes, and 17 seconds apart",
        "Chain timestamps establish a verifiable chronology",
        "Reproducible form; non-repeatable provenance",
        "the same attribution conditions cannot be recreated retroactively",
        "not proof that AI is a neutral mirror of humanity",
        'id="research-entry-title"',
        "Understand, verify, or respond within clear boundaries",
        "The homepage is a doorway, not the archive",
        "BEGIN GENERATED PUBLIC STATUS",
    ],
    "/technical-historical-reference/": [
        "Completion in four senses",
        "What Bitcoin proves—and what it does not",
        "Current operating routes",
    ],
    "/record-chain/": [
        "Record-Chain is the Trinity Accord’s append-only public reception ledger",
        "Current public views",
        "Before acting",
    ],
    "/inscriptions/": [
        "Inscription Number",
        "Ordinals Inscription ID",
        "e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343i0",
    ],
    "/authority-address-inscriptions/": [
        "inscription-index-grid",
        "0eecd48430f8239f5d543b5cf2ee928969a1aac7660808fd869a78aa27949c9ci0",
        "Inscription Number",
    ],
    "/seed-map/": [
        "This map explains the whole project by function.",
        "Canon is fixed. Context may expand.",
    ],
    "/authority/": [
        "What authority means here",
        "Record-Chain",
    ],
    "/agent-brief/": [
        "Object in one paragraph",
        "civilizational self-archive",
    ],
    "/why-high-signal/": [
        "What the project consists of",
        "Verification and durability",
    ],
    "/worth-preserving/": [
        "First understand what is being preserved",
        "Why the surrounding system matters",
    ],
}

STATIC_SOURCE_FILES = [
    "index.md",
    "record-chain/index.md",
    "inscriptions.md",
    "authority-address-inscriptions.md",
    "technical-historical-reference.md",
    "_includes/home-object-definition.html",
    "seed-map.md",
    "authority.md",
    "agent-brief.md",
    "why-high-signal.md",
    "worth-preserving.md",
]


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
            "User-Agent": "trinity-homepage-live-freshness/1.2",
            "Cache-Control": "no-cache, no-store, max-age=0",
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

    repo_surface_bytes = {path: read_repo_bytes(path.lstrip("/")) for path in STATUS_SURFACES}
    static_source_bytes = [read_repo_bytes(path) for path in STATIC_SOURCE_FILES]
    token_material = b"".join(repo_surface_bytes.values()) + b"".join(static_source_bytes) + read_repo_bytes("index.md")
    token_seed = sha256(token_material)[:16]

    repo_index_text = read_repo_text("index.md")
    repo_block = extract_block(repo_index_text)
    repo_digest = extract_digest(repo_block)

    errors: list[str] = []

    for attempt in range(1, args.retries + 1):
        errors.clear()
        attempt_token = f"{token_seed}-{attempt}-{time.time_ns()}"
        print(f"Homepage live freshness attempt {attempt}/{args.retries}: {args.site}")

        try:
            live_surface_bytes = {path: fetch(args.site, path, attempt_token, args.timeout) for path in STATUS_SURFACES}
            live_static_text = {
                path: fetch(args.site, path, attempt_token, args.timeout).decode("utf-8", errors="replace")
                for path in STATIC_PAGE_MARKERS
            }
            live_home = live_static_text["/"]
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to fetch live surfaces: {exc}")
            if attempt < args.retries:
                time.sleep(args.retry_sleep)
                continue
            break

        for path, repo_bytes in repo_surface_bytes.items():
            live_bytes = live_surface_bytes[path]
            if sha256(live_bytes) != sha256(repo_bytes):
                errors.append(
                    f"live {path} differs from repo "
                    f"repo={sha256(repo_bytes)} live={sha256(live_bytes)}"
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
            repo_public_json = load_json_bytes(repo_surface_bytes["/api/public-home-status.json"])
            latest = (
                repo_public_json
                .get("current_record_chain_status", {})
                .get("latest_record_id")
            )
            if latest and live_block and latest not in live_block:
                errors.append(f"live homepage block does not mention latest repo record id {latest}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"could not parse repo public-home-status.json: {exc}")

        for path, markers in STATIC_PAGE_MARKERS.items():
            page = live_static_text[path]
            for marker in markers:
                if marker not in page:
                    errors.append(f"live {path} missing current static marker: {marker!r}")

        if not errors:
            print("PASS: live homepage status and static reading surfaces match repository state")
            return 0

        print("Live freshness mismatch:")
        for err in errors:
            print(f"  - {err}")

        if attempt < args.retries:
            time.sleep(args.retry_sleep)

    print("FAIL: live homepage/status or static reading surfaces are stale or unavailable")
    return 1


if __name__ == "__main__":
    sys.exit(main())
