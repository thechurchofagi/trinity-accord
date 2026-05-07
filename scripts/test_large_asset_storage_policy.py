#!/usr/bin/env python3
"""Ensure production large payloads are not committed to Git repository."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 5_000_000
PAYLOAD_EXTS = (".zip", ".tgz", ".tar.gz", ".bin", ".car", ".mp4", ".mov")

ALLOWLIST = {
    # Pre-existing large assets committed before storage domain policy.
    # These should be migrated to Release/Arweave in a future PR.
    "archive/evidence/flaw-archive-bundle.zip",
    "archive/evidence/flaw-images/指纹/微信图片_20250629170940.jpg",
    "archive/evidence/flaw-images/指纹/微信图片_20250629170932.jpg",
    "archive/evidence/flaw-images/指纹/微信图片_20250629170918.jpg",
    "arweave-backup/files/public_covenant_archive.zip",
}

errors = []

for p in ROOT.rglob("*"):
    if not p.is_file():
        continue

    rel = p.relative_to(ROOT).as_posix()

    if rel.startswith((".git/", "node_modules/", "dist/")):
        continue

    size = p.stat().st_size
    lower = rel.lower()

    if size > MAX_BYTES and rel not in ALLOWLIST:
        errors.append(f"{rel}: {size} bytes exceeds {MAX_BYTES}; large payloads belong in Release/Arweave/IPFS")

if errors:
    print("LARGE_ASSET_STORAGE_POLICY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("LARGE_ASSET_STORAGE_POLICY_OK")
