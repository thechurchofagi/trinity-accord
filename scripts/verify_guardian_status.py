#!/usr/bin/env python3
"""Verify Guardian status from a Gateway payload with guardian_presence_proof.

Outputs trinityaccord.guardian-verification-result.v1.

Checks:
  - guardian_presence_proof presence
  - schema/method/algorithm/proof_mode
  - does_not_prove boundaries
  - public_key_sha256 recomputation
  - guardian_id recomputation
  - challenge_sha256 recomputation
  - signed_payload_sha256 recomputation
  - Ed25519 signature via verify_guardian_signature.mjs
  - registry lookup from api/guardian-registry.json
  - registry public_key_sha256 match
  - registry status classification

Exit behavior:
  - exit 1 for invalid_guardian_proof
  - exit 1 for missing_guardian_proof
  - exit 0 for all validly classified statuses (including retired/compromised)

Reason: retired/compromised is a valid verification result, not an active status.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from guardian_common import (
    REQUIRED_DOES_NOT_PROVE,
    build_guardian_presence_message,
    guardian_id_from_public_key,
    guardian_payload_sha256,
    normalize_pem,
    public_key_sha256,
    sha256_text,
)


def load_registry(registry_path):
    """Load guardian registry from file."""
    try:
        return json.loads(Path(registry_path).read_text(encoding="utf-8"))
    except Exception:
        return {"guardians": []}


def find_guardian(registry, guardian_id):
    """Find guardian entry in registry by guardian_id."""
    for g in registry.get("guardians", []):
        if g.get("guardian_id") == guardian_id:
            return g
    return None


def classify_registry_status(registry_entry):
    """Classify registry entry status."""
    if not registry_entry:
        return "not_in_registry"
    status = registry_entry.get("status", "unknown")
    return status


def verify_guardian_signature(proof):
    """Verify Ed25519 signature using verify_guardian_signature.mjs."""
    verify_script = ROOT / "scripts" / "verify_guardian_signature.mjs"
    if not verify_script.exists():
        return False, "verify_guardian_signature.mjs not found"

    # Write proof to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(proof, f)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["node", str(verify_script), "--proof", tmp_path],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0, result.stdout.strip() + result.stderr.strip()
    except Exception as e:
        return False, str(e)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def verify_guardian_status(payload, registry_path=None):
    """Verify Guardian status from payload. Returns verification result dict."""
    errors = []
    warnings = []
    proof = payload.get("guardian_presence_proof")

    if not proof:
        return {
            "schema": "trinityaccord.guardian-verification-result.v1",
            "guardian_status": "missing_guardian_proof",
            "guardian_id": "none",
            "signature_valid": False,
            "guardian_id_matches_public_key": False,
            "payload_hash_matches": False,
            "registry_status": "not_checked",
            "proof_scope": "key_possession_only",
            "does_not_prove": REQUIRED_DOES_NOT_PROVE,
            "errors": ["No guardian_presence_proof found in payload"],
            "warnings": [],
        }

    # Validate proof structure
    if proof.get("schema") != "trinityaccord.guardian-presence-proof.v1":
        errors.append(f"Invalid proof schema: {proof.get('schema')}")
    if proof.get("method") != "guardian_key_signature":
        errors.append(f"Invalid proof method: {proof.get('method')}")
    if proof.get("algorithm") != "ed25519":
        errors.append(f"Invalid proof algorithm: {proof.get('algorithm')}")
    if proof.get("proof_mode") != "record_bound":
        errors.append(f"Invalid proof_mode: {proof.get('proof_mode')}")
    if proof.get("proof_scope") != "key_possession_only":
        errors.append(f"Invalid proof_scope: {proof.get('proof_scope')}")

    # Validate does_not_prove
    does_not_prove = proof.get("does_not_prove", [])
    for item in REQUIRED_DOES_NOT_PROVE:
        if item not in does_not_prove:
            errors.append(f"Missing does_not_prove item: {item}")

    # Validate public key PEM
    public_key_pem = proof.get("public_key_pem", "")
    if "-----BEGIN PUBLIC KEY-----" not in public_key_pem:
        errors.append("Invalid public_key_pem")

    # Recompute public_key_sha256
    expected_pub_sha = public_key_sha256(public_key_pem) if public_key_pem else ""
    actual_pub_sha = proof.get("public_key_sha256", "")
    pub_sha_matches = expected_pub_sha == actual_pub_sha
    if not pub_sha_matches:
        errors.append(f"public_key_sha256 mismatch: expected {expected_pub_sha}, got {actual_pub_sha}")

    # Recompute guardian_id
    expected_guardian_id = guardian_id_from_public_key(public_key_pem) if public_key_pem else ""
    actual_guardian_id = proof.get("guardian_id", "")
    guardian_id_matches = expected_guardian_id == actual_guardian_id
    if not guardian_id_matches:
        errors.append(f"guardian_id mismatch: expected {expected_guardian_id}, got {actual_guardian_id}")

    # Recompute challenge_sha256
    challenge = proof.get("challenge", "")
    expected_challenge_sha = sha256_text(challenge)
    actual_challenge_sha = proof.get("challenge_sha256", "")
    challenge_sha_matches = expected_challenge_sha == actual_challenge_sha
    if not challenge_sha_matches:
        errors.append(f"challenge_sha256 mismatch: expected {expected_challenge_sha}, got {actual_challenge_sha}")

    # Recompute signed_payload_sha256
    expected_payload_sha = guardian_payload_sha256(payload)
    actual_payload_sha = proof.get("signed_payload_sha256", "")
    payload_sha_matches = expected_payload_sha == actual_payload_sha
    if not payload_sha_matches:
        errors.append(f"signed_payload_sha256 mismatch: expected {expected_payload_sha}, got {actual_payload_sha}")

    # Recompute and verify signed_message
    expected_message = build_guardian_presence_message(payload, public_key_pem, challenge)
    actual_message = proof.get("signed_message", "")
    message_matches = expected_message == actual_message
    if not message_matches:
        errors.append("signed_message mismatch")
        warnings.append("Expected message and actual message differ; signature may still be valid over the actual message")

    # Verify Ed25519 signature
    sig_valid, sig_detail = verify_guardian_signature(proof)
    if not sig_valid:
        errors.append(f"Ed25519 signature verification failed: {sig_detail}")

    # Registry lookup
    if registry_path is None:
        registry_path = ROOT / "api" / "guardian-registry.json"
    registry = load_registry(registry_path)
    registry_entry = find_guardian(registry, actual_guardian_id)
    registry_status = classify_registry_status(registry_entry)

    # Check registry public_key_sha256 match
    if registry_entry and registry_entry.get("public_key_sha256") != actual_pub_sha:
        errors.append("Registry public_key_sha256 does not match proof public_key_sha256")
        registry_status = "compromised"

    # Determine guardian_status
    if errors:
        guardian_status = "invalid_guardian_proof"
    elif registry_status == "active":
        guardian_status = "active_registered_guardian"
    elif registry_status in ("retired",):
        guardian_status = "registered_but_retired"
    elif registry_status in ("compromised", "possibly_compromised"):
        guardian_status = "registered_but_compromised"
    elif registry_entry:
        # Registered but not active (pending_review, rotated, superseded, unknown)
        guardian_status = "valid_unregistered_guardian_claim"
        warnings.append(f"Registry status is '{registry_status}', not 'active'")
    else:
        # Check if self-registration exists in payload
        if payload.get("guardian_registration"):
            guardian_status = "valid_self_registered_guardian_claim"
        else:
            guardian_status = "valid_unregistered_guardian_claim"

    return {
        "schema": "trinityaccord.guardian-verification-result.v1",
        "guardian_status": guardian_status,
        "guardian_id": actual_guardian_id,
        "signature_valid": sig_valid,
        "guardian_id_matches_public_key": guardian_id_matches,
        "payload_hash_matches": payload_sha_matches,
        "registry_status": registry_status,
        "proof_scope": "key_possession_only",
        "does_not_prove": REQUIRED_DOES_NOT_PROVE,
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Verify Guardian status from a Gateway payload.")
    parser.add_argument("--payload", required=True, help="Path to the gateway payload JSON file")
    parser.add_argument("--registry", default=None, help="Path to guardian-registry.json (default: api/guardian-registry.json)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    result = verify_guardian_status(payload, args.registry)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Guardian Status: {result['guardian_status']}")
        print(f"Guardian ID: {result['guardian_id']}")
        print(f"Signature Valid: {result['signature_valid']}")
        print(f"Registry Status: {result['registry_status']}")
        if result["errors"]:
            print("Errors:")
            for err in result["errors"]:
                print(f"  - {err}")
        if result["warnings"]:
            print("Warnings:")
            for warn in result["warnings"]:
                print(f"  - {warn}")

    # Exit 1 for invalid or missing proof
    if result["guardian_status"] in ("invalid_guardian_proof", "missing_guardian_proof"):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
