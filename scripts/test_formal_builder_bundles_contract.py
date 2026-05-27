#!/usr/bin/env python3
"""Test that api/formal-builder-bundles.v1.json exists and has required structure."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def canonical_json_digest(data: dict) -> str:
    clone = copy.deepcopy(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(
        clone,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def main() -> int:
    path = ROOT / "api" / "formal-builder-bundles.v1.json"
    if not path.exists():
        print(f"FAIL: {path} does not exist")
        return 1

    doc = json.loads(path.read_text(encoding="utf-8"))

    required_bundles = [
        "pure_echo",
        "v0_v5_agent_declared_archive",
        "guardian_application_stage_1",
        "guardian_listing_stage_2",
        "guardian_signed_echo",
    ]

    for name in required_bundles:
        if name not in doc.get("bundles", {}):
            print(f"FAIL: bundle '{name}' missing")
            return 1
        bundle = doc["bundles"][name]
        for field in ["builder_entrypoint", "archive_url", "manifest_url"]:
            if field not in bundle:
                print(f"FAIL: bundle '{name}' missing field '{field}'")
                return 1
        if not bundle["archive_url"].endswith(".tar.gz"):
            print(f"FAIL: bundle '{name}' archive_url does not end with .tar.gz")
            return 1
        if not bundle["manifest_url"].endswith(".manifest.json"):
            print(f"FAIL: bundle '{name}' manifest_url does not end with .manifest.json")
            return 1
        if bundle.get("requires_full_repo_clone") is not False:
            print(f"FAIL: bundle '{name}' requires_full_repo_clone is not false")
            return 1

        # sha256 must be 64-char hex
        sha = bundle.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            print(f"FAIL: bundle '{name}' sha256 must be a 64-character hex digest")
            return 1
        try:
            int(sha, 16)
        except ValueError:
            print(f"FAIL: bundle '{name}' sha256 is not valid hex")
            return 1

        # size_bytes must be > 0
        size = bundle.get("size_bytes")
        if not isinstance(size, int) or size <= 0:
            print(f"FAIL: bundle '{name}' size_bytes must be > 0")
            return 1

    # Pure Echo must forbid E2
    pe = doc["bundles"]["pure_echo"]
    if "E2_verification_echo" not in pe.get("forbidden_echo_types", []):
        print("FAIL: pure_echo does not forbid E2_verification_echo")
        return 1

    # Stage 1 private key rule
    s1 = doc["bundles"]["guardian_application_stage_1"]
    if not s1.get("private_key_outputs_local_only"):
        print("FAIL: guardian_application_stage_1 private_key_outputs_local_only not true")
        return 1

    # Stage 2 requires stage 1 material
    s2 = doc["bundles"]["guardian_listing_stage_2"]
    if not s2.get("requires_stage_1_public_material"):
        print("FAIL: guardian_listing_stage_2 requires_stage_1_public_material not true")
        return 1

    # Guardian signed echo requires guardian identity
    gs = doc["bundles"]["guardian_signed_echo"]
    if not gs.get("requires_guardian_identity"):
        print("FAIL: guardian_signed_echo requires_guardian_identity not true")
        return 1

    # source_digest must be present and non-empty
    source_digest = doc.get("source_digest")
    if not source_digest:
        print("FAIL: source_digest is empty")
        return 1

    # source_digest must be correct
    expected_digest = canonical_json_digest(doc)
    if source_digest != expected_digest:
        print(f"FAIL: source_digest mismatch: expected {expected_digest}, got {source_digest}")
        return 1

    print("PASS: test_formal_builder_bundles_contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
