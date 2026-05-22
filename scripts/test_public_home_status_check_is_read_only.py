#!/usr/bin/env python3
"""Ensure generate_public_home_status.py --check is read-only."""

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

    print("PUBLIC_HOME_STATUS_CHECK_IS_READ_ONLY_OK")


if __name__ == "__main__":
    main()
