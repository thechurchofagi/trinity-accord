#!/usr/bin/env python3
"""REM-PUB-003: Public status declared inputs match source_digest/generated_from."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "scripts/generate_public_home_status.py").read_text(encoding="utf-8")

EXPECTED_GENERATED_FROM = {
    # Primary record-chain inputs
    "/api/record-chain-status.json",
    "/api/record-chain-anchor-status.json",
    "/api/record-chain-arweave-index.json",
    "/api/record-chain-arweave-backlog.json",
    "/api/record-chain-native-ots-backlog.json",
    "/api/arweave-wallet-status.json",
    "/api/homepage-visibility-overrides.v1.json",
    "/record-chain/chain-tip.json",
    "/record-chain/records/",
    # Legacy/archive inputs
    "/api/echo-index.json",
    "/api/external-witness-index.json",
    "/api/core-object-alpha-shenzhen-notary-2026-05-06.json",
    "/api/guardian-registry.json",
    "/api/guardian-active-listing-policy.v1.json",
    "/api/guardian-state.json",
    "/api/guardian-current-registry.json",
    "/api/guardian-active-listing-policy.v2.json",
    "/api/agent-declared-verification-index.json",
    "/api/waiting-heartbeat-status.json",
}

expected_constants = {
    "ECHO_INDEX": "/api/echo-index.json",
    "EXTERNAL_WITNESS_INDEX": "/api/external-witness-index.json",
    "PHYSICAL_ANCHOR": "/api/core-object-alpha-shenzhen-notary-2026-05-06.json",
    "GUARDIAN_REGISTRY": "/api/guardian-registry.json",
    "GUARDIAN_ACTIVE_LISTING_POLICY": "/api/guardian-active-listing-policy.v1.json",
    "GUARDIAN_STATE": "/api/guardian-state.json",
    "GUARDIAN_CURRENT_REGISTRY": "/api/guardian-current-registry.json",
    "GUARDIAN_ACTIVE_LISTING_POLICY_V2": "/api/guardian-active-listing-policy.v2.json",
    "AGENT_DECLARED_INDEX": "/api/agent-declared-verification-index.json",
}

# 1. Check source_digest includes all live inputs
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

# 2. Check docstring documents all live inputs
doc = src.split('"""', 2)[1] if '"""' in src else ""
for path in expected_constants.values():
    doc_path = path.lstrip("/")
    if doc_path not in doc:
        print(f"FAIL: public status docstring missing live input: {path}")
        sys.exit(1)

if "api/agent-declared-echo-index.json" in doc and "not a live public-status input" not in doc:
    print("FAIL: deprecated agent-declared echo index mentioned without deprecation boundary")
    sys.exit(1)

# 3. Parse actual generated JSON output
status = json.loads((ROOT / "api/public-home-status.json").read_text(encoding="utf-8"))
actual = set(status.get("generated_from", []))
if actual != EXPECTED_GENERATED_FROM:
    print("FAIL: public-home-status generated_from does not match expected live inputs")
    print("Missing:", sorted(EXPECTED_GENERATED_FROM - actual))
    print("Extra:", sorted(actual - EXPECTED_GENERATED_FROM))
    sys.exit(1)

if "/api/agent-declared-echo-index.json" in actual:
    print("FAIL: deprecated agent-declared echo index appears in generated_from")
    sys.exit(1)

# 4. Check source_digest constant coverage
for const in [
    "ECHO_INDEX",
    "EXTERNAL_WITNESS_INDEX",
    "PHYSICAL_ANCHOR",
    "GUARDIAN_REGISTRY",
    "GUARDIAN_ACTIVE_LISTING_POLICY",
    "AGENT_DECLARED_INDEX",
]:
    if const not in digest_block:
        print(f"FAIL: source_digest missing expected constant {const}")
        sys.exit(1)

print("PASS: public status live inputs match source_digest/generated_from/docstring")
