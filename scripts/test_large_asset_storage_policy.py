#!/usr/bin/env python3
"""Ensure production large payloads are not committed to Git repository."""

import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 5_000_000

# These paths must NEVER appear in Git again — they belong in GitHub Release.
FORBIDDEN_PATHS = {
    "archive/evidence/flaw-archive-bundle.zip",
    "arweave-backup/files/public_covenant_archive.zip",
}

FORBIDDEN_PREFIXES = [
    "archive/evidence/flaw-images/指纹/",
]

errors = []

# Check tracked files via git ls-files
tracked = subprocess.check_output(
    ["git", "ls-files"], cwd=ROOT, text=True
).splitlines()

for rel in tracked:
    if rel in FORBIDDEN_PATHS or any(rel.startswith(p) for p in FORBIDDEN_PREFIXES):
        errors.append(f"{rel}: forbidden large asset path is tracked in Git")

# Check working tree for forbidden paths
for rel in FORBIDDEN_PATHS:
    if (ROOT / rel).exists():
        errors.append(f"forbidden large asset exists in working tree: {rel}")

for prefix in FORBIDDEN_PREFIXES:
    p = ROOT / prefix
    if p.exists():
        errors.append(f"forbidden large asset directory exists in working tree: {prefix}")

# General size check for any other large files
for p in ROOT.rglob("*"):
    if not p.is_file():
        continue

    rel = p.relative_to(ROOT).as_posix()

    if rel.startswith((".git/", "node_modules/", "dist/")):
        continue

    size = p.stat().st_size

    if size > MAX_BYTES and rel not in FORBIDDEN_PATHS and not any(rel.startswith(fp) for fp in FORBIDDEN_PREFIXES):
        errors.append(f"{rel}: {size} bytes exceeds {MAX_BYTES}; large payloads belong in Release/Arweave/IPFS")

if errors:
    print("LARGE_ASSET_STORAGE_POLICY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("LARGE_ASSET_STORAGE_POLICY_OK")
