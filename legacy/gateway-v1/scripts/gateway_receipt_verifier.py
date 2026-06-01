#!/usr/bin/env python3
"""Gateway receipt parsing and validation for GitHub Issue triage."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

TRUSTED_GATEWAY_ACTORS = {
    "trinity-accord-agent-issue-gateway[bot]",
}

GATEWAY_SERVICE = "trinity-agent-issue-gateway"
RECEIPT_MARKER = "trinity-gateway-receipt:v1"
ARCHIVE_DECISION_MARKER = "trinity-auto-archive-decision:v1"
RECEIPT_ID_RE = re.compile(r"^gar-[A-Za-z0-9._-]+$")

LEGACY_REQUIRED_SNIPPETS = [
    "created_by_gateway: true",
    "gateway_service: trinity-agent-issue-gateway",
    "gateway_receipt_id: gar-",
    "render_api_only: true",
    "server_validated: true",
    "server_rendered: true",
]

RECEIPT_BLOCK_RE = re.compile(
    r"<!--\s*trinity-gateway-receipt:v1(?P<body>.*?)-->",
    re.DOTALL,
)

ARCHIVE_DECISION_RE = re.compile(
    r"<!--\s*trinity-auto-archive-decision:v1",
    re.DOTALL,
)

ARCHIVE_LIKE_SNIPPETS = [
    "```trinity-issue-intake",
    "requested_archive_kind:",
    "record_intent: auto_archive_candidate",
    "auto_archive_action:",
    "archive_ready: true",
]

@dataclass(frozen=True)
class ReceiptResult:
    valid: bool
    mode: str
    reason: str
    receipt: dict[str, str]

def _parse_kv_block(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data

def is_trusted_gateway_actor(author_login: str | None) -> bool:
    return bool(author_login) and author_login in TRUSTED_GATEWAY_ACTORS

def issue_is_archive_like(body: str) -> bool:
    return any(snippet in body for snippet in ARCHIVE_LIKE_SNIPPETS)

def has_archive_decision_marker(comments: Iterable[str]) -> bool:
    return any(ARCHIVE_DECISION_RE.search(comment or "") for comment in comments)

def parse_gateway_receipt_marker(body: str) -> dict[str, str] | None:
    match = RECEIPT_BLOCK_RE.search(body or "")
    if not match:
        return None
    return _parse_kv_block(match.group("body"))

def validate_receipt_marker(receipt: dict[str, str], author_login: str | None) -> ReceiptResult:
    if not is_trusted_gateway_actor(author_login):
        return ReceiptResult(False, "marker", "untrusted_actor", receipt)

    required = [
        "receipt_id",
        "gateway_service",
        "gateway_commit",
        "created_by_gateway",
        "render_api_only",
        "server_validated",
        "server_rendered",
        "route_detected",
        "submission_type",
        "requested_archive_kind",
        "payload_sha256",
        "issued_at",
    ]
    missing = [key for key in required if not receipt.get(key)]
    if missing:
        return ReceiptResult(False, "marker", f"missing_fields:{','.join(missing)}", receipt)

    if not RECEIPT_ID_RE.match(receipt.get("receipt_id", "")):
        return ReceiptResult(False, "marker", "bad_receipt_id", receipt)

    if receipt.get("gateway_service") != GATEWAY_SERVICE:
        return ReceiptResult(False, "marker", "bad_gateway_service", receipt)

    for key in ["created_by_gateway", "render_api_only", "server_validated", "server_rendered"]:
        if receipt.get(key) != "true":
            return ReceiptResult(False, "marker", f"{key}_not_true", receipt)

    return ReceiptResult(True, "marker", "valid_gateway_receipt_marker", receipt)

def validate_legacy_gateway_receipt(body: str, author_login: str | None) -> ReceiptResult:
    if not is_trusted_gateway_actor(author_login):
        return ReceiptResult(False, "legacy", "untrusted_actor", {})

    missing = [snippet for snippet in LEGACY_REQUIRED_SNIPPETS if snippet not in body]
    if missing:
        return ReceiptResult(False, "legacy", "missing_legacy_snippets", {})

    match = re.search(r"gateway_receipt_id:\s*(gar-[A-Za-z0-9._-]+)", body)
    if not match:
        return ReceiptResult(False, "legacy", "missing_gateway_receipt_id", {})

    receipt = {
        "receipt_id": match.group(1),
        "gateway_service": GATEWAY_SERVICE,
        "created_by_gateway": "true",
        "render_api_only": "true",
        "server_validated": "true",
        "server_rendered": "true",
    }
    return ReceiptResult(True, "legacy", "valid_legacy_gateway_receipt", receipt)

def validate_gateway_receipt(
    *,
    body: str,
    author_login: str | None,
    comments: Iterable[str] = (),
) -> ReceiptResult:
    marker = parse_gateway_receipt_marker(body)
    if marker is not None:
        return validate_receipt_marker(marker, author_login)

    legacy = validate_legacy_gateway_receipt(body, author_login)
    if legacy.valid:
        return legacy

    if has_archive_decision_marker(comments) and is_trusted_gateway_actor(author_login):
        # Secondary compatibility mode. This must not be the primary path.
        return ReceiptResult(True, "archive_decision_comment", "trusted_gateway_archive_decision_comment", {})

    return ReceiptResult(False, "none", "no_valid_gateway_receipt", {})
