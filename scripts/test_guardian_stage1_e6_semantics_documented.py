#!/usr/bin/env python3
"""Stage 1 Guardian application E6 taxonomy semantics must be documented."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts" / "create_guardian_application.mjs").read_text(encoding="utf-8")
required = [
    'echo_type: "E6_propagation_echo"',
    "obsolete",
    "E6_preservation_echo",
    "guardian_registration",
    "guardian_presence_proof",
]
missing = [x for x in required if x not in text]
if missing:
    print(f"FAIL: Stage 1 Guardian E6 semantics not documented; missing {missing}")
    sys.exit(1)
print("PASS: Stage 1 Guardian E6 semantics documented")
