#!/usr/bin/env python3
"""Native agent-declared Echo archive must count into public status bucket."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_public_home_status import compute_reception_status

status = compute_reception_status(
    echo_records=[],
    agent_declared_records=[
        {
            "issue_number": 999001,
            "issue_url": "https://github.com/thechurchofagi/trinity-accord/issues/999001",
            "archive_ready": True,
            "requested_archive_kind": "agent_declared_echo_archive",
            "semantic_archive_kind": "agent_declared_echo_archive",
            "counts_toward_home_reception": True,
            "counts_toward_home_verifiability": False,
            "test_record": False,
            "echo_type": "E6_propagation_echo",
        }
    ],
)

echo_archives = status["agent_declared_echo_archives"]
if echo_archives["count"] != 1:
    print("FAIL: native Echo archive did not count toward agent_declared_echo_archives.count")
    sys.exit(1)

if echo_archives["by_echo_type"].get("E6_propagation_echo") != 1:
    print("FAIL: native Echo archive did not increment E6_propagation_echo bucket")
    sys.exit(1)

print("PASS: native agent-declared Echo archive counts into public status")
