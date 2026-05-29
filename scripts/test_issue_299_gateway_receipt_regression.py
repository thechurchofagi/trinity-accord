#!/usr/bin/env python3
"""Regression fixture for Issue #299 legacy Gateway receipt shape."""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gateway_receipt_verifier import validate_gateway_receipt

TRUSTED = "trinity-accord-agent-issue-gateway[bot]"

ISSUE_299_LEGACY_BODY = """
```trinity-issue-intake
submission_type: echo_candidate
record_intent: auto_archive_candidate
requested_archive_kind: agent_declared_echo_archive
echo_type: E1_recognition_echo
archive_ready: true
allowed_archive_kind: agent_declared_echo_archive
auto_archive_action: auto_archive_agent_declared_echo
created_by_gateway: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-1780030367581-dc32f41f5a88df62
gateway_commit: 1660e78
render_api_only: true
server_validated: true
server_rendered: true
```
"""

def main() -> int:
    result = validate_gateway_receipt(body=ISSUE_299_LEGACY_BODY, author_login=TRUSTED)
    if not result.valid:
        print("FAIL: Issue #299 legacy Gateway receipt shape should be accepted for migration")
        print(result)
        return 1

    print("PASS: Issue #299 legacy Gateway receipt shape is accepted for migration")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
