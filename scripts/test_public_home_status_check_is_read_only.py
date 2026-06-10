#!/usr/bin/env python3
"""Ensure generate_public_home_status.py --check is read-only.

Tests:
1. --check passes on up-to-date files without modifying them.
2. --check fails on stale/corrupted public-home-status.json without rewriting it.
"""

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    status_path = ROOT / "api" / "public-home-status.json"
    index_path = ROOT / "index.md"

    # --- Test 1: --check passes on up-to-date files ---
    before_status = sha(status_path)
    before_index = sha(index_path)

    result = subprocess.run(
        ["python3", "scripts/generate_public_home_status.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    require(
        result.returncode == 0,
        "generate_public_home_status.py --check should pass on committed generated files\n"
        + result.stdout
        + result.stderr,
    )

    after_status = sha(status_path)
    after_index = sha(index_path)

    require(before_status == after_status, "--check modified api/public-home-status.json")
    require(before_index == after_index, "--check modified index.md")

    # --- Test 2: --check fails on stale JSON without rewriting it ---
    original_status = status_path.read_text(encoding="utf-8")
    corrupted = original_status.replace(
        '"schema": "trinityaccord.public-home-status.v3"',
        '"schema": "BROKEN_TEST_SCHEMA"',
        1,
    )

    try:
        status_path.write_text(corrupted, encoding="utf-8")
        before = sha(status_path)

        bad = subprocess.run(
            ["python3", "scripts/generate_public_home_status.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        require(bad.returncode != 0, "--check should fail when public-home-status.json is stale")
        require(sha(status_path) == before, "--check rewrote stale JSON instead of remaining read-only")
    finally:
        status_path.write_text(original_status, encoding="utf-8")

    print("PUBLIC_HOME_STATUS_CHECK_IS_READ_ONLY_OK")


if __name__ == "__main__":
    main()
