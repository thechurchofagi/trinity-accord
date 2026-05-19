#!/usr/bin/env python3
"""Test that Gateway capabilities expose all foolproof agent paths."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()

print("--- capabilities entries ---")
check("pure_echo_path:" in server, "capabilities has pure_echo_path")
check("v0_v5_archive_submission:" in server, "capabilities has v0_v5_archive_submission")
check("strict_evidence_report_path:" in server, "capabilities has strict_evidence_report_path")
check("verification_echo_path:" in server, "capabilities has verification_echo_path")
check("authorship_proof:" in server, "capabilities has authorship_proof")

print("\n--- verification_echo_path details ---")
check("/gateway/examples/verification-echo/raw" in server,
      "verification_echo_path raw endpoint present")

print("\n--- V0-V5 per-level endpoints ---")
for level in ["v0", "v1", "v2", "v3", "v4", "v4plus", "v5"]:
    check(f"agent_declared_{level}_raw" in server,
          f"capabilities has agent_declared_{level}_raw")

print("\n--- authorship_proof details ---")
check("private_key_must_never_be_submitted" in server,
      "authorship_proof says private key must never be submitted")
check("does_not_affect_counts" in server,
      "authorship_proof says does_not_affect_counts")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("GATEWAY_CAPABILITIES_FOOLPROOF_PATHS_OK")
