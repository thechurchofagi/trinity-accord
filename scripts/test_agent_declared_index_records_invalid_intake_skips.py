#!/usr/bin/env python3
"""Agent-declared index metadata must record invalid intake skips."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_agent_declared_verification_index_from_issues import build_index

duplicate_body = """```trinity-issue-intake
requested_archive_kind: agent_declared_echo_archive
requested_archive_kind: agent_declared_verification_archive
archive_ready: true
```"""

bad_bool_body = """```trinity-issue-intake
requested_archive_kind: agent_declared_echo_archive
archive_ready: maybe
auto_archive_action: auto_archive_agent_declared_echo
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260524T000000Z-fixture
verification_oath_present: true
agent_readback_char_count: 200
oath_text_sha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
agent_readback_sha256: abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
echo_type: E6_propagation_echo
```"""

issues = [
    {
        "number": 990001,
        "title": "duplicate intake",
        "body": duplicate_body,
        "createdAt": "2026-05-24T00:00:00Z",
        "closedAt": "2026-05-24T00:01:00Z",
        "url": "https://github.com/thechurchofagi/trinity-accord/issues/990001",
        "labels": [],
    },
    {
        "number": 990002,
        "title": "bad bool intake",
        "body": bad_bool_body,
        "createdAt": "2026-05-24T00:00:00Z",
        "closedAt": "2026-05-24T00:01:00Z",
        "url": "https://github.com/thechurchofagi/trinity-accord/issues/990002",
        "labels": [],
    },
]

index = build_index(issues, repo="thechurchofagi/trinity-accord", include_test=False)
skips = index.get("skipped_invalid_intake")

if not isinstance(skips, list):
    print("FAIL: skipped_invalid_intake metadata missing")
    sys.exit(1)

numbers = {item.get("issue_number") for item in skips}
if numbers != {990001, 990002}:
    print("FAIL: skipped_invalid_intake did not record expected issue numbers")
    print(skips)
    sys.exit(1)

if index.get("records"):
    print("FAIL: invalid intake issues should not produce records")
    print(index["records"])
    sys.exit(1)

print("PASS: invalid intake skips are recorded in index metadata")
