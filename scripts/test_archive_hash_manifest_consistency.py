#!/usr/bin/env python3
"""Compatibility wrapper for asset-domain-aware hash manifest consistency."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

tests = [
    [sys.executable, str(ROOT / "scripts" / "test_asset_manifest_domain_consistency.py")],
    [sys.executable, str(ROOT / "scripts" / "verify_release_asset_manifest.py"), "--offline"],
]

for cmd in tests:
    p = subprocess.run(cmd, cwd=ROOT, text=True)
    if p.returncode != 0:
        sys.exit(p.returncode)

print("ARCHIVE_HASH_MANIFEST_CONSISTENCY_OK")
