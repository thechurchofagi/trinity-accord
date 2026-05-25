#!/usr/bin/env python3
"""compute_reception_status should fail on non-canonical agent-declared Echo types."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_public_home_status import compute_reception_status

try:
    compute_reception_status(
        echo_records=[],
        agent_declared_records=[
            {
                "issue_number": 999999,
                "issue_url": "https://example.invalid/999999",
                "semantic_archive_kind": "agent_declared_echo_archive",
                "counts_toward_home_reception": True,
                "test_record": False,
                "echo_type": "E5_correction_echo",
            }
        ],
    )
except RuntimeError as e:
    if "Unknown non-canonical echo_type" in str(e):
        print("PASS: non-canonical echo_type rejected")
        sys.exit(0)
    print("FAIL: wrong RuntimeError:", e)
    sys.exit(1)

print("FAIL: non-canonical echo_type was accepted")
sys.exit(1)
