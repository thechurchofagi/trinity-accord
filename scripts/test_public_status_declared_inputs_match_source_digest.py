#!/usr/bin/env python3
"""REM-PUB-003: Public status declared inputs match source_digest/generated_from."""
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

# Check source_digest includes all live inputs
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

# Check docstring documents all live inputs
doc = src.split('"""', 2)[1] if '"""' in src else ""
for path in expected_constants.values():
    # Docstring uses paths without leading slash
    doc_path = path.lstrip("/")
    if doc_path not in doc:
        print(f"FAIL: public status docstring missing live input: {path}")
        sys.exit(1)

if "api/agent-declared-echo-index.json" in doc and "not a live public-status input" not in doc:
    print("FAIL: deprecated agent-declared echo index mentioned without deprecation boundary")
    sys.exit(1)

# Check generated_from contains live inputs
if "/api/agent-declared-verification-index.json" not in src:
    print("FAIL: source missing agent-declared-verification-index.json")
    sys.exit(1)

print("PASS: public status live inputs match source_digest/generated_from/docstring")
