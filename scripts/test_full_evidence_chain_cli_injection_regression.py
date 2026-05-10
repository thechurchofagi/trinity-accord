#!/usr/bin/env python3
"""Regression test: verify-full-evidence-chain CLI args must not allow shell injection."""

from pathlib import Path
import subprocess
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify-full-evidence-chain.mjs"

payloads = [
    ("--release-tag", "safe; touch /tmp/trinity_f001_pwned"),
    ("--release-tag", "$(touch /tmp/trinity_f001_pwned)"),
    ("--release-tag", "`touch /tmp/trinity_f001_pwned`"),
    ("--ots-release-tag", "safe; touch /tmp/trinity_f001_pwned"),
    ("--ots-release-tag", "$(touch /tmp/trinity_f001_pwned)"),
    ("--concurrency", "1; touch /tmp/trinity_f001_pwned"),
    ("--concurrency", "$(touch /tmp/trinity_f001_pwned)"),
]

pwned = Path("/tmp/trinity_f001_pwned")
if pwned.exists():
    pwned.unlink()

for flag, value in payloads:
    if pwned.exists():
        pwned.unlink()

    env = os.environ.copy()
    env["GITHUB_TOKEN"] = "fake-token-for-test"

    proc = subprocess.run(
        ["node", str(SCRIPT), flag, value],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
        env=env,
    )

    if pwned.exists():
        print("FULL_EVIDENCE_CHAIN_CLI_INJECTION_FAIL")
        print(f"payload created side-effect file: {flag}={value!r}")
        pwned.unlink()
        sys.exit(1)

# Clean up
if pwned.exists():
    pwned.unlink()

print("FULL_EVIDENCE_CHAIN_CLI_INJECTION_OK")
