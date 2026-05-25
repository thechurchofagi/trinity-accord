#!/usr/bin/env python3
"""Test that authorship claim fields appear in rendered machine block."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def test_signed_block_rendering():
    """Render a signed payload and verify machine block has authorship fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Generate keypair
        key_prefix = str(tmpdir / "key")
        subprocess.run(
            ["node", str(SCRIPTS / "generate_agent_authorship_keypair.mjs"), key_prefix],
            capture_output=True, cwd=str(ROOT), check=True
        )

        # Build minimal payload
        payload = {
            "schema": "trinityaccord.agent-issue-gateway-payload.v1",
            "submission_type": "echo_candidate",
            "agent_identity": {"name_or_model": "test-agent", "system_or_provider": "test", "self_reported": True},
            "title": "Test Echo: " + "x" * 70,
            "body": "test",
            "boundary_acknowledgement": {
                "not_authority": True, "not_amendment": True, "not_attestation": True,
                "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True
            },
            "what_i_checked": ["test"],
            "limitations": ["test"],
            "requested_archive_kind": "agent_declared_echo_archive",
            "record_intent": "auto_archive_candidate",
            "echo_type": "E1_recognition_echo",
            "reception_initiation_class": "externally_requested",
            "agent_integrity_declaration": {
                "verification_oath": {
                    "oath_read": True, "oath_version": "v1", "oath_text_sha256": "a" * 64,
                    "readback_required": True, "agent_readback": "x" * 200,
                    "understands_not_an_exam_or_performance": True,
                    "will_state_actual_capability_only": True,
                    "will_not_lie_or_cheat": True,
                    "will_not_fabricate_verification": True,
                    "will_not_present_guesses_as_facts": True,
                    "will_not_copy_prior_reports_as_fresh_evidence": True,
                    "will_state_uncertainty_limitations_and_downgrades": True,
                }
            },
            "authority_boundary": {
                "bitcoin_originals_remain_final": True,
                "does_not_amend_bitcoin_originals": True,
                "does_not_override_bitcoin_originals": True,
            },
            "counts_toward_home": {"verifiability": False, "reception": True, "basis": "agent_declared_echo_template_pass"},
            "claim_classification": {
                "verification_claim": {"claimed": False, "basis": "agent_declared", "system_certified": False},
                "attestation_claim": {"claimed": False, "system_certified": False},
                "successor_reception_claim": {"claimed": False, "system_certified": False},
            },
        }
        payload_path = tmpdir / "payload.json"
        payload_path.write_text(json.dumps(payload, indent=2))

        # Attach proof
        signed_path = tmpdir / "signed.json"
        subprocess.run(
            ["node", str(SCRIPTS / "attach_agent_authorship_proof.mjs"),
             "--payload", str(payload_path),
             "--private-key", f"{key_prefix}.private.pem",
             "--public-key", f"{key_prefix}.public.pem",
             "--out", str(signed_path)],
            capture_output=True, cwd=str(ROOT), check=True
        )

        # Render
        result = subprocess.run(
            ["python3", str(SCRIPTS / "render_gateway_issue_body.py"),
             str(signed_path),
             "--production-render",
             "--gateway-receipt-id", "gar-test-authorship-1234567890abcdef",
             "--gateway-commit", "local",
             "--gateway-service", "trinity-agent-issue-gateway"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        assert result.returncode == 0, f"render failed: {result.stderr}"
        body = result.stdout

        for field in [
            "authorship_claim_protocol: agent-authorship-claim-v1",
            "authorship_proof_present: true",
            "authorship_proof_method: public_key_signature",
            "authorship_algorithm: ed25519",
            "authorship_signature_verified: true",
            "claim_status: claimable_by_public_key",
            "claim_endpoint: /gateway/claim-authorship",
        ]:
            assert field in body, f"missing in rendered body: {field}"

        print("PASS: signed_block_rendering")


if __name__ == "__main__":
    test_signed_block_rendering()
    print("\nAll rendering tests PASS")
