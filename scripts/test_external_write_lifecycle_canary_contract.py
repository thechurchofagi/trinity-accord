#!/usr/bin/env python3
"""External write lifecycle canary must be gated and safe by default."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts" / "smoke_external_agent_write_lifecycle_canary.py"

if not script.exists():
    print("FAIL: smoke_external_agent_write_lifecycle_canary.py missing")
    sys.exit(1)

text = script.read_text(encoding="utf-8")

required = [
    "preflight-only",
    "single-write-canary",
    "duplicate-canary",
    "api/live-canary-policy.v1.json",
    "discover_gateway_base_url",
    "gateway_discovery",
    "primary_base_url",
    "base_url_candidates",
    "required_confirmation_for_write_modes",
    "validate_payload_against_policy",
    "gateway_base_url_discovered",
    "write_gate_source",
    "synthetic_fixture",
    "canary",
    "idempotency_key",
    "before_leaving lifecycle report",
    "public_status_readback_performed",
    "verification_state_by_this_agent",
    "unverified_by_this_agent",
    "preflight-only",
    "single-write-canary",
    "duplicate-canary",
    "before_leaving lifecycle report",
]

missing = [phrase for phrase in required if phrase not in text]
if missing:
    print("FAIL: write lifecycle canary missing phrase(s):")
    for phrase in missing:
        print("  -", phrase)
    sys.exit(1)

tree = ast.parse(text)

# POST is allowed only because write modes are gated. Ensure the gate function exists.
if "def require_write_gate" not in text:
    print("FAIL: write canary must define require_write_gate")
    sys.exit(1)

# Ensure default mode is preflight-only.
if 'default="preflight-only"' not in text:
    print("FAIL: write canary default mode must be preflight-only")
    sys.exit(1)

# Forbid old manual requirements
for forbidden in [
    "TRINITY_GATEWAY_URL",
    "TRINITY_LIVE_CANARY_WRITE",
    "secrets.TRINITY_LIVE_CANARY_WRITE",
]:
    if forbidden in text:
        print(f"FAIL: manual configuration dependency remains: {forbidden}")
        sys.exit(1)

print("PASS: external write lifecycle canary contract is guarded")
