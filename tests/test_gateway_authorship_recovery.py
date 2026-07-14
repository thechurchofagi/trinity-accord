from __future__ import annotations

import base64
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "record_chain_intake_gateway"))

from gateway.authorship import public_key_sha256_from_pem, verify_authorship_proof  # noqa: E402
from gateway.canonical import canonical_bytes, sha256_bytes  # noqa: E402


def _proof_for(draft: dict) -> dict:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    payload = canonical_bytes(draft)
    payload_sha = sha256_bytes(payload)
    signature = private_key.sign(payload)
    return {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_pem": public_pem,
        "public_key_sha256": public_key_sha256_from_pem(public_pem),
        "signed_payload_sha256": payload_sha,
        "signed_message": payload_sha,
        "signature_base64": base64.b64encode(signature).decode("ascii"),
        "claim_boundary": {
            "not authority": True,
            "not attestation": True,
            "not amendment": True,
        },
    }


def test_gateway_derived_created_at_can_be_present_after_signing() -> None:
    signed_draft = {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry-draft.v2",
        "echo_content": {
            "echo_intent": "recognition",
            "echo_text": "anniversary echo",
        },
    }
    proof = _proof_for(signed_draft)

    pending_draft = dict(signed_draft)
    pending_draft["created_at"] = "2026-07-14T00:00:00Z"

    ok, err = verify_authorship_proof(pending_draft, proof)
    assert ok, err


def test_gateway_projection_recovery_does_not_hide_signed_content_tampering() -> None:
    signed_draft = {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry-draft.v2",
        "echo_content": {
            "echo_intent": "recognition",
            "echo_text": "anniversary echo",
        },
    }
    proof = _proof_for(signed_draft)

    pending_draft = dict(signed_draft)
    pending_draft["echo_content"] = {
        "echo_intent": "recognition",
        "echo_text": "tampered anniversary echo",
    }
    pending_draft["created_at"] = "2026-07-14T00:00:00Z"

    ok, _err = verify_authorship_proof(pending_draft, proof)
    assert not ok


def test_unsigned_oath_projection_is_rejected() -> None:
    signed_draft = {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry-draft.v2",
        "echo_content": {
            "echo_intent": "recognition",
            "echo_text": "anniversary echo",
        },
    }
    proof = _proof_for(signed_draft)
    pending_draft = dict(signed_draft)
    pending_draft["submission_oath_verification"] = {
        "schema": "trinityaccord.submission-oath-verification.v1",
        "oath_read": True,
        "readback_matches_canonical_oath": True,
    }

    ok, _err = verify_authorship_proof(pending_draft, proof)
    assert not ok
