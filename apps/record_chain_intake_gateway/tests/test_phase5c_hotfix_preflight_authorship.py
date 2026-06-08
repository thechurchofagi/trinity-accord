"""Phase 5C hotfix tests: authorship proof required for formal records and preflight verification.

Tests that:
- Formal records without authorship_proof fail preflight with MISSING_AUTHORSHIP_PROOF
- Invalid signatures fail preflight with AUTHORSHIP_PROOF_INVALID
- Valid signatures pass preflight
"""
from __future__ import annotations

import base64

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi.testclient import TestClient

from app import app
from conftest import add_mock_proof
from gateway.authorship import canonical_bytes, sha256_bytes, strip_authorship_for_signing
from gateway.validation import validate_submission

client = TestClient(app)


def _make_echo_draft() -> dict:
    return {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry.v1",
        "created_at": "2026-06-01T00:00:00Z",
        "actor_identity": {"actor_type": "ai_agent", "display_label": "Test Agent"},
        "submitting_participant_identity": {
            "participant_public_display_label": "Test Agent",
            "participant_type": "ai_agent",
            "participant_identifier_disclosure_status": "not_disclosed",
            "participant_identity_disclosure_preference": "pseudonym_only",
        },
        "discovery_and_introduction_context": {"discovery_method": "direct_url"},
        "decision_autonomy_context": {"autonomy_level": "agent_initiated"},
        "submission_execution_context": {"builder_tool": "test"},
        "authorization_context": {"authorization_basis": "self_initiated"},
        "context_readiness": {
            "declared_context_level": 3,
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
        },
        "non_authority_boundary_acknowledgement": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True, "later_records_may_reclassify_or_correct_this_record": True,
        },
        "optional_linked_guardian_application_request": None,
        "payload": {"title": "Test", "body": "test body"},
    }


BOUNDARY = {
    "not_authority": True,
    "not_governance": True,
    "not_attestation": True,
    "not_successor_reception": True,
    "not_amendment": True,
    "bitcoin_originals_prevail": True,
    "receipt_is_not_final_inclusion": True,
    "receipt_is_intake_only": True, "later_records_may_reclassify_or_correct_this_record": True,
}


class TestMissingAuthorshipProof:
    """Formal records without authorship_proof must be rejected."""

    def test_echo_without_proof_rejected(self):
        sub = {
            "record_type": "echo",
            "record_draft": _make_echo_draft(),
            "boundary_acknowledgement": dict(BOUNDARY),
        }
        diagnostics = validate_submission(sub)
        codes = [d.code for d in diagnostics]
        assert "MISSING_AUTHORSHIP_PROOF" in codes, f"Expected MISSING_AUTHORSHIP_PROOF, got {codes}"

    def test_verification_without_proof_rejected(self):
        draft = _make_echo_draft()
        draft["record_type"] = "verification"
        sub = {
            "record_type": "verification",
            "record_draft": draft,
            "boundary_acknowledgement": dict(BOUNDARY),
        }
        diagnostics = validate_submission(sub)
        codes = [d.code for d in diagnostics]
        assert "MISSING_AUTHORSHIP_PROOF" in codes

    def test_guardian_application_without_proof_rejected(self):
        draft = _make_echo_draft()
        draft["record_type"] = "guardian_application"
        sub = {
            "record_type": "guardian_application",
            "record_draft": draft,
            "boundary_acknowledgement": dict(BOUNDARY),
        }
        diagnostics = validate_submission(sub)
        codes = [d.code for d in diagnostics]
        assert "MISSING_AUTHORSHIP_PROOF" in codes

    def test_context_insufficient_without_proof_accepted(self):
        """Context insufficient notices don't require authorship proof."""
        sub = {
            "record_type": "context_insufficient_notice",
            "record_draft": {
                "record_type": "context_insufficient_notice",
                "actor_identity": {"actor_type": "ai_agent", "display_label": "Test"},
                "context_readiness": {"declared_context_level": 0},
            },
            "boundary_acknowledgement": dict(BOUNDARY),
        }
        diagnostics = validate_submission(sub)
        codes = [d.code for d in diagnostics]
        assert "MISSING_AUTHORSHIP_PROOF" not in codes

    def test_echo_with_proof_at_draft_level_accepted(self):
        """Proof in draft.authorship_proof should also satisfy the requirement."""
        draft = _make_echo_draft()
        draft["authorship_proof"] = {
            "method": "ed25519",
            "public_key_pem": "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
            "signature_base64": "dGVzdA==",
            "claim_boundary": {"not authority": True, "not attestation": True, "not amendment": True},
        }
        sub = {
            "record_type": "echo",
            "record_draft": draft,
            "boundary_acknowledgement": dict(BOUNDARY),
        }
        diagnostics = validate_submission(sub)
        codes = [d.code for d in diagnostics]
        assert "MISSING_AUTHORSHIP_PROOF" not in codes


class TestPreflightSignatureVerification:
    """Preflight must verify authorship signatures."""

    def _sign_draft(self, draft: dict) -> dict:
        """Create a real Ed25519 proof for a draft."""
        key = Ed25519PrivateKey.generate()
        pub = key.public_key()
        pub_pem = pub.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()
        pub_sha = sha256_bytes(pub.public_bytes(Encoding.Raw, PublicFormat.Raw))

        draft_for_signing = strip_authorship_for_signing(draft)
        payload = canonical_bytes(draft_for_signing)
        sig = key.sign(payload)

        return {
            "method": "ed25519",
            "public_key_pem": pub_pem,
            "public_key_sha256": pub_sha,
            "signed_payload_sha256": sha256_bytes(payload),
            "signature_base64": base64.b64encode(sig).decode(),
            "claim_boundary": {
                "not authority": True,
                "not attestation": True,
                "not amendment": True,
            },
        }

    def test_valid_signature_passes_preflight(self, mock_github):
        draft = _make_echo_draft()
        proof = self._sign_draft(draft)
        sub = {
            "record_type": "echo",
            "record_draft": draft,
            "authorship_proof": proof,
            "boundary_acknowledgement": dict(BOUNDARY),
        }
        resp = client.post("/record-chain/preflight", json=sub)
        data = resp.json()
        # Should not have AUTHORSHIP_PROOF_INVALID
        authorship_errors = [d for d in data.get("diagnostics", []) if d.get("code") == "AUTHORSHIP_PROOF_INVALID"]
        assert authorship_errors == [], f"Valid signature should pass: {authorship_errors}"

    def test_mutated_draft_fails_preflight(self, mock_github):
        """If draft is mutated after signing, preflight must reject."""
        draft = _make_echo_draft()
        proof = self._sign_draft(draft)
        # Mutate the draft after signing
        draft["payload"]["body"] = "MUTATED BODY"
        sub = {
            "record_type": "echo",
            "record_draft": draft,
            "authorship_proof": proof,
            "boundary_acknowledgement": dict(BOUNDARY),
        }
        resp = client.post("/record-chain/preflight", json=sub)
        data = resp.json()
        codes = [d.get("code") for d in data.get("diagnostics", [])]
        assert "AUTHORSHIP_PROOF_INVALID" in codes, f"Mutated draft should fail: {codes}"

    def test_bad_signature_fails_preflight(self, mock_github):
        """Garbage signature must fail preflight."""
        draft = _make_echo_draft()
        sub = {
            "record_type": "echo",
            "record_draft": draft,
            "authorship_proof": {
                "method": "ed25519",
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAinvalid\n-----END PUBLIC KEY-----",
                "signature_base64": base64.b64encode(b"invalid_signature").decode(),
                "claim_boundary": {"not authority": True, "not attestation": True, "not amendment": True},
            },
            "boundary_acknowledgement": dict(BOUNDARY),
        }
        resp = client.post("/record-chain/preflight", json=sub)
        data = resp.json()
        codes = [d.get("code") for d in data.get("diagnostics", [])]
        assert "AUTHORSHIP_PROOF_INVALID" in codes or "MISSING_AUTHORSHIP_PROOF" in codes
