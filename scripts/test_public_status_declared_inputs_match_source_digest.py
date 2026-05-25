#!/usr/bin/env python3
"""PUB-INPUT-001: Public status declared inputs match source_digest/generated_from."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "scripts/generate_public_home_status.py").read_text(encoding="utf-8")

expected_constants = {
    "ECHO_INDEX": "/api/echo-index.json",
    "EXTERNAL_WITNESS_INDEX": "/api/external-witness-index.json",
    "PHYSICAL_ANCHOR": "/api/core-object-alpha-shenzhen-notary-2026-05-06.json",
    "GUARDIAN_REGISTRY": "/api/guardian-registry.json",
    "GUARDIAN_ACTIVE_LISTING_POLICY": "/api/guardian-active-listing-policy.v1.json",
    "AGENT_DECLARED_INDEX": "/api/agent-declared-verification-index.json",
}

digest_match = re.search(r"def source_digest\(\).*?return h\.hexdigest\(\)\[:16\]", src, re.S)
if not digest_match:
    print("FAIL: source_digest function not found")
    sys.exit(1)

digest_block = digest_match.group(0)

missing_in_digest = [name for name in expected_constants if name not in digest_block]
if missing_in_digest:
    print(f"FAIL: source_digest missing expected live inputs: {missing_in_digest}")
    sys.exit(1)

if "AGENT_DECLARED_ECHO_INDEX" in digest_block:
    print("FAIL: source_digest includes deprecated AGENT_DECLARED_ECHO_INDEX")
    sys.exit(1)

generated_from_block = re.search(r"generated_from\s*=\s*\[(.*?)\]", src, re.S)
if not generated_from_block:
    print("FAIL: generated_from block not found")
    sys.exit(1)

# Check both static list and conditional appends
# The conditional "if AGENT_DECLARED_INDEX.exists()" adds it dynamically
if "/api/agent-declared-verification-index.json" not in src:
    print("FAIL: generated_from missing agent-declared-verification-index.json")
    sys.exit(1)

missing_generated = [path for path in expected_constants.values() if path not in src]
if missing_generated:
    print(f"FAIL: source missing expected paths: {missing_generated}")
    sys.exit(1)

print("PASS: public status live inputs match source_digest/generated_from")
