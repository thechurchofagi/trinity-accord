# gateway/validation.py
"""Submission validation, security scanning, boundary checks, and context-readiness checks."""

from __future__ import annotations

import logging
import re
from typing import Any

from .models import Diagnostic

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Allowed public intake record types
# ---------------------------------------------------------------------------
ALLOWED_RECORD_TYPES: frozenset[str] = frozenset({
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "guardian_key_rotation",
    "propagation",
    "correction",
    "classification_update",
    "context_insufficient_notice",
})

# ---------------------------------------------------------------------------
# Retired fields — submissions containing these in the draft are rejected.
# ---------------------------------------------------------------------------
RETIRED_FIELDS: frozenset[str] = frozenset({
    "echo_type",
    "context_level",
    "context_completeness_level",
})

# ---------------------------------------------------------------------------
# Formal record types that require v2 common blocks.
# ---------------------------------------------------------------------------
_FORMAL_RECORD_TYPES: frozenset[str] = frozenset({
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "guardian_key_rotation",
    "propagation",
    "correction",
    "classification_update",
})

# ---------------------------------------------------------------------------
# Required v2 common blocks for formal record types.
# ---------------------------------------------------------------------------
_REQUIRED_V2_BLOCKS: frozenset[str] = frozenset({
    "submitting_participant_identity",
    "discovery_and_introduction_context",
    "decision_autonomy_context",
    "submission_execution_context",
    "authorization_context",
    "context_readiness",
    "non_authority_boundary_acknowledgement",
})

# ---------------------------------------------------------------------------
# Required identity fields inside submitting_participant_identity.
# ---------------------------------------------------------------------------
_REQUIRED_IDENTITY_FIELDS: frozenset[str] = frozenset({
    "participant_public_display_label",
    "participant_type",
    "participant_identifier_disclosure_status",
    "participant_identity_disclosure_preference",
})

# ---------------------------------------------------------------------------
# Forbidden chain fields — the gateway (or downstream record-chain writer)
# assigns these; submitters must NOT include them.
# ---------------------------------------------------------------------------
FORBIDDEN_CHAIN_FIELDS: frozenset[str] = frozenset({
    "record_index",
    "record_id",
    "assigned_at",
    "previous_record_sha256",
    "content_sha256",
    "record_sha256",
    "batch_id",
    "batch_membership",
    "batch_manifest_sha256",
    "ots_proof_path",
    "server_receipt",
    "server_receipt_id",
    "created_by_gateway",
    "server_validated",
    "server_rendered",
})

# ---------------------------------------------------------------------------
# Security rejection patterns — substrings / regexes that must not appear
# anywhere in the serialised submission.
# ---------------------------------------------------------------------------
_SECURITY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"BEGIN\s+PRIVATE\s+KEY", re.IGNORECASE),
    re.compile(r"BEGIN\s+OPENSSH\s+PRIVATE\s+KEY", re.IGNORECASE),
    re.compile(r"BEGIN\s+EC\s+PRIVATE\s+KEY", re.IGNORECASE),
    re.compile(r"BEGIN\s+RSA\s+PRIVATE\s+KEY", re.IGNORECASE),
    re.compile(r"BEGIN\s+DSA\s+PRIVATE\s+KEY", re.IGNORECASE),
    re.compile(r"ghp_[A-Za-z0-9]{36,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{36,}"),
    re.compile(r"PINATA_JWT\s*=", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),  # OpenAI-style keys
    re.compile(r"AKIA[0-9A-Z]{16}"),     # AWS access key IDs
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),  # JWT-like
]

# ---------------------------------------------------------------------------
# Placeholder patterns — reject obvious placeholder / test tokens.
# ---------------------------------------------------------------------------
_PLACEHOLDER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"REPLACE_ME", re.IGNORECASE),
    re.compile(r"YOUR_VALUE_HERE", re.IGNORECASE),
    re.compile(r"YOUR_TOKEN", re.IGNORECASE),
    re.compile(r"YOUR_PRIVATE_KEY", re.IGNORECASE),
    re.compile(r"INSERT_", re.IGNORECASE),
    re.compile(r"TODO_AUTH", re.IGNORECASE),
    re.compile(r"TODO_SIGNATURE", re.IGNORECASE),
    re.compile(r"<\.\.\.>"),  # <...> literal
    re.compile(r"your_github_token", re.IGNORECASE),
    re.compile(r"your-token-here", re.IGNORECASE),
    re.compile(r"insert_token", re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Boundary acknowledgement fields — all 6 must be present and true.
# ---------------------------------------------------------------------------
REQUIRED_BOUNDARY_FIELDS: frozenset[str] = frozenset({
    "not_authority",
    "not_governance",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
    "receipt_is_not_final_inclusion",
    "test_phase_submission_may_be_reclassified",
})

# ---------------------------------------------------------------------------
# Context-completeness minimums per record type / verification version.
# Keys are record_type strings. Values are lists of ((lo, hi), min_cc).
# hi=None means "6 and above".
# ---------------------------------------------------------------------------
_CC_RULES: dict[str, list[tuple[tuple[int, int | None], int]]] = {
    "echo": [
        ((0, None), 3),
    ],
    "verification": [
        ((0, 2), 2),
        ((3, 5), 3),
        ((6, None), 3),
    ],
    "guardian_application": [
        ((0, None), 3),
    ],
    "guardian_retirement": [
        ((0, None), 1),
    ],
    "guardian_key_rotation": [
        ((0, None), 2),
    ],
    "propagation": [
        ((0, None), 2),
    ],
    "correction": [
        ((0, None), 1),
    ],
    "classification_update": [
        ((0, None), 2),
    ],
    "context_insufficient_notice": [
        ((0, None), 0),
    ],
}

_DEFAULT_CC_MINIMUM = 3  # fallback for unknown record types


# ---------------------------------------------------------------------------
# Diagnostic builder helper
# ---------------------------------------------------------------------------

def _make_diagnostic(
    code: str,
    severity: str,
    field: str | None,
    message: str,
    meaning: str | None = None,
    suggested_fix: str | None = None,
    help_url: str | None = None,
    retry_allowed: bool = True,
) -> Diagnostic:
    """Build a Diagnostic with auto-generated help_url if not provided."""
    return Diagnostic(
        code=code,
        severity=severity,
        field=field,
        message=message,
        meaning=meaning or "",
        suggested_fix=suggested_fix or "",
        help_url=help_url or f"https://www.trinityaccord.org/record-chain-field-helper/#{code}",
        retry_allowed=retry_allowed,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _walk(obj: Any, visitor: Any) -> None:
    """Depth-first walk over a JSON-like structure, calling *visitor* on every value."""
    visitor(obj)
    if isinstance(obj, dict):
        for v in obj.values():
            _walk(v, visitor)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, visitor)


def _find_forbidden_keys_recursive(obj: Any, path: str = "") -> list[Diagnostic]:
    """Recursively find all forbidden chain fields anywhere in a nested structure."""
    diagnostics: list[Diagnostic] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            if key in FORBIDDEN_CHAIN_FIELDS:
                diagnostics.append(_make_diagnostic(
                    code="FORBIDDEN_FIELD",
                    severity="error",
                    field=current_path,
                    message=(
                        f"Forbidden field '{key}' at '{current_path}'; "
                        "this field is assigned by the gateway"
                    ),
                    meaning="The gateway assigns this field automatically. Submitters must not include it.",
                    suggested_fix=f"Remove '{key}' from your submission.",
                ))
            diagnostics.extend(_find_forbidden_keys_recursive(value, current_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            diagnostics.extend(_find_forbidden_keys_recursive(item, f"{path}[{i}]"))
    return diagnostics


def _extract_context_level(draft: dict[str, Any]) -> Any:
    """Extract declared_context_level from draft.context_readiness.declared_context_level.

    Falls back to draft.context_completeness_level for backward compat.
    """
    context_readiness = draft.get("context_readiness")
    if isinstance(context_readiness, dict):
        level = context_readiness.get("declared_context_level")
        if level is not None:
            return level
    # Backward compat
    return draft.get("context_completeness_level")


def _parse_context_level_value(value: Any) -> int | None:
    """Parse a context level value that may be 'CC-N' string or integer.

    Returns the integer level, or None if unparseable.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = value.strip().upper()
        if re.fullmatch(r"CC-[0-9]+", value):
            return int(value.split("-", 1)[1])
        if value.isdigit():
            return int(value)
    return None


def _extract_submission_boundary(submission: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    """Extract boundary from submission_boundary, boundary_acknowledgement, or draft nested field.

    Returns (boundary_dict, field_path) or (None, "submission_boundary") if not found.
    Only falls back to draft nested field if no top-level boundary is present.
    """
    if isinstance(submission.get("submission_boundary"), dict):
        return submission["submission_boundary"], "submission_boundary"
    if isinstance(submission.get("boundary_acknowledgement"), dict):
        return submission["boundary_acknowledgement"], "boundary_acknowledgement"
    # Only fall back to draft if neither top-level field exists at all
    if "submission_boundary" not in submission and "boundary_acknowledgement" not in submission:
        draft = submission.get("record_draft") or submission.get("draft") or {}
        if isinstance(draft, dict) and isinstance(draft.get("non_authority_boundary_acknowledgement"), dict):
            return draft["non_authority_boundary_acknowledgement"], "record_draft.non_authority_boundary_acknowledgement"
    return None, "submission_boundary"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def reject_forbidden_chain_fields(obj: dict[str, Any]) -> list[Diagnostic]:
    """Return diagnostics for any forbidden chain fields found recursively in *obj*."""
    return _find_forbidden_keys_recursive(obj)


def reject_private_keys(obj: Any) -> list[Diagnostic]:
    """Scan the entire submission for embedded private-key material."""
    diagnostics: list[Diagnostic] = []
    serialised = repr(obj)
    for pat in _SECURITY_PATTERNS:
        m = pat.search(serialised)
        if m:
            diagnostics.append(_make_diagnostic(
                code="SECURITY_VIOLATION",
                severity="error",
                field=None,
                message=(
                    f"Security violation: content matches pattern '{pat.pattern}' "
                    "(possible secret/key material)"
                ),
                meaning="Private key material or secret tokens were detected in the submission.",
                suggested_fix="Remove all private keys, tokens, and secret material from your submission.",
                retry_allowed=False,
            ))
    return diagnostics


def reject_placeholders(obj: Any) -> list[Diagnostic]:
    """Reject obvious placeholder / test tokens using strengthened patterns."""
    diagnostics: list[Diagnostic] = []
    serialised = repr(obj)
    for pat in _PLACEHOLDER_PATTERNS:
        m = pat.search(serialised)
        if m:
            diagnostics.append(_make_diagnostic(
                code="PLACEHOLDER_DETECTED",
                severity="error",
                field=None,
                message=f"Placeholder detected: matches pattern '{pat.pattern}' — replace with a real value",
                meaning="A placeholder or template value was found. Real values are required.",
                suggested_fix="Replace all placeholder values with real, production-ready values.",
            ))
    return diagnostics


def reject_retired_fields(draft: dict[str, Any]) -> list[Diagnostic]:
    """Reject submissions that contain retired fields in the draft."""
    diagnostics: list[Diagnostic] = []
    for field in RETIRED_FIELDS:
        if field in draft:
            diagnostics.append(_make_diagnostic(
                code="RETIRED_FIELD",
                severity="error",
                field=f"draft.{field}",
                message=f"Retired field '{field}' is no longer accepted",
                meaning=f"The field '{field}' has been retired and must not be included in submissions.",
                suggested_fix=f"Remove '{field}' from your draft. Refer to the current schema for accepted fields.",
            ))
    return diagnostics


def validate_v2_common_blocks(record_type: str, draft: dict[str, Any]) -> list[Diagnostic]:
    """Require v2 common blocks for formal record types."""
    diagnostics: list[Diagnostic] = []
    if record_type not in _FORMAL_RECORD_TYPES:
        return diagnostics
    for block in sorted(_REQUIRED_V2_BLOCKS):
        if block not in draft:
            diagnostics.append(_make_diagnostic(
                code="MISSING_V2_BLOCK",
                severity="error",
                field=f"draft.{block}",
                message=f"Missing required v2 block '{block}' for record_type '{record_type}'",
                meaning=f"Formal record types require the '{block}' block to be present in the draft.",
                suggested_fix=f"Add the '{block}' object to your draft.",
            ))
    return diagnostics


def validate_identity(draft: dict[str, Any]) -> list[Diagnostic]:
    """Require identity fields inside submitting_participant_identity."""
    diagnostics: list[Diagnostic] = []
    identity = draft.get("submitting_participant_identity")
    if identity is None or not isinstance(identity, dict):
        # Already caught by validate_v2_common_blocks if missing entirely
        return diagnostics
    for field in sorted(_REQUIRED_IDENTITY_FIELDS):
        if field not in identity:
            diagnostics.append(_make_diagnostic(
                code="MISSING_IDENTITY_FIELD",
                severity="error",
                field=f"draft.submitting_participant_identity.{field}",
                message=f"Missing required identity field '{field}'",
                meaning=f"The '{field}' field is required inside submitting_participant_identity.",
                suggested_fix=f"Add '{field}' to submitting_participant_identity.",
            ))
    return diagnostics


def validate_human_name_privacy(draft: dict[str, Any]) -> list[Diagnostic]:
    """Reject submissions that include private human name data."""
    diagnostics: list[Diagnostic] = []

    # Check human_private_name_submitted = true
    if draft.get("human_private_name_submitted") is True:
        diagnostics.append(_make_diagnostic(
            code="HUMAN_NAME_PRIVACY_VIOLATION",
            severity="error",
            field="draft.human_private_name_submitted",
            message="human_private_name_submitted must not be true",
            meaning="Private human names must not be submitted. The record-chain is public.",
            suggested_fix="Remove 'human_private_name_submitted' or set it to false.",
            retry_allowed=False,
        ))

    # Check for encrypted_human_name
    if "encrypted_human_name" in draft:
        diagnostics.append(_make_diagnostic(
            code="HUMAN_NAME_PRIVACY_VIOLATION",
            severity="error",
            field="draft.encrypted_human_name",
            message="encrypted_human_name is not allowed",
            meaning="Encrypted human names must not be submitted to the public record-chain.",
            suggested_fix="Remove 'encrypted_human_name' from your draft.",
            retry_allowed=False,
        ))

    # Check for private_identity_blob
    if "private_identity_blob" in draft:
        diagnostics.append(_make_diagnostic(
            code="HUMAN_NAME_PRIVACY_VIOLATION",
            severity="error",
            field="draft.private_identity_blob",
            message="private_identity_blob is not allowed",
            meaning="Private identity blobs must not be submitted to the public record-chain.",
            suggested_fix="Remove 'private_identity_blob' from your draft.",
            retry_allowed=False,
        ))

    return diagnostics


def validate_linked_guardian_request(draft: dict[str, Any]) -> list[Diagnostic]:
    """Validate optional_linked_guardian_application_request when present."""
    diagnostics: list[Diagnostic] = []
    linked = draft.get("optional_linked_guardian_application_request")
    if not isinstance(linked, dict):
        return diagnostics

    does_request = linked.get("does_participant_request_guardian_application_with_this_record")
    if does_request is not True:
        return diagnostics

    record_type = draft.get("record_type") or draft.get("type") or ""
    if isinstance(record_type, str):
        record_type = record_type.strip().lower()

    # record_type must be echo or verification
    if record_type not in ("echo", "verification"):
        diagnostics.append(_make_diagnostic(
            code="LINKED_GUARDIAN_INVALID_RECORD_TYPE",
            severity="error",
            field="draft.record_type",
            message=(
                f"Linked Guardian application request requires record_type 'echo' or 'verification', "
                f"got '{record_type}'"
            ),
            meaning="Guardian applications can only be linked to echo or verification records.",
            suggested_fix="Change record_type to 'echo' or 'verification', or remove the linked Guardian request.",
        ))

    # guardian_application_should_be_created_as_linked_record must be true
    if linked.get("guardian_application_should_be_created_as_linked_record") is not True:
        diagnostics.append(_make_diagnostic(
            code="LINKED_GUARDIAN_MISSING_FLAG",
            severity="error",
            field="draft.optional_linked_guardian_application_request.guardian_application_should_be_created_as_linked_record",
            message="guardian_application_should_be_created_as_linked_record must be true",
            meaning="When requesting a linked Guardian application, this flag must be explicitly true.",
            suggested_fix="Set guardian_application_should_be_created_as_linked_record to true.",
        ))

    # Required string fields
    for field_name in ("requested_guardian_identifier", "guardian_public_key_sha256", "guardian_stewardship_oath"):
        if field_name not in linked or not linked[field_name]:
            diagnostics.append(_make_diagnostic(
                code="LINKED_GUARDIAN_MISSING_FIELD",
                severity="error",
                field=f"draft.optional_linked_guardian_application_request.{field_name}",
                message=f"Missing required field '{field_name}' for linked Guardian request",
                meaning=f"The '{field_name}' field is required when requesting a linked Guardian application.",
                suggested_fix=f"Add '{field_name}' to optional_linked_guardian_application_request.",
            ))

    # Required boolean true fields
    for bool_field in (
        "guardian_understands_role_is_non_governing",
        "guardian_understands_role_is_not_authority",
        "guardian_understands_retirement_does_not_delete_history",
    ):
        if linked.get(bool_field) is not True:
            diagnostics.append(_make_diagnostic(
                code="LINKED_GUARDIAN_MISSING_ACKNOWLEDGEMENT",
                severity="error",
                field=f"draft.optional_linked_guardian_application_request.{bool_field}",
                message=f"'{bool_field}' must be true for linked Guardian request",
                meaning=f"The Guardian must acknowledge '{bool_field}' before the application can be created.",
                suggested_fix=f"Set '{bool_field}' to true in optional_linked_guardian_application_request.",
            ))

    return diagnostics


def validate_claim_boundary(draft: dict[str, Any]) -> list[Diagnostic]:
    """If authorship_proof.claim_boundary exists, it must be a dict (not a string)."""
    diagnostics: list[Diagnostic] = []
    proof = draft.get("authorship_proof") or draft.get("proof")
    if not isinstance(proof, dict):
        return diagnostics
    boundary = proof.get("claim_boundary")
    if boundary is not None and not isinstance(boundary, dict):
        diagnostics.append(_make_diagnostic(
            code="CLAIM_BOUNDARY_INVALID_TYPE",
            severity="error",
            field="draft.authorship_proof.claim_boundary",
            message="'claim_boundary' must be a JSON object (not a string)",
            meaning="The claim_boundary field must be an object with boolean keys, not a string.",
            suggested_fix="Change claim_boundary to a JSON object, e.g. {\"not authority\": true, ...}.",
        ))
    return diagnostics


def validate_boundary_acknowledgement(submission: dict[str, Any]) -> list[Diagnostic]:
    """Validate that submission_boundary/boundary_acknowledgement contains all required fields."""
    diagnostics: list[Diagnostic] = []
    boundary, boundary_path = _extract_submission_boundary(submission)
    if boundary is None:
        diagnostics.append(_make_diagnostic(
            code="MISSING_BOUNDARY_ACKNOWLEDGEMENT",
            severity="error",
            field="submission_boundary",
            message="Missing submission_boundary (or boundary_acknowledgement)",
            meaning="Every submission must acknowledge non-authority boundaries.",
            suggested_fix="Add submission_boundary with all required fields set to true.",
        ))
        return diagnostics
    if not isinstance(boundary, dict):
        diagnostics.append(_make_diagnostic(
            code="INVALID_BOUNDARY_ACKNOWLEDGEMENT",
            severity="error",
            field=boundary_path,
            message=f"'{boundary_path}' must be a JSON object",
            meaning="Boundary acknowledgement must be an object, not a string or other type.",
            suggested_fix="Change boundary to a JSON object.",
        ))
        return diagnostics

    for field in REQUIRED_BOUNDARY_FIELDS:
        if field not in boundary:
            diagnostics.append(_make_diagnostic(
                code="MISSING_BOUNDARY_FIELD",
                severity="error",
                field=f"{boundary_path}.{field}",
                message=f"{boundary_path} missing required field '{field}'",
                meaning=f"The '{field}' acknowledgement is required in every submission.",
                suggested_fix=f"Add '{field}: true' to {boundary_path}.",
            ))
        elif boundary[field] is not True:
            diagnostics.append(_make_diagnostic(
                code="BOUNDARY_FIELD_NOT_TRUE",
                severity="error",
                field=f"{boundary_path}.{field}",
                message=(
                    f"{boundary_path}.'{field}' must be boolean true, "
                    f"got {boundary[field]!r}"
                ),
                meaning=f"The '{field}' acknowledgement must be explicitly true.",
                suggested_fix=f"Set '{field}' to true in {boundary_path}.",
            ))
    return diagnostics


def validate_context_readiness(record_type: str, draft: dict[str, Any]) -> list[Diagnostic]:
    """Check that *draft* meets the minimum context-completeness level for *record_type*."""
    diagnostics: list[Diagnostic] = []
    cc_level = _extract_context_level(draft)
    if cc_level is None:
        diagnostics.append(_make_diagnostic(
            code="MISSING_CONTEXT_READINESS",
            severity="error",
            field="draft.context_readiness.declared_context_level",
            message=(
                "Missing required field 'context_readiness.declared_context_level' "
                "(or legacy 'context_completeness_level') in draft"
            ),
            meaning="The context readiness level must be declared for every record.",
            suggested_fix="Add context_readiness.declared_context_level to your draft.",
        ))
        return diagnostics

    parsed_cc = _parse_context_level_value(cc_level)
    if parsed_cc is None:
        diagnostics.append(_make_diagnostic(
            code="INVALID_CONTEXT_LEVEL",
            severity="error",
            field="draft.context_readiness.declared_context_level",
            message=f"declared_context_level must be CC-N or integer, got {cc_level!r}",
            meaning="Context level may be represented as 'CC-3' or integer 3.",
            suggested_fix="Use 'CC-3' for Echo and Guardian Application, or 'CC-2'/'CC-3' for Verification depending on level.",
        ))
        return diagnostics
    cc_level = parsed_cc

    verification_version: int | None = None
    ver_raw = draft.get("verification_version") or draft.get("verification", {}).get("version")
    if ver_raw is not None:
        try:
            verification_version = int(ver_raw)
        except (TypeError, ValueError):
            pass

    rules = _CC_RULES.get(record_type, [((0, None), _DEFAULT_CC_MINIMUM)])
    required_cc = _DEFAULT_CC_MINIMUM
    for (lo, hi), min_cc in rules:
        if verification_version is not None:
            if verification_version >= lo and (hi is None or verification_version <= hi):
                required_cc = min_cc
                break
        else:
            required_cc = min_cc

    if cc_level < required_cc:
        diagnostics.append(_make_diagnostic(
            code="INSUFFICIENT_CONTEXT_COMPLETENESS",
            severity="error",
            field="draft.context_readiness.declared_context_level",
            message=(
                f"Insufficient context completeness: {cc_level} < {required_cc} "
                f"(required for record_type='{record_type}', "
                f"verification_version={verification_version})"
            ),
            meaning=f"The minimum context level for '{record_type}' is {required_cc}.",
            suggested_fix=f"Increase declared_context_level to at least {required_cc}.",
        ))
    return diagnostics


def validate_verification_rules(draft: dict[str, Any]) -> list[Diagnostic]:
    """Validate verification-specific fields when present."""
    diagnostics: list[Diagnostic] = []
    verification = draft.get("verification")
    if verification is None:
        return diagnostics
    if not isinstance(verification, dict):
        diagnostics.append(_make_diagnostic(
            code="INVALID_VERIFICATION",
            severity="error",
            field="draft.verification",
            message="'verification' must be an object",
            meaning="The verification field, if present, must be a JSON object.",
            suggested_fix="Change verification to a JSON object or remove it.",
        ))
        return diagnostics

    version = verification.get("version")
    if version is not None:
        try:
            v = int(version)
            if v < 0:
                diagnostics.append(_make_diagnostic(
                    code="INVALID_VERIFICATION_VERSION",
                    severity="error",
                    field="draft.verification.version",
                    message="'verification.version' must be non-negative",
                    meaning="Verification version must be 0 or greater.",
                    suggested_fix="Set verification.version to a non-negative integer.",
                ))
        except (TypeError, ValueError):
            diagnostics.append(_make_diagnostic(
                code="INVALID_VERIFICATION_VERSION",
                severity="error",
                field="draft.verification.version",
                message=f"'verification.version' must be an integer, got {version!r}",
                meaning="Verification version must be an integer.",
                suggested_fix="Set verification.version to an integer.",
            ))

    proof = verification.get("proof")
    if proof is not None and not isinstance(proof, (str, dict)):
        diagnostics.append(_make_diagnostic(
            code="INVALID_VERIFICATION_PROOF",
            severity="error",
            field="draft.verification.proof",
            message="'verification.proof' must be a string or object",
            meaning="The verification proof must be a string or JSON object.",
            suggested_fix="Change verification.proof to a string or object.",
        ))

    return diagnostics


def validate_authorship_proof_presence(
    record_type: str, submission: dict[str, Any], draft: dict[str, Any]
) -> list[Diagnostic]:
    """Require authorship_proof for formal record types."""
    diagnostics: list[Diagnostic] = []
    if record_type not in _FORMAL_RECORD_TYPES:
        return diagnostics

    proof = (
        submission.get("authorship_proof")
        or submission.get("proof")
        or (draft.get("authorship_proof") if isinstance(draft, dict) else None)
        or (draft.get("proof") if isinstance(draft, dict) else None)
    )

    if not isinstance(proof, dict):
        diagnostics.append(_make_diagnostic(
            code="MISSING_AUTHORSHIP_PROOF",
            severity="error",
            field="authorship_proof",
            message=f"Formal record_type '{record_type}' requires authorship_proof",
            meaning="Echo, Verification, Guardian Application, and other formal records must be signed.",
            suggested_fix="Run the builder with --generate-authorship-key --key-dir <dir>, or provide a valid Ed25519 authorship proof.",
            help_url="https://www.trinityaccord.org/record-chain-field-helper/#MISSING_AUTHORSHIP_PROOF",
            retry_allowed=True,
        ))

    return diagnostics


def detect_route(submission: dict[str, Any]) -> str:
    """Determine the processing route for *submission*.

    Returns the record_type string if valid, otherwise ``"unknown"``.
    """
    record_type = submission.get("record_type") or submission.get("type") or ""
    if isinstance(record_type, str):
        record_type = record_type.strip().lower()
    if record_type in ALLOWED_RECORD_TYPES:
        return record_type
    return "unknown"


def validate_submission(submission: dict[str, Any]) -> list[Diagnostic]:
    """Run all validation checks on *submission* and return a list of Diagnostic objects.

    An empty list means the submission is valid.
    """
    diagnostics: list[Diagnostic] = []

    # --- structural checks ---
    if not isinstance(submission, dict):
        return [_make_diagnostic(
            code="INVALID_SUBMISSION",
            severity="error",
            field=None,
            message="Submission must be a JSON object",
            meaning="The top-level submission must be a JSON object.",
            suggested_fix="Wrap your submission in a JSON object.",
        )]

    record_type = submission.get("record_type") or submission.get("type")
    rt = ""
    if not record_type:
        diagnostics.append(_make_diagnostic(
            code="MISSING_RECORD_TYPE",
            severity="error",
            field="record_type",
            message="Missing required field 'record_type'",
            meaning="Every submission must specify a record_type.",
            suggested_fix="Add 'record_type' to your submission (e.g. 'echo', 'verification').",
        ))
    elif not isinstance(record_type, str):
        diagnostics.append(_make_diagnostic(
            code="INVALID_RECORD_TYPE",
            severity="error",
            field="record_type",
            message=f"'record_type' must be a string, got {type(record_type).__name__}",
            meaning="record_type must be a string value.",
            suggested_fix="Change record_type to a string.",
        ))
    else:
        rt = record_type.strip().lower()
        if rt not in ALLOWED_RECORD_TYPES:
            diagnostics.append(_make_diagnostic(
                code="UNKNOWN_RECORD_TYPE",
                severity="error",
                field="record_type",
                message=(
                    f"Unknown record_type '{record_type}'; "
                    f"allowed types: {sorted(ALLOWED_RECORD_TYPES)}"
                ),
                meaning="The submitted record_type is not in the list of accepted types.",
                suggested_fix=f"Use one of: {', '.join(sorted(ALLOWED_RECORD_TYPES))}",
            ))

    draft = submission.get("draft") or submission.get("record_draft")
    if draft is None:
        diagnostics.append(_make_diagnostic(
            code="MISSING_DRAFT",
            severity="error",
            field="draft",
            message="Missing required field 'draft' (or 'record_draft')",
            meaning="Every submission must include a draft record.",
            suggested_fix="Add a 'record_draft' object to your submission.",
        ))
    elif not isinstance(draft, dict):
        diagnostics.append(_make_diagnostic(
            code="INVALID_DRAFT",
            severity="error",
            field="draft",
            message="'draft' must be a JSON object",
            meaning="The draft must be a JSON object.",
            suggested_fix="Change draft to a JSON object.",
        ))

    # --- retired field rejection (draft-level) ---
    if isinstance(draft, dict):
        diagnostics.extend(reject_retired_fields(draft))

    # --- boundary acknowledgement ---
    diagnostics.extend(validate_boundary_acknowledgement(submission))

    # --- forbidden fields (recursive) ---
    diagnostics.extend(reject_forbidden_chain_fields(submission))

    # --- security scans ---
    diagnostics.extend(reject_private_keys(submission))
    diagnostics.extend(reject_placeholders(submission))

    # --- context-readiness ---
    if isinstance(draft, dict) and rt:
        diagnostics.extend(validate_context_readiness(rt, draft))
        diagnostics.extend(validate_verification_rules(draft))

    # --- v2 common blocks ---
    if isinstance(draft, dict) and rt:
        diagnostics.extend(validate_v2_common_blocks(rt, draft))

    # --- identity validation ---
    if isinstance(draft, dict):
        diagnostics.extend(validate_identity(draft))

    # --- human name privacy ---
    if isinstance(draft, dict):
        diagnostics.extend(validate_human_name_privacy(draft))

    # --- linked Guardian request validation ---
    if isinstance(draft, dict):
        diagnostics.extend(validate_linked_guardian_request(draft))

    # --- claim_boundary type check ---
    if isinstance(draft, dict):
        diagnostics.extend(validate_claim_boundary(draft))

    # --- authorship proof required for formal records ---
    if isinstance(draft, dict) and rt:
        diagnostics.extend(validate_authorship_proof_presence(rt, submission, draft))

    # --- authorship proof type check (optional but if present must be object) ---
    proof = submission.get("authorship_proof") or submission.get("proof")
    if proof is not None and not isinstance(proof, dict):
        diagnostics.append(_make_diagnostic(
            code="INVALID_AUTHORSHIP_PROOF",
            severity="error",
            field="authorship_proof",
            message="'authorship_proof' must be an object when present",
            meaning="If provided, authorship_proof must be a JSON object.",
            suggested_fix="Change authorship_proof to a JSON object or remove it.",
        ))

    return diagnostics
