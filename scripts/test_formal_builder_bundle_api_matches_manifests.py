#!/usr/bin/env python3
"""formal-builder-bundles API must match generated bundle manifests if present."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api" / "formal-builder-bundles.v1.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    data = json.loads(API.read_text(encoding="utf-8"))
    errors = []

    for name, bundle in data.get("bundles", {}).items():
        archive = ROOT / bundle["archive_url"].lstrip("/")
        manifest = ROOT / bundle["manifest_url"].lstrip("/")

        # If bundles are not committed, this test should not fail here.
        # Pages/live smoke will verify deployed bundles.
        if not archive.exists() and not manifest.exists():
            continue

        if not archive.exists():
            errors.append(f"{name}: archive missing but manifest exists")
            continue
        if not manifest.exists():
            errors.append(f"{name}: manifest missing but archive exists")
            continue

        actual_sha = sha256_file(archive)
        if bundle.get("sha256") != actual_sha:
            errors.append(f"{name}: API sha256 does not match archive")

        if bundle.get("size_bytes") != archive.stat().st_size:
            errors.append(f"{name}: API size_bytes does not match archive")

        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        if manifest_data.get("archive_sha256") != actual_sha:
            errors.append(f"{name}: manifest archive_sha256 does not match archive")

    if errors:
        print("FAIL: formal builder bundle API/manifest mismatch:")
        for e in errors:
            print("  -", e)
        return 1

    print("PASS: formal builder bundle API matches committed manifests when present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
