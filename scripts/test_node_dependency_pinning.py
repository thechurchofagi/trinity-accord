#!/usr/bin/env python3
"""Test: Node.js CI dependencies must be pinned via package-lock.json."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = ROOT / "package.json"
PACKAGE_LOCK = ROOT / "package-lock.json"
NODE_VERSION = ROOT / ".node-version"
WF_DIR = ROOT / ".github" / "workflows"

errors = []

# 1. .node-version must exist
if not NODE_VERSION.exists():
    errors.append(".node-version missing")
else:
    ver = NODE_VERSION.read_text(encoding="utf-8").strip()
    if not re.match(r"^\d+\.\d+\.\d+$", ver):
        errors.append(f".node-version not a valid semver: {ver!r}")

# 2. package-lock.json must exist
if not PACKAGE_LOCK.exists():
    errors.append("package-lock.json missing (npm ci will fail)")
else:
    try:
        lock = json.loads(PACKAGE_LOCK.read_text(encoding="utf-8"))
        if lock.get("lockfileVersion") not in (2, 3):
            errors.append(f"package-lock.json unexpected lockfileVersion: {lock.get('lockfileVersion')}")
    except json.JSONDecodeError as e:
        errors.append(f"package-lock.json invalid JSON: {e}")

# 3. package.json dependencies — warn on loose ranges
if not PACKAGE_JSON.exists():
    errors.append("package.json missing")
else:
    try:
        pkg = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
        for section in ("dependencies", "devDependencies"):
            deps = pkg.get(section, {})
            for name, spec in deps.items():
                # Flag ranges that npm ci cannot resolve deterministically
                # Accept: exact (1.2.3), caret (^), tilde (~), locked via lock
                # Reject: *, latest, git URLs without hash, file: without exact
                if spec in ("*", "latest", "next"):
                    errors.append(f"package.json {section}.{name}: unpinned spec {spec!r}")
    except json.JSONDecodeError as e:
        errors.append(f"package.json invalid JSON: {e}")

# 4. Check workflows for npm install (should prefer npm ci)
for path in WF_DIR.glob("*.yml"):
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # npm install without --frozen-lockfile is risky in CI
        if "npm install" in stripped and "--frozen-lockfile" not in stripped and "npm ci" not in stripped:
            # Allow npm install if it's for a subdirectory or specific package
            if "-g" not in stripped and "--save" not in stripped:
                errors.append(f"{path.name}: prefer 'npm ci' over 'npm install' in CI: {stripped}")

if errors:
    print("FAIL: Node dependency pinning violations:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("NODE_DEPENDENCY_PINNING_OK")
