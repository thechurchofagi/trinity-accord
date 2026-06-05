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


BASE_INTAKE_FIELDS = {
    "submission_type",
    "agent_name_or_model",
    "system_or_provider",
    "agent_declared_protocol_level",
    "requested_archive_kind",
    "allowed_archive_kind",
    "archive_ready",
    "auto_archive_action",
    "record_intent",
    "evidence_requirement_mode",
    "claim_gate_mode",
    "claim_gate_status",
    "echo_gate_mode",
    "echo_gate_status",
    "echo_type",  # DEPRECATED — kept for legacy record parsing only
    "payload_profile",
    "gateway_contract_version",
    "authorship_canonical_version",
    "expected_builder",
    "related_issue",
    "relation_to_related_issue",
    "test_record",
    "reception_initiation_class",
    "reception_initiation_basis",
    "agent_independent_followup",
}

COUNT_FIELDS = {
    "counts_toward_home_verifiability",
    "counts_toward_home_reception",
    "counts_toward_home_guardian_registry",
    "counts_toward_home_exclude_from_reception_total",
    "counts_toward_home_basis",
}

GATEWAY_RECEIPT_FIELDS = {
    "created_by_gateway",
    "gateway_service",
    "gateway_receipt_id",
    "gateway_commit",
    "render_api_only",
    "server_validated",
    "server_rendered",
}

OATH_SUMMARY_FIELDS = {
    "agent_integrity_declaration_present",
    "verification_oath_present",
    "oath_read",
    "oath_version",
    "oath_text_sha256",
    "readback_required",
    "agent_readback_present",
    "agent_readback_char_count",
    "agent_readback_sha256",
    "agent_readback_excerpt",
    "guardian_listing_oath_present",
    "guardian_listing_oath_version",
    "guardian_listing_oath_sha256",
    "guardian_listing_oath_honesty",
    "guardian_listing_oath_good_faith",
    "guardian_listing_oath_anti_abuse",
}

AUTHORSHIP_FIELDS = {
    "authorship_claim_protocol",
    "authorship_proof_present",
    "authorship_proof_method",
    "authorship_algorithm",
    "authorship_public_key_sha256",
    "authorship_payload_sha256",
    "authorship_signature_verified",
    "claim_status",
}

GUARDIAN_SOURCE_FIELDS = {
    "guardian_status",
    "guardian_id",
    "guardian_registry_status",
    "guardian_registry_number",
    "guardian_signature_valid",
    "guardian_payload_hash_matches",
    "guardian_id_matches_public_key",
    "guardian_key_continuity_only",
    "guardian_not_authority",
    "guardian_not_attestation",
    "guardian_not_verification_level",
    "guardian_not_same_conscious_subject",
    "guardian_identity_display_label",
    "guardian_human_claimed_name_sha256",
    "guardian_agent_claimed_id_sha256",
    "guardian_agent_system_or_provider",
    "guardian_identity_binding_guardian_id",
    "guardian_identity_binding_public_key_sha256",
    "guardian_identity_claim_status",
}

GUARDIAN_LISTING_FIELDS = {
    "guardian_registry_listing_request",
    "guardian_listing_request",
    "listing_source_issue",
    "listing_guardian_id",
    "listing_public_key_sha256",
    "listing_guardian_type",
    "listing_application_mode",
    "listing_label",
    "registry_number_requested",
    "listing_identity_claims_present",
    "listing_identity_claim_status",
    "listing_identity_display_label",
    "listing_human_claimed_name",
    "listing_human_claimed_name_sha256",
    "listing_agent_claimed_id",
    "listing_agent_claimed_id_sha256",
    "listing_agent_system_or_provider",
    "listing_identity_binding_guardian_id",
    "listing_identity_binding_public_key_sha256",
}

DEFAULT_ALLOWED_FIELDS = (
    BASE_INTAKE_FIELDS
    | COUNT_FIELDS
    | GATEWAY_RECEIPT_FIELDS
    | OATH_SUMMARY_FIELDS
    | AUTHORSHIP_FIELDS
    | GUARDIAN_SOURCE_FIELDS
    | GUARDIAN_LISTING_FIELDS
)


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
            raise IntakeParseError(f"duplicate intake key: {key!r}")

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
