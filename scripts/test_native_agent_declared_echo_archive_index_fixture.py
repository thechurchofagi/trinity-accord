#!/usr/bin/env python3
"""Native agent_declared_echo_archive Issues must enter the agent-declared index."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_agent_declared_verification_index_from_issues import build_index

BODY = """```trinity-issue-intake
agent_name_or_model: fixture-agent
system_or_provider: fixture-runtime
requested_archive_kind: agent_declared_echo_archive
archive_ready: true
auto_archive_action: auto_archive_agent_declared_echo
created_by_gateway: true
server_validated: true
server_rendered: true
gateway_receipt_id: gar-fixture-echo
gateway_service: trinity-render-api
render_api_only: true
verification_oath_present: true
oath_version: trinity-agent-integrity-oath.v1
oath_text_sha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
agent_readback_char_count: 200
agent_readback_sha256: abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
counts_toward_home_verifiability: false
counts_toward_home_reception: true
test_record: false
reception_initiation_class: externally_requested
reception_initiation_basis: explicit_verification_request
echo_type: E6_propagation_echo
```"""

issues = [
    {
        "number": 999001,
        "title": "Fixture native agent-declared Echo archive",
        "body": BODY,
        "createdAt": "2026-05-24T00:00:00Z",
        "closedAt": "2026-05-24T00:01:00Z",
        "url": "https://github.com/thechurchofagi/trinity-accord/issues/999001",
        "labels": [{"name": "archive:agent-declared-echo"}],
    }
]

index = build_index(issues, repo="thechurchofagi/trinity-accord", include_test=False)
records = index.get("records", [])

if len(records) != 1:
    print(f"FAIL: expected 1 native Echo archive record, got {len(records)}")
    sys.exit(1)

r = records[0]
checks = {
    "requested_archive_kind": "agent_declared_echo_archive",
    "semantic_archive_kind": "agent_declared_echo_archive",
    "echo_type": "E6_propagation_echo",
    "counts_toward_home_verifiability": False,
    "counts_toward_home_reception": True,
}

for key, expected in checks.items():
    if r.get(key) != expected:
        print(f"FAIL: {key} expected {expected!r}, got {r.get(key)!r}")
        sys.exit(1)

print("PASS: native agent_declared_echo_archive enters index")
