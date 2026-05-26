#!/usr/bin/env python3
"""Test that all Gateway payload builders support authorship proof options."""
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


for builder_path in BUILDERS:
    builder = ROOT / builder_path
    name = builder.name
    print(f"\n--- {name} ---")

    if not builder.exists():
        check(False, f"{name} exists")
        continue

    source = builder.read_text()

    # Check --authorship-key-prefix in help
    result = subprocess.run(
        [sys.executable, str(builder), "--help"],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    check("--authorship-key-prefix" in result.stdout,
          f"{name} --help contains --authorship-key-prefix")

    # Check imports gateway_payload_authorship
    check("gateway_payload_authorship" in source,
          f"{name} imports gateway_payload_authorship")

    # Check calls attach_authorship_if_requested
    check("attach_authorship_if_requested" in source,
          f"{name} calls attach_authorship_if_requested")

    # Check no private key submission guidance
    check("private key may be submitted" not in source.lower(),
          f"{name} does not say private key may be submitted")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("GATEWAY_PAYLOAD_AUTHORSHIP_BUILDER_OPTIONS_OK")
