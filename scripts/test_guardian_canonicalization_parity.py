#!/usr/bin/env python3
"""Test Python/Node Guardian canonicalization parity."""
import subprocess, json, sys, os, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def main():
    from guardian_common import guardian_payload_sha256, canonical_payload_for_guardian_signature

    payload = {
        "schema": "trinityaccord.guardian-registration.v1",
        "guardian_id": "placeholder",
        "guardian_type": "human_with_ai_agent",
        "application_mode": "joint_human_ai",
        "signing_guardian_role": "human_key_holder",
        "joint_applicants": [
            {
                "role": "human",
                "label": "测试用户",
                "self_reported": True,
                "consent_declared": True,
            },
            {
                "role": "ai_agent",
                "label": "测试AI",
                "self_reported": True,
                "consent_declared": True,
            }
        ],
        "public_key_sha256": "placeholder",
        "algorithm": "ed25519",
        "declared_intent": "测试联合申请",
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
        # Dynamic fields that should be stripped
        "guardian_presence_proof": {"fake": True},
        "_guardian_status": "test",
        "guardian_verification_result": {"test": True},
    }

    py_canonical = canonical_payload_for_guardian_signature(payload)
    py_hash = guardian_payload_sha256(payload)

    # Verify dynamic fields removed
    assert "guardian_presence_proof" not in py_canonical
    assert "_guardian_status" not in py_canonical
    assert "guardian_verification_result" not in py_canonical

    # Verify substantive fields retained
    assert "guardian_registration" in py_canonical or "guardian_type" in py_canonical
    assert "joint_applicants" in py_canonical or "human_with_ai_agent" in py_canonical

    # Verify Chinese not escaped
    assert "\\u" not in py_canonical, "Chinese characters should not be escaped"

    # Run Node digest
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, ensure_ascii=False)
        tmp_path = f.name

    try:
        script_dir = os.path.join(os.path.dirname(__file__), "proof_payload_digest.mjs")
        result = subprocess.run(
            ["node", script_dir, "--payload", tmp_path],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print(f"Node script failed: {result.stderr}")
            sys.exit(1)

        node_output = json.loads(result.stdout)
        node_hash = node_output["proof_payload_sha256"]
        node_canonical = node_output["canonical_payload"]

        # Compare hashes
        assert py_hash == node_hash, f"Hash mismatch: Python={py_hash} Node={node_hash}"
        assert py_canonical == node_canonical, f"Canonical payload mismatch"

        print("GUARDIAN_CANONICALIZATION_PARITY_OK")
    finally:
        os.unlink(tmp_path)

if __name__ == "__main__":
    main()
