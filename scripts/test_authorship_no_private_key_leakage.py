#!/usr/bin/env python3
"""Test that private key material is rejected in authorship_proof."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PRIVATE_KEY_SAMPLES = [
    "-----BEGIN PRIVATE KEY-----\nMC4CAQAwBQYDK2VwBCIEIJ\n-----END PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjE\n-----END OPENSSH PRIVATE KEY-----",
    "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQ\n-----END RSA PRIVATE KEY-----",
]


def test_private_key_markers_rejected():
    """Validator rejects payloads containing private key markers in authorship_proof."""
    from validate_gateway_payload import validate_authorship_proof

    for marker_text in PRIVATE_KEY_SAMPLES:
        payload = {
            "authorship_proof": {
                "schema": "trinityaccord.agent-authorship-proof.v1",
                "method": "public_key_signature",
                "algorithm": "ed25519",
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----\n",
                "public_key_sha256": "a" * 64,
                "signed_payload_sha256": "b" * 64,
                "signature_base64": "A" * 40,
                "signed_message": "x" * 80,
                "note": marker_text,
            }
        }
        errors = []
        validate_authorship_proof(payload, errors)
        assert any("private key" in e.lower() for e in errors), f"failed to reject: {marker_text[:40]}... errors={errors}"

    print("PASS: private_key_markers_rejected")


def test_forbidden_keys_rejected():
    """Validator rejects forbidden key names in authorship_proof."""
    from validate_gateway_payload import validate_authorship_proof

    for forbidden in ["private_key", "private_key_pem", "secret", "token", "claim_secret"]:
        payload = {
            "authorship_proof": {
                "schema": "trinityaccord.agent-authorship-proof.v1",
                "method": "public_key_signature",
                "algorithm": "ed25519",
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----\n",
                "public_key_sha256": "a" * 64,
                "signed_payload_sha256": "b" * 64,
                "signature_base64": "A" * 40,
                "signed_message": "x" * 80,
                forbidden: "should-not-be-here",
            }
        }
        errors = []
        validate_authorship_proof(payload, errors)
        assert any(forbidden in e for e in errors), f"failed to reject key: {forbidden}, errors={errors}"

    print("PASS: forbidden_keys_rejected")


if __name__ == "__main__":
    test_private_key_markers_rejected()
    test_forbidden_keys_rejected()
    print("\nAll private key leakage tests PASS")
