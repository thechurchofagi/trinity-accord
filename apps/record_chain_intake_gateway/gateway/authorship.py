# gateway/authorship.py
"""Ed25519 authorship verification utilities."""

from __future__ import annotations

import base64
import json
import logging
import re
from itertools import combinations
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_pem_public_key

from .canonical import canonical_bytes, sha256_bytes

logger = logging.getLogger(__name__)

UNSIGNED_PROJECTION_FIELDS = frozenset({
    "actor_identity", "boundary", "boundary_acknowledgement", "server_normalization",
    "server_append_metadata", "append_assigned_metadata", "authorship_verification_status",
    "record_id", "record_index", "assigned_at", "previous_record_sha256", "content_sha256",
    "content_sha256_v2", "record_sha256", "chain_id", "what_i_checked", "limitations",
    "related_records", "immutability_policy",
})

# Gateway intake and system automation may materialize these top-level projection
# fields after the original builder draft was signed. Final re-verification tries
# both the current signed domain and narrow projection-recovery domains.
GATEWAY_DERIVED_UNSIGNED_FIELDS = frozenset({"created_at", "system_waiting_heartbeat"})

_REQUIRED_CLAIM_BOUNDARY_KEYS = frozenset({"not authority", "not attestation", "not amendment"})


def strip_unsigned_projection_fields(record_draft: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(record_draft)
    for field in UNSIGNED_PROJECTION_FIELDS:
        cleaned.pop(field, None)
    return cleaned


def strip_gateway_derived_unsigned_fields(record_draft: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(record_draft)
    for field in GATEWAY_DERIVED_UNSIGNED_FIELDS:
        cleaned.pop(field, None)
    return cleaned


def strip_authorship_for_signing(record_draft: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(record_draft)
    cleaned.pop("authorship_proof", None)
    cleaned.pop("proof", None)
    return cleaned


def _append_unique_candidate(candidates: list[tuple[str, dict[str, Any], bytes, str]], scope: str, draft: dict[str, Any]) -> None:
    payload = canonical_bytes(draft)
    payload_sha = sha256_bytes(payload)
    if any(existing_sha == payload_sha for *_rest, existing_sha in candidates):
        return
    candidates.append((scope, draft, payload, payload_sha))


def _signing_payload_candidates(record_draft: dict[str, Any]) -> list[tuple[str, dict[str, Any], bytes, str]]:
    primary_draft = strip_authorship_for_signing(record_draft)
    candidates: list[tuple[str, dict[str, Any], bytes, str]] = []
    _append_unique_candidate(candidates, "record_draft", primary_draft)

    present_projection_fields = [field for field in sorted(GATEWAY_DERIVED_UNSIGNED_FIELDS) if field in primary_draft]
    for size in range(1, len(present_projection_fields) + 1):
        for fields in combinations(present_projection_fields, size):
            recovered = dict(primary_draft)
            for field in fields:
                recovered.pop(field, None)
            scope = "record_draft_without_" + "_and_".join(fields)
            _append_unique_candidate(candidates, scope, recovered)

    return candidates


def signed_payload_sha256(record_draft: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(record_draft))


def public_key_sha256_from_pem(public_key_pem: str) -> str:
    key = load_pem_public_key(public_key_pem.encode("utf-8") if isinstance(public_key_pem, str) else public_key_pem)
    raw = key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
    return sha256_bytes(raw)


def _extract_signature_b64(proof: dict[str, Any]) -> str | None:
    sig = proof.get("signature_base64")
    return sig if sig is not None else proof.get("signature")


def _check_claim_boundary(proof: dict[str, Any]) -> str | None:
    boundary = proof.get("claim_boundary")
    if boundary is None:
        return "authorship_proof missing required 'claim_boundary'"
    if not isinstance(boundary, dict):
        return "'claim_boundary' must be a JSON object (not a string)"
    for key in _REQUIRED_CLAIM_BOUNDARY_KEYS:
        if boundary.get(key) is not True:
            return f"claim_boundary.'{key}' must be boolean true; author cannot claim authority/attestation/amendment"
    return None


def _load_public_key(pub_pem: Any) -> tuple[Ed25519PublicKey | None, str | None]:
    try:
        public_key = load_pem_public_key(pub_pem.encode("utf-8") if isinstance(pub_pem, str) else pub_pem)
    except Exception as exc:
        logger.debug("Failed to load public key: %s", exc)
        return None, f"Invalid public key PEM: {exc}"
    if not isinstance(public_key, Ed25519PublicKey):
        return None, "Public key must be Ed25519"
    return public_key, None


def _verify_public_key_sha(public_key: Ed25519PublicKey, expected_pub_sha: Any) -> str | None:
    if expected_pub_sha is None:
        return None
    actual_pub_sha = sha256_bytes(public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw))
    if actual_pub_sha != expected_pub_sha:
        return f"public_key_sha256 mismatch: expected {actual_pub_sha}, got {expected_pub_sha}"
    return None


def verify_authorship_proof(record_draft: dict[str, Any], proof: dict[str, Any]) -> tuple[bool, str | None]:
    pub_pem = proof.get("public_key_pem")
    sig_b64 = _extract_signature_b64(proof)
    if not pub_pem:
        return False, "authorship_proof must contain 'public_key_pem'"
    if not sig_b64:
        return False, "authorship_proof must contain 'signature_base64' (or legacy 'signature')"

    boundary_err = _check_claim_boundary(proof)
    if boundary_err:
        return False, boundary_err

    public_key, key_err = _load_public_key(pub_pem)
    if public_key is None:
        return False, key_err

    pub_sha_err = _verify_public_key_sha(public_key, proof.get("public_key_sha256"))
    if pub_sha_err:
        return False, pub_sha_err

    try:
        signature = base64.b64decode(sig_b64)
    except Exception as exc:
        return False, f"Invalid base64 signature: {exc}"

    expected_payload_sha = proof.get("signed_payload_sha256")
    last_payload_sha: str | None = None
    matched_payload = False
    for scope, _candidate_draft, payload, actual_payload_sha in _signing_payload_candidates(record_draft):
        last_payload_sha = actual_payload_sha
        if expected_payload_sha is not None and actual_payload_sha != expected_payload_sha:
            continue
        matched_payload = True
        try:
            public_key.verify(signature, payload)
            if scope != "record_draft":
                logger.info("Authorship proof verified using projection recovery scope: %s", scope)
            return True, None
        except InvalidSignature:
            continue
        except Exception as exc:
            logger.warning("Unexpected verification error: %s", exc)
            return False, f"Verification error: {exc}"

    if expected_payload_sha is not None and not matched_payload:
        return False, f"signed_payload_sha256 mismatch: expected {last_payload_sha}, got {expected_payload_sha}"
    return False, "Ed25519 signature verification failed"


def verify_authorship_proof_submission(submission: dict[str, Any]) -> tuple[bool, str | None, str | None]:
    proof = submission.get("authorship_proof")
    if not isinstance(proof, dict):
        return False, "MISSING_AUTHORSHIP_PROOF", "Missing top-level authorship_proof."

    if proof.get("schema") != "trinityaccord.agent-authorship-proof.v1":
        return False, "INVALID_AUTHORSHIP_SCHEMA", "Invalid authorship proof schema."
    if proof.get("method") != "public_key_signature":
        return False, "INVALID_AUTHORSHIP_METHOD", "Invalid authorship proof method."
    if proof.get("algorithm") != "ed25519":
        return False, "INVALID_AUTHORSHIP_ALGORITHM", "Authorship proof must use Ed25519."

    public_key_pem = proof.get("public_key_pem")
    public_key_sha256 = proof.get("public_key_sha256")
    expected_payload_sha = proof.get("signed_payload_sha256")
    signature_base64 = proof.get("signature_base64")

    public_header = "BEGIN " + "PUBLIC KEY"
    private_marker = "BEGIN " + "PRIVATE KEY"
    private_filename = "authorship-" + "private.pem"

    if not isinstance(public_key_pem, str) or public_header not in public_key_pem:
        return False, "INVALID_AUTHORSHIP_PUBLIC_KEY", "Invalid or missing public_key_pem."
    if private_marker in public_key_pem:
        return False, "PRIVATE_KEY_LEAK", "Private key material appears in public key field."
    if not isinstance(public_key_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", public_key_sha256):
        return False, "INVALID_AUTHORSHIP_PUBLIC_KEY_SHA", "Invalid public_key_sha256."
    if not isinstance(expected_payload_sha, str) or not re.fullmatch(r"[a-f0-9]{64}", expected_payload_sha):
        return False, "INVALID_AUTHORSHIP_SIGNED_PAYLOAD_SHA", "Invalid signed_payload_sha256."
    if not isinstance(signature_base64, str) or not signature_base64:
        return False, "INVALID_AUTHORSHIP_SIGNATURE", "Missing signature_base64."

    boundary_err = _check_claim_boundary(proof)
    if boundary_err:
        return False, "AUTHORSHIP_CLAIM_BOUNDARY_INVALID", boundary_err

    draft = submission.get("record_draft")
    if not isinstance(draft, dict):
        return False, "MISSING_RECORD_DRAFT", "Missing record_draft."

    payload: bytes | None = None
    payload_sha: str | None = None
    for scope, _candidate_draft, candidate_payload, candidate_sha in _signing_payload_candidates(draft):
        if candidate_sha == expected_payload_sha:
            payload = candidate_payload
            payload_sha = candidate_sha
            if scope != "record_draft":
                logger.info("Submission authorship verified using projection recovery scope: %s", scope)
            break
    if payload is None or payload_sha is None:
        primary_sha = _signing_payload_candidates(draft)[0][3]
        return False, "AUTHORSHIP_PAYLOAD_SHA_MISMATCH", f"record_draft hash does not match signed_payload_sha256: expected {primary_sha}, got {expected_payload_sha}."
    if proof.get("signed_message") != payload_sha:
        return False, "AUTHORSHIP_SIGNED_MESSAGE_MISMATCH", "signed_message does not match record_draft hash."

    try:
        public_key = load_pem_public_key(public_key_pem.encode("utf-8"))
        if not isinstance(public_key, Ed25519PublicKey):
            return False, "AUTHORSHIP_PUBLIC_KEY_NOT_ED25519", "Public key is not Ed25519."
        actual_pub_sha = sha256_bytes(public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw))
        if actual_pub_sha != public_key_sha256:
            return False, "AUTHORSHIP_PUBLIC_KEY_SHA_MISMATCH", "public_key_sha256 does not match public_key_pem."
        public_key.verify(base64.b64decode(signature_base64, validate=True), payload)
    except InvalidSignature:
        return False, "AUTHORSHIP_SIGNATURE_INVALID", "Ed25519 signature is invalid."
    except Exception:
        return False, "AUTHORSHIP_VERIFICATION_ERROR", "Could not verify authorship proof."

    spi = draft.get("submitting_participant_identity") or {}
    if spi.get("participant_public_key_sha256") != public_key_sha256:
        return False, "PARTICIPANT_KEY_MISMATCH", "participant_public_key_sha256 must match authorship_proof.public_key_sha256."

    if draft.get("record_type") == "guardian_application":
        guardian_key = (draft.get("guardian_application_content") or {}).get("guardian_public_key_sha256")
        if guardian_key != public_key_sha256:
            return False, "GUARDIAN_KEY_MISMATCH", "guardian_public_key_sha256 must match authorship_proof.public_key_sha256."

    if draft.get("record_type") == "guardian_retirement":
        guardian_key = draft.get("guardian_public_key_sha256")
        if guardian_key != public_key_sha256:
            return False, "GUARDIAN_RETIREMENT_KEY_MISMATCH", "guardian_retirement.guardian_public_key_sha256 must match authorship_proof.public_key_sha256."

    linked = draft.get("optional_linked_guardian_application_request")
    if isinstance(linked, dict) and linked.get("does_participant_request_guardian_application_with_this_record") is True:
        linked_key = linked.get("guardian_public_key_sha256")
        if linked_key and linked_key != public_key_sha256:
            return False, "LINKED_GUARDIAN_KEY_MISMATCH", "linked guardian_public_key_sha256 must match authorship_proof.public_key_sha256."

    raw = json.dumps(submission, ensure_ascii=False)
    if private_marker in raw or private_filename in raw:
        return False, "PRIVATE_KEY_LEAK", "Private key material must not appear in submission."

    return True, None, None
