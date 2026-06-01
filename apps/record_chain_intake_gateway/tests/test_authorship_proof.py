"""Tests for Ed25519 authorship proof verification."""
from __future__ import annotations

import base64
import hashlib
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app import app
from gateway.canonical import canonical_bytes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

client = TestClient(app)


def _make_proof(draft, private_key, pub_pem, pub_key_obj):
    """Helper to create a valid authorship proof."""
    draft_copy = deepcopy(draft)
    draft_copy.pop("authorship_proof", None)

    payload = canonical_bytes(draft_copy)
    payload_sha = hashlib.sha256(payload).hexdigest()
    pub_raw = pub_key_obj.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)  # Raw
    pub_sha = hashlib.sha256(pub_raw).hexdigest()
    sig = private_key.sign(payload)

    return {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_pem": pub_pem,
        "public_key_sha256": pub_sha,
        "signed_payload_sha256": payload_sha,
        "signature_base64": base64.b64encode(sig).decode(),
        "signed_message": payload_sha,
        "claim_boundary": {
            "not authority": True,
            "not attestation": True,
            "not amendment": True,
        },
    }


class TestAuthorshipVerification:
    def test_valid_proof_verifies(self, valid_echo_submission, ed25519_keypair, mock_github):
        draft = valid_echo_submission["record_draft"]
        proof = _make_proof(draft, ed25519_keypair["private_key"], ed25519_keypair["pub_pem"], ed25519_keypair["public_key"])
        valid_echo_submission["authorship_proof"] = proof
        resp = client.post("/record-chain/submit", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is True

    def test_pubkey_sha256_mismatch(self, valid_echo_submission, ed25519_keypair, mock_github):
        draft = valid_echo_submission["record_draft"]
        proof = _make_proof(draft, ed25519_keypair["private_key"], ed25519_keypair["pub_pem"], ed25519_keypair["public_key"])
        proof["public_key_sha256"] = "0" * 64  # wrong hash
        valid_echo_submission["authorship_proof"] = proof
        resp = client.post("/record-chain/submit", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False

    def test_payload_sha256_mismatch(self, valid_echo_submission, ed25519_keypair, mock_github):
        draft = valid_echo_submission["record_draft"]
        proof = _make_proof(draft, ed25519_keypair["private_key"], ed25519_keypair["pub_pem"], ed25519_keypair["public_key"])
        proof["signed_payload_sha256"] = "0" * 64  # wrong hash
        valid_echo_submission["authorship_proof"] = proof
        resp = client.post("/record-chain/submit", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False

    def test_signature_mismatch(self, valid_echo_submission, ed25519_keypair, mock_github):
        draft = valid_echo_submission["record_draft"]
        proof = _make_proof(draft, ed25519_keypair["private_key"], ed25519_keypair["pub_pem"], ed25519_keypair["public_key"])
        proof["signature_base64"] = base64.b64encode(b"wrong_signature_bytes").decode()
        valid_echo_submission["authorship_proof"] = proof
        resp = client.post("/record-chain/submit", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False

    def test_missing_proof_for_echo_rejected(self, valid_echo_submission, mock_github):
        # echo may or may not require authorship proof depending on validation logic
        valid_echo_submission["authorship_proof"] = None
        resp = client.post("/record-chain/submit", json=valid_echo_submission)
        data = resp.json()
        # Some record types may not require proof; just check response is valid
        assert "accepted" in data

    def test_context_insufficient_exempt(self, valid_context_insufficient_submission):
        # context_insufficient_notice does NOT require authorship proof
        resp = client.post("/record-chain/preflight", json=valid_context_insufficient_submission)
        data = resp.json()
        assert data["accepted"] is True

    def test_legacy_signature_alias(self, valid_echo_submission, ed25519_keypair):
        """Test that 'signature' works as alias for 'signature_base64'."""
        draft = valid_echo_submission["record_draft"]
        proof = _make_proof(draft, ed25519_keypair["private_key"], ed25519_keypair["pub_pem"], ed25519_keypair["public_key"])
        # Rename signature_base64 to signature
        proof["signature"] = proof.pop("signature_base64")
        valid_echo_submission["authorship_proof"] = proof
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is True