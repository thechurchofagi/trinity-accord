"""Gateway authorship proof validation tests.

Tests validate_submission() with:
  - valid builder-generated submission
  - missing authorship_proof
  - tampered record_draft after signing
  - guardian key mismatch
"""
from __future__ import annotations

import copy
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

# Import validation directly
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gateway.validation import validate_submission

ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"


def _build_submission(record_type: str = "echo", tmp_dir: str | None = None) -> dict:
    """Build a real submission using the builder."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        out_file = Path(td) / "submission.json"

        # Get oath
        oath_result = subprocess.run(
            ["node", str(BUILDER), "print-oath", "--record-type", record_type],
            capture_output=True, text=True, timeout=10,
        )
        assert oath_result.returncode == 0, f"print-oath failed: {oath_result.stderr}"

        cmd = [
            "node", str(BUILDER), record_type if record_type != "guardian_application" else "guardian-application",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--body", "Test echo body for gateway validation.",
            "--echo-intent", "recognition",
            "--context-level", "CC-3",
            "--context-sufficient-for-selected-action", "true",
            "--loaded-urls", "https://www.trinityaccord.org/",
            "--discovery-mode", "self_discovered",
            "--record-decision", "self",
            "--submission-executor", "self",
            "--human-operator-involved", "false",
            "--readback", oath_result.stdout,
            "--key-dir", str(key_dir),
            "--out", str(out_file),
        ]

        if record_type == "verification":
            cmd.extend([
                "--verification-level", "V3",
                "--scope-label", "test",
                "--what-was-checked", "test",
                "--verification-claim", "test claim",
                "--fresh-actions", "test action",
            ])
        elif record_type == "guardian_application":
            cmd.extend(["--guardian-id", "test-guardian"])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        assert result.returncode == 0, f"builder failed: {result.stderr[:500]}"

        return json.loads(out_file.read_text())


class TestAuthorshipProofValidation:
    """Test validate_submission() authorship checks."""

    def test_valid_builder_echo(self):
        """A valid builder-generated echo passes authorship validation."""
        sub = _build_submission("echo")
        diags = validate_submission(sub)
        # Filter to authorship-related errors only (ignore oath policy hash mismatch etc.)
        authorship_codes = {"MISSING_AUTHORSHIP_PROOF", "AUTHORSHIP_SIGNATURE_INVALID",
                           "PARTICIPANT_KEY_MISMATCH", "GUARDIAN_KEY_MISMATCH",
                           "PRIVATE_KEY_LEAK", "INVALID_AUTHORSHIP_PROOF"}
        errors = [d for d in diags if d.severity == "error" and d.code in authorship_codes]
        assert not errors, f"Authorship errors: {[d.code for d in errors]}"

    def test_missing_authorship_proof(self):
        """Missing authorship_proof is rejected."""
        sub = _build_submission("echo")
        del sub["authorship_proof"]
        diags = validate_submission(sub)
        codes = [d.code for d in diags if d.severity == "error"]
        assert "MISSING_AUTHORSHIP_PROOF" in codes, f"Expected MISSING_AUTHORSHIP_PROOF, got {codes}"

    def test_tampered_draft_after_signing(self):
        """Tampering record_draft after signing invalidates signature."""
        sub = _build_submission("echo")
        # Tamper with the draft
        sub["record_draft"]["echo_content"]["echo_text"] = "TAMPERED TEXT"
        diags = validate_submission(sub)
        codes = [d.code for d in diags if d.severity == "error"]
        assert "AUTHORSHIP_SIGNATURE_INVALID" in codes, f"Expected AUTHORSHIP_SIGNATURE_INVALID, got {codes}"

    def test_guardian_key_mismatch(self):
        """Guardian application with mismatched key is rejected."""
        sub = _build_submission("guardian_application")
        # Tamper guardian key to something different
        sub["record_draft"]["guardian_application_content"]["guardian_public_key_sha256"] = "a" * 64
        diags = validate_submission(sub)
        codes = [d.code for d in diags if d.severity == "error"]
        assert "GUARDIAN_KEY_MISMATCH" in codes, f"Expected GUARDIAN_KEY_MISMATCH, got {codes}"

    def test_participant_key_mismatch(self):
        """Participant key mismatch is rejected."""
        sub = _build_submission("echo")
        sub["record_draft"]["submitting_participant_identity"]["participant_public_key_sha256"] = "b" * 64
        diags = validate_submission(sub)
        codes = [d.code for d in diags if d.severity == "error"]
        assert "PARTICIPANT_KEY_MISMATCH" in codes, f"Expected PARTICIPANT_KEY_MISMATCH, got {codes}"

    def test_private_key_leak_rejected(self):
        """Private key material in submission is rejected."""
        sub = _build_submission("echo")
        sub["record_draft"]["echo_content"]["echo_text"] = "BEGIN PRIVATE KEY leaked"
        diags = validate_submission(sub)
        codes = [d.code for d in diags if d.severity == "error"]
        assert "PRIVATE_KEY_LEAK" in codes, f"Expected PRIVATE_KEY_LEAK, got {codes}"

    def test_valid_builder_verification(self):
        """A valid builder-generated verification passes authorship validation."""
        sub = _build_submission("verification")
        diags = validate_submission(sub)
        authorship_codes = {"MISSING_AUTHORSHIP_PROOF", "AUTHORSHIP_SIGNATURE_INVALID",
                           "PARTICIPANT_KEY_MISMATCH", "GUARDIAN_KEY_MISMATCH",
                           "PRIVATE_KEY_LEAK", "INVALID_AUTHORSHIP_PROOF"}
        errors = [d for d in diags if d.severity == "error" and d.code in authorship_codes]
        assert not errors, f"Authorship errors: {[d.code for d in errors]}"
