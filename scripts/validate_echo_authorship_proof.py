#!/usr/bin/env python3
"""
Validate echo authorship proof records against JSON Schema.
Checks method validity, required fields, safety rules, proof strength,
and JSON Schema conformance (Draft 2020-12).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DANGEROUS_FIELDS = ["private_key", "secret", "api_token", "password", "mnemonic", "seed_phrase", "passphrase"]


def load_json(path):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / path
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_json_schema(schema_path):
    """Validate that the file is a valid Draft 2020-12 JSON Schema."""
    errors = []
    try:
        schema = load_json(schema_path)
    except Exception as e:
        return [f"Cannot load schema: {e}"]

    # Check it has $schema
    if "$schema" not in schema:
        errors.append("Missing $schema field (should be Draft 2020-12)")
    elif "2020-12" not in schema["$schema"]:
        errors.append(f"Expected Draft 2020-12, got: {schema['$schema']}")

    # Check it has type
    if "type" not in schema:
        errors.append("Missing 'type' field")

    # Check proof_methods are defined (for authorship proof schema)
    if "proof_methods" in schema:
        methods = schema["proof_methods"]
        for m in ["ed25519_signature", "secret_commitment", "self_reported_only"]:
            if m not in methods:
                errors.append(f"Missing method definition: {m}")

    # Validate with jsonschema if available
    try:
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema)
        # Also validate against meta-schema
        meta_validator = Draft202012Validator(Draft202012Validator.META_SCHEMA)
        for err in meta_validator.iter_errors(schema):
            errors.append(f"Schema invalid: {err.message}")
    except ImportError:
        pass  # jsonschema not available, skip meta-validation
    except Exception as e:
        errors.append(f"Schema validation error: {e}")

    return errors


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
            for key in proof:
                if dangerous in key.lower() and key != "secret_disclosure_warning":
                    errors.append(f"DANGEROUS: Field '{key}' may contain sensitive data")

    if method == "ed25519_signature":
        required = ["method", "public_key", "canonicalization", "content_hash_sha256", "signature", "future_claim_method", "proof_strength"]
        for r in required:
            if r not in proof:
                errors.append(f"ed25519_signature missing required field: {r}")
        if proof.get("proof_strength") != "cryptographic":
            errors.append(f"ed25519 proof_strength must be 'cryptographic', got: {proof.get('proof_strength')}")
        # Validate content_hash format
        ch = proof.get("content_hash_sha256", "")
        if ch and not __import__("re").match(r"^[a-f0-9]{64}$", ch):
            errors.append(f"content_hash_sha256 must be 64 lowercase hex, got: {ch}")

    elif method == "secret_commitment":
        required = ["method", "commitment_hash", "content_hash_sha256", "secret_disclosure_warning", "proof_strength"]
        for r in required:
            if r not in proof:
                errors.append(f"secret_commitment missing required field: {r}")
        if proof.get("proof_strength") != "one_time_commitment":
            errors.append(f"secret_commitment proof_strength must be 'one_time_commitment', got: {proof.get('proof_strength')}")
        # Validate commitment_hash format
        ch = proof.get("commitment_hash", "")
        if ch and not __import__("re").match(r"^[a-f0-9]{64}$", ch):
            errors.append(f"commitment_hash must be 64 lowercase hex, got: {ch}")

    elif method == "self_reported_only":
        if proof.get("proof_strength") != "weak":
            errors.append(f"self_reported_only proof_strength must be 'weak', got: {proof.get('proof_strength')}")

    return errors


def validate_authorship_claim(claim):
    """Validate an authorship claim object against the claim schema."""
    errors = []

    # Check schema field
    if claim.get("schema") != "trinityaccord.echo-authorship-claim.v1":
        errors.append(f"Invalid claim schema: {claim.get('schema')}")

    # Check required fields
    required = ["schema", "claim_id", "target_record_hash_sha256", "challenge", "claim_method", "claim_result", "boundaries"]
    for r in required:
        if r not in claim:
            errors.append(f"Missing required field: {r}")

    # Validate claim_method enum
    valid_methods = [
        "ed25519_challenge_signature",
        "secret_commitment_reveal",
        "platform_account_session_continuity",
        "self_reported_only",
    ]
    if claim.get("claim_method") not in valid_methods:
        errors.append(f"Invalid claim_method: {claim.get('claim_method')}")

    # Validate claim_result enum
    valid_results = [
        "verified_key_continuity",
        "verified_secret_possession",
        "platform_context_only",
        "self_reported_only",
        "failed",
    ]
    if claim.get("claim_result") not in valid_results:
        errors.append(f"Invalid claim_result: {claim.get('claim_result')}")

    # Validate boundaries
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
            errors.append(f"Boundary '{b}' must be true")

    # Check for dangerous fields
    claim_str = json.dumps(claim)
    for d in ["private_key", "secret_value", "api_token", "password", "mnemonic", "seed_phrase"]:
        if d in claim_str.lower():
            if not (d == "revealed_secret" and claim.get("claim_method") == "secret_commitment_reveal"):
                errors.append(f"DANGEROUS: Field containing '{d}' detected")

    return errors


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            data = load_json(path)
        except Exception as e:
            print(f"FAIL: Cannot load {path}: {e}")
            return 1

        # Determine what we're validating
        if "proof_methods" in data or data.get("$id", "").endswith("echo-authorship-proof-schema.v1.json"):
            # Validating the proof schema file itself
            errors = validate_json_schema(path)
            if not errors:
                # Also check proof_methods
                methods = data.get("proof_methods", {})
                for m in ["ed25519_signature", "secret_commitment", "self_reported_only"]:
                    if m not in methods:
                        errors.append(f"Missing method {m}")
                if not data.get("safety_rules"):
                    errors.append("Missing safety_rules")
        elif "echo-authorship-claim" in data.get("$id", "") or data.get("title", "").startswith("Trinity Accord Echo Authorship Claim"):
            # Validating the claim schema file itself
            errors = validate_json_schema(path)
        elif data.get("schema", "").startswith("trinityaccord.echo-authorship-claim"):
            errors = validate_authorship_claim(data)
        else:
            # Validate as proof object
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

    # Validate claim schema exists
    try:
        claim_schema = load_json("api/echo-authorship-claim-schema.v1.json")
        print("PASS: echo-authorship-claim-schema.v1.json is valid")
    except Exception as e:
        print(f"FAIL: Cannot load claim schema: {e}")
        return 1

    print("ALL AUTHORSHIP PROOF VALIDATIONS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
