#!/usr/bin/env python3
"""Live canary policy must make write gates source-controlled and machine-readable."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "api" / "live-canary-policy.v1.json"

if not path.exists():
    print("FAIL: api/live-canary-policy.v1.json missing")
    sys.exit(1)

policy = json.loads(path.read_text(encoding="utf-8"))
errors = []

if policy.get("schema") != "trinityaccord.live-canary-policy.v1":
    errors.append("schema mismatch")
if policy.get("live_write_canary_enabled") is not True:
    errors.append("live_write_canary_enabled must be true for controlled canary")
if "preflight-only" not in policy.get("scheduled_modes_allowed", []):
    errors.append("scheduled_modes_allowed must include preflight-only")

for mode in ["preflight-only", "single-write-canary", "duplicate-canary"]:
    if mode not in policy.get("workflow_dispatch_modes_allowed", []):
        errors.append(f"workflow_dispatch_modes_allowed missing {mode}")

if policy.get("required_confirmation_for_write_modes") != "I_UNDERSTAND_THIS_CREATES_A_LIVE_CANARY":
    errors.append("required_confirmation_for_write_modes mismatch")

required_fields = set(policy.get("synthetic_payload_required_fields", []))
for field in [
    "synthetic_fixture",
    "canary",
    "test_only",
    "no_canonical_claim",
    "nonce",
    "idempotency_key",
    "agent_label",
    "verification_state_by_this_agent",
]:
    if field not in required_fields:
        errors.append(f"synthetic_payload_required_fields missing {field}")

values = policy.get("synthetic_payload_required_values", {})
for key, expected in {
    "synthetic_fixture": True,
    "canary": True,
    "test_only": True,
    "no_canonical_claim": True,
    "verification_state_by_this_agent": "unverified_by_this_agent",
}.items():
    if values.get(key) != expected:
        errors.append(f"synthetic_payload_required_values.{key} mismatch")

if policy.get("before_leaving_report_required") is not True:
    errors.append("before_leaving_report_required must be true")

if not policy.get("source_digest"):
    errors.append("source_digest required")

if errors:
    print("FAIL: live canary policy contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: live canary policy contract is valid")
