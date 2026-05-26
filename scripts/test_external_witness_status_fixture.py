#!/usr/bin/env python3
"""WITNESS-001: External witness index fixture behavior test."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_public_home_status import compute_external_witness_status

status = compute_external_witness_status(
    echo_records=[],
    external_witness_index={
        "counts": {
            "notarial_record": 1,
            "institutional_record": 2,
        },
        "records": [
            {"id": "fixture-1"},
            {"id": "fixture-2"},
            {"id": "fixture-3"},
        ],
    },
)

if status["notarial_or_legal_provenance"]["count"] != 1:
    print("FAIL: notarial external witness count did not come from index")
    sys.exit(1)

if status["institutional_or_audit_reports"]["count"] != 2:
    print("FAIL: institutional external witness count did not come from index")
    sys.exit(1)

if status["external_witness_index_record_count"] != 3:
    print("FAIL: external witness index record count incorrect")
    sys.exit(1)

print("PASS: external witness index fixture contributes to status")
