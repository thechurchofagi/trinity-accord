#!/usr/bin/env python3
"""Lightweight tests for evidence-images-manifest.json and RELEASE-LARGE-DATA-MANIFEST.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS = 0


def check(condition: bool, msg: str) -> None:
    global ERRORS
    if condition:
        print(f"  PASS: {msg}")
    else:
        print(f"  FAIL: {msg}")
        ERRORS += 1


def test_evidence_manifest() -> None:
    print("=== evidence-images-manifest.json ===")
    path = ROOT / "evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json"
    check(path.exists(), "manifest file exists")
    data = json.loads(path.read_text(encoding="utf-8"))

    assets = data.get("assets", [])
    check(len(assets) == 10, f"manifest has 10 assets (got {len(assets)})")

    for i, asset in enumerate(assets):
        fn = asset.get("filename", f"asset_{i}")
        check("filename" in asset, f"{fn}: has filename")
        check("sha256" in asset and len(asset["sha256"]) == 64, f"{fn}: has valid sha256")
        check("size_bytes" in asset and asset["size_bytes"] > 0, f"{fn}: has valid size_bytes")
        check("download_url" in asset and asset["download_url"].startswith("https://"), f"{fn}: has valid download_url")

        url = asset.get("download_url", "")
        tag = data.get("release_tag", "")
        check(tag in url, f"{fn}: download_url contains release_tag '{tag}'")

    release_tag = data.get("release_tag", "")
    check(release_tag == "notarial-certificate-images-v1", f"release_tag is notarial-certificate-images-v1 (got '{release_tag}')")


def test_release_manifest() -> None:
    print("\n=== RELEASE-LARGE-DATA-MANIFEST.json ===")
    path = ROOT / "RELEASE-LARGE-DATA-MANIFEST.json"
    check(path.exists(), "manifest file exists")
    data = json.loads(path.read_text(encoding="utf-8"))

    assets = data.get("assets", [])
    check(len(assets) == 11, f"manifest has 11 assets (got {len(assets)})")

    note = data.get("note", "")
    check("asset-level release_tag takes precedence" in note.lower() or "asset-level" in note.lower(),
          "note clarifies asset-level release_tag precedence")

    top_tag = data.get("release_tag", "")
    jpg_assets = [a for a in assets if a.get("logical_path", "").endswith(".jpg")]
    check(len(jpg_assets) == 10, f"10 JPG assets in release manifest (got {len(jpg_assets)})")

    for a in jpg_assets:
        fn = a.get("logical_path", "")
        asset_tag = a.get("release_tag", "")
        check(asset_tag == "notarial-certificate-images-v1",
              f"{fn}: asset release_tag is 'notarial-certificate-images-v1' (got '{asset_tag}')")
        check(a.get("source_path_exists") is False,
              f"{fn}: source_path_exists=false (Git copy removed)")
        check(a.get("non_amending") is True,
              f"{fn}: non_amending=true")
        check("sha256" in a and len(a["sha256"]) == 64,
              f"{fn}: has valid sha256")


def main() -> int:
    test_evidence_manifest()
    test_release_manifest()
    print()
    if ERRORS:
        print(f"FAILED: {ERRORS} check(s) failed")
        return 1
    else:
        print("ALL PASSED")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
