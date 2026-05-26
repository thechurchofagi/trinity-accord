#!/usr/bin/env python3
"""Common helpers for Guardian Alliance verification.

Shared by Guardian proof attachment, verification, and status scripts.
"""
import copy
import hashlib
import json


DYNAMIC_PROOF_FIELDS = (
    "authorship_proof",
    "_authorship_claim",
    "guardian_presence_proof",
    "_guardian_status",
    "guardian_verification_result",
)


def sha256_text(text: str) -> str:
    """Return lowercase hex sha256 of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_pem(public_key_pem: str) -> str:
    """Strip outer whitespace and return PEM with exactly one trailing newline."""
    return public_key_pem.strip() + "\n"


def public_key_sha256(public_key_pem: str) -> str:
    """Hash normalized PEM text."""
    return sha256_text(normalize_pem(public_key_pem))


def guardian_id_from_public_key(public_key_pem: str) -> str:
    """Derive guardian_id from public key."""
    return "guardian_ed25519_" + public_key_sha256(public_key_pem)[:16]


def canonical_payload_for_guardian_signature(payload: dict) -> str:
    """Return canonical JSON for Guardian signature.

    Guardian proof signs the submitted record content while excluding
    dynamic proof/result wrappers that may be attached later.

    It intentionally keeps guardian_registration and guardian_retirement
    if present, because those are substantive record claims.
    """
    data = copy.deepcopy(payload)
    for field in DYNAMIC_PROOF_FIELDS:
        data.pop(field, None)
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def guardian_payload_sha256(payload: dict) -> str:
    """Hash canonical payload for Guardian signature."""
    return sha256_text(canonical_payload_for_guardian_signature(payload))


def build_guardian_presence_message(payload: dict, public_key_pem: str, challenge: str) -> str:
    """Build the TRINITY_GUARDIAN_PRESENCE_PROOF_V1 canonical message."""
    guardian_id = guardian_id_from_public_key(public_key_pem)
    return "\n".join([
        "TRINITY_GUARDIAN_PRESENCE_PROOF_V1",
        "proof_mode=record_bound",
        f"guardian_id={guardian_id}",
        f"payload_sha256={guardian_payload_sha256(payload)}",
        f"challenge_sha256={sha256_text(challenge)}",
        f"schema={payload.get('schema', '')}",
        f"submission_type={payload.get('submission_type', '')}",
        f"requested_archive_kind={payload.get('requested_archive_kind', '')}",
        "boundary=key_possession_only_not_authority_not_attestation_not_same_conscious_subject",
    ])


REQUIRED_DOES_NOT_PROVE = [
    "truth",
    "authority",
    "verification_level",
    "verification_correctness",
    "formal_attestation",
    "same_conscious_subject",
    "same_model_instance",
    "human_identity",
    "institutional_authorization",
    "successor_reception",
    "future_intelligence_obligation",
    "amendment",
]
