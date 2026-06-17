# gateway/authorship.py
"""Ed25519 authorship verification utilities."""

from __future__ import annotations

import base64
import hashlib
import logging
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)

import json

from .canonical import canonical_bytes, sha256_bytes

logger = logging.getLogger(__name__)

# Fields that are assigned or derived by the server/append layer and are not
# part of the participant's pre-append signed payload.
#
# These must never affect authorship verification for a pending record. They are
# either compatibility projections (actor_identity, boundary) or append-assigned
# chain-integrity metadata (record_id, record_index, hashes, etc.).
UNSIGNED_PROJECTION_FIELDS = frozenset({
    "actor_identity",
    "boundary",
    "boundary_acknowledgement",
    "server_normalization",
    "server_append_metadata",
    "append_assigned_metadata",
    "authorship_verification_status",
    "record_id",
    "record_index",
    "assigned_at",
    "previous_record_sha256",
    "content_sha256",
    "content_sha256_v2",
    "record_sha256",
    "chain_id",
    "what_i_checked",
    "limitations",
    "related_records",
    "immutability_policy",
})


def strip_unsigned_projection_fields(record_draft: dict[str, Any]) -> dict[str, Any]:
    """Return a copy without server-derived or append-assigned projection fields.

    This helper is intentionally shallow because all current projection fields
    are top-level. It preserves the participant-authored nested draft content.
    """
    cleaned = dict(record_draft)
    for field in UNSIGNED_PROJECTION_FIELDS:
        cleaned.pop(field, None)
    return cleaned


# Required claim_boundary keys that must be True
_REQUIRED_CLAIM_BOUNDARY_KEYS = frozenset({
    "not authority",
    "not attestation",
    "not amendment",
})


def strip_authorship_for_signing(record_draft: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of *record_draft* with proof material removed.

    The proof cannot sign itself, so it must be stripped before computing the
    signed payload.

    This function intentionally does not strip server projection fields. Call
    strip_unsigned_projection_fields() first when verifying a pending record
    that may contain server-derived projection fields.
    """
    cleaned = dict(record_draft)
    cleaned.pop("authorship_proof", None)
    cleaned.pop("proof", None)
    return cleaned


def signed_payload_sha256(record_draft: dict[str, Any]) -> str:
    """Compute the SHA-256 hex digest of the canonical JSON of *record_draft*.

    This is the payload that the author signs.
    """
    return sha256_bytes(canonical_bytes(record_draft))


def public_key_sha256_from_pem(public_key_pem: str) -> str:
    """Return the SHA-256 hex digest of the raw public-key bytes (32 bytes for Ed25519)."""
    key = load_pem_public_key(public_key_pem.encode("utf-8") if isinstance(public_key_pem, str) else public_key_pem)
    raw = key.public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )
    return sha256_bytes(raw)


def _extract_signature_b64(proof: dict[str, Any]) -> str | None:
    """Extract signature_base64, accepting 'signature' as a legacy alias."""
    sig = proof.get("signature_base64")
    if sig is not None:
        return sig
    return proof.get("signature")  # legacy alias


def _check_claim_boundary(proof: dict[str, Any]) -> str | None:
    """Verify that claim_boundary contains all required keys set to True.

    Returns an error message string on failure, None on success.
    """
    boundary = proof.get("claim_boundary")
    if boundary is None:
        return "authorship_proof missing required 'claim_boundary'"
    if not isinstance(boundary, dict):
        return "'claim_boundary' must be a JSON object (not a string)"

    for key in _REQUIRED_CLAIM_BOUNDARY_KEYS:
        if boundary.get(key) is not True:
            return (
                f"claim_boundary.'{key}' must be boolean true; "
                f"author cannot claim authority/attestation/amendment"
            )
    return None


def verify_authorship_proof(
    record_draft: dict[str, Any],
    proof: dict[str, Any],
) -> tuple[bool, str | None]:
    """Verify an Ed25519 authorship proof against *record_draft*.

    Parameters
    ----------
    record_draft:
        The record draft object (will be canonicalised before hashing).
        authorship_proof is stripped before computing the signed payload.
    proof:
        The authorship proof dict. Expected shape:
        - ``schema``: proof schema identifier (optional)
        - ``method``: signing method, e.g. "ed25519" (optional)
        - ``algorithm``: algorithm identifier (optional)
        - ``public_key_pem``: PEM-encoded Ed25519 public key (required)
        - ``public_key_sha256``: SHA-256 hex of raw public key bytes (verified if present)
        - ``signed_payload_sha256``: SHA-256 hex of canonical draft bytes (verified if present)
        - ``signature_base64`` (or legacy ``signature``): Base-64 Ed25519 signature (required)
        - ``signed_message``: human-readable message (optional)
        - ``claim_boundary``: dict with required boundary claims (required)

    Returns
    -------
    (ok, error_message)
        ``ok`` is ``True`` when the signature is valid; ``error_message`` is
        ``None`` on success or a human-readable explanation on failure.
    """
    # --- extract fields ---
    pub_pem = proof.get("public_key_pem")
    sig_b64 = _extract_signature_b64(proof)

    if not pub_pem:
        return False, "authorship_proof must contain 'public_key_pem'"
    if not sig_b64:
        return False, "authorship_proof must contain 'signature_base64' (or legacy 'signature')"

    # --- claim boundary check ---
    boundary_err = _check_claim_boundary(proof)
    if boundary_err:
        return False, boundary_err

    # --- load public key ---
    try:
        if isinstance(pub_pem, str):
            pub_pem_bytes = pub_pem.encode("utf-8")
        else:
            pub_pem_bytes = pub_pem
        public_key: Ed25519PublicKey = load_pem_public_key(pub_pem_bytes)  # type: ignore[assignment]
    except Exception as exc:
        logger.debug("Failed to load public key: %s", exc)
        return False, f"Invalid public key PEM: {exc}"

    if not isinstance(public_key, Ed25519PublicKey):
        return False, "Public key must be Ed25519"

    # --- verify public_key_sha256 if supplied ---
    expected_pub_sha = proof.get("public_key_sha256")
    if expected_pub_sha is not None:
        raw_pub = public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )
        actual_pub_sha = sha256_bytes(raw_pub)
        if actual_pub_sha != expected_pub_sha:
            return False, (
                f"public_key_sha256 mismatch: expected {actual_pub_sha}, "
                f"got {expected_pub_sha}"
            )

    # --- decode signature ---
    try:
        signature = base64.b64decode(sig_b64)
    except Exception as exc:
        return False, f"Invalid base64 signature: {exc}"

    # --- compute expected payload (strip proof from draft first) ---
    draft_for_signing = strip_authorship_for_signing(record_draft)
    payload = canonical_bytes(draft_for_signing)

    # --- verify signed_payload_sha256 if supplied ---
    expected_payload_sha = proof.get("signed_payload_sha256")
    if expected_payload_sha is not None:
        actual_payload_sha = sha256_bytes(payload)
        if actual_payload_sha != expected_payload_sha:
            return False, (
                f"signed_payload_sha256 mismatch: expected {actual_payload_sha}, "
                f"got {expected_payload_sha}"
            )

    # --- verify signature ---
    try:
        public_key.verify(signature, payload)
    except InvalidSignature:
        return False, "Ed25519 signature verification failed"
    except Exception as exc:
        logger.warning("Unexpected verification error: %s", exc)
        return False, f"Verification error: {exc}"

    return True, None


def verify_authorship_proof_submission(
    submission: dict[str, Any],
) -> tuple[bool, str | None, str | None]:
    """Verify an Ed25519 authorship proof from a full submission dict.

    This is the submission-level entry point used by the gateway intake.
    It extracts the proof from the submission, validates structure, verifies
    the signature, and checks key bindings.

    Parameters
    ----------
    submission:
        The full submission dict containing ``authorship_proof`` and ``record_draft``.

    Returns
    -------
    (ok, error_code, error_message)
        ``ok`` is ``True`` when the proof is valid; ``error_code`` and
        ``error_message`` are ``None`` on success.
    """
    proof = submission.get("authorship_proof")
    if not isinstance(proof, dict):
        return False, "MISSING_AUTHORSHIP_PROOF", "Missing top-level authorship_proof."

    # Check schema/method/algorithm
    if proof.get("schema") != "trinityaccord.agent-authorship-proof.v1":
        return False, "INVALID_AUTHORSHIP_SCHEMA", "Invalid authorship proof schema."
    if proof.get("method") != "public_key_signature":
        return False, "INVALID_AUTHORSHIP_METHOD", "Invalid authorship proof method."
    if proof.get("algorithm") != "ed25519":
        return False, "INVALID_AUTHORSHIP_ALGORITHM", "Authorship proof must use Ed25519."

    public_key_pem = proof.get("public_key_pem")
    public_key_sha256 = proof.get("public_key_sha256")
    signed_payload_sha256 = proof.get("signed_payload_sha256")
    signature_base64 = proof.get("signature_base64")

    if not isinstance(public_key_pem, str) or "BEGIN PUBLIC KEY" not in public_key_pem:
        return False, "INVALID_AUTHORSHIP_PUBLIC_KEY", "Invalid or missing public_key_pem."
    if "PRIVATE KEY" in public_key_pem:
        return False, "PRIVATE_KEY_LEAK", "Private key material appears in public key field."
    import re as _re
    if not isinstance(public_key_sha256, str) or not _re.fullmatch(r"[a-f0-9]{64}", public_key_sha256):
        return False, "INVALID_AUTHORSHIP_PUBLIC_KEY_SHA", "Invalid public_key_sha256."
    if not isinstance(signed_payload_sha256, str) or not _re.fullmatch(r"[a-f0-9]{64}", signed_payload_sha256):
        return False, "INVALID_AUTHORSHIP_SIGNED_PAYLOAD_SHA", "Invalid signed_payload_sha256."
    if not isinstance(signature_base64, str) or not signature_base64:
        return False, "INVALID_AUTHORSHIP_SIGNATURE", "Missing signature_base64."

    boundary_err = _check_claim_boundary(proof)
    if boundary_err:
        return False, "AUTHORSHIP_CLAIM_BOUNDARY_INVALID", boundary_err

    draft = submission.get("record_draft")
    if not isinstance(draft, dict):
        return False, "MISSING_RECORD_DRAFT", "Missing record_draft."

    # Verify payload hash
    draft_for_signing = strip_authorship_for_signing(draft)
    payload = canonical_bytes(draft_for_signing)
    payload_sha = sha256_bytes(payload)
    if payload_sha != signed_payload_sha256:
        return False, "AUTHORSHIP_PAYLOAD_SHA_MISMATCH", "record_draft hash does not match signed_payload_sha256."
    if proof.get("signed_message") != payload_sha:
        return False, "AUTHORSHIP_SIGNED_MESSAGE_MISMATCH", "signed_message does not match record_draft hash."

    # Load and verify public key
    try:
        public_key = load_pem_public_key(public_key_pem.encode("utf-8"))
        if not isinstance(public_key, Ed25519PublicKey):
            return False, "AUTHORSHIP_PUBLIC_KEY_NOT_ED25519", "Public key is not Ed25519."

        raw_public = public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )
        actual_pub_sha = sha256_bytes(raw_public)
        if actual_pub_sha != public_key_sha256:
            return False, "AUTHORSHIP_PUBLIC_KEY_SHA_MISMATCH", "public_key_sha256 does not match public_key_pem."

        signature = base64.b64decode(signature_base64, validate=True)
        public_key.verify(signature, payload)
    except InvalidSignature:
        return False, "AUTHORSHIP_SIGNATURE_INVALID", "Ed25519 signature is invalid."
    except Exception:
        return False, "AUTHORSHIP_VERIFICATION_ERROR", "Could not verify authorship proof."

    # Check participant key binding
    spi = draft.get("submitting_participant_identity") or {}
    if spi.get("participant_public_key_sha256") != public_key_sha256:
        return False, "PARTICIPANT_KEY_MISMATCH", "participant_public_key_sha256 must match authorship_proof.public_key_sha256."

    # Check Guardian key binding. Guardian applications and retirements are
    # key-continuity events: the public Guardian key named by the record must be
    # the same Ed25519 key that signed the authorship proof. Otherwise any
    # participant could file a retirement/exit notice for another Guardian.
    if draft.get("record_type") == "guardian_application":
        guardian_key = (draft.get("guardian_application_content") or {}).get("guardian_public_key_sha256")
        if guardian_key != public_key_sha256:
            return False, "GUARDIAN_KEY_MISMATCH", "guardian_public_key_sha256 must match authorship_proof.public_key_sha256."

    if draft.get("record_type") == "guardian_retirement":
        guardian_key = draft.get("guardian_public_key_sha256")
        if guardian_key != public_key_sha256:
            return False, "GUARDIAN_RETIREMENT_KEY_MISMATCH", "guardian_retirement.guardian_public_key_sha256 must match authorship_proof.public_key_sha256."

    # Check linked guardian key binding
    linked = draft.get("optional_linked_guardian_application_request")
    if isinstance(linked, dict) and linked.get("does_participant_request_guardian_application_with_this_record") is True:
        linked_key = linked.get("guardian_public_key_sha256")
        if linked_key and linked_key != public_key_sha256:
            return False, "LINKED_GUARDIAN_KEY_MISMATCH", "linked guardian_public_key_sha256 must match authorship_proof.public_key_sha256."

    # Security scan for private key leaks
    raw = json.dumps(submission, ensure_ascii=False)
    if "BEGIN PRIVATE KEY" in raw or "authorship-private.pem" in raw:
        return False, "PRIVATE_KEY_LEAK", "Private key material must not appear in submission."

    return True, None, None
