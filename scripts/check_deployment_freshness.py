#!/usr/bin/env python3
"""Compare deployed/built public surfaces against the current repository state."""
from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURFACES = [
    "/llms.txt",
    "/ai.txt",
    "/api/agent-first-contact.json",
    "/api/agent-start.v2.json",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/pages-production-closure.v1.json",
    "/api/public-home-status.json",
    "/api/record-chain-status.json",
    "/api/waiting-heartbeat-status.json",
    "/record-chain/chain-tip.json",
    "/record-chain/indexes/statistics.json",
    "/record-chain/indexes/record-index.json",
    "/downloads/record-chain-builder.mjs",
]
FORBIDDEN_ACTIVE = [
    "/agent-submit",
    "/gateway/preflight",
    "/api/agent-start.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/gateway-workflows.v1.json",
]

# Human-facing pages are generated HTML, so compare revision-specific required
# markers instead of attempting to compare Markdown source bytes to HTML bytes.
STATIC_PAGE_MARKERS = {
    "/": [
        'id="what-this-is"',
        "A fixed record, with a verifiable preservation system around it",
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
    "_includes/home-object-definition.html",
    "seed-map.md",
    "authority.md",
    "agent-brief.md",
    "why-high-signal.md",
    "worth-preserving.md",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_repo(path: str) -> bytes:
    return (ROOT / path.lstrip("/")).read_bytes()


def read_site_dir(site_dir: Path, path: str) -> bytes:
    return (site_dir / path.lstrip("/")).read_bytes()


def read_static_site_dir(site_dir: Path, path: str) -> bytes:
    if path == "/":
        target = site_dir / "index.html"
    else:
        target = site_dir / path.strip("/") / "index.html"
    return target.read_bytes()


def read_live(site: str, path: str, token: str, timeout: int) -> bytes:
    url = site.rstrip("/") + path
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("freshness", token))
    busted = urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib.parse.urlencode(query),
            parsed.fragment,
        )
    )
    req = urllib.request.Request(
        busted,
        headers={
            "User-Agent": "trinity-deployment-freshness/1.1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def check_forbidden(path: str, text: str, errors: list[str]) -> None:
    checked_paths = {
        "/llms.txt",
        "/ai.txt",
        "/api/agent-first-contact.json",
        "/api/agent-start.v2.json",
    }
    if path in checked_paths:
        for bad in FORBIDDEN_ACTIVE:
            if bad in text:
                errors.append(
                    f"{path} contains retired active-route token {bad!r}; "
                    "omit legacy endpoints from active discovery surfaces"
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--site-dir", type=Path)
    src.add_argument("--site")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    token_material = b"".join(read_repo(path) for path in SURFACES)
    token_material += b"".join(read_repo(path) for path in STATIC_SOURCE_FILES)
    token = sha256(token_material)[:16]
    errors: list[str] = []

    for path in SURFACES:
        repo = read_repo(path)
        try:
            other = (
                read_site_dir(args.site_dir, path)
                if args.site_dir
                else read_live(args.site, path, token, args.timeout)
            )
        except Exception as exc:  # noqa: BLE001 - command-line diagnostic
            errors.append(f"{path}: failed to read deployed artifact: {exc}")
            continue
        repo_sha = sha256(repo)
        other_sha = sha256(other)
        print(f"{path}: repo={repo_sha} deployed={other_sha}")
        if repo_sha != other_sha:
            errors.append(
                f"{path}: digest mismatch repo={repo_sha} deployed={other_sha}"
            )
        try:
            check_forbidden(path, other.decode("utf-8"), errors)
        except UnicodeDecodeError:
            pass

    for path, markers in STATIC_PAGE_MARKERS.items():
        try:
            page_bytes = (
                read_static_site_dir(args.site_dir, path)
                if args.site_dir
                else read_live(args.site, path, token, args.timeout)
            )
            page = page_bytes.decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001 - command-line diagnostic
            errors.append(f"{path}: failed to read static page: {exc}")
            continue

        missing = [marker for marker in markers if marker not in page]
        if missing:
            for marker in missing:
                errors.append(f"{path}: missing current static marker {marker!r}")
        else:
            print(f"{path}: current static markers present")

    if errors:
        print("FAIL: deployment freshness check errors:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(
        "PASS: deployment digests, active-route boundaries, and current static "
        "reading surfaces match repository state"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
