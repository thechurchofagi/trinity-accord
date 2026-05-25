#!/usr/bin/env python3
"""Shared Gateway trinity-issue-intake parser.

All Gateway archive/index paths must use this file instead of scanning arbitrary
Issue Markdown text.
"""

from __future__ import annotations

import re


class IntakeParseError(ValueError):
    pass


class BoolParseError(ValueError):
    pass


DEFAULT_ALLOWED_FIELDS = {
    "agent_name_or_model",
    "system_or_provider",
    "agent_declared_protocol_level",
    "requested_archive_kind",
    "archive_ready",
    "auto_archive_action",
    "record_intent",
    "evidence_requirement_mode",
    "claim_gate_mode",
    "claim_gate_status",
    "counts_toward_home_verifiability",
    "counts_toward_home_reception",
    "test_record",
    "reception_initiation_class",
    "reception_initiation_basis",
    "agent_independent_followup",

    # Gateway receipt fields
    "created_by_gateway",
    "gateway_service",
    "gateway_receipt_id",
    "gateway_commit",
    "render_api_only",
    "server_validated",
    "server_rendered",

    # Oath summary fields
    "verification_oath_present",
    "oath_read",
    "oath_version",
    "oath_text_sha256",
    "readback_required",
    "agent_readback_present",
    "agent_readback_char_count",
    "agent_readback_sha256",

    # Authorship fields
    "authorship_claim_protocol",
    "authorship_proof_present",
    "authorship_proof_method",
    "authorship_algorithm",
    "authorship_public_key_sha256",
    "authorship_payload_sha256",
    "authorship_signature_verified",
    "claim_status",

    # Echo / Guardian fields
    "echo_type",
    "guardian_registry_listing_request",
    "guardian_listing_request",
}


def find_intake_blocks(body: str) -> list[str]:
    if not body:
        return []
    return re.findall(r"```trinity-issue-intake\s*\n(.*?)```", body, re.DOTALL | re.I)


def parse_intake_block(
    body: str,
    *,
    required: bool = False,
    allowed_fields: set[str] | None = None,
) -> dict[str, str] | None:
    allowed = allowed_fields or DEFAULT_ALLOWED_FIELDS
    matches = find_intake_blocks(body)

    if not matches:
        if required:
            raise IntakeParseError("missing trinity-issue-intake block")
        return None

    if len(matches) > 1:
        raise IntakeParseError(f"multiple trinity-issue-intake blocks found: {len(matches)}")

    fields: dict[str, str] = {}
    seen: set[str] = set()

    for line_no, raw_line in enumerate(matches[0].strip().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        if ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if key not in allowed:
            continue

        if key in seen:
            raise IntakeParseError(f"duplicate intake key {key!r} at line {line_no}")

        seen.add(key)
        fields[key] = value

    if not fields:
        if required:
            raise IntakeParseError("trinity-issue-intake block contains no recognized fields")
        return None

    return fields


def parse_bool(value: str | None, *, field: str = "unknown", issue_number: int | None = None) -> bool | None:
    if value is None:
        return None

    v = value.strip().lower()
    if v in {"true", "1", "yes"}:
        return True
    if v in {"false", "0", "no"}:
        return False

    issue = f" issue #{issue_number}" if issue_number is not None else ""
    raise BoolParseError(f"Invalid boolean{issue}: {field}={value!r}")
