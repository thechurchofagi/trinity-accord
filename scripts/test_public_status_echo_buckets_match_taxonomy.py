#!/usr/bin/env python3
"""REM-PUB-001/002: Public status Echo buckets must be generated from canonical taxonomy."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types
from generate_public_home_status import compute_reception_status

src = (ROOT / "scripts/generate_public_home_status.py").read_text(encoding="utf-8")

# Public status must use the taxonomy loader, not a hand-written bucket map
if "allowed_canonical_echo_types" not in src:
    print("FAIL: generate_public_home_status.py does not use allowed_canonical_echo_types")
    sys.exit(1)

bad_terms = [
    "E1_read_oriented_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
]
for term in bad_terms:
    if term in src:
        print(f"FAIL: public status still contains stale/conflicting Echo bucket: {term}")
        sys.exit(1)

# Verify actual output structure
status = compute_reception_status([], [])
try:
    buckets = status["agent_declared_echo_archives"]["by_echo_type"]
except KeyError as e:
    print(f"FAIL: could not locate agent_declared_echo_archives.by_echo_type: {e}")
    sys.exit(1)

actual = set(buckets.keys())
expected = allowed_canonical_echo_types()

if actual != expected:
    print("FAIL: public status Echo bucket set does not equal canonical taxonomy")
    print("Missing:", sorted(expected - actual))
    print("Extra:", sorted(actual - expected))
    sys.exit(1)

print("PASS: public status Echo buckets exactly match canonical taxonomy")
