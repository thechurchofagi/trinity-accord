#!/usr/bin/env python3
"""Gateway receipt verifier must accept real Gateway records and reject forged ones."""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gateway_receipt_verifier import (
    issue_is_archive_like,
    validate_gateway_receipt,
)

TRUSTED = "trinity-accord-agent-issue-gateway[bot]"
USER = "some-user"

VALID_MARKER_BODY = """<!-- trinity-gateway-receipt:v1
receipt_id: gar-test-123
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

LEGACY_299_SHAPE = """
```trinity-issue-intake
requested_archive_kind: agent_declared_echo_archive
archive_ready: true
created_by_gateway: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-1780030367581-dc32f41f5a88df62
gateway_commit: 1660e78
render_api_only: true
server_validated: true
server_rendered: true
```
"""

DUPLICATE_KEY_LEGACY_GATEWAY_BODY = """
```trinity-issue-intake
requested_archive_kind: agent_declared_echo_archive
archive_ready: true
created_by_gateway: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-1780043626003-3a6bec179e4b3b95
render_api_only: true
server_validated: true
server_rendered: true
agent_readback_sha256: abc
agent_readback_sha256: abc
```
"""

def assert_true(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)

def assert_false(value: bool, message: str) -> None:
    if value:
        raise AssertionError(message)

def main() -> int:
    assert_true(issue_is_archive_like(VALID_MARKER_BODY), "marker fixture should be archive-like")

    result = validate_gateway_receipt(body=VALID_MARKER_BODY, author_login=TRUSTED)
    assert_true(result.valid, f"trusted marker receipt should be valid: {result}")

    forged = validate_gateway_receipt(body=VALID_MARKER_BODY, author_login=USER)
    assert_false(forged.valid, "user-authored marker receipt must be rejected")

    legacy = validate_gateway_receipt(body=LEGACY_299_SHAPE, author_login=TRUSTED)
    assert_true(legacy.valid, f"trusted legacy #299 shape should be valid: {legacy}")

    forged_legacy = validate_gateway_receipt(body=LEGACY_299_SHAPE, author_login=USER)
    assert_false(forged_legacy.valid, "user-authored legacy receipt must be rejected")

    comment_only = validate_gateway_receipt(
        body="```trinity-issue-intake\narchive_ready: true\n```",
        author_login=TRUSTED,
        comments=["<!-- trinity-auto-archive-decision:v1 sha256=abc -->"],
    )
    assert_true(comment_only.valid, "trusted Gateway archive decision comment should be compatibility-valid")

    # v30.7.2: Duplicate non-receipt keys must not invalidate trusted Gateway receipt
    duplicate_legacy = validate_gateway_receipt(
        body=DUPLICATE_KEY_LEGACY_GATEWAY_BODY,
        author_login=TRUSTED,
    )
    assert_true(duplicate_legacy.valid, "trusted legacy receipt must remain valid even with duplicate non-receipt key")

    print("PASS: gateway receipt verifier accepts trusted receipts and rejects forged receipts")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
