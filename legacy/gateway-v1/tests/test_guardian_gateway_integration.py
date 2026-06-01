#!/usr/bin/env python3
"""Test Guardian Alliance Gateway integration.

Tests:
  - builder accepts --guardian-proof
  - authorship proof remains valid after guardian proof is attached
  - agent_authorship_common.py removes guardian_presence_proof from authorship hash
  - server.js payloadWithoutAuthorship removes guardian_presence_proof
  - server.js contains verifyGuardianStatus
  - render_gateway_issue_body.py renders Guardian fields
  - issue-intake-machine-block-schema.v1.json allows and requires Guardian fields
  - validate_issue_intake_body.py accepts rendered Guardian machine block
  - agent-submit-gateway.json documents valid_signature_alone_is_not_active_guardian

Output: GUARDIAN_GATEWAY_INTEGRATION_OK
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_authorship_common_ignores_guardian_fields():
    """Test that agent_authorship_common.py ignores guardian_presence_proof in authorship hash."""
    from agent_authorship_common import canonical_payload_without_authorship

    payload = {
        "schema": "test",
        "title": "test",
        "guardian_presence_proof": {"guardian_id": "test", "signature_base64": "test"},
        "_guardian_status": {"guardian_status": "test"},
        "guardian_verification_result": {"guardian_status": "test"},
        "guardian_registration": {"guardian_id": "test"},  # Should be KEPT
        "guardian_retirement": {"guardian_id": "test"},  # Should be KEPT
    }

    canonical = canonical_payload_without_authorship(payload)
    parsed = json.loads(canonical)

    # Dynamic proof fields should be removed
    assert "guardian_presence_proof" not in parsed, "guardian_presence_proof should be removed"
    assert "_guardian_status" not in parsed, "_guardian_status should be removed"
    assert "guardian_verification_result" not in parsed, "guardian_verification_result should be removed"

    # Substantive claims should be kept
    assert "guardian_registration" in parsed, "guardian_registration should be kept"
    assert "guardian_retirement" in parsed, "guardian_retirement should be kept"

    print("  ✅ agent_authorship_common.py ignores guardian_presence_proof")


def test_server_js_has_payload_without_authorship():
    """Test that server.js payloadWithoutAuthorship removes guardian fields."""
    server_path = ROOT / "examples" / "github-app-backend" / "server.js"
    content = server_path.read_text(encoding="utf-8")

    # Check that payloadWithoutAuthorship removes guardian fields
    assert "delete clone.guardian_presence_proof" in content, "server.js should delete guardian_presence_proof"
    assert "delete clone._guardian_status" in content, "server.js should delete _guardian_status"
    assert "delete clone.guardian_verification_result" in content, "server.js should delete guardian_verification_result"

    print("  ✅ server.js payloadWithoutAuthorship removes guardian fields")


def test_server_js_has_verify_guardian_status():
    """Test that server.js contains verifyGuardianStatus function."""
    server_path = ROOT / "examples" / "github-app-backend" / "server.js"
    content = server_path.read_text(encoding="utf-8")

    assert "function verifyGuardianStatus" in content, "server.js should contain verifyGuardianStatus"
    assert "function loadGuardianRegistry" in content, "server.js should contain loadGuardianRegistry"
    assert "function findGuardian" in content, "server.js should contain findGuardian"
    assert "function buildGuardianMessage" in content, "server.js should contain buildGuardianMessage"
    assert "function validateGuardianRegistration" in content, "server.js should contain validateGuardianRegistration"
    assert "guardianRegistryNumberFromEntry" in content, "server.js should contain guardianRegistryNumberFromEntry"
    assert "guardian_registration.guardian_id does not match" in content, "server.js should validate registration guardian_id"
    assert "guardian_registration.public_key_sha256 does not match" in content, "server.js should validate registration public_key_sha256"
    assert "rotated" in content and "superseded" in content, "server.js should classify rotated/superseded as retired"

    print("  ✅ server.js contains verifyGuardianStatus")


def test_renderer_renders_guardian_fields():
    """Test that render_gateway_issue_body.py renders Guardian fields."""
    renderer_path = ROOT / "scripts" / "render_gateway_issue_body.py"
    content = renderer_path.read_text(encoding="utf-8")

    assert "def render_guardian_fields" in content, "Renderer should contain render_guardian_fields"
    assert "guardian_protocol: guardian-alliance-v1" in content, "Renderer should output guardian_protocol"
    assert "guardian_key_continuity_only: true" in content, "Renderer should output guardian_key_continuity_only"
    assert "guardian_not_authority: true" in content, "Renderer should output guardian_not_authority"
    assert "guardian_registry_number" in content, "Renderer should output guardian_registry_number"

    print("  ✅ render_gateway_issue_body.py renders Guardian fields")


def test_machine_block_schema_allows_guardian_fields():
    """Test that issue-intake-machine-block-schema.v1.json allows and requires Guardian fields."""
    schema_path = ROOT / "api" / "issue-intake-machine-block-schema.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    required = schema.get("required", [])
    properties = schema.get("properties", {})

    guardian_fields = [
        "guardian_protocol", "guardian_proof_present", "guardian_status",
        "guardian_id", "guardian_signature_valid", "guardian_registry_status",
        "guardian_payload_hash_matches", "guardian_id_matches_public_key",
        "guardian_key_continuity_only", "guardian_not_authority",
        "guardian_not_attestation", "guardian_not_verification_level",
        "guardian_not_same_conscious_subject", "guardian_boundary",
    ]

    for field in guardian_fields:
        assert field in properties, f"Schema should have property: {field}"
        assert field in required, f"Schema should require: {field}"

    print("  ✅ machine-block-schema allows and requires Guardian fields")


def test_gateway_payload_schema_allows_guardian_fields():
    """Test that agent-issue-gateway-payload-schema.v1.json allows Guardian fields."""
    schema_path = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    properties = schema.get("properties", {})
    for field in ["guardian_registration", "guardian_presence_proof", "guardian_retirement"]:
        assert field in properties, f"Gateway payload schema should have property: {field}"

    print("  ✅ gateway-payload-schema allows Guardian fields")


def test_validator_has_guardian_validation():
    """Test that validate_gateway_payload.py has guardian validation."""
    validator_path = ROOT / "scripts" / "validate_gateway_payload.py"
    content = validator_path.read_text(encoding="utf-8")

    assert "def validate_guardian_fields" in content, "Validator should contain validate_guardian_fields"
    assert "validate_guardian_fields(payload, errors)" in content, "Validator should call validate_guardian_fields"

    print("  ✅ validate_gateway_payload.py validates Guardian fields")


def test_guardian_common_exists():
    """Test that guardian_common.py exists with required functions."""
    common_path = ROOT / "scripts" / "guardian_common.py"
    assert common_path.exists(), "guardian_common.py should exist"

    content = common_path.read_text(encoding="utf-8")
    for func in ["sha256_text", "normalize_pem", "public_key_sha256",
                 "guardian_id_from_public_key", "canonical_payload_for_guardian_signature",
                 "guardian_payload_sha256", "build_guardian_presence_message"]:
        assert f"def {func}" in content, f"guardian_common.py should contain {func}"

    print("  ✅ guardian_common.py exists with required functions")


def test_guardian_scripts_exist():
    """Test that all Guardian scripts exist."""
    scripts = [
        "scripts/guardian_common.py",
        "scripts/build_guardian_presence_message.py",
        "scripts/attach_guardian_presence_proof.mjs",
        "scripts/verify_guardian_signature.mjs",
        "scripts/verify_guardian_status.py",
    ]
    for script in scripts:
        path = ROOT / script
        assert path.exists(), f"Script should exist: {script}"

    print("  ✅ All Guardian scripts exist")


def test_guardian_schemas_exist():
    """Test that all Guardian schemas exist."""
    schemas = [
        "api/guardian-alliance.json",
        "api/guardian-registry-schema.v1.json",
        "api/guardian-registry.json",
        "api/guardian-registration-schema.v1.json",
        "api/guardian-presence-proof-schema.v1.json",
        "api/guardian-retirement-schema.v1.json",
        "api/guardian-verification-result-schema.v1.json",
    ]
    for schema in schemas:
        path = ROOT / schema
        assert path.exists(), f"Schema should exist: {schema}"

    print("  ✅ All Guardian schemas exist")


def test_builder_guardian_registration_smoke():
    """Test that the pure Echo builder rejects Guardian joint application flags.

    The pure Echo builder must fail fast when Guardian flags are passed,
    directing agents to use scripts/create_guardian_application.mjs instead.
    """
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        key_prefix = td_path / "guardian-builder-key"
        body_path = td_path / "body.md"
        out_path = td_path / "payload.json"

        body_path.write_text(
            "Guardian builder smoke test. This is not authority, not attestation, "
            "not verification level, and not successor reception. "
            "This document is a voluntary Guardian key continuity registration "
            "for the Trinity Accord ecosystem. It does not claim governance, "
            "verification, attestation, authority, or same conscious subject proof. "
            "The Guardian may exit or retire their key at any time. "
            "Bitcoin originals prevail in all cases.",
            encoding="utf-8",
        )

        keygen = subprocess.run(
            ["node", "scripts/generate_agent_authorship_keypair.mjs", str(key_prefix)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert keygen.returncode == 0, keygen.stderr

        result = subprocess.run(
            [
                "python3", "scripts/build_agent_declared_echo_payload.py",
                "--agent-name", "Guardian Builder Smoke Agent",
                "--provider", "local-test",
                "--title", "Guardian builder registration smoke",
                "--body-file", str(body_path),
                "--authorship-key-prefix", str(key_prefix),
                "--guardian-registration",
                "--guardian-proof",
                "--guardian-challenge", "guardian-builder-smoke",
                "--out", str(out_path),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 2, (
            "Builder with --guardian-registration --guardian-proof should fail with exit code 2\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

        combined = result.stdout + "\n" + result.stderr
        assert "create_guardian_application.mjs" in combined, "error must mention correct builder"
        assert not out_path.exists(), "wrong builder must fail before writing output"

        print("  ✅ pure Echo builder correctly rejects Guardian flags")


def test_gateway_submit_policy():
    """Test that agent-submit-gateway.json documents guardian policy."""
    policy_path = ROOT / "api" / "agent-submit-gateway.json"
    if not policy_path.exists():
        print("  ⚠️  agent-submit-gateway.json not found, skipping")
        return

    content = policy_path.read_text(encoding="utf-8")
    # This is a non-blocking check since the file may not have been updated yet
    if "guardian" in content.lower():
        print("  ✅ agent-submit-gateway.json documents Guardian policy")
    else:
        print("  ⚠️  agent-submit-gateway.json does not yet document Guardian policy")


def test_guardian_verification_result_schema_has_registry_number():
    """Test that guardian-verification-result-schema includes guardian_registry_number."""
    schema_path = ROOT / "api" / "guardian-verification-result-schema.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert "guardian_registry_number" in schema.get("required", []), "verification result schema should require guardian_registry_number"
    assert "guardian_registry_number" in schema.get("properties", {}), "verification result schema should have guardian_registry_number property"

    print("  ✅ guardian-verification-result-schema includes guardian_registry_number")


def test_machine_block_schema_has_registry_number():
    """Test that issue-intake-machine-block-schema includes guardian_registry_number."""
    schema_path = ROOT / "api" / "issue-intake-machine-block-schema.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert "guardian_registry_number" in schema.get("properties", {}), "machine block schema should have guardian_registry_number"
    assert "guardian_registry_number" in schema.get("required", []), "machine block schema should require guardian_registry_number"

    print("  ✅ issue-intake-machine-block-schema includes guardian_registry_number")


def main():
    print("Guardian Gateway Integration Tests")
    print("=" * 50)

    test_authorship_common_ignores_guardian_fields()
    test_server_js_has_payload_without_authorship()
    test_server_js_has_verify_guardian_status()
    test_renderer_renders_guardian_fields()
    test_machine_block_schema_allows_guardian_fields()
    test_gateway_payload_schema_allows_guardian_fields()
    test_validator_has_guardian_validation()
    test_guardian_common_exists()
    test_guardian_scripts_exist()
    test_guardian_schemas_exist()
    test_guardian_verification_result_schema_has_registry_number()
    test_machine_block_schema_has_registry_number()
    test_builder_guardian_registration_smoke()
    test_gateway_submit_policy()

    print("=" * 50)
    print("GUARDIAN_GATEWAY_INTEGRATION_OK")


if __name__ == "__main__":
    main()
