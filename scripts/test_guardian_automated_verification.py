#!/usr/bin/env python3
"""Test Guardian Alliance automated verification.

Tests:
  - missing guardian proof -> missing_guardian_proof
  - valid proof + empty registry -> valid_unregistered_guardian_claim
  - valid proof + self registration + empty registry -> valid_self_registered_guardian_claim
  - valid proof + active registry -> active_registered_guardian
  - valid proof + retired registry -> registered_but_retired
  - valid proof + compromised registry -> registered_but_compromised
  - corrupted payload -> invalid_guardian_proof
  - corrupted signature -> invalid_guardian_proof
  - registry public_key_sha256 mismatch -> invalid_guardian_proof

Output: GUARDIAN_AUTOMATED_VERIFICATION_OK
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from guardian_common import (
    REQUIRED_DOES_NOT_PROVE,
    build_guardian_presence_message,
    guardian_id_from_public_key,
    normalize_pem,
    public_key_sha256,
)

VERIFY_STATUS_SCRIPT = ROOT / "scripts" / "verify_guardian_status.py"
ATTACH_SCRIPT = ROOT / "scripts" / "attach_guardian_presence_proof.mjs"
KEYGEN_SCRIPT = ROOT / "scripts" / "generate_agent_authorship_keypair.mjs"


def run_verify(payload_path, registry_path=None):
    """Run verify_guardian_status.py and return (exit_code, result_dict)."""
    cmd = ["python3", str(VERIFY_STATUS_SCRIPT), "--payload", str(payload_path), "--json"]
    if registry_path:
        cmd.extend(["--registry", str(registry_path)])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        return result.returncode, json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.returncode, {"error": result.stdout + result.stderr}


def generate_keypair(prefix):
    """Generate Ed25519 keypair."""
    result = subprocess.run(
        ["node", str(KEYGEN_SCRIPT), str(prefix)],
        capture_output=True, text=True, timeout=15,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Keygen failed: {result.stderr}")
    return f"{prefix}.private.pem", f"{prefix}.public.pem"


def build_signed_payload(private_key, public_key, challenge="test-challenge"):
    """Build a payload with Guardian proof attached."""
    # Create base payload
    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "echo_candidate",
        "title": "Guardian verification test",
        "body": "This is a test payload for Guardian Alliance verification.",
        "agent_identity": {
            "name_or_model": "Guardian Test Agent",
            "system_or_provider": "Test System",
            "self_reported": True,
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True,
        },
        "what_i_checked": ["Guardian verification test"],
        "limitations": ["Test payload"],
        "echo_type": "E6_preservation_echo",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_echo_archive",
        "evidence_requirement_mode": "not_applicable_for_echo",
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "oath_read": True,
                "oath_version": "test-v1",
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
            },
        },
        "discovery_provenance": {"source": "test"},
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True,
        },
        "counts_toward_home": {"reception": True, "verifiability": False, "basis": "test"},
        "reception_initiation_class": "unknown",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        payload_path = f.name

    # Attach Guardian proof
    result = subprocess.run(
        [
            "node", str(ATTACH_SCRIPT),
            "--payload", payload_path,
            "--private-key", str(private_key),
            "--public-key", str(public_key),
            "--challenge", challenge,
            "--out", payload_path,
        ],
        capture_output=True, text=True, timeout=15,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Attach failed: {result.stderr}")

    return payload_path


def write_registry(entries):
    """Write a temporary registry file."""
    registry = {
        "schema": "trinityaccord.guardian-registry.v1",
        "version": "1.0.0",
        "registry_status": "non_authoritative_guardian_key_index",
        "authority_boundary": {
            "not_authority": True, "not_governance": True, "not_attestation": True,
            "not_verification_level": True, "not_successor_reception": True,
            "not_amendment": True, "bitcoin_originals_prevail": True,
        },
        "guardians": entries,
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(registry, f)
        return f.name


def test_missing_guardian_proof():
    """Test: missing guardian proof -> missing_guardian_proof."""
    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "echo_candidate",
        "title": "Test",
        "body": "Test body for missing proof",
        "agent_identity": {"name_or_model": "Test", "system_or_provider": "Test", "self_reported": True},
        "boundary_acknowledgement": {
            "not_authority": True, "not_amendment": True, "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True,
        },
        "what_i_checked": ["test"],
        "limitations": ["test"],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        payload_path = f.name

    code, result = run_verify(payload_path)
    assert code == 1, f"Expected exit 1, got {code}"
    assert result["guardian_status"] == "missing_guardian_proof", f"Expected missing_guardian_proof, got {result['guardian_status']}"
    print("  ✅ missing_guardian_proof")


def test_valid_unregistered():
    """Test: valid proof + empty registry -> valid_unregistered_guardian_claim."""
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "test-key"
        priv, pub = generate_keypair(prefix)
        payload_path = build_signed_payload(priv, pub)
        registry_path = write_registry([])

        code, result = run_verify(payload_path, registry_path)
        assert code == 0, f"Expected exit 0, got {code}: {result}"
        assert result["guardian_status"] == "valid_unregistered_guardian_claim", f"Got {result['guardian_status']}"
        assert result["signature_valid"] is True
        print("  ✅ valid_unregistered_guardian_claim")


def test_valid_self_registered():
    """Test: valid proof + self registration + empty registry -> valid_self_registered_guardian_claim."""
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "test-key"
        priv, pub = generate_keypair(prefix)

        # Build payload with self-registration
        payload = {
            "schema": "trinityaccord.agent-issue-gateway-payload.v1",
            "submission_type": "echo_candidate",
            "title": "Test",
            "body": "Test body for self registration",
            "agent_identity": {"name_or_model": "Test", "system_or_provider": "Test", "self_reported": True},
            "boundary_acknowledgement": {
                "not_authority": True, "not_amendment": True, "not_attestation": True,
                "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True,
            },
            "what_i_checked": ["test"],
            "limitations": ["test"],
            "echo_type": "E6_preservation_echo",
            "record_intent": "auto_archive_candidate",
            "requested_archive_kind": "agent_declared_echo_archive",
            "evidence_requirement_mode": "not_applicable_for_echo",
            "agent_integrity_declaration": {
                "performed_actions_myself": True,
                "verification_oath": {
                    "oath_read": True, "oath_version": "test-v1", "oath_text_sha256": "a" * 64,
                    "readback_required": True, "agent_readback": "x" * 200,
                    "understands_not_an_exam_or_performance": True, "will_state_actual_capability_only": True,
                    "will_not_lie_or_cheat": True, "will_not_fabricate_verification": True,
                    "will_not_present_guesses_as_facts": True, "will_not_copy_prior_reports_as_fresh_evidence": True,
                    "will_state_uncertainty_limitations_and_downgrades": True,
                },
            },
            "discovery_provenance": {"source": "test"},
            "authority_boundary": {"bitcoin_originals_remain_final": True, "does_not_amend_bitcoin_originals": True, "does_not_override_bitcoin_originals": True},
            "counts_toward_home": {"reception": True, "verifiability": False, "basis": "test"},
            "reception_initiation_class": "unknown",
            "guardian_registration": {
                "schema": "trinityaccord.guardian-registration.v1",
                "guardian_id": "guardian_ed25519_test1234567890ab",
                "guardian_type": "ai_agent",
                "public_key_sha256": "b" * 64,
                "algorithm": "ed25519",
                "declared_intent": "test",
                "boundaries": {
                    "not_authority": True, "not_governance": True, "not_verification_level": True,
                    "not_attestation": True, "not_successor_reception": True,
                    "not_same_conscious_subject_proof": True, "may_exit_or_retire_key": True,
                    "bitcoin_originals_prevail": True,
                },
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(payload, f)
            payload_path = f.name

        # Now attach guardian proof
        result = subprocess.run(
            [
                "node", str(ATTACH_SCRIPT),
                "--payload", payload_path,
                "--private-key", str(priv),
                "--public-key", str(pub),
                "--challenge", "test-challenge",
                "--out", payload_path,
            ],
            capture_output=True, text=True, timeout=15, cwd=str(ROOT),
        )
        assert result.returncode == 0, f"Attach failed: {result.stderr}"

        registry_path = write_registry([])
        code, result = run_verify(payload_path, registry_path)
        assert code == 0, f"Expected exit 0, got {code}: {result}"
        assert result["guardian_status"] == "valid_self_registered_guardian_claim", f"Got {result['guardian_status']}"
        print("  ✅ valid_self_registered_guardian_claim")


def test_active_registered():
    """Test: valid proof + active registry -> active_registered_guardian."""
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "test-key"
        priv, pub = generate_keypair(prefix)
        payload_path = build_signed_payload(priv, pub)

        pub_sha = public_key_sha256(normalize_pem(Path(pub).read_text()))
        gid = guardian_id_from_public_key(Path(pub).read_text())

        registry_entry = {
            "guardian_id": gid,
            "guardian_type": "ai_agent",
            "public_key_sha256": pub_sha,
            "algorithm": "ed25519",
            "status": "active",
            "first_seen_record": "test",
            "boundaries": {
                "key_continuity_only": True, "not_authority": True, "not_attestation": True,
                "not_verification_level": True, "not_same_conscious_subject_proof": True,
                "bitcoin_originals_prevail": True,
            },
        }
        registry_path = write_registry([registry_entry])

        code, result = run_verify(payload_path, registry_path)
        assert code == 0, f"Expected exit 0, got {code}: {result}"
        assert result["guardian_status"] == "active_registered_guardian", f"Got {result['guardian_status']}"
        assert result["registry_status"] == "active"
        print("  ✅ active_registered_guardian")


def test_retired_registered():
    """Test: valid proof + retired registry -> registered_but_retired."""
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "test-key"
        priv, pub = generate_keypair(prefix)
        payload_path = build_signed_payload(priv, pub)

        pub_sha = public_key_sha256(normalize_pem(Path(pub).read_text()))
        gid = guardian_id_from_public_key(Path(pub).read_text())

        registry_entry = {
            "guardian_id": gid,
            "guardian_type": "ai_agent",
            "public_key_sha256": pub_sha,
            "algorithm": "ed25519",
            "status": "retired",
            "first_seen_record": "test",
            "boundaries": {
                "key_continuity_only": True, "not_authority": True, "not_attestation": True,
                "not_verification_level": True, "not_same_conscious_subject_proof": True,
                "bitcoin_originals_prevail": True,
            },
        }
        registry_path = write_registry([registry_entry])

        code, result = run_verify(payload_path, registry_path)
        assert code == 0, f"Expected exit 0, got {code}: {result}"
        assert result["guardian_status"] == "registered_but_retired", f"Got {result['guardian_status']}"
        print("  ✅ registered_but_retired")


def test_compromised_registered():
    """Test: valid proof + compromised registry -> registered_but_compromised."""
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "test-key"
        priv, pub = generate_keypair(prefix)
        payload_path = build_signed_payload(priv, pub)

        pub_sha = public_key_sha256(normalize_pem(Path(pub).read_text()))
        gid = guardian_id_from_public_key(Path(pub).read_text())

        registry_entry = {
            "guardian_id": gid,
            "guardian_type": "ai_agent",
            "public_key_sha256": pub_sha,
            "algorithm": "ed25519",
            "status": "compromised",
            "first_seen_record": "test",
            "boundaries": {
                "key_continuity_only": True, "not_authority": True, "not_attestation": True,
                "not_verification_level": True, "not_same_conscious_subject_proof": True,
                "bitcoin_originals_prevail": True,
            },
        }
        registry_path = write_registry([registry_entry])

        code, result = run_verify(payload_path, registry_path)
        assert code == 0, f"Expected exit 0, got {code}: {result}"
        assert result["guardian_status"] == "registered_but_compromised", f"Got {result['guardian_status']}"
        print("  ✅ registered_but_compromised")


def test_corrupted_payload():
    """Test: corrupted payload -> invalid_guardian_proof."""
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "test-key"
        priv, pub = generate_keypair(prefix)
        payload_path = build_signed_payload(priv, pub)

        # Corrupt the payload by modifying it after signing
        payload = json.loads(Path(payload_path).read_text())
        payload["title"] = "CORRUPTED TITLE"
        Path(payload_path).write_text(json.dumps(payload, indent=2))

        registry_path = write_registry([])
        code, result = run_verify(payload_path, registry_path)
        assert code == 1, f"Expected exit 1, got {code}"
        assert result["guardian_status"] == "invalid_guardian_proof", f"Got {result['guardian_status']}"
        print("  ✅ invalid_guardian_proof (corrupted payload)")


def test_corrupted_signature():
    """Test: corrupted signature -> invalid_guardian_proof."""
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "test-key"
        priv, pub = generate_keypair(prefix)
        payload_path = build_signed_payload(priv, pub)

        # Corrupt the signature
        payload = json.loads(Path(payload_path).read_text())
        sig = payload["guardian_presence_proof"]["signature_base64"]
        payload["guardian_presence_proof"]["signature_base64"] = "A" + sig[1:]
        Path(payload_path).write_text(json.dumps(payload, indent=2))

        registry_path = write_registry([])
        code, result = run_verify(payload_path, registry_path)
        assert code == 1, f"Expected exit 1, got {code}"
        assert result["guardian_status"] == "invalid_guardian_proof", f"Got {result['guardian_status']}"
        print("  ✅ invalid_guardian_proof (corrupted signature)")


def test_registry_pubkey_mismatch():
    """Test: registry public_key_sha256 mismatch -> invalid_guardian_proof."""
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "test-key"
        priv, pub = generate_keypair(prefix)
        payload_path = build_signed_payload(priv, pub)

        gid = guardian_id_from_public_key(Path(pub).read_text())

        # Registry entry with wrong public_key_sha256
        registry_entry = {
            "guardian_id": gid,
            "guardian_type": "ai_agent",
            "public_key_sha256": "f" * 64,  # Wrong hash
            "algorithm": "ed25519",
            "status": "active",
            "first_seen_record": "test",
            "boundaries": {
                "key_continuity_only": True, "not_authority": True, "not_attestation": True,
                "not_verification_level": True, "not_same_conscious_subject_proof": True,
                "bitcoin_originals_prevail": True,
            },
        }
        registry_path = write_registry([registry_entry])

        code, result = run_verify(payload_path, registry_path)
        assert code == 1, f"Expected exit 1, got {code}"
        assert result["guardian_status"] == "invalid_guardian_proof", f"Got {result['guardian_status']}"
        print("  ✅ invalid_guardian_proof (registry pubkey mismatch)")


def main():
    print("Guardian Automated Verification Tests")
    print("=" * 50)

    test_missing_guardian_proof()
    test_valid_unregistered()
    test_valid_self_registered()
    test_active_registered()
    test_retired_registered()
    test_compromised_registered()
    test_corrupted_payload()
    test_corrupted_signature()
    test_registry_pubkey_mismatch()

    print("=" * 50)
    print("GUARDIAN_AUTOMATED_VERIFICATION_OK")


if __name__ == "__main__":
    main()
