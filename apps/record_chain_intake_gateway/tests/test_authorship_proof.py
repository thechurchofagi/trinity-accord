from __future__ import annotations

import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from gateway.authorship import verify_authorship_proof, verify_authorship_proof_submission
from gateway.canonical import canonical_bytes, sha256_bytes


def _signed_submission(draft: dict) -> dict:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    public_sha = sha256_bytes(public_key.public_bytes(Encoding.Raw, PublicFormat.Raw))
    draft = dict(draft)
    draft.setdefault("submitting_participant_identity", {})[
        "participant_public_key_sha256"
    ] = public_sha
    payload = canonical_bytes(draft)
    payload_sha = sha256_bytes(payload)
    proof = {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_pem": public_pem,
        "public_key_sha256": public_sha,
        "signed_payload_sha256": payload_sha,
        "signed_message": payload_sha,
        "signature_base64": base64.b64encode(private_key.sign(payload)).decode("ascii"),
        "claim_boundary": {
            "not authority": True,
            "not attestation": True,
            "not amendment": True,
        },
    }
    return {"record_draft": draft, "authorship_proof": proof}


def test_submission_rejects_created_at_added_after_signing() -> None:
    submission = _signed_submission({
        "record_type": "echo",
        "echo_content": {"echo_intent": "recognition", "echo_text": "hello"},
    })
    submission["record_draft"]["created_at"] = "2099-01-01T00:00:00Z"

    ok, code, _message = verify_authorship_proof_submission(submission)

    assert ok is False
    assert code == "AUTHORSHIP_PAYLOAD_SHA_MISMATCH"


def test_repository_pending_recovery_still_accepts_gateway_added_created_at() -> None:
    submission = _signed_submission({
        "record_type": "echo",
        "echo_content": {"echo_intent": "recognition", "echo_text": "hello"},
    })
    pending = dict(submission["record_draft"])
    pending["created_at"] = "2026-07-12T00:00:00Z"

    ok, error = verify_authorship_proof(pending, submission["authorship_proof"])

    assert ok is True, error
