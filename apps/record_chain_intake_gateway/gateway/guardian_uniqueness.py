"""Immutable uniqueness claims for Guardian applications.

Submission-hash idempotency prevents the exact same envelope from being
materialized twice.  Guardian applications also need semantic uniqueness:
different signed envelopes must not claim the same Guardian identifier or
Ed25519 continuity key.  These helpers define the two deterministic claim
paths that are created atomically with a Guardian intake transaction.
"""
from __future__ import annotations

import re
from typing import Any


CLAIM_SCHEMA = "trinityaccord.guardian-application-uniqueness-claim.v1"
GUARDIAN_STATE_PATH = "record-chain/indexes/guardian-state.json"

_GUARDIAN_ID_RE = re.compile(r"guardian_ed25519_[a-f0-9]{16}")
_PUBLIC_KEY_SHA256_RE = re.compile(r"[a-f0-9]{64}")


def extract_guardian_application_identity(
    draft: dict[str, Any],
) -> tuple[str, str] | None:
    """Return ``(guardian_id, public_key_sha256)`` for a valid-shape draft."""
    if draft.get("record_type") != "guardian_application":
        return None
    content = draft.get("guardian_application_content")
    if not isinstance(content, dict):
        return None
    guardian_id = content.get("requested_guardian_identifier")
    public_key_sha256 = content.get("guardian_public_key_sha256")
    if not isinstance(guardian_id, str) or _GUARDIAN_ID_RE.fullmatch(guardian_id) is None:
        return None
    if (
        not isinstance(public_key_sha256, str)
        or _PUBLIC_KEY_SHA256_RE.fullmatch(public_key_sha256) is None
    ):
        return None
    if guardian_id != f"guardian_ed25519_{public_key_sha256[:16]}":
        return None
    return guardian_id, public_key_sha256


def guardian_uniqueness_claim_paths(
    guardian_id: str,
    public_key_sha256: str,
) -> dict[str, str]:
    """Return deterministic immutable claim paths for a Guardian identity."""
    if _GUARDIAN_ID_RE.fullmatch(guardian_id) is None:
        raise ValueError("invalid guardian_id for uniqueness claim path")
    if _PUBLIC_KEY_SHA256_RE.fullmatch(public_key_sha256) is None:
        raise ValueError("invalid Guardian public-key SHA-256 for uniqueness claim path")
    if guardian_id != f"guardian_ed25519_{public_key_sha256[:16]}":
        raise ValueError("guardian_id does not derive from Guardian public-key SHA-256")
    return {
        "guardian_id": f"record-chain/intake/by-guardian-id/{guardian_id}.json",
        "guardian_public_key_sha256": (
            "record-chain/intake/by-guardian-public-key-sha256/"
            f"{public_key_sha256}.json"
        ),
    }


def build_guardian_uniqueness_claim(
    *,
    claim_kind: str,
    guardian_id: str,
    public_key_sha256: str,
    submission_sha256: str,
    receipt_id: str,
    receipt_path: str,
    pending_file_path: str,
    intake_submission_path: str,
    created_at: str,
) -> dict[str, Any]:
    """Build one immutable semantic-uniqueness claim object."""
    paths = guardian_uniqueness_claim_paths(guardian_id, public_key_sha256)
    if claim_kind not in paths:
        raise ValueError(f"unsupported Guardian uniqueness claim kind: {claim_kind}")
    claim_value = guardian_id if claim_kind == "guardian_id" else public_key_sha256
    return {
        "schema": CLAIM_SCHEMA,
        "claim_kind": claim_kind,
        "claim_value": claim_value,
        "claim_path": paths[claim_kind],
        "guardian_id": guardian_id,
        "guardian_public_key_sha256": public_key_sha256,
        "submission_sha256": submission_sha256,
        "receipt_id": receipt_id,
        "receipt_path": receipt_path,
        "pending_file_path": pending_file_path,
        "intake_submission_path": intake_submission_path,
        "created_at": created_at,
        "immutable": True,
        "uniqueness_scope": "first_guardian_application_per_identifier_and_public_key",
    }


def guardian_uniqueness_claim_errors(
    claim: dict[str, Any],
    *,
    claim_kind: str,
    guardian_id: str,
    public_key_sha256: str,
) -> list[str]:
    """Validate invariant fields that do not depend on a receipt transaction."""
    errors: list[str] = []
    try:
        paths = guardian_uniqueness_claim_paths(guardian_id, public_key_sha256)
    except ValueError as exc:
        return [str(exc)]
    expected_value = guardian_id if claim_kind == "guardian_id" else public_key_sha256
    expected = {
        "schema": CLAIM_SCHEMA,
        "claim_kind": claim_kind,
        "claim_value": expected_value,
        "claim_path": paths[claim_kind],
        "guardian_id": guardian_id,
        "guardian_public_key_sha256": public_key_sha256,
        "immutable": True,
        "uniqueness_scope": "first_guardian_application_per_identifier_and_public_key",
    }
    for field, expected_value in expected.items():
        if claim.get(field) != expected_value:
            errors.append(
                f"{field} mismatch: expected {expected_value!r}, got {claim.get(field)!r}"
            )
    for field in (
        "submission_sha256",
        "receipt_id",
        "receipt_path",
        "pending_file_path",
        "intake_submission_path",
        "created_at",
    ):
        if not isinstance(claim.get(field), str) or not claim[field]:
            errors.append(f"{field} must be a non-empty string")
    submission_sha256 = claim.get("submission_sha256")
    if (
        isinstance(submission_sha256, str)
        and _PUBLIC_KEY_SHA256_RE.fullmatch(submission_sha256) is None
    ):
        errors.append("submission_sha256 must be 64 lowercase hexadecimal characters")
    return errors
