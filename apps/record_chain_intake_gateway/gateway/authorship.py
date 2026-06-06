from __future__ import annotations

import base64
import hashlib
import json
import re
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def verify_authorship_proof(submission: dict[str, Any]) -> tuple[bool, str | None, str | None]:
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
    signed_payload_sha256 = proof.get("signed_payload_sha256")
    signature_base64 = proof.get("signature_base64")

    if not isinstance(public_key_pem, str) or "BEGIN PUBLIC KEY" not in public_key_pem:
        return False, "INVALID_AUTHORSHIP_PUBLIC_KEY", "Invalid or missing public_key_pem."
    if "PRIVATE KEY" in public_key_pem:
        return False, "PRIVATE_KEY_LEAK", "Private key material appears in public key field."
    if not isinstance(public_key_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", public_key_sha256):
        return False, "INVALID_AUTHORSHIP_PUBLIC_KEY_SHA", "Invalid public_key_sha256."
    if not isinstance(signed_payload_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", signed_payload_sha256):
        return False, "INVALID_AUTHORSHIP_SIGNED_PAYLOAD_SHA", "Invalid signed_payload_sha256."
    if not isinstance(signature_base64, str) or not signature_base64:
        return False, "INVALID_AUTHORSHIP_SIGNATURE", "Missing signature_base64."

    draft = submission.get("record_draft")
    if not isinstance(draft, dict):
        return False, "MISSING_RECORD_DRAFT", "Missing record_draft."

    payload = canonical_json_bytes(draft)
    payload_sha = hashlib.sha256(payload).hexdigest()
    if payload_sha != signed_payload_sha256:
        return False, "AUTHORSHIP_PAYLOAD_SHA_MISMATCH", "record_draft hash does not match signed_payload_sha256."
    if proof.get("signed_message") != payload_sha:
        return False, "AUTHORSHIP_SIGNED_MESSAGE_MISMATCH", "signed_message does not match record_draft hash."

    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
        if not isinstance(public_key, Ed25519PublicKey):
            return False, "AUTHORSHIP_PUBLIC_KEY_NOT_ED25519", "Public key is not Ed25519."

        raw_public = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        actual_pub_sha = hashlib.sha256(raw_public).hexdigest()
        if actual_pub_sha != public_key_sha256:
            return False, "AUTHORSHIP_PUBLIC_KEY_SHA_MISMATCH", "public_key_sha256 does not match public_key_pem."

        signature = base64.b64decode(signature_base64, validate=True)
        public_key.verify(signature, payload)
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

    linked = draft.get("optional_linked_guardian_application_request")
    if isinstance(linked, dict) and linked.get("does_participant_request_guardian_application_with_this_record") is True:
        linked_key = linked.get("guardian_public_key_sha256")
        if linked_key and linked_key != public_key_sha256:
            return False, "LINKED_GUARDIAN_KEY_MISMATCH", "linked guardian_public_key_sha256 must match authorship_proof.public_key_sha256."

    raw = json.dumps(submission, ensure_ascii=False)
    if "BEGIN PRIVATE KEY" in raw or "authorship-private.pem" in raw:
        return False, "PRIVATE_KEY_LEAK", "Private key material must not appear in submission."

    return True, None, None
