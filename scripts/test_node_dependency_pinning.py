#!/usr/bin/env python3
"""Test: Node runtime must be pinned; npm ci must be used, not npm install."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"
NODE_VERSION = ROOT / ".node-version"
PACKAGE_LOCK = ROOT / "package-lock.json"

errors = []

if not NODE_VERSION.exists():
    errors.append(".node-version missing")
else:
    v = NODE_VERSION.read_text(encoding="utf-8").strip()
    if not v or v.count(".") < 2:
        errors.append(f".node-version should pin exact major.minor.patch, got: {v!r}")

for path in WF_DIR.glob("*.yml"):
    text = path.read_text(encoding="utf-8")

    if "node --check" in text or "node scripts/" in text:
        if "actions/setup-node@" not in text and "setup-node@" not in text:
            errors.append(f"{path.name}: runs node but does not setup pinned node")

    if "npm install" in text:
        errors.append(f"{path.name}: uses npm install; use npm ci with lockfile")

    if "npx " in text:
        errors.append(f"{path.name}: uses npx; require pinned version or avoid")

    if "npm ci" in text and not PACKAGE_LOCK.exists():
        errors.append(f"{path.name}: uses npm ci but package-lock.json missing")

if errors:
    print("FAIL: Node/npm pinning violations:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("NODE_DEPENDENCY_PINNING_OK")
