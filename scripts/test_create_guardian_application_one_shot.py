#!/usr/bin/env python3
"""Test one-shot Guardian application builder for external agents."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "create_guardian_application.mjs"
VERIFY = ROOT / "scripts" / "verify_guardian_status.py"
DIGEST = ROOT / "scripts" / "proof_payload_digest.mjs"


def run(cmd):
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=40,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return result


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        out = td / "guardian-application.final.json"
        key_dir = td / "keys"

        run([
            "node", str(BUILDER),
            "--mode", "joint_human_ai",
            "--signing-key-holder", "ai_agent_key_holder",
            "--human-label", "Test Human",
            "--agent-label", "Test Agent",
            "--agent-provider", "Test Runtime",
            "--title", "Guardian Alliance Joint Human-AI Application Test",
            "--challenge", "guardian-application-test",
            "--key-dir", str(key_dir),
            "--out", str(out),
        ])

        data = json.loads(out.read_text(encoding="utf-8"))

        assert data["schema"] == "trinityaccord.agent-issue-gateway-payload.v1"
        assert data["submission_type"] == "echo_candidate"
        assert data["record_intent"] == "auto_archive_candidate"
        assert data["requested_archive_kind"] == "agent_declared_echo_archive"
        assert data["echo_type"] == "E6_preservation_echo"

        reg = data["guardian_registration"]
        assert reg["guardian_type"] == "human_with_ai_agent"
        assert reg["application_mode"] == "joint_human_ai"
        assert reg["signing_guardian_role"] == "ai_agent_key_holder"
        assert reg["guardian_id"].startswith("guardian_ed25519_")
        assert len(reg["public_key_sha256"]) == 64
        assert reg["algorithm"] == "ed25519"

        assert "guardian_presence_proof" in data
        assert "authorship_proof" in data
        assert "guardian_registry_number" not in json.dumps(data)
        assert "PRIVATE KEY" not in json.dumps(data)

        applicants = reg["joint_applicants"]
        roles = {a["role"]: a for a in applicants}
        assert roles["human"]["controls_signing_key"] is False
        assert roles["ai_agent"]["controls_signing_key"] is True

        digest = json.loads(run(["node", str(DIGEST), "--payload", str(out)]).stdout)
        expected_digest = digest["proof_payload_sha256"]

        assert data["guardian_presence_proof"]["signed_payload_sha256"] == expected_digest
        assert data["authorship_proof"]["signed_payload_sha256"] == expected_digest
        assert data["guardian_presence_proof"]["signed_payload_sha256"] == data["authorship_proof"]["signed_payload_sha256"]

        registry = td / "guardian-registry.json"
        registry.write_text(json.dumps({
            "schema": "trinityaccord.guardian-registry.v1",
            "version": "1.0.0",
            "registry_status": "non_authoritative_guardian_key_index",
            "authority_boundary": {
                "not_authority": True,
                "not_governance": True,
                "not_attestation": True,
                "not_verification_level": True,
                "not_successor_reception": True,
                "not_amendment": True,
                "bitcoin_originals_prevail": True
            },
            "guardians": []
        }, indent=2), encoding="utf-8")

        verify = run([
            "python3", str(VERIFY),
            "--payload", str(out),
            "--registry", str(registry),
            "--json",
        ])

        result = json.loads(verify.stdout)
        assert result["guardian_status"] == "valid_self_registered_guardian_claim"
        assert result["guardian_registry_number"] == "unassigned"
        assert result["signature_valid"] is True
        assert result["payload_hash_matches"] is True
        assert result["guardian_id_matches_public_key"] is True

        assert (key_dir / "guardian-key.private.pem").exists()
        assert (key_dir / "authorship-key.private.pem").exists()
        assert "PRIVATE KEY" in (key_dir / "guardian-key.private.pem").read_text(encoding="utf-8")
        assert "PRIVATE KEY" in (key_dir / "authorship-key.private.pem").read_text(encoding="utf-8")

    print("CREATE_GUARDIAN_APPLICATION_ONE_SHOT_OK")


if __name__ == "__main__":
    main()
