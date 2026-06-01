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

from .canonical import canonical_bytes, sha256_bytes

logger = logging.getLogger(__name__)

# Required claim_boundary keys that must be True
_REQUIRED_CLAIM_BOUNDARY_KEYS = frozenset({
    "not authority",
    "not attestation",
    "not amendment",
})


def strip_authorship_for_signing(record_draft: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of *record_draft* with ``authorship_proof`` removed.

    The proof cannot sign itself, so it must be stripped before computing the
    signed payload.
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
        return "'claim_boundary' must be a JSON object"

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
