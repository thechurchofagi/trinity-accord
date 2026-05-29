#!/usr/bin/env python3
"""Regression: trusted Gateway receipt must not be classified as direct Issue archive attempt."""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gateway_receipt_verifier import issue_is_archive_like, validate_gateway_receipt

TRUSTED = "trinity-accord-agent-issue-gateway[bot]"

BODY = """<!-- trinity-gateway-receipt:v1
receipt_id: gar-test-299
gateway_service: trinity-agent-issue-gateway
gateway_commit: 1660e78
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
route_detected: pure_echo
submission_type: echo_candidate
requested_archive_kind: agent_declared_echo_archive
payload_sha256: abc123
issued_at: 2026-05-29T00:00:00Z
-->
```trinity-issue-intake
requested_archive_kind: agent_declared_echo_archive
record_intent: auto_archive_candidate
archive_ready: true
auto_archive_action: auto_archive_agent_declared_echo
```
"""

def should_close_as_direct_issue_archive_attempt(body: str, author: str) -> bool:
    if not issue_is_archive_like(body):
        return False
    receipt = validate_gateway_receipt(body=body, author_login=author)
    return not receipt.valid

def main() -> int:
    if should_close_as_direct_issue_archive_attempt(BODY, TRUSTED):
        print("FAIL: trusted Gateway receipt was classified as direct Issue archive attempt")
        return 1

    print("PASS: trusted Gateway receipt is not classified as direct Issue archive attempt")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
