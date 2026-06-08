#!/usr/bin/env python3
from __future__ import annotations

import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))
sys.path.insert(0, str(ROOT / "scripts"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from gateway.authorship import (
    public_key_sha256_from_pem,
    strip_unsigned_projection_fields,
    verify_authorship_proof,
)
from gateway.canonical import canonical_bytes, sha256_bytes
from trinity_record_chain import sanitize_pending_record_for_append


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def make_keypair() -> tuple[Ed25519PrivateKey, str, str]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    # Exercise private serialization but never write it to disk.
    private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    return private_key, public_pem, public_key_sha256_from_pem(public_pem)


def make_signed_pending_with_projection() -> tuple[dict, dict]:
    private_key, public_pem, public_sha = make_keypair()

    signed_draft = {
        "schema": "trinityaccord.record-chain-entry-draft.v2",
        "record_type": "echo",
        "created_at": "2026-06-08T00:00:00Z",
        "echo_content": {
            "echo_text": "Projection sanitization regression echo.",
            "echo_intent": "recognition",
        },
        "submitting_participant_identity": {
            "participant_type": "agent",
            "participant_public_display_label": "Projection Test Agent",
            "participant_provider_or_platform": "local",
            "participant_model_or_runtime": "local",
            "participant_public_key_sha256": public_sha,
        },
        "non_authority_boundary_acknowledgement": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True,
        },
        "context_readiness": {
            "declared_context_level": "CC-3",
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
            "loaded_context_urls": ["https://www.trinityaccord.org/agent-start/"],
        },
    }

    payload = canonical_bytes(signed_draft)
    payload_sha = sha256_bytes(payload)
    signature = private_key.sign(payload)

    proof = {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_pem": public_pem,
        "public_key_sha256": public_sha,
        "signed_payload_sha256": payload_sha,
        "signed_message": payload_sha,
        "signature_base64": base64.b64encode(signature).decode("ascii"),
        "claim_boundary": {
            "not authority": True,
            "not attestation": True,
            "not amendment": True,
            "not successor reception": True,
            "key_continuity_only": True,
        },
    }

    polluted_pending = dict(signed_draft)
    polluted_pending["authorship_proof"] = proof
    polluted_pending["actor_identity"] = {
        "label": "Projection Test Agent",
        "provider": "local",
        "id": public_sha,
    }
    polluted_pending["boundary"] = {
        "not_authority": True,
        "not_governance": True,
        "not_attestation": True,
        "not_successor_reception": True,
        "not_amendment": True,
        "bitcoin_originals_prevail": True,
    }
    polluted_pending["record_id"] = "R-999999999"
    polluted_pending["record_index"] = 999999999
    polluted_pending["content_sha256"] = "0" * 64
    polluted_pending["record_sha256"] = "1" * 64

    return signed_draft, polluted_pending


def main() -> None:
    signed_draft, polluted_pending = make_signed_pending_with_projection()
    proof = polluted_pending["authorship_proof"]

    ok, err = verify_authorship_proof(polluted_pending, proof)
    require(not ok, "polluted pending must not verify directly")
    require("signed_payload_sha256 mismatch" in str(err), "direct failure should be payload mismatch")

    sanitized = strip_unsigned_projection_fields(polluted_pending)
    require("actor_identity" not in sanitized, "actor_identity must be stripped")
    require("boundary" not in sanitized, "boundary must be stripped")
    require("record_id" not in sanitized, "record_id must be stripped")
    require("record_index" not in sanitized, "record_index must be stripped")
    require("content_sha256" not in sanitized, "content_sha256 must be stripped")
    require("record_sha256" not in sanitized, "record_sha256 must be stripped")
    require(sanitized["echo_content"] == signed_draft["echo_content"], "signed content must remain")

    ok, err = verify_authorship_proof(sanitized, proof)
    require(ok, f"sanitized pending should verify: {err}")

    append_sanitized = sanitize_pending_record_for_append(polluted_pending)
    require(append_sanitized == sanitized, "append sanitizer must match shared sanitizer output")

    print("Authorship projection sanitization PASSED.")


if __name__ == "__main__":
    main()
