#!/usr/bin/env python3
"""Signature contract for zero-clone builder bundle manifests."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KEY_CONTRACT = ROOT / "api" / "builder-bundle-signing-key.v1.json"
SIG_CONTRACT = ROOT / "api" / "formal-builder-bundle-signatures.v1.json"
PUBLIC_KEY = ROOT / "api" / "builder-bundle-signing-public-key.pem"

REQUIRED_ROUTES = [
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
    "guardian_listing_stage_2",
    "guardian_signed_echo",
]

def main() -> int:
    errors: list[str] = []

    for path in [KEY_CONTRACT, SIG_CONTRACT, PUBLIC_KEY]:
        if not path.exists():
            errors.append(f"missing required signature file: {path.relative_to(ROOT)}")

    if KEY_CONTRACT.exists():
        key = json.loads(KEY_CONTRACT.read_text(encoding="utf-8"))
        if key.get("not_canonical_authority") is not True:
            errors.append("key contract must say not_canonical_authority=true")
        if key.get("canonical_authority") != "Bitcoin Originals only":
            errors.append("key contract must preserve Bitcoin Originals authority boundary")
        if key.get("public_key_pem_path") != "/api/builder-bundle-signing-public-key.pem":
            errors.append("key contract public key path mismatch")

    if SIG_CONTRACT.exists():
        sigs = json.loads(SIG_CONTRACT.read_text(encoding="utf-8"))
        signed = sigs.get("signed_files", {})
        for route in REQUIRED_ROUTES:
            item = signed.get(route)
            if not isinstance(item, dict):
                errors.append(f"signature contract missing route: {route}")
                continue
            if not item.get("manifest", "").endswith(".manifest.json"):
                errors.append(f"{route}: manifest path must end with .manifest.json")
            if not item.get("signature", "").endswith(".manifest.sig"):
                errors.append(f"{route}: signature path must end with .manifest.sig")
            sig_path = ROOT / item.get("signature", "").lstrip("/")
            if not sig_path.exists():
                errors.append(f"{route}: signature file missing: {sig_path.relative_to(ROOT)}")

    if errors:
        print("FAIL: formal builder bundle signature contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: formal builder bundle signature contract is valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
