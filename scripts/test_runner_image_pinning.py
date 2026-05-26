#!/usr/bin/env python3
"""Test: All workflows must use pinned runner images, not ubuntu-latest."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"

BAD = ["ubuntu-latest", "windows-latest", "macos-latest"]
ALLOWED = ["ubuntu-24.04", "ubuntu-22.04"]

errors = []

for path in WF_DIR.glob("*.yml"):
    text = path.read_text(encoding="utf-8")
    for bad in BAD:
        if bad in text:
            # Allow in comments or test fixture strings only
            for line in text.splitlines():
                if bad in line and not line.strip().startswith("#"):
                    errors.append(f"{path.name}: uses drifting runner label {bad}")
                    break

    if "runs-on:" in text and not any(a in text for a in ALLOWED):
        errors.append(f"{path.name}: has runs-on but no allowed pinned Ubuntu image")

if errors:
    print("FAIL: runner image pinning violations:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("RUNNER_IMAGE_PINNING_OK")
