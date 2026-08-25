#!/usr/bin/env python3
"""Keep the Harvard review guide byte-identical and outside workflow shell text."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "preservation" / "SOFTWARE-REVIEW-README-v2.md"
WORKFLOW = ROOT / ".github" / "workflows" / "harvard-software-review-components-v1.yml"
EXPECTED_SIZE = 2884
EXPECTED_SHA256 = "37dc90e492d8b98823167169d9e6775f4a423715b086264c43edbfefe1272029"


def main() -> int:
    data = GUIDE.read_bytes()
    if len(data) != EXPECTED_SIZE:
        raise SystemExit(f"FAIL: Harvard software review guide size drifted: {len(data)}")
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"FAIL: Harvard software review guide SHA-256 drifted: {digest}")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    expected_copy = (
        'cp preservation/SOFTWARE-REVIEW-README-v2.md '
        '"$RUNNER_TEMP/harvard-review/SOFTWARE-REVIEW-README-v2.md"'
    )
    if expected_copy not in workflow:
        raise SystemExit("FAIL: Harvard workflow does not copy the frozen standalone guide")
    if EXPECTED_SHA256 not in workflow:
        raise SystemExit("FAIL: Harvard workflow does not enforce the frozen guide SHA-256")
    if "cat > \"$RUNNER_TEMP/harvard-review/SOFTWARE-REVIEW-README-v2.md\"" in workflow:
        raise SystemExit("FAIL: Harvard review guide must not be embedded in workflow shell text")

    print("PASS: Harvard software review guide is standalone and byte-identical to v2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
