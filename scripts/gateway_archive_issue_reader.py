#!/usr/bin/env python3
"""Normalize receipt-bearing Gateway Issues for repository archive persistence."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any, Iterable

try:
    from gateway_receipt_verifier import validate_gateway_receipt
except ImportError:
    from scripts.gateway_receipt_verifier import validate_gateway_receipt  # type: ignore

TRIAGE_MARKER = "trinity-echo-triage-v2"
ARCHIVE_MARKER = "trinity-receipt-bearing-archive-v1"

REQUIRED_LABELS = {
    "agent-gateway-intake",
    "agent-declared",
    "archive:agent-declared-echo",
    "reception-only",
}

FORBIDDEN_LABELS = {
    "echo:invalid",
    "invalid:direct-issue-archive-attempt",
    "not-counted",
    "render-api-required",
}

@dataclass(frozen=True)
class GatewayArchiveInput:
    issue_number: int
    issue_url: str
    title: str
    author_login: str
    state: str
    state_reason: str | None
    receipt_id: str
    gateway_commit: str
    route_detected: str
    submission_type: str
    requested_archive_kind: str
    payload_sha256: str
    issued_at: str
    echo_type: str  # DEPRECATED — kept for legacy record parsing
    agent_name_or_model: str
    system_or_provider: str
    agent_readback_sha256: str
    boundary_sentence: str

def _parse_kv(text: str) -> dict[str, str]:
    out = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out

def extract_receipt_marker(body: str) -> dict[str, str]:
    m = re.search(r"<!--\s*trinity-gateway-receipt:v1(?P<body>.*?)-->", body or "", re.DOTALL)
    return _parse_kv(m.group("body")) if m else {}

def extract_intake_block(body: str) -> str:
    matches = re.findall(r"```trinity-issue-intake\s*\n([\s\S]*?)```", body or "")
    if len(matches) != 1:
        raise ValueError(f"expected exactly one trinity-issue-intake block, got {len(matches)}")
    return matches[0]

def parse_intake_block_loose(body: str) -> dict[str, Any]:
    block = extract_intake_block(body)
    out: dict[str, Any] = {}
    duplicates: dict[str, int] = {}
    current_list: str | None = None

    for raw in block.splitlines():
        if raw.startswith("  - ") and current_list:
            out.setdefault(current_list, []).append(raw[4:].strip())
            continue

        if ":" not in raw:
            continue

        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_list = None

        if key in out:
            duplicates[key] = duplicates.get(key, 1) + 1
            continue

        if value == "":
            out[key] = []
            current_list = key
        elif value == "true":
            out[key] = True
        elif value == "false":
            out[key] = False
        else:
            out[key] = value

    if duplicates:
        out["_duplicate_keys"] = duplicates

    return out

def _has_archive_comment_markers(comments: Iterable[str]) -> bool:
    text = "\n".join(comments)
    return TRIAGE_MARKER in text and ARCHIVE_MARKER in text

def normalize_gateway_archive_issue(issue: dict[str, Any], comments: Iterable[str]) -> GatewayArchiveInput:
    body = issue.get("body") or ""
    author = ((issue.get("user") or {}).get("login")) or issue.get("author_login") or ""
    labels = {x["name"] if isinstance(x, dict) else str(x) for x in issue.get("labels", [])}

    receipt = validate_gateway_receipt(body=body, author_login=author, comments=comments)
    if not receipt.valid:
        raise ValueError(f"invalid gateway receipt: {receipt.reason}")

    bad = FORBIDDEN_LABELS & labels
    if bad:
        raise ValueError(f"forbidden labels present: {sorted(bad)}")

    missing = REQUIRED_LABELS - labels
    if missing:
        raise ValueError(f"missing required archive labels: {sorted(missing)}")

    if not _has_archive_comment_markers(comments):
        raise ValueError("missing triage receipt-bearing archive markers")

    marker = extract_receipt_marker(body)
    intake = parse_intake_block_loose(body)

    if marker.get("requested_archive_kind") != "agent_declared_echo_archive":
        raise ValueError(f"unsupported archive kind: {marker.get('requested_archive_kind')}")

    if intake.get("archive_ready") is not True:
        raise ValueError("archive_ready must be true")

    return GatewayArchiveInput(
        issue_number=int(issue.get("number") or issue.get("issue_number")),
        issue_url=issue.get("html_url") or issue.get("display_url") or issue.get("url") or "",
        title=issue.get("title") or "",
        author_login=author,
        state=issue.get("state") or "",
        state_reason=issue.get("state_reason"),
        receipt_id=marker.get("receipt_id") or str(intake.get("gateway_receipt_id") or ""),
        gateway_commit=marker.get("gateway_commit") or str(intake.get("gateway_commit") or ""),
        route_detected=marker.get("route_detected") or "pure_echo",
        submission_type=marker.get("submission_type") or str(intake.get("submission_type") or ""),
        requested_archive_kind=marker.get("requested_archive_kind") or str(intake.get("requested_archive_kind") or ""),
        payload_sha256=marker.get("payload_sha256") or "",
        issued_at=marker.get("issued_at") or "",
        echo_type=str(intake.get("echo_type") or ""),
        agent_name_or_model=str(intake.get("agent_name_or_model") or ""),
        system_or_provider=str(intake.get("system_or_provider") or ""),
        agent_readback_sha256=str(intake.get("agent_readback_sha256") or ""),
        boundary_sentence=str(intake.get("boundary_sentence") or intake.get("canonical_boundary_sentence") or ""),
    )

def to_jsonable(value: GatewayArchiveInput) -> dict[str, Any]:
    return asdict(value)
