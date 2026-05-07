#!/usr/bin/env python3
"""Prevent reintroducing large evidence payload paths into Git."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_EXACT = {
    "archive/evidence/flaw-archive-bundle.zip",
    "arweave-backup/files/public_covenant_archive.zip",
}

FORBIDDEN_PREFIXES = [
    "archive/evidence/flaw-images/指纹/",
]

errors = []

tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()

for rel in tracked:
    if rel in FORBIDDEN_EXACT or any(rel.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        errors.append(f"forbidden large asset path is tracked: {rel}")

for rel in FORBIDDEN_EXACT:
    if (ROOT / rel).exists():
        errors.append(f"forbidden large asset exists in working tree: {rel}")

for prefix in FORBIDDEN_PREFIXES:
    p = ROOT / prefix
    if p.exists():
        errors.append(f"forbidden large asset directory exists in working tree: {prefix}")

if errors:
    print("NO_FORBIDDEN_LARGE_PATHS_TRACKED_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("NO_FORBIDDEN_LARGE_PATHS_TRACKED_OK")
