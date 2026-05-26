#!/usr/bin/env python3
"""DEEP-WITNESS-001: external witness index contributes to public status."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "scripts/generate_public_home_status.py"
text = p.read_text(encoding="utf-8")

required = [
    "compute_external_witness_status(echo_records, external_witness)",
    "external_witness_index",
    "external_witness_index_record_count",
]

missing = [s for s in required if s not in text]
if missing:
    print(f"FAIL: external witness index is not fully used in public status: {missing}")
    sys.exit(1)

print("PASS: external witness index contributes to public status")
