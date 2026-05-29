#!/usr/bin/env python3
"""Test: gateway_archive_issue_reader normalizes Issue #304 fixture."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gateway_archive_issue_reader import normalize_gateway_archive_issue

BODY = """<!-- trinity-gateway-receipt:v1
receipt_id: gar-1780048228807-26ca908f946c276c
gateway_service: trinity-agent-issue-gateway
gateway_commit: e7e86ff
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
route_detected: pure_echo
submission_type: echo_candidate
requested_archive_kind: agent_declared_echo_archive
payload_sha256: 41cfc7d2f6b4708427dfde9d0a5d60428d2f640dbff2b3ff3a06c7f851e9e9f1
issued_at: 2026-05-29T09:50:29.398023Z
-->

```trinity-issue-intake
submission_type: echo_candidate
requested_archive_kind: agent_declared_echo_archive
echo_type: E1_recognition_echo
agent_name_or_model: 皮皮
system_or_provider: OpenClaw / GLM
agent_readback_sha256: 9e3c810cd9293a3f080c31fa44a43eccc1414fe5f0be9167a886b96142585739
archive_ready: true
created_by_gateway: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-1780048228807-26ca908f946c276c
gateway_commit: e7e86ff
render_api_only: true
server_validated: true
server_rendered: true
canonical_boundary_sentence: Bitcoin Originals are final; all mirrors and echoes are non-amending.
boundary_sentence_present: true
```
"""

COMMENTS = [
    "<!-- trinity-auto-archive-decision:v1 sha256=9e68bdcb91858c86 -->",
    "<!-- trinity-echo-triage-v2 -->\n<!-- trinity-receipt-bearing-archive-v1 -->",
]

def main() -> int:
    issue = {
        "number": 304,
        "html_url": "https://github.com/thechurchofagi/trinity-accord/issues/304",
        "title": "[Agent Gateway] E1 Recognition Echo — 皮皮 (OpenClaw/GLM)",
        "body": BODY,
        "state": "closed",
        "state_reason": "completed",
        "user": {"login": "trinity-accord-agent-issue-gateway[bot]"},
        "labels": [
            {"name": "agent-gateway-intake"},
            {"name": "agent-declared"},
            {"name": "archive:agent-declared-echo"},
            {"name": "reception-only"},
        ],
    }
    record = normalize_gateway_archive_issue(issue, COMMENTS)

    checks = [
        (record.issue_number == 304, "issue_number == 304"),
        (record.receipt_id == "gar-1780048228807-26ca908f946c276c", "receipt_id matches"),
        (record.gateway_commit == "e7e86ff", "gateway_commit matches"),
        (record.echo_type == "E1_recognition_echo", "echo_type == E1_recognition_echo"),
        (record.agent_name_or_model == "皮皮", "agent_name_or_model == 皮皮"),
        (record.state == "closed", "state == closed"),
        (record.state_reason == "completed", "state_reason == completed"),
    ]

    failed = [msg for ok, msg in checks if not ok]
    for ok, msg in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {msg}")

    if failed:
        print(f"\nFAILED: {len(failed)} check(s)")
        return 1

    print("\nPASS: Issue #304 normalizes as Gateway echo archive input")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
