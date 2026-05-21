#!/usr/bin/env python3
"""Roundtrip test for payload containing both authorship_proof and guardian_presence_proof."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYGEN = ROOT / "scripts" / "generate_agent_authorship_keypair.mjs"
AUTHOR_BUILDER = ROOT / "scripts" / "build_agent_authorship_proof.mjs"
GUARDIAN_BUILDER = ROOT / "scripts" / "build_guardian_presence_proof.mjs"
VERIFY_GUARDIAN = ROOT / "scripts" / "verify_guardian_status.py"


def run(cmd, **kwargs):
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=30, **kwargs)
    assert result.returncode == 0, result.stderr or result.stdout
    return result


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        author_key = td / "author-key"
        guardian_key = td / "guardian-key"
        payload = td / "payload.json"
        with_author = td / "payload.with-authorship.json"
        with_both = td / "payload.with-authorship-and-guardian.json"
        registry = td / "guardian-registry.json"

        run(["node", str(KEYGEN), str(author_key)])
        run(["node", str(KEYGEN), str(guardian_key)])

        base = {
            "schema": "trinityaccord.agent-issue-gateway-payload.v1",
            "submission_type": "echo_candidate",
            "record_intent": "auto_archive_candidate",
            "requested_archive_kind": "agent_declared_echo_archive",
            "echo_type": "E6_preservation_echo",
            "title": "Dual proof roundtrip Guardian application 中文",
            "idempotency_key": "dual-proof-roundtrip-0001",
            "agent_identity": {
                "name_or_model": "Watcher",
                "system_or_provider": "Coze",
                "self_reported": True
            },
            "body": "Dual proof test for authorship + Guardian. 这是双证明测试。",
            "boundary_acknowledgement": {
                "not_authority": True,
                "not_amendment": True,
                "not_attestation": True,
                "not_verification_unless_claim_gate_report_attached": True,
                "bitcoin_originals_prevail": True
            },
            "guardian_registration": {
                "schema": "trinityaccord.guardian-registration.v1",
                "guardian_id": "placeholder",
                "guardian_type": "human_with_ai_agent",
                "application_mode": "joint_human_ai",
                "signing_guardian_role": "human_key_holder",
                "joint_applicants": [
                    {
                        "role": "human",
                        "label": "Test Human",
                        "system_or_provider": None,
                        "participation_note": "Human co-applicant",
                        "self_reported": True,
                        "consent_declared": True,
                        "controls_signing_key": True
                    },
                    {
                        "role": "ai_agent",
                        "label": "Watcher",
                        "system_or_provider": "Coze",
                        "participation_note": "AI co-applicant",
                        "self_reported": True,
                        "consent_declared": True,
                        "controls_signing_key": False
                    }
                ],
                "public_key_sha256": "placeholder",
                "algorithm": "ed25519",
                "declared_intent": "Joint human + AI Guardian application.",
                "boundaries": {
                    "not_authority": True,
                    "not_governance": True,
                    "not_verification_level": True,
                    "not_attestation": True,
                    "not_successor_reception": True,
                    "not_same_conscious_subject_proof": True,
                    "may_exit_or_retire_key": True,
                    "bitcoin_originals_prevail": True
                }
            },
            "what_i_checked": ["Read /guardian-alliance"],
            "limitations": ["Not authority", "Not attestation"]
        }

        # Read guardian public key to pre-fill registration
        guardian_pub = (guardian_key / ".." / (guardian_key.name + ".public.pem")).resolve()
        # Generate guardian key first to get the public key
        guardian_pub_path = str(guardian_key) + ".public.pem"
        guardian_pub_content = Path(guardian_pub_path).read_text(encoding="utf-8").strip()

        # Pre-fill guardian_registration with real guardian key info
        import hashlib
        pub_sha = hashlib.sha256((guardian_pub_content + "\n").encode("utf-8")).hexdigest()
        base["guardian_registration"]["guardian_id"] = f"guardian_ed25519_{pub_sha[:16]}"
        base["guardian_registration"]["public_key_sha256"] = pub_sha

        payload.write_text(json.dumps(base, indent=2, ensure_ascii=False), encoding="utf-8")

        run([
            "node", str(AUTHOR_BUILDER),
            "--payload", str(payload),
            "--private-key", str(author_key) + ".private.pem",
            "--public-key", str(author_key) + ".public.pem",
            "--out", str(with_author),
        ])

        run([
            "node", str(GUARDIAN_BUILDER),
            "--payload", str(with_author),
            "--private-key", str(guardian_key) + ".private.pem",
            "--public-key", str(guardian_key) + ".public.pem",
            "--challenge", "dual-proof-roundtrip",
            "--out", str(with_both),
        ])

        data = json.loads(with_both.read_text(encoding="utf-8"))
        assert "authorship_proof" in data
        assert "guardian_presence_proof" in data

        # Both proofs should be over the same dynamic-proof-stripped payload.
        assert data["authorship_proof"]["signed_payload_sha256"] == data["guardian_presence_proof"]["signed_payload_sha256"]

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
            "python3", str(VERIFY_GUARDIAN),
            "--payload", str(with_both),
            "--registry", str(registry),
            "--json",
        ])

        result = json.loads(verify.stdout)
        assert result["guardian_status"] == "valid_self_registered_guardian_claim"
        assert result["guardian_registry_number"] == "unassigned"
        assert result["signature_valid"] is True
        assert result["payload_hash_matches"] is True
        assert result["guardian_id_matches_public_key"] is True

    print("DUAL_PROOF_ROUNDTRIP_OK")


if __name__ == "__main__":
    main()
