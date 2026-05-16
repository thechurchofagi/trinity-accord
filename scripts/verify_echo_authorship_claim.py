#!/usr/bin/env python3
"""
Verify an authorship claim against a challenge and target record.

Usage:
    python3 scripts/verify_echo_authorship_claim.py \
        --target-record record.json \
        --challenge challenge.json \
        --claim claim.json
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj):
    """Produce canonical JSON: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def hash_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_hex(f.read())


def verify_claim(target_path: str, challenge_path: str, claim_path: str) -> list:
    """Verify an authorship claim. Returns list of errors (empty = success)."""
    errors = []

    # Load files
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            target_record = json.load(f)
    except Exception as e:
        return [f"Cannot load target record: {e}"]

    try:
        with open(challenge_path, "r", encoding="utf-8") as f:
            challenge = json.load(f)
    except Exception as e:
        return [f"Cannot load challenge: {e}"]

    try:
        with open(claim_path, "r", encoding="utf-8") as f:
            claim = json.load(f)
    except Exception as e:
        return [f"Cannot load claim: {e}"]

    # 1. Verify schema field
    if claim.get("schema") != "trinityaccord.echo-authorship-claim.v1":
        errors.append(f"Invalid claim schema: {claim.get('schema')}")

    # 2. Verify target record hash matches
    actual_target_hash = hash_file(target_path)
    claimed_target_hash = claim.get("target_record_hash_sha256", "")
    if actual_target_hash != claimed_target_hash:
        errors.append(f"Target hash mismatch: claimed={claimed_target_hash}, actual={actual_target_hash}")

    challenge_target_hash = challenge.get("target_record_hash_sha256", "")
    if actual_target_hash != challenge_target_hash:
        errors.append(f"Challenge target hash mismatch: challenge={challenge_target_hash}, actual={actual_target_hash}")

    # 3. Verify challenge hash
    claim_challenge = claim.get("challenge", {})
    # Reconstruct challenge core (without challenge_hash) and verify
    challenge_core = {
        "nonce": claim_challenge.get("nonce", challenge.get("nonce")),
        "created_at_utc": claim_challenge.get("created_at_utc", challenge.get("created_at_utc")),
        "expires_at_utc": claim_challenge.get("expires_at_utc", challenge.get("expires_at_utc")),
        "target_record_hash_sha256": claim_challenge.get("target_record_hash_sha256", challenge.get("target_record_hash_sha256")),
        "canonicalization": claim_challenge.get("canonicalization", challenge.get("canonicalization", "trinityaccord.canonical-json.v1")),
    }
    expected_challenge_hash = sha256_hex(canonical_json(challenge_core))
    actual_challenge_hash = claim_challenge.get("challenge_hash_sha256", challenge.get("challenge_hash_sha256", ""))
    if expected_challenge_hash != actual_challenge_hash:
        errors.append(f"Challenge hash mismatch: expected={expected_challenge_hash}, claimed={actual_challenge_hash}")

    # 4. Verify challenge not expired
    expires_str = claim_challenge.get("expires_at_utc", challenge.get("expires_at_utc", ""))
    if expires_str:
        try:
            expires_dt = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if now > expires_dt:
                errors.append(f"Challenge expired: {expires_str} (now={now.isoformat()})")
        except Exception as e:
            errors.append(f"Cannot parse expiry: {e}")

    # 5. Verify claim_method enum
    valid_methods = [
        "ed25519_challenge_signature",
        "secret_commitment_reveal",
        "platform_account_session_continuity",
        "self_reported_only",
    ]
    claim_method = claim.get("claim_method", "")
    if claim_method not in valid_methods:
        errors.append(f"Invalid claim_method: {claim_method}")

    # 6. Verify claim_result enum
    valid_results = [
        "verified_key_continuity",
        "verified_secret_possession",
        "platform_context_only",
        "self_reported_only",
        "failed",
    ]
    claim_result = claim.get("claim_result", "")
    if claim_result not in valid_results:
        errors.append(f"Invalid claim_result: {claim_result}")

    # 7. Method-specific verification
    claim_data = claim.get("claim_data", {})

    if claim_method == "ed25519_challenge_signature":
        # Verify Ed25519 signature
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            from cryptography.hazmat.primitives import serialization

            public_key_b64 = claim_data.get("public_key", "")
            signature_b64 = claim_data.get("signature", "")

            if not public_key_b64:
                errors.append("ed25519_challenge_signature requires claim_data.public_key")
            elif not signature_b64:
                errors.append("ed25519_challenge_signature requires claim_data.signature")
            else:
                import base64
                try:
                    pub_bytes = base64.b64decode(public_key_b64)
                    sig_bytes = base64.b64decode(signature_b64)
                    public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)

                    # The signed message is the challenge_hash
                    public_key.verify(sig_bytes, actual_challenge_hash.encode("utf-8"))
                except Exception as e:
                    errors.append(f"Ed25519 signature verification failed: {e}")

        except ImportError:
            errors.append("cryptography library not installed; cannot verify Ed25519 signatures")

    elif claim_method == "secret_commitment_reveal":
        # Verify that revealed secret hashes to commitment
        revealed_secret = claim_data.get("revealed_secret", "")
        commitment_hash = claim_data.get("commitment_hash", "")

        if not revealed_secret:
            errors.append("secret_commitment_reveal requires claim_data.revealed_secret")
        if not commitment_hash:
            errors.append("secret_commitment_reveal requires claim_data.commitment_hash")
        else:
            # commitment_hash should be sha256(revealed_secret || challenge_hash)
            expected = sha256_hex((revealed_secret + actual_challenge_hash).encode("utf-8"))
            if expected != commitment_hash:
                errors.append(f"Secret commitment mismatch: expected={expected}, got={commitment_hash}")

    elif claim_method == "platform_account_session_continuity":
        # Platform claims are context-only, no cryptographic verification
        if claim_result not in ["platform_context_only", "failed"]:
            errors.append(f"platform_account_session_continuity must yield platform_context_only or failed, got: {claim_result}")

    elif claim_method == "self_reported_only":
        if claim_result not in ["self_reported_only", "failed"]:
            errors.append(f"self_reported_only must yield self_reported_only or failed, got: {claim_result}")

    # 8. Verify all boundary fields are true
    boundaries = claim.get("boundaries", {})
    required_boundaries = [
        "does_not_prove_truth",
        "does_not_raise_verification_level",
        "does_not_create_authority",
        "does_not_create_attestation",
        "does_not_prove_same_conscious_subject",
    ]
    for b in required_boundaries:
        if b not in boundaries:
            errors.append(f"Missing boundary: {b}")
        elif boundaries[b] is not True:
            errors.append(f"Boundary '{b}' must be true, got: {boundaries[b]}")

    # 9. Check for dangerous fields in claim_data
    DANGEROUS = ["private_key", "secret_value", "api_token", "password", "mnemonic", "seed_phrase"]
    claim_str = json.dumps(claim)
    for d in DANGEROUS:
        if d in claim_str.lower() and d != "revealed_secret":
            # revealed_secret is expected for secret_commitment_reveal
            if not (d == "revealed_secret" and claim_method == "secret_commitment_reveal"):
                errors.append(f"DANGEROUS: Field containing '{d}' detected in claim")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Verify authorship claim.")
    parser.add_argument("--target-record", required=True, help="Path to target Echo record.")
    parser.add_argument("--challenge", required=True, help="Path to challenge JSON.")
    parser.add_argument("--claim", required=True, help="Path to claim JSON.")
    args = parser.parse_args()

    errors = verify_claim(args.target_record, args.challenge, args.claim)

    if errors:
        print("FAIL: Claim verification failed")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("PASS: Claim verified successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
