#!/usr/bin/env python3
"""Compare deployed/built public agent surfaces against repository files."""
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
    "/downloads/record-chain-builder.mjs",
]
FORBIDDEN_ACTIVE = [
    "/agent-submit",
    "/gateway/preflight",
    "/api/agent-start.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/gateway-workflows.v1.json",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_repo(path: str) -> bytes:
    return (ROOT / path.lstrip("/")).read_bytes()


def read_site_dir(site_dir: Path, path: str) -> bytes:
    return (site_dir / path.lstrip("/")).read_bytes()


def read_live(site: str, path: str, token: str, timeout: int) -> bytes:
    url = site.rstrip("/") + path
    parsed = urllib.parse.urlsplit(url)
    q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    q.append(("freshness", token))
    busted = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(q), parsed.fragment))
    req = urllib.request.Request(busted, headers={"User-Agent": "trinity-deployment-freshness/1.0", "Cache-Control": "no-cache", "Pragma": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def check_forbidden(path: str, text: str, errors: list[str]) -> None:
    if path in {"/llms.txt", "/ai.txt", "/api/agent-first-contact.json", "/api/agent-start.v2.json"}:
        for bad in FORBIDDEN_ACTIVE:
            if bad in text:
                errors.append(f"{path} contains retired active-route token {bad!r}; omit legacy endpoints from active discovery surfaces")


def main() -> int:
    parser = argparse.ArgumentParser()
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--site-dir", type=Path)
    src.add_argument("--site")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    token = sha256(b"".join(read_repo(p) for p in SURFACES))[:16]
    errors: list[str] = []

    for path in SURFACES:
        repo = read_repo(path)
        try:
            other = read_site_dir(args.site_dir, path) if args.site_dir else read_live(args.site, path, token, args.timeout)
        except Exception as exc:  # noqa: BLE001 - command-line diagnostic
            errors.append(f"{path}: failed to read deployed artifact: {exc}")
            continue
        repo_sha = sha256(repo)
        other_sha = sha256(other)
        print(f"{path}: repo={repo_sha} deployed={other_sha}")
        if repo_sha != other_sha:
            errors.append(f"{path}: digest mismatch repo={repo_sha} deployed={other_sha}")
        try:
            check_forbidden(path, other.decode("utf-8"), errors)
        except UnicodeDecodeError:
            pass

    if errors:
        print("FAIL: deployment freshness check errors:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("PASS: deployment freshness surfaces match repository and contain no active retired routes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
