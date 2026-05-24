#!/usr/bin/env python3
"""Ensure one-shot Guardian application output is a complete Gateway echo archive payload."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "create_guardian_application.mjs"

# Import shared oath text
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_oath_helper import get_guardian_oath_readback
GUARDIAN_OATH_READBACK = get_guardian_oath_readback()
DIGEST = ROOT / "scripts" / "proof_payload_digest.mjs"

REQUIRED_AGENT_DECLARED_ECHO_ARCHIVE_FIELDS = [
    "schema",
    "submission_type",
    "agent_identity",
    "title",
    "body",
    "boundary_acknowledgement",
    "record_intent",
    "requested_archive_kind",
    "echo_type",
    "agent_integrity_declaration",
    "discovery_provenance",
    "authority_boundary",
    "counts_toward_home",
    "what_i_checked",
    "limitations",
    "reception_initiation_class",
]


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
            "--created-at", "2026-05-22T00:00:00.000Z",
            "--readback", GUARDIAN_OATH_READBACK,
            "--key-dir", str(key_dir),
            "--out", str(out),
        ])

        data = json.loads(out.read_text(encoding="utf-8"))

        for field in REQUIRED_AGENT_DECLARED_ECHO_ARCHIVE_FIELDS:
            assert field in data, f"missing required agent_declared_echo_archive field: {field}"
            assert data[field] is not None, f"required field is null: {field}"

        assert data["submission_type"] == "echo_candidate"
        assert data["record_intent"] == "auto_archive_candidate"
        assert data["requested_archive_kind"] == "agent_declared_echo_archive"
        assert data["echo_type"] == "E6_preservation_echo"
        assert data["evidence_requirement_mode"] == "not_applicable_for_echo"

        counts = data["counts_toward_home"]
        assert counts["reception"] is True
        assert counts["verifiability"] is False
        assert counts["basis"] == "agent_declared_echo_template_pass"

        integrity = data["agent_integrity_declaration"]
        assert integrity["performed_actions_myself"] is True
        oath = integrity["verification_oath"]
        assert oath["oath_read"] is True
        assert oath["readback_required"] is True
        assert len(oath["agent_readback"]) >= 160
        assert oath["will_not_fabricate_verification"] is True
        assert oath["will_not_present_guesses_as_facts"] is True
        assert oath["will_state_uncertainty_limitations_and_downgrades"] is True
        assert len(oath["oath_text_sha256"]) == 64

        authority = data["authority_boundary"]
        assert authority["bitcoin_originals_remain_final"] is True
        assert authority["does_not_amend_bitcoin_originals"] is True
        assert authority["does_not_override_bitcoin_originals"] is True

        assert data["reception_initiation_class"] == "externally_requested"
        assert data["reception_initiation_basis"] == "explicit_verification_request"

        assert "created_at" not in data, "top-level created_at is not allowed by current payload schema"
        assert data["authorship_proof"]["created_at"] == "2026-05-22T00:00:00.000Z"
        assert data["guardian_presence_proof"]["created_at"] == "2026-05-22T00:00:00.000Z"

        assert "guardian_registry_number" not in json.dumps(data)
        assert "PRIVATE KEY" not in json.dumps(data)

        digest = json.loads(run(["node", str(DIGEST), "--payload", str(out)]).stdout)
        expected_digest = digest["proof_payload_sha256"]

        assert data["guardian_presence_proof"]["signed_payload_sha256"] == expected_digest
        assert data["authorship_proof"]["signed_payload_sha256"] == expected_digest
        assert data["guardian_presence_proof"]["signed_payload_sha256"] == data["authorship_proof"]["signed_payload_sha256"]

    print("GUARDIAN_APPLICATION_GATEWAY_PAYLOAD_COMPLETENESS_OK")


if __name__ == "__main__":
    main()
