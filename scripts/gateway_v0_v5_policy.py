#!/usr/bin/env python3
"""V0-V5 fail-closed submission policy helpers.

V0–V5 verification submissions are fail-closed:
they either pass as agent_declared_verification_archive and become archive-ready,
or they are rejected before Issue creation.
There is no V0–V5 strict/intake fallback.
"""

V0_V5_LEVELS = {"V0", "V1", "V2", "V3", "V4", "V5"}

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
