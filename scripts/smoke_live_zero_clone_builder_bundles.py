#!/usr/bin/env python3
"""Live smoke for the active zero-clone Record-Chain Builder publication."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path


REQUIRED_RECORD_TYPES = {
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "propagation",
    "correction",
    "classification_update",
    "context_insufficient_notice",
}


def fetch(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TrinityCurrentBuilderPublicationSmoke/2.0", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default="https://www.trinityaccord.org")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    site = args.site.rstrip("/")
    manifest = json.loads(fetch(f"{site}/api/record-chain-builder-bundles.v1.json", args.timeout))
    if manifest.get("status") != "active":
        raise RuntimeError("current Builder manifest is not active")

    info = manifest.get("canonical_builder", {})
    builder_bytes = fetch(site + str(info.get("url", "")), args.timeout)
    actual_sha = hashlib.sha256(builder_bytes).hexdigest()
    if actual_sha != info.get("sha256"):
        raise RuntimeError(f"public Builder SHA mismatch: {actual_sha} != {info.get('sha256')}")
    if len(builder_bytes) != info.get("size_bytes"):
        raise RuntimeError("public Builder size does not match active manifest")

    supported = set(info.get("supports", []))
    missing = sorted(REQUIRED_RECORD_TYPES - supported)
    if missing:
        raise RuntimeError(f"active Builder manifest is missing routes: {missing}")

    with tempfile.TemporaryDirectory(prefix="trinity-live-current-builder-") as temp_dir:
        builder = Path(temp_dir) / "record-chain-builder.mjs"
        builder.write_bytes(builder_bytes)
        for command in (["help"], ["print-oath", "--record-type", "echo"],
                        ["print-oath", "--record-type", "guardian_retirement"]):
            result = subprocess.run(
                ["node", str(builder), *command],
                text=True,
                capture_output=True,
                timeout=args.timeout,
            )
            if result.returncode != 0 or not result.stdout.strip():
                raise RuntimeError(f"public Builder command failed: {' '.join(command)}\n{result.stderr[:1000]}")

    print("PASS: active zero-clone Record-Chain Builder is hash-aligned and executable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
