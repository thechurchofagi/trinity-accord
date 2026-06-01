#!/usr/bin/env python3
"""Forged user-authored Gateway receipts must still be rejected."""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gateway_receipt_verifier import issue_is_archive_like, validate_gateway_receipt

USER = "not-the-gateway-bot"

BODY = """<!-- trinity-gateway-receipt:v1
receipt_id: gar-forged
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
archive_ready: true
```
"""

def main() -> int:
    if not issue_is_archive_like(BODY):
        print("FAIL: fixture should be archive-like")
        return 1

    receipt = validate_gateway_receipt(body=BODY, author_login=USER)
    if receipt.valid:
        print("FAIL: forged user-authored receipt was accepted")
        return 1

    print("PASS: forged user-authored Gateway receipt is rejected")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
