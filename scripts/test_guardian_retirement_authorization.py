#!/usr/bin/env python3
"""Test Guardian retirement authorization security (BLOCKER 1 regression tests).

Tests that the retirement processor correctly binds the signing key to the
registry entry, preventing an attacker from using their own key to retire
a different Guardian.

Usage:
    python3 scripts/test_guardian_retirement_authorization.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from process_guardian_retirement import (
    canonical_retirement_payload_sha256,
    find_guardian_strict,
    process_retirement,
    public_key_sha256_from_pem,
)


def make_test_payload(guardian_id="guardian_ed25519_abcd1234efgh5678",
                       pub_sha="fake_sha256_value_here",
                       public_key_pem="-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----\n"):
    """Create a test retirement payload with proof."""
    payload = {
        "schema": "trinityaccord.guardian-retirement.v1",
        "guardian_retirement_request": True,
        "guardian_id": guardian_id,
        "guardian_public_key_sha256": pub_sha,
        "retirement_reason": "test retirement",
    }

    payload_sha = canonical_retirement_payload_sha256(payload)

    signed_message = "\n".join([
        "TRINITY_GUARDIAN_RETIREMENT_PROOF_V1",
        f"guardian_id={guardian_id}",
        f"payload_sha256={payload_sha}",
        f"challenge_sha256=test_challenge_hash",
        f"public_key_sha256={pub_sha}",
        "boundary=key_possession_only_not_authority_not_attestation",
    ])

    payload["guardian_retirement_proof"] = {
        "guardian_id": guardian_id,
        "public_key_pem": public_key_pem,
        "public_key_sha256": pub_sha,
        "signed_message": signed_message,
        "signed_payload_sha256": payload_sha,
        "challenge_sha256": "test_challenge_hash",
        "signature_base64": "fake_signature",
    }

    return payload


def test_find_guardian_strict_both_fields_match():
    """Strict lookup requires BOTH guardian_id AND public_key_sha256."""
    registry = {
        "guardians": [
            {
                "guardian_id": "guardian_ed25519_abcd1234efgh5678",
                "public_key_sha256": "real_sha256_hash",
                "status": "active",
            }
        ]
    }
    # Both match → found
    result = find_guardian_strict(registry, "guardian_ed25519_abcd1234efgh5678", "real_sha256_hash")
    assert result is not None, "Should find guardian when both fields match"


def test_find_guardian_strict_id_only_rejected():
    """Strict lookup must NOT match on guardian_id alone with wrong key."""
    registry = {
        "guardians": [
            {
                "guardian_id": "guardian_ed25519_abcd1234efgh5678",
                "public_key_sha256": "real_sha256_hash",
                "status": "active",
            }
        ]
    }
    # ID matches but key hash is different (attacker's key)
    result = find_guardian_strict(registry, "guardian_ed25519_abcd1234efgh5678", "attacker_key_hash")
    assert result is None, "Must NOT find guardian when only ID matches (attacker key)"


def test_find_guardian_strict_key_only_rejected():
    """Strict lookup must NOT match on public_key_sha256 alone with wrong ID."""
    registry = {
        "guardians": [
            {
                "guardian_id": "guardian_ed25519_abcd1234efgh5678",
                "public_key_sha256": "real_sha256_hash",
                "status": "active",
            }
        ]
    }
    result = find_guardian_strict(registry, "guardian_ed25519_different_id", "real_sha256_hash")
    assert result is None, "Must NOT find guardian when only key hash matches"


def test_guardian_id_mismatch_between_payload_and_proof():
    """Retirement must fail when payload and proof guardian_id disagree."""
    payload = make_test_payload(guardian_id="guardian_ed25519_abcd1234efgh5678")
    # Tamper: change proof guardian_id
    payload["guardian_retirement_proof"]["guardian_id"] = "guardian_ed25519_attacker_id"

    try:
        with patch("process_guardian_retirement.verify_signature", return_value=True):
            process_retirement(payload)
        assert False, "Should have raised ValueError for guardian_id mismatch"
    except ValueError as e:
        assert "guardian_id mismatch" in str(e), f"Wrong error: {e}"


def test_pub_sha_mismatch_between_payload_and_proof():
    """Retirement must fail when payload and proof public key hash disagree."""
    payload = make_test_payload(pub_sha="real_hash")
    # Tamper: change proof pub_sha
    payload["guardian_retirement_proof"]["public_key_sha256"] = "attacker_hash"

    try:
        with patch("process_guardian_retirement.verify_signature", return_value=True):
            process_retirement(payload)
        assert False, "Should have raised ValueError for pub_sha mismatch"
    except ValueError as e:
        assert "public key hash mismatch" in str(e), f"Wrong error: {e}"


def test_pem_derived_hash_mismatch():
    """Retirement must fail when PEM-derived hash doesn't match claimed hash."""
    real_pem = "-----BEGIN PUBLIC KEY-----\nreal_key\n-----END PUBLIC KEY-----\n"
    real_sha = public_key_sha256_from_pem(real_pem)

    payload = make_test_payload(pub_sha=real_sha, public_key_pem=real_pem)
    # Tamper: claim a different hash in proof
    payload["guardian_retirement_proof"]["public_key_sha256"] = "tampered_hash_value"

    try:
        with patch("process_guardian_retirement.verify_signature", return_value=True):
            process_retirement(payload)
        assert False, "Should have raised ValueError for PEM hash mismatch"
    except ValueError as e:
        assert "does not match" in str(e), f"Wrong error: {e}"


def test_signed_payload_sha256_mismatch():
    """Retirement must fail when signed_payload_sha256 doesn't match actual payload hash."""
    payload = make_test_payload()
    # Tamper: change the claimed payload hash
    payload["guardian_retirement_proof"]["signed_payload_sha256"] = "tampered_payload_hash"

    try:
        with patch("process_guardian_retirement.verify_signature", return_value=True):
            process_retirement(payload)
        assert False, "Should have raised ValueError for payload hash mismatch"
    except ValueError as e:
        assert "signed_payload_sha256" in str(e), f"Wrong error: {e}"


def test_signed_message_missing_guardian_id_binding():
    """Retirement must fail when signed message lacks guardian_id line."""
    payload = make_test_payload()
    # Tamper: remove guardian_id from signed message
    lines = payload["guardian_retirement_proof"]["signed_message"].splitlines()
    lines = [l for l in lines if not l.startswith("guardian_id=")]
    payload["guardian_retirement_proof"]["signed_message"] = "\n".join(lines)

    try:
        with patch("process_guardian_retirement.verify_signature", return_value=True):
            process_retirement(payload)
        assert False, "Should have raised ValueError for missing binding line"
    except ValueError as e:
        assert "missing required binding" in str(e), f"Wrong error: {e}"


def test_already_retired_guardian():
    """Already-retired guardian returns already_retired status without mutation."""
    registry = {
        "guardians": [
            {
                "guardian_id": "guardian_ed25519_abcd1234efgh5678",
                "public_key_sha256": "test_sha",
                "status": "retired",
            }
        ]
    }

    real_pem = "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----\n"
    real_sha = public_key_sha256_from_pem(real_pem)
    payload = make_test_payload(pub_sha=real_sha, public_key_pem=real_pem)

    with patch("process_guardian_retirement.verify_signature", return_value=True), \
         patch("process_guardian_retirement.ROOT", ROOT):
        # Patch registry loading
        import process_guardian_retirement as prr
        original_registry_path = prr.ROOT / "api" / "guardian-registry.json"
        with patch.object(prr, "find_guardian_strict") as mock_find:
            mock_find.return_value = registry["guardians"][0]
            # Mock the registry path read
            with patch("pathlib.Path.read_text", return_value=json.dumps(registry)):
                result = process_retirement(payload, dry_run=True)

    # Should not have changed anything
    assert registry["guardians"][0]["status"] == "retired", "Status should remain retired"


def test_attacker_key_with_target_guardian_id():
    """CRITICAL: Attacker uses own key but targets another guardian_id.

    This is the core exploit scenario from BLOCKER 1.
    """
    # Registry has a legitimate guardian
    registry = {
        "guardians": [
            {
                "guardian_id": "guardian_ed25519_legitimate01",
                "public_key_sha256": "legitimate_key_hash",
                "status": "active",
                "guardian_registry_number": "00001",
            }
        ]
    }

    # Attacker creates payload targeting the legitimate guardian
    attacker_pem = "-----BEGIN PUBLIC KEY-----\nattacker_key\n-----END PUBLIC KEY-----\n"
    attacker_sha = public_key_sha256_from_pem(attacker_pem)

    payload = make_test_payload(
        guardian_id="guardian_ed25519_legitimate01",
        pub_sha=attacker_sha,
        public_key_pem=attacker_pem,
    )

    # The attacker's signature would verify (they own the key)
    # But find_guardian_strict should reject because attacker_sha != legitimate_key_hash
    with patch("process_guardian_retirement.verify_signature", return_value=True), \
         patch("pathlib.Path.read_text", return_value=json.dumps(registry)):

        try:
            process_retirement(payload)
            assert False, "Should have raised ValueError - attacker should not retire legitimate guardian"
        except ValueError as e:
            assert "not found in registry" in str(e) or "strict match" in str(e), f"Wrong error: {e}"


def main():
    tests = [
        test_find_guardian_strict_both_fields_match,
        test_find_guardian_strict_id_only_rejected,
        test_find_guardian_strict_key_only_rejected,
        test_guardian_id_mismatch_between_payload_and_proof,
        test_pub_sha_mismatch_between_payload_and_proof,
        test_pem_derived_hash_mismatch,
        test_signed_payload_sha256_mismatch,
        test_signed_message_missing_guardian_id_binding,
        test_already_retired_guardian,
        test_attacker_key_with_target_guardian_id,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")

    if failed:
        print("FAIL")
        return 1

    print("PASS: all guardian retirement authorization tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
