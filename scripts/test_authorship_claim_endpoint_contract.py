#!/usr/bin/env python3
"""Test /gateway/claim-authorship endpoint contract (source-level checks)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_endpoint_exists():
    """server.js contains /gateway/claim-authorship route."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert '"/gateway/claim-authorship"' in server or "'/gateway/claim-authorship'" in server, \
        "claim-authorship route not found in server.js"
    print("PASS: endpoint_exists")


def test_uses_crypto_verify():
    """Endpoint uses crypto.verify for signature verification."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "verify(" in server, "crypto.verify not used in server.js"
    assert "Buffer.from(signature_base64" in server or "Buffer.from(claim_message" in server, \
        "signature verification not properly implemented"
    print("PASS: uses_crypto_verify")


def test_adds_labels():
    """Endpoint adds authorship:claimed and authorship:key-verified labels."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "authorship:claimed" in server, "authorship:claimed label not found"
    assert "authorship:key-verified" in server, "authorship:key-verified label not found"
    print("PASS: adds_labels")


def test_no_private_key_accepted():
    """Endpoint rejects private key material."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "rejectSecretPatterns" in server or "secret" in server.lower(), \
        "no secret detection in claim endpoint"
    print("PASS: no_private_key_accepted")


def test_verifies_public_key_hash():
    """Endpoint compares submitted public key hash to machine block hash."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "submittedPubKeySha" in server or "public_key_sha256" in server, \
        "public key hash comparison not found"
    print("PASS: verifies_public_key_hash")


def test_getRepoParts_used():
    """Claim endpoint uses getRepoParts() not raw REPO_OWNER/REPO_NAME."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "function getRepoParts()" in server, "getRepoParts() not defined"
    # Check claim-authorship route section uses it (find app.post, not capabilities string)
    idx = server.find('app.post("/gateway/claim-authorship"')
    assert idx > 0, "claim-authorship route not found"
    chunk = server[idx:idx+3000]
    assert "getRepoParts()" in chunk, "claim-authorship does not use getRepoParts()"
    print("PASS: getRepoParts_used")


def test_validates_machine_block():
    """Endpoint validates machine block proof state."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "validateClaimableMachineBlock" in server, "validateClaimableMachineBlock not found"
    assert "authorship_proof_present" in server, "authorship_proof_present check missing"
    assert "authorship_signature_verified" in server, "authorship_signature_verified check missing"
    assert "authorship_proof_method" in server, "authorship_proof_method check missing"
    print("PASS: validates_machine_block")


def test_idempotent():
    """Endpoint has idempotent response path."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "idempotent" in server, "idempotent not found"
    print("PASS: idempotent")


def test_canonical_message_builder():
    """Endpoint uses buildAuthorshipClaimMessage helper."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "buildAuthorshipClaimMessage" in server, "buildAuthorshipClaimMessage not found"
    assert "expectedClaimMessage" in server, "expectedClaimMessage not found"
    print("PASS: canonical_message_builder")


def test_gatewayError_consistent():
    """Claim endpoint uses gatewayError/sendGatewayError consistently."""
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    idx = server.find('app.post("/gateway/claim-authorship"')
    assert idx > 0
    chunk = server[idx:]
    assert "gatewayError(" in chunk, "gatewayError() not used in claim endpoint"
    assert "sendGatewayError(" in chunk, "sendGatewayError() not used in claim endpoint"
    print("PASS: gatewayError_consistent")


if __name__ == "__main__":
    test_endpoint_exists()
    test_uses_crypto_verify()
    test_adds_labels()
    test_no_private_key_accepted()
    test_verifies_public_key_hash()
    test_getRepoParts_used()
    test_validates_machine_block()
    test_idempotent()
    test_canonical_message_builder()
    test_gatewayError_consistent()
    print("\nAll endpoint contract tests PASS")
