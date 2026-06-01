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

from gateway.canonical import canonical_bytes, sha256_bytes

logger = logging.getLogger(__name__)


def signed_payload_sha256(record_draft: dict[str, Any]) -> str:
    """Compute the SHA-256 hex digest of the canonical JSON of *record_draft*.

    This is the payload that the author signs.
    """
    return sha256_bytes(canonical_bytes(record_draft))


def public_key_sha256(public_key_pem: str) -> str:
    """Return the SHA-256 hex digest of the raw public-key bytes (32 bytes for Ed25519)."""
    key = load_pem_public_key(public_key_pem.encode("utf-8") if isinstance(public_key_pem, str) else public_key_pem)
    raw = key.public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )
    return sha256_bytes(raw)


def verify_authorship_proof(
    record_draft: dict[str, Any],
    proof: dict[str, Any],
) -> tuple[bool, str | None]:
    """Verify an Ed25519 authorship proof against *record_draft*.

    Parameters
    ----------
    record_draft:
        The record draft object (will be canonicalised before hashing).
    proof:
        Must contain:
        - ``public_key_pem``: PEM-encoded Ed25519 public key
        - ``signature``: Base-64 encoded Ed25519 signature over the canonical
          JSON hash of *record_draft*.

    Returns
    -------
    (ok, error_message)
        ``ok`` is ``True`` when the signature is valid; ``error_message`` is
        ``None`` on success or a human-readable explanation on failure.
    """
    pub_pem = proof.get("public_key_pem")
    sig_b64 = proof.get("signature")

    if not pub_pem or not sig_b64:
        return False, "authorship_proof must contain 'public_key_pem' and 'signature'"

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

    # --- decode signature ---
    try:
        signature = base64.b64decode(sig_b64)
    except Exception as exc:
        return False, f"Invalid base64 signature: {exc}"

    # --- compute expected payload ---
    payload = canonical_bytes(record_draft)

    # --- verify ---
    try:
        public_key.verify(signature, payload)
    except InvalidSignature:
        return False, "Ed25519 signature verification failed"
    except Exception as exc:
        logger.warning("Unexpected verification error: %s", exc)
        return False, f"Verification error: {exc}"

    return True, None
