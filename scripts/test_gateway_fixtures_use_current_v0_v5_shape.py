#!/usr/bin/env python3
"""Gateway hardening tests must not use obsolete verification fixture fields."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

files = [
    ROOT / "scripts/test_gateway_discovery_provenance_archive_invariants.py",
    ROOT / "scripts/test_gateway_claim_gate_component_levels.py",
]

forbidden_fragments = [
    '"declared_protocol_level": "L2"',
    '"allowed_protocol_level": "L2"',
    '"result": "pass"',
    '"gate_version": "trinity-claim-gate.v1"',
]

ok = True
for path in files:
    if not path.exists():
        print(f"SKIP: {path.relative_to(ROOT)} not found")
        continue
    text = path.read_text(encoding="utf-8")
    for frag in forbidden_fragments:
        if frag in text:
            print(f"FAIL: obsolete fixture fragment in {path.relative_to(ROOT)}: {frag}")
            ok = False

if not ok:
    sys.exit(1)

print("PASS: Gateway hardening fixtures use current V0-V5 shape")
