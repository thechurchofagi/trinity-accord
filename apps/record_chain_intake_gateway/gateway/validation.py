# gateway/validation.py
"""Submission validation, security scanning, and context-readiness checks."""

from __future__ import annotations

import re
from typing import Any

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
# Context-completeness minimums per record type / verification version.
# Keys are (record_type, verification_version_range_description).
# Values are the minimum CC level required.
#
# Verification versions are encoded as integers (e.g. V0 = 0, V6 = 6).
# We store ranges as (lo, hi) tuples; hi=None means "6 and above".
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
    "council_record": [
        ((0, None), 3),
    ],
    "memory_anchor": [
        ((0, None), 3),
    ],
    "attestation": [
        ((0, None), 3),
    ],
    "amendment": [
        ((0, None), 3),
    ],
}

_DEFAULT_CC_MINIMUM = 3  # fallback for unknown record types


def _walk(obj: Any, visitor: Any) -> None:
    """Depth-first walk over a JSON-like structure, calling *visitor* on every value."""
    visitor(obj)
    if isinstance(obj, dict):
        for v in obj.values():
            _walk(v, visitor)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, visitor)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def reject_forbidden_chain_fields(obj: dict[str, Any]) -> list[str]:
    """Return a list of error messages for any forbidden chain fields found in *obj*.

    Only the top-level keys of *obj* and of nested ``draft`` / ``record_draft``
    dicts are checked (the places where submitters might try to set server-owned
    fields).
    """
    errors: list[str] = []
    for scope_name, scope in [("submission", obj), ("draft", obj.get("draft") or obj.get("record_draft") or {})]:
        if not isinstance(scope, dict):
            continue
        for key in scope:
            if key in FORBIDDEN_CHAIN_FIELDS:
                errors.append(
                    f"Forbidden field '{key}' found in {scope_name}; "
                    "this field is assigned by the gateway"
                )
    return errors


def reject_private_keys(obj: Any) -> list[str]:
    """Scan the entire submission for embedded private-key material."""
    errors: list[str] = []
    serialised = repr(obj)  # cheap stringification
    for pat in _SECURITY_PATTERNS:
        m = pat.search(serialised)
        if m:
            errors.append(
                f"Security violation: content matches pattern '{pat.pattern}' "
                "(possible secret/key material)"
            )
    return errors


def reject_placeholders(obj: Any) -> list[str]:
    """Reject obvious placeholder / test tokens."""
    errors: list[str] = []
    serialised = repr(obj).lower()
    placeholders = [
        "your_github_token",
        "your-token-here",
        "insert_token",
        "replace_me",
        "todo",
        "xxx",
        "example.com",
    ]
    for ph in placeholders:
        if ph in serialised:
            errors.append(f"Placeholder detected: '{ph}' — replace with a real value")
    return errors


def validate_context_readiness(record_type: str, draft: dict[str, Any]) -> list[str]:
    """Check that *draft* meets the minimum context-completeness level for *record_type*."""
    errors: list[str] = []
    cc_level = draft.get("context_completeness_level")
    if cc_level is None:
        errors.append("Missing required field 'context_completeness_level' in draft")
        return errors

    try:
        cc_level = int(cc_level)
    except (TypeError, ValueError):
        errors.append(f"'context_completeness_level' must be an integer, got {cc_level!r}")
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
            # No version info; use the broadest match
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

    Returns one of: ``"echo"``, ``"verification"``, ``"guardian_application"``,
    ``"council_record"``, ``"memory_anchor"``, ``"attestation"``, ``"amendment"``,
    or ``"unknown"``.
    """
    record_type = submission.get("record_type") or submission.get("type") or ""
    if isinstance(record_type, str):
        record_type = record_type.strip().lower()
    if record_type in _CC_RULES:
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

    draft = submission.get("draft") or submission.get("record_draft")
    if draft is None:
        errors.append("Missing required field 'draft' (or 'record_draft')")
    elif not isinstance(draft, dict):
        errors.append("'draft' must be a JSON object")

    # --- forbidden fields ---
    errors.extend(reject_forbidden_chain_fields(submission))

    # --- security scans ---
    errors.extend(reject_private_keys(submission))
    errors.extend(reject_placeholders(submission))

    # --- context-readiness ---
    if isinstance(draft, dict) and record_type:
        errors.extend(validate_context_readiness(str(record_type), draft))
        errors.extend(validate_verification_rules(draft))

    # --- authorship proof presence (optional but recommended) ---
    proof = submission.get("authorship_proof") or submission.get("proof")
    if proof is not None and not isinstance(proof, dict):
        errors.append("'authorship_proof' must be an object when present")

    return errors
