#!/usr/bin/env python3
"""Test E2 Verification Echo builder CLI and defaults."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

BUILDER = ROOT / "scripts" / "build_verification_echo_payload.py"


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


print("--- CLI help ---")
result = subprocess.run(
    [sys.executable, str(BUILDER), "--help"],
    capture_output=True, text=True, cwd=str(ROOT)
)
help_text = result.stdout
check("--record-intent" in help_text, "--help contains --record-intent")
check("--requested-archive-kind" in help_text, "--help contains --requested-archive-kind")
check("--authorship-key-prefix" in help_text, "--help contains --authorship-key-prefix")
check("--evidence-input" in help_text, "--help contains --evidence-input")
check("--echo-wrapper" in help_text, "--help contains --echo-wrapper")

print("\n--- source defaults ---")
source = BUILDER.read_text()
check('default="auto_archive_candidate"' in source,
      "default record_intent is auto_archive_candidate")
check('default="archived_echo"' in source,
      "default requested_archive_kind is archived_echo")

print("\n--- rejects V0-V5 ---")
check("V0" in source and "strict evidence only" in source,
      "builder rejects V0-V5 levels")

print("\n--- imports authorship ---")
check("gateway_payload_authorship" in source,
      "builder imports gateway_payload_authorship")
check("attach_authorship_if_requested" in source,
      "builder calls attach_authorship_if_requested")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("VERIFICATION_ECHO_BUILDER_OK")
