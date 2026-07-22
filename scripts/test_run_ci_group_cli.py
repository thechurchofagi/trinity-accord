#!/usr/bin/env python3
"""CLI regressions for grouped CI discovery and required execution input."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_ci_group.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


listing = run("--list")
if listing.returncode != 0:
    raise AssertionError(
        f"--list must not require a group (rc={listing.returncode}): "
        f"{listing.stderr.strip()}"
    )

expected_groups = {
    "p0-current",
    "trust-root",
    "supply-chain",
    "echo-archive",
    "fast-regression",
}
listed_groups = {
    line.strip().split(":", 1)[0]
    for line in listing.stdout.splitlines()
    if line.strip()
}
missing = expected_groups - listed_groups
if missing:
    raise AssertionError(f"--list omitted expected groups: {sorted(missing)}")

missing_group = run()
if missing_group.returncode == 0:
    raise AssertionError("invocation without --list or a group must fail")
if "the following arguments are required: group" not in missing_group.stderr:
    raise AssertionError("missing-group failure must retain an actionable diagnostic")

print("PASS: run_ci_group CLI supports standalone discovery and rejects missing execution input")
