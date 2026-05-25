#!/usr/bin/env python3
"""V0-V5 fail-closed submission policy helpers.

V0–V5 verification submissions are fail-closed:
they either pass as agent_declared_verification_archive and become archive-ready,
or they are rejected before Issue creation.
There is no V0–V5 strict/intake fallback.
"""
import re

V0_V5_LEVELS = {"V0", "V1", "V2", "V3", "V4", "V4+", "V5"}

# Canonical gateway receipt ID pattern: gar-YYYYMMDDTHHMMSSZ-xxxxxx
GATEWAY_RECEIPT_ID_PATTERN = re.compile(r"^gar-[A-Za-z0-9T._:-]{16,}$")

RENDER_API_ONLY_EFFECTIVE_AT = "2026-05-17T05:30:00Z"

V0_V5_WRONG_PATH_ERROR = (
    "WRONG_PATH_FOR_V0_V5: V0-V5 verification submissions must use "
    "requested_archive_kind=agent_declared_verification_archive, "
    "record_intent=auto_archive_candidate, "
    "evidence_requirement_mode=waived_for_v0_v5, "
    "and claim_gate.mode=template_for_v0_v5. "
    "Strict/intake fallback is rejected before Issue creation."
)


def extract_declared_level(payload):
    """Extract the declared verification level from a payload."""
    claim_gate = payload.get("claim_gate") or {}
    return (
        payload.get("agent_declared_protocol_level")
        or payload.get("verification_level_claimed")
        or claim_gate.get("allowed_protocol_level")
        or ""
    )


def is_v0_v5_level(level):
    """Check if a level is V0-V5."""
    return level in V0_V5_LEVELS


def is_verification_submission(payload):
    """Check if payload is a verification submission."""
    return payload.get("submission_type") in {
        "verification_report_candidate",
        "verification_echo_candidate",
    }


def is_v0_v5_verification_submission(payload):
    """Check if payload is a V0-V5 verification submission."""
    return (
        is_verification_submission(payload)
        and is_v0_v5_level(extract_declared_level(payload))
    )


def is_agent_declared_archive(payload):
    """Check if payload uses the agent-declared archive path."""
    return payload.get("requested_archive_kind") == "agent_declared_verification_archive"


def is_valid_v0_v5_agent_declared_path(payload):
    """Check if payload is a valid V0-V5 agent-declared archive submission."""
    return (
        payload.get("submission_type") == "verification_report_candidate"
        and payload.get("record_intent") == "auto_archive_candidate"
        and payload.get("requested_archive_kind") == "agent_declared_verification_archive"
        and payload.get("agent_declared_protocol_level") in V0_V5_LEVELS
        and payload.get("evidence_requirement_mode") == "waived_for_v0_v5"
        and (payload.get("claim_gate") or {}).get("mode") == "template_for_v0_v5"
    )


def should_reject_v0_v5_wrong_path(payload):
    """Determine if a V0-V5 payload should be rejected (fail-closed).

    Returns True if the payload is a V0-V5 verification submission
    that does NOT use the valid agent-declared archive path.
    """
    if not is_v0_v5_verification_submission(payload):
        return False

    if is_valid_v0_v5_agent_declared_path(payload):
        return False

    return True


def parse_bool(value):
    """Strictly parse a boolean-like value.

    Returns True / False for known encodings.
    Returns None for missing or malformed values.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "1", "yes"):
            return True
        if v in ("false", "0", "no"):
            return False
        return None
    return None

def is_valid_gateway_receipt_id(receipt_id):
    """Check if a gateway_receipt_id matches the canonical pattern."""
    if not receipt_id or not isinstance(receipt_id, str):
        return False
    return bool(GATEWAY_RECEIPT_ID_PATTERN.match(receipt_id.strip()))


def is_valid_gateway_receipt_block(intake):
    """Strict validation of a gateway receipt block.

    All fields must be present and correct for a record to be considered
    as created by the Render API gateway. This prevents hand-written Issues
    with fake receipts from being indexed.
    """
    receipt = intake.get("gateway_receipt_id", "")
    return (
        parse_bool(intake.get("created_by_gateway")) is True
        and parse_bool(intake.get("render_api_only")) is True
        and parse_bool(intake.get("server_validated")) is True
        and parse_bool(intake.get("server_rendered")) is True
        and intake.get("gateway_service") == "trinity-agent-issue-gateway"
        and is_valid_gateway_receipt_id(receipt)
    )


def has_valid_gateway_receipt_in_text(text):
    """Strict check for valid gateway receipt fields in raw issue body text.

    Used by triage to detect whether an Issue has a real Render API receipt,
    not just a hand-written gateway_receipt_id line.
    """
    return (
        bool(re.search(r"created_by_gateway\s*:\s*true", text, re.IGNORECASE))
        and bool(re.search(r"render_api_only\s*:\s*true", text, re.IGNORECASE))
        and bool(re.search(r"server_validated\s*:\s*true", text, re.IGNORECASE))
        and bool(re.search(r"server_rendered\s*:\s*true", text, re.IGNORECASE))
        and bool(re.search(r"gateway_service\s*:\s*trinity-agent-issue-gateway", text, re.IGNORECASE))
        and bool(re.search(r"gateway_receipt_id\s*:\s*gar-[A-Za-z0-9T._:-]{16,}", text, re.IGNORECASE))
    )
