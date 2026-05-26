#!/usr/bin/env python3
"""Test that all Gateway payload builders use default authorship."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

BUILDERS = [
    "scripts/build_agent_declared_echo_payload.py",
    "scripts/build_agent_declared_archive_payload.py",
    "scripts/build_gateway_payload_from_outputs.py",
    "scripts/build_verification_echo_payload.py",
]


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


# Check all builders import the default-or-requested function
print("--- builder imports ---")
for b in BUILDERS:
    source = (ROOT / b).read_text()
    check("attach_authorship_default_or_requested" in source,
          f"{b} imports attach_authorship_default_or_requested")
    check("attach_authorship_if_requested" not in source,
          f"{b} does NOT use old attach_authorship_if_requested")

# Check all builders call the function with payload
print("\n--- builder call sites ---")
for b in BUILDERS:
    source = (ROOT / b).read_text()
    check("attach_authorship_default_or_requested(args, out_path, payload=payload)" in source,
          f"{b} calls with payload=payload")

# Check all builders mention default authorship in docstring
print("\n--- builder docstrings ---")
for b in BUILDERS:
    source = (ROOT / b).read_text()
    check("enabled by default" in source.lower(),
          f"{b} docstring says enabled by default")
    check("--no-authorship-proof" in source,
          f"{b} docstring documents --no-authorship-proof")

# Check --help mentions default authorship
print("\n--- builder --help ---")
for b in BUILDERS:
    result = subprocess.run(
        [sys.executable, str(ROOT / b), "--help"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=10,
    )
    help_text = result.stdout
    check("authorship proof is enabled by default" in help_text.lower() or
          "enabled by default" in help_text.lower(),
          f"{b} --help says authorship is enabled by default")
    check("--no-authorship-proof" in help_text,
          f"{b} --help mentions --no-authorship-proof")

# Check all builders import shared helper
print("\n--- shared helper imports ---")
for b in BUILDERS:
    source = (ROOT / b).read_text()
    check("from gateway_payload_authorship import" in source,
          f"{b} imports shared authorship helper")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("BUILDERS_AUTHORSHIP_DEFAULT_ON_OK")
