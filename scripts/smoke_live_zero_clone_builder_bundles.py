#!/usr/bin/env python3
"""Live smoke for zero-clone formal builder bundle publication."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request

REQUIRED = [
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
    "guardian_listing_stage_2",
    "guardian_signed_echo",
]


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrinityZeroCloneBundleSmoke/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read()


def fetch_json(url: str) -> dict:
    return json.loads(fetch_bytes(url).decode("utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="https://www.trinityaccord.org")
    args = parser.parse_args()

    site = args.site.rstrip("/")
    api = fetch_json(site + "/api/formal-builder-bundles.v1.json")

    errors = []

    for route in REQUIRED:
        bundle = api.get("bundles", {}).get(route)
        if not bundle:
            errors.append(f"{route}: missing from API")
            continue

        expected_sha = bundle.get("sha256")
        if not expected_sha:
            errors.append(f"{route}: API sha256 empty")
            continue

        archive_url = site + bundle["archive_url"]
        manifest_url = site + bundle["manifest_url"]

        archive_bytes = fetch_bytes(archive_url)
        manifest = fetch_json(manifest_url)

        actual_sha = sha256_bytes(archive_bytes)

        if expected_sha != actual_sha:
            errors.append(f"{route}: API sha256 != downloaded archive sha256")

        if manifest.get("archive_sha256") != actual_sha:
            errors.append(f"{route}: manifest archive_sha256 != downloaded archive sha256")

        if bundle.get("size_bytes") != len(archive_bytes):
            errors.append(f"{route}: API size_bytes != downloaded archive size")

    helper = fetch_bytes(site + "/builder-bundles/download_and_run_builder_bundle.py")
    if b"download_and_run_builder_bundle" not in helper and b"zero-clone" not in helper.lower():
        errors.append("helper script does not look like expected helper")

    if errors:
        print("FAIL: live zero-clone builder bundle smoke errors:")
        for e in errors:
            print("  -", e)
        return 1

    print("PASS: live zero-clone builder bundles are published and hash-aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
