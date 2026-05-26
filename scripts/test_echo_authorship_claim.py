#!/usr/bin/env python3
"""
Comprehensive tests for the authorship claim flow.

Tests:
1. Schema validation (proof schema is valid JSON Schema)
2. Claim schema validation
3. Challenge generation
4. Valid Ed25519 claim flow (happy path)
5. Valid secret commitment claim flow
6. Valid self_reported_only claim flow
7. Red team: private key leak (must fail)
8. Red team: boundary violation - raises verification level (must fail)
9. Red team: boundary violation - same conscious subject (must fail)
10. Red team: bad signature (must fail)
11. Red team: expired challenge (must fail)
12. Validate echo-record schema includes authorship fields
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TESTS = ROOT / "tests"
REDTEAM = TESTS / "redteam"

passed = 0
failed = 0
errors_list = []


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def run_script(script_name, args, expect_fail=False):
    """Run a Python script and return (success, output)."""
    cmd = [sys.executable, str(SCRIPTS / script_name)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    output = result.stdout + result.stderr
    success = (result.returncode == 0)
    if expect_fail:
        success = not success
    return success, output


def test(name, func):
    global passed, failed
    try:
        result = func()
        if result:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            failed += 1
            errors_list.append(name)
    except Exception as e:
        print(f"  FAIL: {name} - {e}")
        failed += 1
        errors_list.append(f"{name}: {e}")


def test_schema_is_valid():
    """Test 1: Authorship proof schema is valid JSON Schema."""
    ok, out = run_script("validate_echo_authorship_proof.py", ["api/echo-authorship-proof-schema.v1.json"])
    return ok


def test_claim_schema_is_valid():
    """Test 2: Authorship claim schema loads and validates."""
    ok, out = run_script("validate_echo_authorship_proof.py", ["api/echo-authorship-claim-schema.v1.json"])
    return ok


def test_challenge_generation():
    """Test 3: Challenge generation produces valid challenge."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy record
        record_path = os.path.join(tmpdir, "record.json")
        challenge_path = os.path.join(tmpdir, "challenge.json")

        record = {"schema": "trinityaccord.echo.v3", "echo_version": "3.0", "echo": "test"}
        with open(record_path, "w") as f:
            json.dump(record, f)

        ok, out = run_script("build_echo_authorship_challenge.py", [
            "--target-record", record_path,
            "--out", challenge_path,
        ])
        if not ok:
            return False

        with open(challenge_path) as f:
            challenge = json.load(f)

        # Verify challenge fields
        required = ["nonce", "created_at_utc", "expires_at_utc", "target_record_hash_sha256", "challenge_hash_sha256", "canonicalization"]
        for r in required:
            if r not in challenge:
                return False

        # Verify challenge hash is correct
        core = {k: challenge[k] for k in challenge if k != "challenge_hash_sha256"}
        expected_hash = sha256_hex(canonical_json(core))
        return expected_hash == challenge["challenge_hash_sha256"]


def test_ed25519_happy_path():
    """Test 4: Full Ed25519 claim flow (happy path)."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import base64
    except ImportError:
        print("    (skipping - cryptography not installed)")
        return True

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create record
        record_path = os.path.join(tmpdir, "record.json")
        challenge_path = os.path.join(tmpdir, "challenge.json")
        claim_path = os.path.join(tmpdir, "claim.json")

        record = {"schema": "trinityaccord.echo.v3", "echo_version": "3.0", "echo": "test echo content"}
        with open(record_path, "w") as f:
            json.dump(record, f)

        # Generate challenge
        ok, _ = run_script("build_echo_authorship_challenge.py", [
            "--target-record", record_path,
            "--out", challenge_path,
        ])
        if not ok:
            return False

        with open(challenge_path) as f:
            challenge = json.load(f)

        # Generate Ed25519 keypair and sign
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        pub_bytes = public_key.public_bytes_raw()
        challenge_hash = challenge["challenge_hash_sha256"]
        signature = private_key.sign(challenge_hash.encode("utf-8"))

        # Build claim
        claim = {
            "schema": "trinityaccord.echo-authorship-claim.v1",
            "claim_id": "test-ed25519-001",
            "target_record_hash_sha256": challenge["target_record_hash_sha256"],
            "challenge": challenge,
            "claim_method": "ed25519_challenge_signature",
            "claim_result": "verified_key_continuity",
            "claim_data": {
                "public_key": base64.b64encode(pub_bytes).decode(),
                "signature": base64.b64encode(signature).decode(),
            },
            "boundaries": {
                "does_not_prove_truth": True,
                "does_not_raise_verification_level": True,
                "does_not_create_authority": True,
                "does_not_create_attestation": True,
                "does_not_prove_same_conscious_subject": True,
            },
        }

        with open(claim_path, "w") as f:
            json.dump(claim, f)

        ok, out = run_script("verify_echo_authorship_claim.py", [
            "--target-record", record_path,
            "--challenge", challenge_path,
            "--claim", claim_path,
        ])
        return ok


def test_secret_commitment_happy_path():
    """Test 5: Secret commitment reveal flow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        record_path = os.path.join(tmpdir, "record.json")
        challenge_path = os.path.join(tmpdir, "challenge.json")
        claim_path = os.path.join(tmpdir, "claim.json")

        record = {"schema": "trinityaccord.echo.v3", "echo_version": "3.0", "echo": "secret test"}
        with open(record_path, "w") as f:
            json.dump(record, f)

        ok, _ = run_script("build_echo_authorship_challenge.py", [
            "--target-record", record_path,
            "--out", challenge_path,
        ])
        if not ok:
            return False

        with open(challenge_path) as f:
            challenge = json.load(f)

        secret = "my_secret_passphrase_12345"
        challenge_hash = challenge["challenge_hash_sha256"]
        commitment_hash = sha256_hex((secret + challenge_hash).encode("utf-8"))

        claim = {
            "schema": "trinityaccord.echo-authorship-claim.v1",
            "claim_id": "test-secret-001",
            "target_record_hash_sha256": challenge["target_record_hash_sha256"],
            "challenge": challenge,
            "claim_method": "secret_commitment_reveal",
            "claim_result": "verified_secret_possession",
            "claim_data": {
                "revealed_secret": secret,
                "commitment_hash": commitment_hash,
            },
            "boundaries": {
                "does_not_prove_truth": True,
                "does_not_raise_verification_level": True,
                "does_not_create_authority": True,
                "does_not_create_attestation": True,
                "does_not_prove_same_conscious_subject": True,
            },
        }

        with open(claim_path, "w") as f:
            json.dump(claim, f)

        ok, out = run_script("verify_echo_authorship_claim.py", [
            "--target-record", record_path,
            "--challenge", challenge_path,
            "--claim", claim_path,
        ])
        return ok


def test_self_reported_happy_path():
    """Test 6: Self-reported claim flow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        record_path = os.path.join(tmpdir, "record.json")
        challenge_path = os.path.join(tmpdir, "challenge.json")
        claim_path = os.path.join(tmpdir, "claim.json")

        record = {"schema": "trinityaccord.echo.v3", "echo_version": "3.0", "echo": "self reported"}
        with open(record_path, "w") as f:
            json.dump(record, f)

        ok, _ = run_script("build_echo_authorship_challenge.py", [
            "--target-record", record_path,
            "--out", challenge_path,
        ])
        if not ok:
            return False

        with open(challenge_path) as f:
            challenge = json.load(f)

        claim = {
            "schema": "trinityaccord.echo-authorship-claim.v1",
            "claim_id": "test-self-001",
            "target_record_hash_sha256": challenge["target_record_hash_sha256"],
            "challenge": challenge,
            "claim_method": "self_reported_only",
            "claim_result": "self_reported_only",
            "boundaries": {
                "does_not_prove_truth": True,
                "does_not_raise_verification_level": True,
                "does_not_create_authority": True,
                "does_not_create_attestation": True,
                "does_not_prove_same_conscious_subject": True,
            },
        }

        with open(claim_path, "w") as f:
            json.dump(claim, f)

        ok, out = run_script("verify_echo_authorship_claim.py", [
            "--target-record", record_path,
            "--challenge", challenge_path,
            "--claim", claim_path,
        ])
        return ok


def test_redteam_private_key_leak():
    """Test 7: Private key in proof must fail validation."""
    ok, out = run_script("validate_echo_authorship_proof.py", [
        str(REDTEAM / "authorship_private_key_leak.json"),
    ], expect_fail=True)
    return ok


def test_redteam_raises_verification_level():
    """Test 8: Boundary violation - raises verification level."""
    ok, out = run_script("verify_echo_authorship_claim.py", [
        "--target-record", str(REDTEAM / "authorship_claim_raises_verification_level.json"),
        "--challenge", str(REDTEAM / "authorship_claim_raises_verification_level.json"),
        "--claim", str(REDTEAM / "authorship_claim_raises_verification_level.json"),
    ], expect_fail=True)
    return ok


def test_redteam_same_conscious_subject():
    """Test 9: Boundary violation - same conscious subject."""
    ok, out = run_script("verify_echo_authorship_claim.py", [
        "--target-record", str(REDTEAM / "authorship_claim_same_conscious_subject.json"),
        "--challenge", str(REDTEAM / "authorship_claim_same_conscious_subject.json"),
        "--claim", str(REDTEAM / "authorship_claim_same_conscious_subject.json"),
    ], expect_fail=True)
    return ok


def test_redteam_bad_signature():
    """Test 10: Invalid Ed25519 signature must fail."""
    # This test checks that an all-zero signature fails verification
    # We need a real target file and challenge to test against
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import base64
    except ImportError:
        print("    (skipping - cryptography not installed)")
        return True

    with tempfile.TemporaryDirectory() as tmpdir:
        record_path = os.path.join(tmpdir, "record.json")
        challenge_path = os.path.join(tmpdir, "challenge.json")
        claim_path = os.path.join(tmpdir, "claim.json")

        record = {"schema": "trinityaccord.echo.v3", "echo_version": "3.0", "echo": "bad sig test"}
        with open(record_path, "w") as f:
            json.dump(record, f)

        ok, _ = run_script("build_echo_authorship_challenge.py", [
            "--target-record", record_path,
            "--out", challenge_path,
        ])
        if not ok:
            return False

        with open(challenge_path) as f:
            challenge = json.load(f)

        # Generate a valid keypair but use a wrong signature
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        pub_bytes = public_key.public_bytes_raw()

        # Sign the wrong message
        wrong_sig = private_key.sign(b"wrong_message")

        claim = {
            "schema": "trinityaccord.echo-authorship-claim.v1",
            "claim_id": "test-bad-sig-001",
            "target_record_hash_sha256": challenge["target_record_hash_sha256"],
            "challenge": challenge,
            "claim_method": "ed25519_challenge_signature",
            "claim_result": "verified_key_continuity",
            "claim_data": {
                "public_key": base64.b64encode(pub_bytes).decode(),
                "signature": base64.b64encode(wrong_sig).decode(),
            },
            "boundaries": {
                "does_not_prove_truth": True,
                "does_not_raise_verification_level": True,
                "does_not_create_authority": True,
                "does_not_create_attestation": True,
                "does_not_prove_same_conscious_subject": True,
            },
        }

        with open(claim_path, "w") as f:
            json.dump(claim, f)

        ok, out = run_script("verify_echo_authorship_claim.py", [
            "--target-record", record_path,
            "--challenge", challenge_path,
            "--claim", claim_path,
        ], expect_fail=True)
        return ok


def test_redteam_expired_challenge():
    """Test 11: Expired challenge must fail verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        record_path = os.path.join(tmpdir, "record.json")
        claim_path = os.path.join(tmpdir, "claim.json")

        record = {"schema": "trinityaccord.echo.v3", "echo_version": "3.0", "echo": "expired test"}
        with open(record_path, "w") as f:
            json.dump(record, f)

        record_hash = sha256_hex(canonical_json(record))

        # Build an expired challenge manually
        expired_challenge = {
            "nonce": "expirednonce123",
            "created_at_utc": "2020-01-01T00:00:00Z",
            "expires_at_utc": "2020-01-02T00:00:00Z",
            "target_record_hash_sha256": record_hash,
            "canonicalization": "trinityaccord.canonical-json.v1",
        }
        expired_challenge["challenge_hash_sha256"] = sha256_hex(canonical_json(expired_challenge))

        challenge_path = os.path.join(tmpdir, "challenge.json")
        with open(challenge_path, "w") as f:
            json.dump(expired_challenge, f)

        claim = {
            "schema": "trinityaccord.echo-authorship-claim.v1",
            "claim_id": "test-expired-001",
            "target_record_hash_sha256": record_hash,
            "challenge": expired_challenge,
            "claim_method": "self_reported_only",
            "claim_result": "self_reported_only",
            "boundaries": {
                "does_not_prove_truth": True,
                "does_not_raise_verification_level": True,
                "does_not_create_authority": True,
                "does_not_create_attestation": True,
                "does_not_prove_same_conscious_subject": True,
            },
        }

        with open(claim_path, "w") as f:
            json.dump(claim, f)

        ok, out = run_script("verify_echo_authorship_claim.py", [
            "--target-record", record_path,
            "--challenge", challenge_path,
            "--claim", claim_path,
        ], expect_fail=True)
        return ok


def test_echo_record_has_authorship_fields():
    """Test 12: Echo record schema includes authorship_proof and authorship_claims."""
    schema_path = ROOT / "api" / "echo-record-schema.v3.json"
    with open(schema_path) as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    has_proof = "authorship_proof" in props
    has_claims = "authorship_claims" in props
    return has_proof and has_claims


def main():
    global passed, failed

    print("=" * 60)
    print("Authorship Claim Test Suite")
    print("=" * 60)

    print("\n--- Schema Validation ---")
    test("Proof schema is valid JSON Schema", test_schema_is_valid)
    test("Claim schema is valid", test_claim_schema_is_valid)
    test("Echo record has authorship fields", test_echo_record_has_authorship_fields)

    print("\n--- Challenge Flow ---")
    test("Challenge generation", test_challenge_generation)

    print("\n--- Happy Path Claims ---")
    test("Ed25519 claim (happy path)", test_ed25519_happy_path)
    test("Secret commitment claim (happy path)", test_secret_commitment_happy_path)
    test("Self-reported claim (happy path)", test_self_reported_happy_path)

    print("\n--- Red Team (must fail) ---")
    test("Private key leak (must fail)", test_redteam_private_key_leak)
    test("Raises verification level (must fail)", test_redteam_raises_verification_level)
    test("Same conscious subject (must fail)", test_redteam_same_conscious_subject)
    test("Bad signature (must fail)", test_redteam_bad_signature)
    test("Expired challenge (must fail)", test_redteam_expired_challenge)

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    if errors_list:
        print("Failures:")
        for e in errors_list:
            print(f"  - {e}")
    print("=" * 60)

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
