#!/usr/bin/env python3
"""
Validate echo authorship proof records.
Checks method validity, required fields, safety rules, and proof strength.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return json.load(f)

DANGEROUS_FIELDS = ["private_key", "secret", "api_token", "password", "mnemonic", "seed_phrase", "passphrase"]

def validate_authorship_proof(proof, agent_identity=None):
    """Validate an authorship proof object."""
    errors = []

    method = proof.get("method")
    valid_methods = ["ed25519_signature", "secret_commitment", "self_reported_only"]
    if method not in valid_methods:
        errors.append(f"Invalid method: {method}. Must be one of {valid_methods}")

    # Check for dangerous fields
    proof_str = json.dumps(proof)
    for dangerous in DANGEROUS_FIELDS:
        if dangerous in proof_str.lower():
            # Check it's not actually a value being submitted
            for key in proof:
                if dangerous in key.lower() and key != "secret_disclosure_warning":
                    errors.append(f"DANGEROUS: Field '{key}' may contain sensitive data")

    if method == "ed25519_signature":
        if not proof.get("public_key"):
            errors.append("ed25519_signature requires public_key")
        if not proof.get("content_hash_sha256"):
            errors.append("ed25519_signature requires content_hash_sha256")
        if not proof.get("signature"):
            errors.append("ed25519_signature requires signature")
        if not proof.get("future_claim_method"):
            errors.append("ed25519_signature requires future_claim_method")
        if proof.get("proof_strength") != "cryptographic":
            errors.append(f"ed25519 proof_strength must be 'cryptographic', got: {proof.get('proof_strength')}")

    elif method == "secret_commitment":
        if not proof.get("commitment_hash"):
            errors.append("secret_commitment requires commitment_hash")
        if not proof.get("content_hash_sha256"):
            errors.append("secret_commitment requires content_hash_sha256")
        if not proof.get("secret_disclosure_warning"):
            errors.append("secret_commitment requires secret_disclosure_warning")
        if proof.get("proof_strength") != "one_time_commitment":
            errors.append(f"secret_commitment proof_strength must be 'one_time_commitment', got: {proof.get('proof_strength')}")

    elif method == "self_reported_only":
        if proof.get("proof_strength") != "weak":
            errors.append(f"self_reported_only proof_strength must be 'weak', got: {proof.get('proof_strength')}")

    return errors

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            data = load_json(path)
        except Exception as e:
            print(f"FAIL: Cannot load {path}: {e}")
            return 1

        proof = data.get("authorship_proof", data)
        identity = data.get("agent_identity")
        errors = validate_authorship_proof(proof, identity)

        if errors:
            print(f"FAIL: {path}")
            for e in errors:
                print(f"  - {e}")
            return 1
        else:
            print(f"PASS: {path}")
            return 0

    # Validate the schema itself
    try:
        schema = load_json("api/echo-authorship-proof-schema.v1.json")
        print("PASS: echo-authorship-proof-schema.v1.json is valid")
        methods = schema.get("proof_methods", {})
        for m in ["ed25519_signature", "secret_commitment", "self_reported_only"]:
            if m not in methods:
                print(f"FAIL: Missing method {m}")
                return 1
        if not schema.get("safety_rules"):
            print("FAIL: Missing safety_rules")
            return 1
    except Exception as e:
        print(f"FAIL: {e}")
        return 1

    print("ALL AUTHORSHIP PROOF VALIDATIONS PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
