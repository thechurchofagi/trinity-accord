# gateway/validation.py
"""Submission validation, security scanning, boundary checks, and context-readiness checks."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import unicodedata
from typing import Any

from .models import Diagnostic
from .authorship import verify_authorship_proof_submission
from .security import (
    find_private_human_identity_hits,
    find_secret_hits,
    normalize_oath_text,
    sha256_text,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Oath policy hash canonicalization
# ---------------------------------------------------------------------------

OATH_POLICY_HASH_METADATA_KEYS: frozenset[str] = frozenset({
    "oath_policy_sha256",
    "oath_policy_sha256_semantics",
    "canonical_oath_text_hash_is_record_type_specific",
})


def canonicalize_oath_policy_for_hash(policy: dict[str, Any]) -> dict[str, Any]:
    """Return the policy object that is actually covered by oath_policy_sha256.

    The public API file may contain self-describing metadata fields. Those fields
    must not be part of the hash domain, otherwise the file attempts to hash
    itself and builder/Gateway hashes drift.
    """
    return {
        key: value
        for key, value in policy.items()
        if key not in OATH_POLICY_HASH_METADATA_KEYS
    }


def compute_oath_policy_sha256(policy: dict[str, Any]) -> str:
    """SHA-256 of canonical JSON for the oath policy hash domain."""
    material = canonicalize_oath_policy_for_hash(policy)
    canonical = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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


_AUTHORIZATION_SCOPE_BY_RECORD_TYPE: dict[str, str] = {
    "echo": "create_echo_record",
    "verification": "create_verification_record",
    "guardian_application": "create_guardian_application_record",
    "guardian_retirement": "create_guardian_retirement_record",
    "guardian_key_rotation": "create_guardian_key_rotation_record",
    "propagation": "create_propagation_record",
    "correction": "create_correction_record",
    "classification_update": "create_classification_update_record",
    "context_insufficient_notice": "create_context_insufficient_notice_record",
}

# ---------------------------------------------------------------------------
# Record-type separation hardening
# ---------------------------------------------------------------------------

_GUARDIAN_APPLICATION_ONLY_KEYS: frozenset[str] = frozenset({
    "guardian_application_content",
    "guardian_public_key_sha256",
    "guardian_stewardship_oath",
    "requested_guardian_identifier",
    "guardian_application_statement",
    "guardian_application_reason",
    "guardian_commitment",
    "active_guardian_status_claim",
    "no_active_guardian_status_claim",
    "optional_linked_guardian_application_request",
})

_ECHO_ONLY_KEYS: frozenset[str] = frozenset({
    "echo_content",
})

_VERIFICATION_ONLY_KEYS: frozenset[str] = frozenset({
    "verification_content",
    "verification",
    "verification_version",
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
    "receipt_is_intake_only",
    "later_records_may_reclassify_or_correct_this_record",
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

MIN_CONTEXT_LEVEL = 0
MAX_CONTEXT_LEVEL = 5


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


def _find_keys_recursive(obj: Any, keys: frozenset[str], path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            if key in keys:
                found.append(current_path)
            found.extend(_find_keys_recursive(value, keys, current_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            found.extend(_find_keys_recursive(item, keys, f"{path}[{i}]"))
    return found


def validate_record_type_separation(record_type: str, draft: dict[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    if record_type in {"echo", "verification"}:
        found = _find_keys_recursive(draft, _GUARDIAN_APPLICATION_ONLY_KEYS)
        for path in found:
            diagnostics.append(_make_diagnostic(
                code="RECORD_TYPE_SEPARATION_VIOLATION",
                severity="error",
                field=f"record_draft.{path}",
                message=(
                    f"record_type '{record_type}' must not include Guardian Application field '{path}'. "
                    "Submit a separate guardian_application record instead."
                ),
                meaning="Echo, Verification, and Guardian Application are separate record types.",
                suggested_fix="Remove Guardian Application fields and submit a standalone guardian_application record.",
                retry_allowed=True,
            ))

    if record_type == "guardian_application":
        found = [
            *_find_keys_recursive(draft, _ECHO_ONLY_KEYS),
            *_find_keys_recursive(draft, _VERIFICATION_ONLY_KEYS),
        ]
        for path in found:
            diagnostics.append(_make_diagnostic(
                code="RECORD_TYPE_SEPARATION_VIOLATION",
                severity="error",
                field=f"record_draft.{path}",
                message=(
                    f"guardian_application must not include Echo/Verification field '{path}'. "
                    "Submit echo or verification as separate records."
                ),
                meaning="Guardian Application must be standalone.",
                suggested_fix="Remove Echo/Verification fields from guardian_application.",
                retry_allowed=True,
            ))

    return diagnostics


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


def _parse_verification_level_value(value: Any) -> int | None:
    """Parse verification level from V3, V3+, 3, or legacy integer values."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if raw.isdigit():
            return int(raw)
        match = re.fullmatch(r"[Vv]([0-9]+)\+?", raw)
        if match:
            return int(match.group(1))
    return None


def _extract_verification_version(draft: dict[str, Any]) -> int | None:
    candidates: list[Any] = []

    candidates.append(draft.get("verification_version"))

    verification = draft.get("verification")
    if isinstance(verification, dict):
        candidates.append(verification.get("version"))

    verification_content = draft.get("verification_content")
    if isinstance(verification_content, dict):
        candidates.append(verification_content.get("verification_level"))

    for candidate in candidates:
        parsed = _parse_verification_level_value(candidate)
        if parsed is not None:
            return parsed

    return None


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
    """Extract and merge boundary acknowledgements from public and draft fields.

    The public schema keeps top-level ``submission_boundary`` to the six canonical
    non-authority fields. Operational receipt/reclassification acknowledgements
    live in ``record_draft.non_authority_boundary_acknowledgement``. The gateway
    validates the merged view so builder output can satisfy both contracts.
    """
    draft = submission.get("record_draft") or {}
    draft_boundary = None
    if isinstance(draft, dict) and isinstance(draft.get("non_authority_boundary_acknowledgement"), dict):
        draft_boundary = draft["non_authority_boundary_acknowledgement"]

    top_boundary = None
    top_path = "submission_boundary"
    if isinstance(submission.get("submission_boundary"), dict):
        top_boundary = submission["submission_boundary"]
        top_path = "submission_boundary"
    elif isinstance(submission.get("boundary_acknowledgement"), dict):
        top_boundary = submission["boundary_acknowledgement"]
        top_path = "boundary_acknowledgement"

    if top_boundary is not None and draft_boundary is not None:
        merged = dict(draft_boundary)
        merged.update(top_boundary)
        return merged, top_path
    if top_boundary is not None:
        return top_boundary, top_path
    if draft_boundary is not None:
        return draft_boundary, "record_draft.non_authority_boundary_acknowledgement"
    return None, "submission_boundary"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def reject_forbidden_chain_fields(obj: dict[str, Any]) -> list[Diagnostic]:
    """Return diagnostics for any forbidden chain fields found recursively in *obj*."""
    return _find_forbidden_keys_recursive(obj)


def reject_private_keys(obj: Any) -> list[Diagnostic]:
    """Scan the entire submission recursively for embedded private-key/secret material."""
    diagnostics: list[Diagnostic] = []
    for hit in find_secret_hits(obj):
        diagnostics.append(_make_diagnostic(
            code="SECURITY_VIOLATION",
            severity="error",
            field=hit["path"],
            message=f"Security violation: {hit['code']} detected at {hit['path']}",
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
    """Reject private human identity data anywhere inside the draft."""
    diagnostics: list[Diagnostic] = []
    for hit in find_private_human_identity_hits(draft):
        diagnostics.append(_make_diagnostic(
            code=hit["code"],
            severity="error",
            field=f"draft.{hit['path'].removeprefix('$.')}",
            message="Private human identity fields are not allowed in public record-chain submissions",
            meaning="The record-chain is public; private human identity material must not be embedded, encrypted, or flagged as submitted.",
            suggested_fix="Remove the private human identity field. If a human is involved, disclose only public/non-identifying context.",
            retry_allowed=False,
        ))
    return diagnostics


def validate_linked_guardian_request(draft: dict[str, Any]) -> list[Diagnostic]:
    """DEPRECATED: Validate optional_linked_guardian_application_request when present.

    Kept for backward compatibility. The primary rejection path is now
    validate_linked_guardian_disabled() which rejects at preflight time.
    """
    diagnostics: list[Diagnostic] = []
    linked = draft.get("optional_linked_guardian_application_request")
    if not isinstance(linked, dict):
        return diagnostics

    does_request = linked.get("does_participant_request_guardian_application_with_this_record")
    if does_request is not True:
        return diagnostics

    record_type = draft.get("record_type") or ""
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


def validate_linked_guardian_disabled(draft: dict[str, Any]) -> list[Diagnostic]:
    """Reject linked Guardian auto-creation requests at validation/preflight time."""
    linked = draft.get("optional_linked_guardian_application_request")
    if not isinstance(linked, dict):
        return []
    if linked.get("does_participant_request_guardian_application_with_this_record") is not True:
        return []

    return [_make_diagnostic(
        code="LINKED_GUARDIAN_AUTO_CREATION_DISABLED",
        severity="error",
        field="record_draft.optional_linked_guardian_application_request",
        message="Linked guardian auto-creation is disabled. Submit a separate signed guardian_application record instead.",
        meaning="The gateway must not copy an authorship proof from one draft onto a newly constructed guardian_application draft.",
        suggested_fix="Build and sign a standalone guardian_application submission.",
        retry_allowed=True,
    )]


def validate_record_type_specific_content(record_type: str, draft: dict[str, Any]) -> list[Diagnostic]:
    """Require content blocks that match the public schema for each record type."""
    diagnostics: list[Diagnostic] = []

    def missing(code: str, field: str, message: str) -> None:
        diagnostics.append(_make_diagnostic(
            code=code,
            severity="error",
            field=field,
            message=message,
            meaning="Public schema and gateway validation require record-type-specific content.",
            suggested_fix="Rebuild with the current record-chain-builder.mjs and provide the required fields.",
        ))

    auth_scope = draft.get("authorization_context", {}).get("authorization_scope")
    expected_scope = _AUTHORIZATION_SCOPE_BY_RECORD_TYPE.get(record_type)
    if expected_scope and auth_scope != expected_scope:
        missing(
            "AUTHORIZATION_SCOPE_MISMATCH",
            "draft.authorization_context.authorization_scope",
            f"authorization_scope must be {expected_scope!r} for record_type {record_type!r}, got {auth_scope!r}",
        )

    if record_type == "echo":
        content = draft.get("echo_content")
        if not isinstance(content, dict) or not content.get("echo_text") or not content.get("echo_intent"):
            missing("MISSING_ECHO_CONTENT", "draft.echo_content", "Echo records require echo_content.echo_text and echo_content.echo_intent")
    elif record_type == "verification":
        content = draft.get("verification_content")
        if not isinstance(content, dict):
            missing("MISSING_VERIFICATION_CONTENT", "draft.verification_content", "Verification records require verification_content")
        else:
            required = {
                "verification_level": content.get("verification_level"),
                "what_was_checked": content.get("what_was_checked"),
                "verification_claim": content.get("verification_claim"),
                "fresh_actions_performed": content.get("fresh_actions_performed"),
            }
            if (
                not required["verification_level"]
                or not isinstance(required["what_was_checked"], list) or not required["what_was_checked"]
                or not required["verification_claim"]
                or not isinstance(required["fresh_actions_performed"], list) or not required["fresh_actions_performed"]
            ):
                missing("MISSING_VERIFICATION_CONTENT", "draft.verification_content", "Verification records require explicit level, checked items, claim, and fresh actions")
    elif record_type == "guardian_application":
        content = draft.get("guardian_application_content")
        if not isinstance(content, dict) or not content.get("requested_guardian_identifier") or not content.get("guardian_public_key_sha256") or not content.get("guardian_stewardship_oath"):
            missing("MISSING_GUARDIAN_APPLICATION_CONTENT", "draft.guardian_application_content", "Guardian applications require requested identifier, guardian public key SHA-256, and stewardship oath")
    elif record_type == "guardian_retirement":
        payload = draft.get("payload") if isinstance(draft.get("payload"), dict) else {}
        for field in ("guardian_id", "guardian_public_key_sha256", "reason"):
            if not (draft.get(field) or payload.get(field)):
                missing("MISSING_GUARDIAN_RETIREMENT_FIELD", f"draft.{field}", f"Guardian retirement requires {field}")
    elif record_type in {"propagation", "correction"}:
        for field in ("title", "body"):
            if not draft.get(field):
                missing("MISSING_RECORD_CONTENT", f"draft.{field}", f"{record_type} requires {field}")
    elif record_type == "classification_update":
        content = draft.get("classification_update_content")
        if not isinstance(content, dict):
            missing(
                "MISSING_CLASSIFICATION_UPDATE_CONTENT",
                "draft.classification_update_content",
                "Classification updates require classification_update_content",
            )
        else:
            required_fields = {
                "target_record_id": content.get("target_record_id"),
                "target_record_sha256": content.get("target_record_sha256"),
                "previous_classification": content.get("previous_classification"),
                "new_classification": content.get("new_classification"),
                "classification_reason": content.get("classification_reason"),
                "evidence_or_review_basis": content.get("evidence_or_review_basis"),
            }
            for field_name, value in required_fields.items():
                if not isinstance(value, str) or not value.strip():
                    missing(
                        "MISSING_CLASSIFICATION_UPDATE_CONTENT",
                        f"draft.classification_update_content.{field_name}",
                        f"Classification updates require non-empty {field_name}",
                    )

            target_sha = content.get("target_record_sha256")
            if isinstance(target_sha, str) and not re.fullmatch(r"[a-f0-9]{64}", target_sha):
                missing(
                    "INVALID_CLASSIFICATION_TARGET_SHA",
                    "draft.classification_update_content.target_record_sha256",
                    "target_record_sha256 must be a 64-character lowercase hex SHA-256",
                )
    elif record_type == "context_insufficient_notice" and not draft.get("reason"):
        missing("MISSING_CONTEXT_INSUFFICIENT_REASON", "draft.reason", "Context-insufficient notices require reason")

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

    if cc_level < MIN_CONTEXT_LEVEL or cc_level > MAX_CONTEXT_LEVEL:
        diagnostics.append(_make_diagnostic(
            code="INVALID_CONTEXT_LEVEL_RANGE",
            severity="error",
            field="draft.context_readiness.declared_context_level",
            message=f"declared_context_level must be between CC-{MIN_CONTEXT_LEVEL} and CC-{MAX_CONTEXT_LEVEL}, got {cc_level!r}",
            meaning="The public schema accepts only bounded CC levels.",
            suggested_fix=f"Use CC-{MIN_CONTEXT_LEVEL} through CC-{MAX_CONTEXT_LEVEL}.",
        ))
        return diagnostics

    verification_version = _extract_verification_version(draft)

    rules = _CC_RULES.get(record_type, [((0, None), _DEFAULT_CC_MINIMUM)])
    required_cc = _DEFAULT_CC_MINIMUM
    for (lo, hi), min_cc in rules:
        if verification_version is not None:
            if verification_version >= lo and (hi is None or verification_version <= hi):
                required_cc = min_cc
                break
        else:
            required_cc = min_cc

    context_readiness = draft.get("context_readiness") if isinstance(draft.get("context_readiness"), dict) else {}
    loaded_urls = context_readiness.get("loaded_context_urls") if isinstance(context_readiness, dict) else None
    if cc_level >= 3 and (not isinstance(loaded_urls, list) or len(loaded_urls) == 0):
        diagnostics.append(_make_diagnostic(
            code="CC3_REQUIRES_LOADED_CONTEXT_URLS",
            severity="error",
            field="draft.context_readiness.loaded_context_urls",
            message="CC-3 declarations require non-empty loaded_context_urls",
            meaning="Context claims must be backed by the URLs actually loaded.",
            suggested_fix="Add loaded_context_urls or lower declared_context_level.",
        ))
    if context_readiness.get("context_sufficient_for_selected_action") is True and cc_level > 0 and (not isinstance(loaded_urls, list) or len(loaded_urls) == 0):
        diagnostics.append(_make_diagnostic(
            code="CONTEXT_SUFFICIENT_REQUIRES_LOADED_URLS",
            severity="error",
            field="draft.context_readiness.loaded_context_urls",
            message="context_sufficient_for_selected_action=true requires loaded_context_urls",
            meaning="Sufficient-context claims must be auditable from the loaded context URLs.",
            suggested_fix="Add loaded_context_urls or set context_sufficient_for_selected_action=false.",
        ))

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
    """Require top-level authorship_proof for all public record types."""
    diagnostics: list[Diagnostic] = []
    if record_type not in ALLOWED_RECORD_TYPES:
        return diagnostics

    proof = submission.get("authorship_proof")

    if not isinstance(proof, dict):
        diagnostics.append(_make_diagnostic(
            code="MISSING_AUTHORSHIP_PROOF",
            severity="error",
            field="authorship_proof",
            message=f"Public record_type '{record_type}' requires top-level authorship_proof",
            meaning="All public Record-Chain submissions must be signed with an Ed25519 authorship key.",
            suggested_fix="Rebuild with the current builder using --key-dir <persistent-directory>.",
            help_url="https://www.trinityaccord.org/record-chain-field-helper/#MISSING_AUTHORSHIP_PROOF",
            retry_allowed=True,
        ))

    return diagnostics


# ---------------------------------------------------------------------------
# Part A: envelope alias / record-type helpers
# ---------------------------------------------------------------------------

_DRAFT_MISSING = object()


def normalize_record_type_value(value: Any) -> str:
    """Normalize a record_type value to lowercase underscored form."""
    if isinstance(value, str):
        return value.strip().lower().replace("-", "_")
    return ""


def record_draft_value(submission: dict[str, Any]) -> Any:
    """Return the raw record_draft value, or _DRAFT_MISSING sentinel."""
    return submission.get("record_draft", _DRAFT_MISSING)


def extract_record_draft(submission: dict[str, Any]) -> dict[str, Any] | None:
    """Return record_draft if it is a dict, else None."""
    draft = submission.get("record_draft")
    return draft if isinstance(draft, dict) else None


def validate_envelope_aliases_and_record_type(
    submission: dict[str, Any],
    draft: dict[str, Any] | None,
) -> list[Diagnostic]:
    """Reject retired top-level aliases and enforce record_type consistency."""
    diagnostics: list[Diagnostic] = []

    if "draft" in submission:
        diagnostics.append(_make_diagnostic(
            code="DRAFT_ALIAS_RETIRED",
            severity="error",
            field="draft",
            message="The top-level 'draft' alias is retired. Use only 'record_draft'.",
            meaning="The gateway signs, verifies, and persists record_draft. Keeping draft creates ambiguous signing semantics.",
            suggested_fix="Remove top-level draft, keep record_draft, and rebuild the authorship proof if the signed object changed.",
            retry_allowed=True,
        ))

    if "type" in submission:
        diagnostics.append(_make_diagnostic(
            code="TYPE_ALIAS_RETIRED",
            severity="error",
            field="type",
            message="The top-level 'type' alias is retired. Use only 'record_type'.",
            meaning="The gateway must not route using a legacy type alias when record_type is the public schema field.",
            suggested_fix="Remove top-level type and set record_type explicitly.",
            retry_allowed=True,
        ))

    top_rt = normalize_record_type_value(submission.get("record_type"))
    if not top_rt:
        diagnostics.append(_make_diagnostic(
            code="MISSING_RECORD_TYPE",
            severity="error",
            field="record_type",
            message="Missing required field 'record_type'.",
            meaning="Every public submission must specify record_type.",
            suggested_fix="Add a top-level record_type matching record_draft.record_type.",
            retry_allowed=True,
        ))

    if draft is None:
        return diagnostics

    draft_rt = normalize_record_type_value(draft.get("record_type"))
    if not draft_rt:
        diagnostics.append(_make_diagnostic(
            code="MISSING_DRAFT_RECORD_TYPE",
            severity="error",
            field="record_draft.record_type",
            message="record_draft.record_type is required.",
            meaning="The signed record draft must declare the same record type as the submission envelope.",
            suggested_fix="Add record_draft.record_type matching top-level record_type and rebuild the authorship proof.",
            retry_allowed=True,
        ))
        return diagnostics

    if top_rt and draft_rt and top_rt != draft_rt:
        diagnostics.append(_make_diagnostic(
            code="RECORD_TYPE_MISMATCH",
            severity="error",
            field="record_draft.record_type",
            message=f"Top-level record_type {top_rt!r} does not match record_draft.record_type {draft_rt!r}.",
            meaning="The gateway cannot route one record type while persisting a signed draft of another record type.",
            suggested_fix="Rebuild so record_type and record_draft.record_type are identical.",
            retry_allowed=True,
        ))

    return diagnostics


def detect_route(submission: dict[str, Any]) -> str:
    """Determine the processing route for *submission*.

    Returns the record_type string if valid, otherwise ``"unknown"``.
    """
    if "type" in submission or "draft" in submission:
        return "unknown"

    top_rt = normalize_record_type_value(submission.get("record_type"))
    draft = extract_record_draft(submission)
    draft_rt = normalize_record_type_value((draft or {}).get("record_type")) if draft else ""

    if top_rt and draft_rt and top_rt != draft_rt:
        return "unknown"

    record_type = draft_rt or top_rt
    return record_type if record_type in ALLOWED_RECORD_TYPES else "unknown"


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

    # --- Part A: sentinel-safe record_draft extraction ---
    draft_raw = record_draft_value(submission)
    draft: dict[str, Any] | None = None

    if draft_raw is _DRAFT_MISSING:
        diagnostics.append(_make_diagnostic(
            code="MISSING_DRAFT",
            severity="error",
            field="record_draft",
            message="Missing required field 'record_draft'.",
            meaning="Every public submission must include a signed record_draft object.",
            suggested_fix="Add record_draft and rebuild the authorship proof.",
            retry_allowed=True,
        ))
    elif not isinstance(draft_raw, dict):
        diagnostics.append(_make_diagnostic(
            code="INVALID_DRAFT",
            severity="error",
            field="record_draft",
            message="'record_draft' must be a JSON object.",
            meaning="The signed draft must be a JSON object.",
            suggested_fix="Change record_draft to an object and rebuild the authorship proof.",
            retry_allowed=True,
        ))
    else:
        draft = draft_raw

    # --- Part A: reject retired aliases + enforce record_type consistency ---
    diagnostics.extend(validate_envelope_aliases_and_record_type(submission, draft))

    # Derive rt from record_type only (not legacy 'type' alias)
    record_type = submission.get("record_type")
    rt = ""
    if isinstance(record_type, str):
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

    # --- linked Guardian auto-creation disabled (fail-fast at preflight) ---
    if isinstance(draft, dict):
        diagnostics.extend(validate_linked_guardian_disabled(draft))

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
        diagnostics.extend(validate_record_type_specific_content(rt, draft))

    # --- identity validation ---
    if isinstance(draft, dict):
        diagnostics.extend(validate_identity(draft))

    # --- human name privacy ---
    if isinstance(draft, dict):
        diagnostics.extend(validate_human_name_privacy(draft))

    # --- record type separation ---
    if isinstance(draft, dict) and rt:
        diagnostics.extend(validate_record_type_separation(rt, draft))

    # --- claim_boundary type check (moved to verify_authorship_proof_submission) ---
    # Authoritative validation is now in authorship.py at submission level.
    # validate_claim_boundary() is retained for backward compatibility but not called here.

    # --- oath gate validation (before authorship proof) ---
    if isinstance(draft, dict) and rt:
        diagnostics.extend(validate_submission_oath(rt, submission if isinstance(submission, dict) else {}, draft))

    # --- authorship proof required for formal records ---
    if isinstance(draft, dict) and rt:
        diagnostics.extend(validate_authorship_proof_presence(rt, submission, draft))

    # --- authorship proof type check (top-level only) ---
    proof = submission.get("authorship_proof")
    if proof is not None and not isinstance(proof, dict):
        diagnostics.append(_make_diagnostic(
            code="INVALID_AUTHORSHIP_PROOF",
            severity="error",
            field="authorship_proof",
            message="'authorship_proof' must be an object when present",
            meaning="If provided, authorship_proof must be a JSON object.",
            suggested_fix="Change authorship_proof to a JSON object or remove it.",
        ))

    # --- Ed25519 authorship proof verification ---
    if isinstance(draft, dict) and rt in ALLOWED_RECORD_TYPES:
        ok, code, message = verify_authorship_proof_submission(submission)
        if not ok:
            diagnostics.append(_make_diagnostic(
                code=code or "AUTHORSHIP_VERIFICATION_FAILED",
                severity="error",
                field="authorship_proof",
                message=message or "Authorship proof verification failed.",
                meaning="Public submissions must be signed by an Ed25519 authorship key.",
                suggested_fix="Rebuild the submission with the current builder using --key-dir <persistent-directory>.",
            ))

    return diagnostics


# ---------------------------------------------------------------------------
# Oath gate constants
# ---------------------------------------------------------------------------
_OATH_REQUIRED_RECORD_TYPES: frozenset[str] = frozenset({
    "echo", "verification", "guardian_application", "guardian_retirement",
    "guardian_key_rotation", "propagation", "correction", "classification_update",
})

_OATH_NO_SHORTCUT_FIELDS: frozenset[str] = frozenset({
    "oath_read", "participant_readback_provided", "readback_matches_canonical_oath",
    "readback_was_not_piped_from_file", "readback_was_not_generated_by_script",
    "readback_was_not_loaded_from_cache", "readback_was_not_summary_or_paraphrase",
    "readback_was_not_generated_by_external_automation",
    "readback_was_not_auto_filled_by_builder", "no_shortcut_oath_acknowledged",
})

_OATH_BOUNDARY_FIELDS: frozenset[str] = frozenset({
    "oath_does_not_prove_subjective_understanding",
    "oath_verifies_exact_readback_only",
})


def validate_submission_oath(
    record_type: str,
    submission: dict[str, Any],
    draft: dict[str, Any],
) -> list[Diagnostic]:
    """Validate the no-shortcut oath gate for formal record types."""
    diagnostics: list[Diagnostic] = []

    # Skip context_insufficient_notice
    if record_type == "context_insufficient_notice":
        return diagnostics

    if record_type not in _OATH_REQUIRED_RECORD_TYPES:
        return diagnostics

    # Require submission_oath_verification in draft
    oath_verification = draft.get("submission_oath_verification")
    if not isinstance(oath_verification, dict):
        diagnostics.append(_make_diagnostic(
            code="MISSING_SUBMISSION_OATH",
            severity="error",
            field="record_draft.submission_oath_verification",
            message=f"Formal record_type '{record_type}' requires submission_oath_verification",
            meaning="All formal Record-Chain submissions must pass the no-shortcut oath gate.",
            suggested_fix="Run the builder with print-oath to get the canonical oath, then provide an exact readback.",
        ))
        return diagnostics

    # Require client_oath_readback for formal records
    client_oath = submission.get("client_oath_readback")
    if not isinstance(client_oath, dict):
        diagnostics.append(_make_diagnostic(
            code="MISSING_CLIENT_OATH_READBACK",
            severity="error",
            field="client_oath_readback",
            message=f"Formal record_type '{record_type}' requires client_oath_readback with readback_text",
            meaning="The raw oath readback is required for gateway validation. It will be redacted before persistence.",
            suggested_fix="Add client_oath_readback with readback_text containing the exact canonical oath.",
        ))
        return diagnostics

    if not client_oath.get("readback_text"):
        diagnostics.append(_make_diagnostic(
            code="OATH_READBACK_MISSING",
            severity="error",
            field="client_oath_readback.readback_text",
            message="client_oath_readback.readback_text must not be empty",
            meaning="The readback text must contain the exact canonical oath text.",
            suggested_fix="Provide the exact canonical oath text in readback_text.",
        ))

    # Load local oath policy
    import hashlib
    import json as _json
    import os
    policy_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "api", "record-chain-oath-policy.v1.json"
    )
    try:
        with open(policy_path, "r", encoding="utf-8") as f:
            local_policy = _json.load(f)
    except (FileNotFoundError, _json.JSONDecodeError):
        diagnostics.append(_make_diagnostic(
            code="OATH_POLICY_LOAD_ERROR",
            severity="error",
            field=None,
            message="Cannot load local api/record-chain-oath-policy.v1.json",
            meaning="The oath policy file is required for validation.",
            suggested_fix="Ensure api/record-chain-oath-policy.v1.json exists in the repository.",
        ))
        return diagnostics

    # Compute local policy hash over the stable policy-core domain.
    local_policy_sha256 = compute_oath_policy_sha256(local_policy)

    # Require and validate hash fields (must exist and be 64 hex)
    import re as _re
    _HEX64 = _re.compile(r"^[0-9a-f]{64}$")

    submitted_policy_hash = oath_verification.get("oath_policy_sha256", "")
    if not submitted_policy_hash or not _HEX64.match(submitted_policy_hash):
        diagnostics.append(_make_diagnostic(
            code="OATH_REQUIRED_HASH_MISSING",
            severity="error",
            field="record_draft.submission_oath_verification.oath_policy_sha256",
            message="oath_policy_sha256 must be a 64-char lowercase hex sha256",
            meaning="The oath policy hash is required for all formal submissions.",
            suggested_fix="Rebuild with the latest builder to include oath_policy_sha256.",
        ))
        return diagnostics

    # Compare policy hash
    if submitted_policy_hash != local_policy_sha256:
        diagnostics.append(_make_diagnostic(
            code="OATH_POLICY_HASH_MISMATCH",
            severity="error",
            field="record_draft.submission_oath_verification.oath_policy_sha256",
            message=f"Oath policy hash mismatch: submitted {submitted_policy_hash[:16]}... != local {local_policy_sha256[:16]}...",
            meaning="The embedded oath policy hash does not match the gateway's current policy.",
            suggested_fix="Rebuild with the latest builder to pick up the current oath policy.",
        ))

    # Determine expected modules
    expected_modules = list(local_policy.get("record_type_modules", {}).get(record_type, []))
    linked = draft.get("optional_linked_guardian_application_request")
    if isinstance(linked, dict) and linked.get("does_participant_request_guardian_application_with_this_record") is True:
        if "guardian_stewardship_v1" not in expected_modules:
            expected_modules.append("guardian_stewardship_v1")

    # Check oath modules match
    submitted_modules = oath_verification.get("oath_modules", [])
    if submitted_modules != expected_modules:
        diagnostics.append(_make_diagnostic(
            code="OATH_MODULES_MISMATCH",
            severity="error",
            field="record_draft.submission_oath_verification.oath_modules",
            message=f"Oath modules mismatch: got {submitted_modules}, expected {expected_modules}",
            meaning="The oath modules must match the expected modules for this record type.",
            suggested_fix=f"Use modules: {expected_modules}",
        ))

    # Build canonical oath text and verify hash
    modules_obj = local_policy.get("modules", {})
    canonical_parts = []
    for mod_id in expected_modules:
        mod = modules_obj.get(mod_id)
        if mod:
            canonical_parts.append(f"=== {mod['label']} ({mod_id}) ===\n\n{unicodedata.normalize('NFC', normalize_oath_text(mod['text']))}")

    joiner = local_policy.get("canonicalization", {}).get("module_joiner", "\n\n---\n\n")
    canonical_text = joiner.join(canonical_parts).strip()
    canonical_hash = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()

    submitted_canonical_hash = oath_verification.get("canonical_oath_text_sha256", "")
    if not submitted_canonical_hash or not _HEX64.match(submitted_canonical_hash):
        diagnostics.append(_make_diagnostic(
            code="OATH_REQUIRED_HASH_MISSING",
            severity="error",
            field="record_draft.submission_oath_verification.canonical_oath_text_sha256",
            message="canonical_oath_text_sha256 must be a 64-char lowercase hex sha256",
            meaning="The canonical oath text hash is required for all formal submissions.",
            suggested_fix="Rebuild with the latest builder to include canonical_oath_text_sha256.",
        ))
    elif submitted_canonical_hash != canonical_hash:
        diagnostics.append(_make_diagnostic(
            code="OATH_CANONICAL_HASH_MISMATCH",
            severity="error",
            field="record_draft.submission_oath_verification.canonical_oath_text_sha256",
            message="Canonical oath text hash mismatch",
            meaning="The canonical oath text hash does not match the gateway's computation.",
            suggested_fix="Rebuild with the latest builder.",
        ))

    # Normalize and compare readback
    readback_text = client_oath.get("readback_text", "")
    normalized_readback = unicodedata.normalize("NFC", normalize_oath_text(readback_text))
    readback_hash = sha256_text(normalized_readback)

    if normalized_readback != canonical_text:
        diagnostics.append(_make_diagnostic(
            code="OATH_READBACK_MISMATCH",
            severity="error",
            field="client_oath_readback.readback_text",
            message="Oath readback does not match canonical oath text",
            meaning="The readback must be an exact match of the canonical oath text.",
            suggested_fix="Use the builder print-oath command to get the exact canonical text, then provide it as readback.",
        ))

    # Check readback hash matches signed field
    signed_readback_hash = oath_verification.get("participant_readback_sha256", "")
    if not signed_readback_hash or not _HEX64.match(signed_readback_hash):
        diagnostics.append(_make_diagnostic(
            code="OATH_REQUIRED_HASH_MISSING",
            severity="error",
            field="record_draft.submission_oath_verification.participant_readback_sha256",
            message="participant_readback_sha256 must be a 64-char lowercase hex sha256",
            meaning="The participant readback hash is required for all formal submissions.",
            suggested_fix="Rebuild with the latest builder to include participant_readback_sha256.",
        ))
    elif signed_readback_hash != readback_hash:
        diagnostics.append(_make_diagnostic(
            code="OATH_READBACK_HASH_MISMATCH",
            severity="error",
            field="record_draft.submission_oath_verification.participant_readback_sha256",
            message="Signed readback hash does not match actual readback hash",
            meaning="The participant_readback_sha256 must match the sha256 of the provided readback.",
            suggested_fix="Ensure the readback hash is computed from the exact readback text.",
        ))

    # Check readback method
    method = oath_verification.get("readback_method_declared", "")
    if method and method != "participant_generated_in_current_context":
        diagnostics.append(_make_diagnostic(
            code="OATH_READBACK_METHOD_INVALID",
            severity="error",
            field="record_draft.submission_oath_verification.readback_method_declared",
            message=f"Invalid readback method: '{method}', expected 'participant_generated_in_current_context'",
            meaning="The readback must be generated in the current context, not piped or cached.",
            suggested_fix="Set readback_method_declared to 'participant_generated_in_current_context'.",
        ))

    # Check all no-shortcut declarations are true
    for field_name in _OATH_NO_SHORTCUT_FIELDS:
        if oath_verification.get(field_name) is not True:
            diagnostics.append(_make_diagnostic(
                code="OATH_REQUIRED_FIELD_NOT_TRUE",
                severity="error",
                field=f"record_draft.submission_oath_verification.{field_name}",
                message=f"'{field_name}' must be true",
                meaning=f"The no-shortcut declaration '{field_name}' is required.",
                suggested_fix=f"Set '{field_name}' to true in submission_oath_verification.",
            ))

    # Check boundary booleans
    for field_name in _OATH_BOUNDARY_FIELDS:
        if oath_verification.get(field_name) is not True:
            diagnostics.append(_make_diagnostic(
                code="OATH_REQUIRED_FIELD_NOT_TRUE",
                severity="error",
                field=f"record_draft.submission_oath_verification.{field_name}",
                message=f"'{field_name}' must be true",
                meaning=f"The oath boundary '{field_name}' is required.",
                suggested_fix=f"Set '{field_name}' to true.",
            ))

    # Reject test_mode_oath_fixture in production
    if oath_verification.get("test_mode_oath_fixture") is True:
        test_mode_ok = os.environ.get("TRINITY_OATH_TEST_MODE") == "1" or os.environ.get("NODE_ENV") == "test"
        if not test_mode_ok:
            diagnostics.append(_make_diagnostic(
                code="OATH_TEST_FIXTURE_NOT_ALLOWED",
                severity="error",
                field="record_draft.submission_oath_verification.test_mode_oath_fixture",
                message="test_mode_oath_fixture is not allowed in production",
                meaning="Test-mode oath fixtures must not be used in production submissions.",
                suggested_fix="Remove test_mode_oath_fixture or use a proper test environment.",
            ))

    return diagnostics


def redact_transient_oath_readback(submission: dict[str, Any]) -> dict[str, Any]:
    """Redact raw readback_text from submission before persistence."""
    import copy
    redacted = copy.deepcopy(submission)
    client_oath = redacted.get("client_oath_readback")
    if isinstance(client_oath, dict):
        raw_readback_text = client_oath.get("readback_text", "") or ""
        normalized_readback_text = normalize_oath_text(raw_readback_text)
        readback_hash = (
            sha256_text(normalized_readback_text)
            if normalized_readback_text
            else client_oath.get("readback_text_sha256", "")
        )
        redacted["client_oath_readback"] = {
            "schema": client_oath.get("schema", "trinityaccord.client-oath-readback.v1"),
            "record_type": client_oath.get("record_type", ""),
            "oath_policy_sha256": client_oath.get("oath_policy_sha256", ""),
            "oath_modules": client_oath.get("oath_modules", []),
            "readback_text_sha256": readback_hash,
            "readback_text_hash_canonicalization": "NFC_CRLF_TO_LF_STRIP",
            "readback_text_char_count": len(normalized_readback_text),
            "redacted_after_gateway_validation": True,
        }
    return redacted
