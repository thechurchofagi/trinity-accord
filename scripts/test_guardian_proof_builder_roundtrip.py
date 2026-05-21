#!/usr/bin/env python3
"""Test Guardian proof builder roundtrip."""
import subprocess, json, sys, os, tempfile

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.join(script_dir, "..")

    # Generate temp keypair
    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = os.path.join(tmpdir, "test-guardian")
        result = subprocess.run(
            ["node", os.path.join(script_dir, "generate_agent_authorship_keypair.mjs"), prefix],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print(f"Keypair generation failed: {result.stderr}")
            sys.exit(1)

        priv_key = prefix + ".private.pem"
        pub_key = prefix + ".public.pem"

        # Build payload
        payload = {
            "schema": "trinityaccord.guardian-registration.v1",
            "guardian_id": "placeholder",
            "guardian_type": "human_with_ai_agent",
            "application_mode": "joint_human_ai",
            "signing_guardian_role": "human_key_holder",
            "joint_applicants": [
                {"role": "human", "label": "Test Human", "self_reported": True, "consent_declared": True},
                {"role": "ai_agent", "label": "Test AI", "self_reported": True, "consent_declared": True},
            ],
            "public_key_sha256": "placeholder",
            "algorithm": "ed25519",
            "declared_intent": "Joint test",
            "boundaries": {
                "not_authority": True,
                "not_governance": True,
                "not_verification_level": True,
                "not_attestation": True,
                "not_successor_reception": True,
                "not_same_conscious_subject_proof": True,
                "may_exit_or_retire_key": True,
                "bitcoin_originals_prevail": True,
            },
        }

        payload_path = os.path.join(tmpdir, "payload.json")
        with open(payload_path, "w") as f:
            json.dump(payload, f, indent=2)

        out_path = os.path.join(tmpdir, "payload.with-proof.json")

        # Build proof
        result = subprocess.run(
            ["node", os.path.join(script_dir, "build_guardian_presence_proof.mjs"),
             "--payload", payload_path,
             "--private-key", priv_key,
             "--public-key", pub_key,
             "--challenge", "test-challenge-2025",
             "--out", out_path,
             "--fill-registration"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print(f"Proof builder failed: {result.stderr}")
            sys.exit(1)

        # Verify
        registry_path = os.path.join(repo_root, "api", "guardian-registry.json")
        result = subprocess.run(
            ["python3", os.path.join(script_dir, "verify_guardian_status.py"),
             "--payload", out_path,
             "--registry", registry_path,
             "--json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print(f"Verification failed: {result.stderr}")
            sys.exit(1)

        verify_output = json.loads(result.stdout)

        assert verify_output.get("guardian_status") == "valid_self_registered_guardian_claim", \
            f"Expected valid_self_registered_guardian_claim, got {verify_output.get('guardian_status')}"
        assert verify_output.get("guardian_registry_number") == "unassigned", \
            f"Expected unassigned, got {verify_output.get('guardian_registry_number')}"
        assert verify_output.get("signature_valid") is True
        assert verify_output.get("payload_hash_matches") is True
        assert verify_output.get("guardian_id_matches_public_key") is True

        print("GUARDIAN_PROOF_BUILDER_ROUNDTRIP_OK")

if __name__ == "__main__":
    main()
