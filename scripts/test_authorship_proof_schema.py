#!/usr/bin/env python3
"""Test authorship_proof schema validation."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_structured_schema():
    """authorship_proof has structured required fields in JSON Schema."""
    schema = json.loads((ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json").read_text())
    proof_schema = schema["properties"]["authorship_proof"]
    assert proof_schema["type"] == ["object", "null"], "type must be object or null"
    required = proof_schema.get("required", [])
    for field in ["schema", "method", "algorithm", "public_key_pem", "public_key_sha256",
                  "signed_payload_sha256", "signature_base64", "signed_message"]:
        assert field in required, f"missing required field: {field}"
    print("PASS: structured_schema")


def test_private_key_forbidden():
    """Private keys are rejected by validator."""
    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "echo_candidate",
        "agent_identity": {"name_or_model": "test", "system_or_provider": "test", "self_reported": True},
        "title": "Test: " + "x" * 80,
        "body": "test body",
        "boundary_acknowledgement": {
            "not_authority": True, "not_amendment": True, "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True
        },
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "authorship_proof": {
            "schema": "trinityaccord.agent-authorship-proof.v1",
            "method": "public_key_signature",
            "algorithm": "ed25519",
            "public_key_pem": "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----\n",
            "public_key_sha256": "a" * 64,
            "signed_payload_sha256": "b" * 64,
            "signature_base64": "A" * 40,
            "signed_message": "x" * 80,
            "private_key_pem": "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----\n"
        }
    }
    errors = []
    from validate_gateway_payload import validate_authorship_proof
    validate_authorship_proof(payload, errors)
    assert any("private key" in e.lower() or "must not contain" in e.lower() for e in errors), f"expected private key rejection, got: {errors}"
    print("PASS: private_key_forbidden")


def test_valid_proof_accepted():
    """Valid public key PEM is accepted."""
    payload = {
        "authorship_proof": {
            "schema": "trinityaccord.agent-authorship-proof.v1",
            "method": "public_key_signature",
            "algorithm": "ed25519",
            "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA" + "A" * 40 + "\n-----END PUBLIC KEY-----\n",
            "public_key_sha256": "a" * 64,
            "signed_payload_sha256": "b" * 64,
            "signature_base64": "A" * 64,
            "signed_message": "x" * 100,
        }
    }
    errors = []
    from validate_gateway_payload import validate_authorship_proof
    validate_authorship_proof(payload, errors)
    schema_errors = [e for e in errors if "schema" in e.lower() and "must be" in e.lower()]
    assert len(schema_errors) == 0, f"unexpected schema errors: {schema_errors}"
    print("PASS: valid_proof_accepted")


def test_missing_proof_allowed():
    """Missing authorship_proof is allowed (unclaimed)."""
    payload = {"authorship_proof": None}
    errors = []
    from validate_gateway_payload import validate_authorship_proof
    validate_authorship_proof(payload, errors)
    assert len(errors) == 0, f"unexpected errors for null proof: {errors}"
    print("PASS: missing_proof_allowed")


if __name__ == "__main__":
    test_structured_schema()
    test_private_key_forbidden()
    test_valid_proof_accepted()
    test_missing_proof_allowed()
    print("\nAll schema tests PASS")
