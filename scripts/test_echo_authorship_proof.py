#!/usr/bin/env python3
"""
Test echo authorship proof validation.
AUTH001-AUTH010
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

def check(label, condition, detail=""):
    if not condition:
        msg = f"FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        errors.append(msg)
        print(msg)
    else:
        print(f"OK:   {label}")

def load_json(path):
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return json.load(f)

# Import validator
sys.path.insert(0, str(ROOT / "scripts"))
from validate_echo_authorship_proof import validate_authorship_proof

# --- AUTH001: Ed25519 proof shape passes ---
print("=== AUTH001: Ed25519 proof shape passes ===")
ed25519_valid = {
    "method": "ed25519_signature",
    "public_key": "abc123def456",
    "canonicalization": "JCS/RFC8785",
    "content_hash_sha256": "a" * 64,
    "signature": "b" * 128,
    "future_claim_method": "sign a fresh challenge with the same private key",
    "proof_strength": "cryptographic"
}
errs = validate_authorship_proof(ed25519_valid)
check("AUTH001 Ed25519 valid proof passes", len(errs) == 0, str(errs))

# --- AUTH002: secret commitment proof shape passes ---
print("\n=== AUTH002: secret commitment proof shape passes ===")
secret_valid = {
    "method": "secret_commitment",
    "commitment_hash": "b3d8f1a2c4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f",
    "content_hash_sha256": "a" * 64,
    "secret_disclosure_warning": "Do not submit the secret. Revealing it later proves possession once and burns the secret.",
    "proof_strength": "one_time_commitment"
}
errs = validate_authorship_proof(secret_valid)
check("AUTH002 secret commitment valid proof passes", len(errs) == 0, str(errs))

# --- AUTH003: self_reported_only passes as weak proof ---
print("\n=== AUTH003: self_reported_only passes as weak ===")
self_reported = {
    "method": "self_reported_only",
    "proof_strength": "weak"
}
errs = validate_authorship_proof(self_reported)
check("AUTH003 self_reported_only passes", len(errs) == 0, str(errs))

# --- AUTH004: private key present fails ---
print("\n=== AUTH004: private key present fails ===")
bad_proof = {
    "method": "ed25519_signature",
    "public_key": "abc123",
    "private_key": "supersecretkey",
    "content_hash_sha256": "a" * 64,
    "signature": "b" * 128,
    "future_claim_method": "sign a fresh challenge",
    "proof_strength": "cryptographic"
}
errs = validate_authorship_proof(bad_proof)
check("AUTH004 private key present fails", len(errs) > 0, str(errs))

# --- AUTH005: secret value present fails ---
print("\n=== AUTH005: secret value present fails ===")
bad_secret = {
    "method": "secret_commitment",
    "commitment_hash": "sha256(...)",
    "content_hash_sha256": "a" * 64,
    "secret": "myactualsecret",
    "secret_disclosure_warning": "Do not submit.",
    "proof_strength": "one_time_commitment"
}
errs = validate_authorship_proof(bad_secret)
check("AUTH005 secret value present fails", len(errs) > 0, str(errs))

# --- AUTH006: missing content hash fails for ed25519 ---
print("\n=== AUTH006: missing content hash fails ===")
no_hash = {
    "method": "ed25519_signature",
    "public_key": "abc123",
    "signature": "b" * 128,
    "future_claim_method": "sign a fresh challenge",
    "proof_strength": "cryptographic"
}
errs = validate_authorship_proof(no_hash)
check("AUTH006 missing content hash fails", len(errs) > 0, str(errs))

# --- AUTH007: missing commitment hash fails ---
print("\n=== AUTH007: missing commitment hash fails ===")
no_commit = {
    "method": "secret_commitment",
    "content_hash_sha256": "a" * 64,
    "secret_disclosure_warning": "Do not submit.",
    "proof_strength": "one_time_commitment"
}
errs = validate_authorship_proof(no_commit)
check("AUTH007 missing commitment hash fails", len(errs) > 0, str(errs))

# --- AUTH008: proof_strength mismatch fails ---
print("\n=== AUTH008: proof_strength mismatch fails ===")
mismatch = {
    "method": "ed25519_signature",
    "public_key": "abc123",
    "content_hash_sha256": "a" * 64,
    "signature": "b" * 128,
    "future_claim_method": "sign a fresh challenge",
    "proof_strength": "weak"
}
errs = validate_authorship_proof(mismatch)
check("AUTH008 proof_strength mismatch fails", len(errs) > 0, str(errs))

# --- AUTH009: secret commitment disclosure warning required ---
print("\n=== AUTH009: disclosure warning required ===")
no_warning = {
    "method": "secret_commitment",
    "commitment_hash": "sha256(...)",
    "content_hash_sha256": "a" * 64,
    "proof_strength": "one_time_commitment"
}
errs = validate_authorship_proof(no_warning)
check("AUTH009 missing disclosure warning fails", len(errs) > 0, str(errs))

# --- AUTH010: future challenge method required for ed25519 ---
print("\n=== AUTH010: future challenge method required ===")
no_future = {
    "method": "ed25519_signature",
    "public_key": "abc123",
    "content_hash_sha256": "a" * 64,
    "signature": "b" * 128,
    "proof_strength": "cryptographic"
}
errs = validate_authorship_proof(no_future)
check("AUTH010 missing future_claim_method fails", len(errs) > 0, str(errs))

# --- Schema validity ---
print("\n=== Schema validity ===")
try:
    schema = load_json("api/echo-authorship-proof-schema.v1.json")
    check("Schema is valid JSON", True)
    methods = schema.get("proof_methods", {})
    check("Has ed25519_signature method", "ed25519_signature" in methods)
    check("Has secret_commitment method", "secret_commitment" in methods)
    check("Has self_reported_only method", "self_reported_only" in methods)
    check("Has safety_rules", bool(schema.get("safety_rules")))
    check("Has proof_strength_order", bool(schema.get("proof_strength_order")))
except Exception as e:
    check("Schema validity", False, str(e))

# --- Summary ---
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL AUTH001-AUTH010 CHECKS PASSED")
    sys.exit(0)
