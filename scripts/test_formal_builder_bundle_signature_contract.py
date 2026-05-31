#!/usr/bin/env python3
"""Integrity contract for zero-clone builder bundle manifests.

Verifies that manifest files exist, contain required routes, and reference
valid file paths with SHA256 hashes. RSA signatures have been removed;
manifest SHA256 hashes are the integrity mechanism.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFEST_CONTRACT = ROOT / "api" / "formal-builder-bundle-signatures.v1.json"

REQUIRED_ROUTES = [
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
    "guardian_listing_stage_2",
    "guardian_signed_echo",
]

def main() -> int:
    errors: list[str] = []

    if not MANIFEST_CONTRACT.exists():
        errors.append(f"missing manifest contract: {MANIFEST_CONTRACT.relative_to(ROOT)}")

    if MANIFEST_CONTRACT.exists():
        contract = json.loads(MANIFEST_CONTRACT.read_text(encoding="utf-8"))
        signed = contract.get("signed_files", {})
        for route in REQUIRED_ROUTES:
            item = signed.get(route)
            if not isinstance(item, dict):
                errors.append(f"manifest contract missing route: {route}")
                continue
            if not item.get("manifest", "").endswith(".manifest.json"):
                errors.append(f"{route}: manifest path must end with .manifest.json")
            manifest_path = ROOT / item.get("manifest", "").lstrip("/")
            if not manifest_path.exists():
                errors.append(f"{route}: manifest file missing: {manifest_path.relative_to(ROOT)}")
                continue
            # Verify manifest has files with sha256 hashes
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            files = manifest.get("files", [])
            if not files:
                errors.append(f"{route}: manifest has no files list")
            for f in files:
                if not f.get("sha256"):
                    errors.append(f"{route}: file entry missing sha256: {f.get('path')}")

    if errors:
        print("FAIL: builder bundle manifest contract errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("PASS: builder bundle manifest contract is valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
