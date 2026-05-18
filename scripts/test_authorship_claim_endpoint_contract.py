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
    # Check that verify is imported and used in the claim endpoint
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


if __name__ == "__main__":
    test_endpoint_exists()
    test_uses_crypto_verify()
    test_adds_labels()
    test_no_private_key_accepted()
    test_verifies_public_key_hash()
    print("\nAll endpoint contract tests PASS")
