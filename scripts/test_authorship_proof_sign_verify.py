#!/usr/bin/env python3
"""Test authorship proof sign and verify cycle."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def test_sign_verify_cycle():
    """Generate keypair, build payload, attach proof, verify signature."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 1. Generate keypair
        key_prefix = str(tmpdir / "test-key")
        result = subprocess.run(
            ["node", str(SCRIPTS / "generate_agent_authorship_keypair.mjs"), key_prefix],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        assert result.returncode == 0, f"keygen failed: {result.stderr}"
        assert Path(f"{key_prefix}.public.pem").exists()
        assert Path(f"{key_prefix}.private.pem").exists()

        # 2. Build a minimal echo payload
        payload = {
            "schema": "trinityaccord.agent-issue-gateway-payload.v1",
            "submission_type": "echo_candidate",
            "agent_identity": {
                "name_or_model": "test-authorship-agent",
                "system_or_provider": "local-test",
                "self_reported": True
            },
            "title": "Authorship Test Echo: " + "x" * 60,
            "body": "This is a test echo for authorship proof verification.",
            "boundary_acknowledgement": {
                "not_authority": True,
                "not_amendment": True,
                "not_attestation": True,
                "not_verification_unless_claim_gate_report_attached": True,
                "bitcoin_originals_prevail": True
            },
            "what_i_checked": ["authorship proof sign/verify cycle"],
            "limitations": ["test only"],
            "requested_archive_kind": "agent_declared_echo_archive",
            "record_intent": "auto_archive_candidate",
            "echo_type": "E1_read_oriented_echo",
            "reception_initiation_class": "externally_requested",
            "reception_initiation_basis": "explicit_verification_request",
            "agent_integrity_declaration": {
                "verification_oath": {
                    "oath_read": True,
                    "oath_version": "v1",
                    "oath_text_sha256": "a" * 64,
                    "readback_required": True,
                    "agent_readback": "x" * 200,
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
            "counts_toward_home": {
                "verifiability": False,
                "reception": True,
                "basis": "agent_declared_echo_template_pass",
            },
            "claim_classification": {
                "verification_claim": {"claimed": False, "basis": "agent_declared", "system_certified": False},
                "attestation_claim": {"claimed": False, "system_certified": False},
                "successor_reception_claim": {"claimed": False, "system_certified": False},
            },
        }
        payload_path = tmpdir / "payload.json"
        payload_path.write_text(json.dumps(payload, indent=2))

        # 3. Attach authorship proof
        result = subprocess.run(
            ["node", str(SCRIPTS / "attach_agent_authorship_proof.mjs"),
             "--payload", str(payload_path),
             "--private-key", f"{key_prefix}.private.pem",
             "--public-key", f"{key_prefix}.public.pem",
             "--out", str(tmpdir / "signed.json")],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        assert result.returncode == 0, f"attach failed: {result.stderr}\n{result.stdout}"

        signed = json.loads((tmpdir / "signed.json").read_text())
        proof = signed["authorship_proof"]
        assert proof["schema"] == "trinityaccord.agent-authorship-proof.v1"
        assert proof["method"] == "public_key_signature"
        assert proof["algorithm"] == "ed25519"
        assert len(proof["public_key_sha256"]) == 64
        assert len(proof["signed_payload_sha256"]) == 64
        assert len(proof["signature_base64"]) >= 40

        # 4. Verify using Node.js crypto
        verify_script = tmpdir / "verify.mjs"
        verify_script.write_text(f"""
import {{ verify }} from "node:crypto";
import {{ readFileSync }} from "node:fs";

const signed = JSON.parse(readFileSync("{tmpdir / 'signed.json'}", "utf8"));
const proof = signed.authorship_proof;
const pubKey = proof.public_key_pem;
const msg = Buffer.from(proof.signed_message, "utf8");
const sig = Buffer.from(proof.signature_base64, "base64");

const ok = verify(null, msg, pubKey, sig);
console.log(ok ? "VERIFY_PASS" : "VERIFY_FAIL");
process.exit(ok ? 0 : 1);
""")
        result = subprocess.run(
            ["node", str(verify_script)],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        assert result.returncode == 0, f"verify failed: {result.stderr}\n{result.stdout}"
        assert "VERIFY_PASS" in result.stdout
        print("PASS: sign_verify_cycle")


if __name__ == "__main__":
    test_sign_verify_cycle()
    print("\nAll sign/verify tests PASS")
