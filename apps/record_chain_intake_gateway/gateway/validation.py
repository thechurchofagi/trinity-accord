# gateway/validation.py
"""Submission validation, security scanning, boundary checks, and context-readiness checks."""

from __future__ import annotations

import logging
import re
from typing import Any

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


def _find_forbidden_keys_recursive(obj: Any, path: str = "") -> list[str]:
    """Recursively find all forbidden chain fields anywhere in a nested structure."""
    errors: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            if key in FORBIDDEN_CHAIN_FIELDS:
                errors.append(
                    f"Forbidden field '{key}' at '{current_path}'; "
                    "this field is assigned by the gateway"
                )
            errors.extend(_find_forbidden_keys_recursive(value, current_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            errors.extend(_find_forbidden_keys_recursive(item, f"{path}[{i}]"))
    return errors


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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def reject_forbidden_chain_fields(obj: dict[str, Any]) -> list[str]:
    """Return error messages for any forbidden chain fields found recursively in *obj*."""
    return _find_forbidden_keys_recursive(obj)


def reject_private_keys(obj: Any) -> list[str]:
    """Scan the entire submission for embedded private-key material."""
    errors: list[str] = []
    serialised = repr(obj)
    for pat in _SECURITY_PATTERNS:
        m = pat.search(serialised)
        if m:
            errors.append(
                f"Security violation: content matches pattern '{pat.pattern}' "
                "(possible secret/key material)"
            )
    return errors


def reject_placeholders(obj: Any) -> list[str]:
    """Reject obvious placeholder / test tokens using strengthened patterns."""
    errors: list[str] = []
    serialised = repr(obj)
    for pat in _PLACEHOLDER_PATTERNS:
        m = pat.search(serialised)
        if m:
            errors.append(
                f"Placeholder detected: matches pattern '{pat.pattern}' — replace with a real value"
            )
    return errors


def validate_boundary_acknowledgement(submission: dict[str, Any]) -> list[str]:
    """Validate that boundary_acknowledgement contains all 6 required boolean true fields."""
    errors: list[str] = []
    boundary = submission.get("boundary_acknowledgement")
    if boundary is None:
        errors.append("Missing required field 'boundary_acknowledgement'")
        return errors
    if not isinstance(boundary, dict):
        errors.append("'boundary_acknowledgement' must be a JSON object")
        return errors

    for field in REQUIRED_BOUNDARY_FIELDS:
        if field not in boundary:
            errors.append(f"boundary_acknowledgement missing required field '{field}'")
        elif boundary[field] is not True:
            errors.append(
                f"boundary_acknowledgement.'{field}' must be boolean true, "
                f"got {boundary[field]!r}"
            )
    return errors


def validate_context_readiness(record_type: str, draft: dict[str, Any]) -> list[str]:
    """Check that *draft* meets the minimum context-completeness level for *record_type*."""
    errors: list[str] = []
    cc_level = _extract_context_level(draft)
    if cc_level is None:
        errors.append(
            "Missing required field 'context_readiness.declared_context_level' "
            "(or legacy 'context_completeness_level') in draft"
        )
        return errors

    try:
        cc_level = int(cc_level)
    except (TypeError, ValueError):
        errors.append(f"'declared_context_level' must be an integer, got {cc_level!r}")
        return errors

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
        errors.append(
            f"Insufficient context completeness: {cc_level} < {required_cc} "
            f"(required for record_type='{record_type}', "
            f"verification_version={verification_version})"
        )
    return errors


def validate_verification_rules(draft: dict[str, Any]) -> list[str]:
    """Validate verification-specific fields when present."""
    errors: list[str] = []
    verification = draft.get("verification")
    if verification is None:
        return errors
    if not isinstance(verification, dict):
        errors.append("'verification' must be an object")
        return errors

    version = verification.get("version")
    if version is not None:
        try:
            v = int(version)
            if v < 0:
                errors.append("'verification.version' must be non-negative")
        except (TypeError, ValueError):
            errors.append(f"'verification.version' must be an integer, got {version!r}")

    proof = verification.get("proof")
    if proof is not None and not isinstance(proof, (str, dict)):
        errors.append("'verification.proof' must be a string or object")

    return errors


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


def validate_submission(submission: dict[str, Any]) -> list[str]:
    """Run all validation checks on *submission* and return a list of error strings.

    An empty list means the submission is valid.
    """
    errors: list[str] = []

    # --- structural checks ---
    if not isinstance(submission, dict):
        return ["Submission must be a JSON object"]

    record_type = submission.get("record_type") or submission.get("type")
    if not record_type:
        errors.append("Missing required field 'record_type'")
    elif not isinstance(record_type, str):
        errors.append(f"'record_type' must be a string, got {type(record_type).__name__}")
    else:
        rt = record_type.strip().lower()
        if rt not in ALLOWED_RECORD_TYPES:
            errors.append(
                f"Unknown record_type '{record_type}'; "
                f"allowed types: {sorted(ALLOWED_RECORD_TYPES)}"
            )

    draft = submission.get("draft") or submission.get("record_draft")
    if draft is None:
        errors.append("Missing required field 'draft' (or 'record_draft')")
    elif not isinstance(draft, dict):
        errors.append("'draft' must be a JSON object")

    # --- boundary acknowledgement ---
    errors.extend(validate_boundary_acknowledgement(submission))

    # --- forbidden fields (recursive) ---
    errors.extend(reject_forbidden_chain_fields(submission))

    # --- security scans ---
    errors.extend(reject_private_keys(submission))
    errors.extend(reject_placeholders(submission))

    # --- context-readiness ---
    if isinstance(draft, dict) and record_type:
        rt = record_type.strip().lower() if isinstance(record_type, str) else ""
        errors.extend(validate_context_readiness(rt, draft))
        errors.extend(validate_verification_rules(draft))

    # --- authorship proof presence (optional but recommended) ---
    proof = submission.get("authorship_proof") or submission.get("proof")
    if proof is not None and not isinstance(proof, dict):
        errors.append("'authorship_proof' must be an object when present")

    return errors
