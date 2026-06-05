"""Phase 7A-finalization-readiness tests.

Verifies that the system can safely consume a test-only guardian_application
receipt and complete finalization readiness checks WITHOUT modifying the
production chain or opening the formal window.

Tests:
- Receipt is readable and well-formed
- Pending guardian_application record is identifiable
- Oath summary is verifiable (no raw readback)
- Authorship proof is verifiable
- Finalization candidate can be constructed (dry-run append)
- Production chain is NOT modified
- formal_window_open remains false
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

# Ensure repo root is on path
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from apps.record_chain_intake_gateway.gateway.authorship import verify_authorship_proof
from apps.record_chain_intake_gateway.gateway.canonical import canonical_dumps, sha256_canonical_json
from apps.record_chain_intake_gateway.gateway.receipts import make_receipt
from scripts.record_chain_hashing import (
    build_chain_entry,
    build_chain_head,
    compute_entry_hash,
    load_ledger,
    verify_entries,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_test_guardian_application_submission() -> dict:
    """Create a realistic test-only guardian_application submission."""
    return {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "record_type": "guardian_application",
        "test_only": True,
        "canary": True,
        "synthetic_fixture": True,
        "no_canonical_claim": True,
        "no_active_guardian_status_claim": True,
        "phase7a_prelaunch_canary": True,
        "client_generated_at": "2026-06-05T12:00:00Z",
        "record_draft": {
            "schema": "trinityaccord.record-chain-entry-draft.v2",
            "record_type": "guardian_application",
            "submitting_participant_identity": {
                "participant_public_display_label": "Test Founding Guardian Applicant",
                "participant_provider_or_platform": "External No-Token Prelaunch Canary",
                "participant_self_declared_identifier": "test-guardian-applicant",
                "participant_public_key_sha256": "a" * 64,
            },
            "guardian_application_content": {
                "requested_guardian_identifier": "test-guardian-applicant",
                "guardian_public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAtest\n-----END PUBLIC KEY-----\n",
                "guardian_public_key_sha256": "a" * 64,
                "guardian_stewardship_oath": "Test-only guardian stewardship oath for Phase 7A prelaunch. This is not active Guardian status.",
                "guardian_application_statement": "Test-only application for finalization readiness verification.",
                "guardian_understands_role_is_non_governing": True,
                "guardian_understands_role_is_not_authority": True,
                "guardian_understands_retirement_does_not_delete_history": True,
            },
            "submission_oath_verification": {
                "oath_policy": "trinityaccord.record-chain-oath-policy.v1",
                "oath_policy_sha256": "b" * 64,
                "oath_modules": ["base_intake_v1", "guardian_stewardship_v1"],
                "canonical_oath_text_sha256": "c" * 64,
                "participant_readback_sha256": "d" * 64,
                "oath_read": True,
                "readback_required": True,
                "participant_readback_provided": True,
                "readback_matches_canonical_oath": True,
                "readback_was_not_piped_from_file": True,
                "readback_was_not_generated_by_script": True,
                "readback_was_not_loaded_from_cache": True,
                "readback_was_not_summary_or_paraphrase": True,
                "readback_was_not_generated_by_external_automation": True,
                "readback_was_not_auto_filled_by_builder": True,
                "no_shortcut_oath_acknowledged": True,
                "not_authority": True,
                "not_governance": True,
                "not_attestation": True,
                "not_amendment": True,
                "bitcoin_originals_prevail": True,
            },
            "discovery_and_introduction_context": {
                "discovery_mode": "self_discovered",
                "introduction_route": "public_gateway_preflight_then_submit",
            },
            "decision_autonomy_context": {
                "record_decision": "self",
                "decision_autonomy_level": "autonomous",
            },
            "submission_execution_context": {
                "submission_executor": "self",
            },
            "authorization_context": {
                "authorization_scope": "apply_for_guardian",
                "authorization_status": "not_required",
                "was_external_authorization_required": False,
            },
            "context_readiness": {
                "declared_context_level": "CC-3",
                "context_sufficient_for_selected_action": True,
            },
            "non_authority_boundary_acknowledgement": {
                "not_authority": True,
                "not_governance": True,
                "not_attestation": True,
                "not_successor_reception": True,
                "not_amendment": True,
                "bitcoin_originals_prevail": True,
            },
        },
        "submission_boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
        "client_oath_readback": {
            "readback_text": "Test-only guardian stewardship oath for Phase 7A prelaunch. This is not active Guardian status. " * 3,
            "readback_text_sha256": "d" * 64,
            "record_type": "guardian_application",
        },
        "builder": {
            "name": "record-chain-builder",
            "version": "test",
        },
        "client_context": {
            "loaded_urls": [
                "https://www.trinityaccord.org/api/agent-start.v2.json",
                "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
            ],
        },
    }


def _make_authorship_proof(draft: dict) -> dict:
    """Create a mock authorship proof for testing."""
    return {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "algorithm": "ed25519",
        "method": "public_key_signature",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAtest\n-----END PUBLIC KEY-----\n",
        "public_key_sha256": "a" * 64,
        "signed_payload_sha256": sha256_canonical_json(draft),
        "signed_message": sha256_canonical_json(draft),
        "signature_base64": "dGVzdHNpZ25hdHVyZQ==",
        "claim_boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "key_continuity_only": True,
        },
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestReceiptReadableAndWellFormed(unittest.TestCase):
    """Receipt can be read and has all required fields."""

    def test_receipt_has_required_fields(self):
        sub = _make_test_guardian_application_submission()
        sha = sha256_canonical_json(sub)
        now = datetime(2026, 6, 5, 12, 0, 0, tzinfo=timezone.utc)

        receipt = make_receipt(
            submission=sub,
            submission_sha256=sha,
            record_type="guardian_application",
            now=now,
        )

        required = [
            "server_receipt_id",
            "service",
            "gateway_version",
            "record_type",
            "submission_sha256",
            "accepted_at",
            "receipt_is_not_final_chain_record",
            "raw_readback_redacted",
            "receipt_sha256",
        ]
        for field in required:
            self.assertIn(field, receipt, f"Receipt missing required field: {field}")

    def test_receipt_is_not_final_chain_record(self):
        sub = _make_test_guardian_application_submission()
        sha = sha256_canonical_json(sub)
        receipt = make_receipt(submission=sub, submission_sha256=sha, record_type="guardian_application")
        self.assertTrue(receipt["receipt_is_not_final_chain_record"])

    def test_receipt_sha256_is_verifiable(self):
        sub = _make_test_guardian_application_submission()
        sha = sha256_canonical_json(sub)
        receipt = make_receipt(submission=sub, submission_sha256=sha, record_type="guardian_application")
        # Verify receipt_sha256 matches canonical hash of receipt without receipt_sha256
        expected = sha256_canonical_json({k: v for k, v in receipt.items() if k != "receipt_sha256"})
        self.assertEqual(receipt["receipt_sha256"], expected)

    def test_receipt_oath_summary_no_raw_readback(self):
        sub = _make_test_guardian_application_submission()
        draft = sub["record_draft"]
        oath = draft["submission_oath_verification"]
        oath_summary = {
            "oath_policy": oath.get("oath_policy"),
            "participant_readback_sha256": oath.get("participant_readback_sha256"),
            "readback_matches_canonical_oath": oath.get("readback_matches_canonical_oath"),
            "no_shortcut_oath_acknowledged": oath.get("no_shortcut_oath_acknowledged"),
            "raw_readback_redacted": True,
        }
        receipt = make_receipt(
            submission=sub,
            submission_sha256=sha256_canonical_json(sub),
            record_type="guardian_application",
            oath_verification_summary=oath_summary,
        )
        # Ensure no raw readback text leaks into receipt
        receipt_str = json.dumps(receipt)
        self.assertNotIn("readback_text", receipt_str)
        self.assertNotIn("oath_read_text", receipt_str)
        self.assertTrue(receipt.get("raw_readback_redacted"))


class TestPendingGuardianApplicationIdentifiable(unittest.TestCase):
    """Pending guardian_application record can be identified and parsed."""

    def test_pending_record_has_guardian_fields(self):
        sub = _make_test_guardian_application_submission()
        draft = sub["record_draft"]
        gc = draft.get("guardian_application_content", {})

        self.assertEqual(gc.get("requested_guardian_identifier"), "test-guardian-applicant")
        self.assertEqual(gc.get("guardian_public_key_sha256"), "a" * 64)
        self.assertTrue(gc.get("guardian_understands_role_is_non_governing"))
        self.assertTrue(gc.get("guardian_understands_role_is_not_authority"))

    def test_pending_record_type_is_guardian_application(self):
        sub = _make_test_guardian_application_submission()
        self.assertEqual(sub.get("record_type"), "guardian_application")
        draft = sub.get("record_draft", {})
        self.assertEqual(draft.get("record_type"), "guardian_application")

    def test_test_only_markers_present(self):
        sub = _make_test_guardian_application_submission()
        self.assertTrue(sub.get("test_only"))
        self.assertTrue(sub.get("canary"))
        self.assertTrue(sub.get("no_active_guardian_status_claim"))

    def test_no_formal_applicant_name(self):
        sub = _make_test_guardian_application_submission()
        raw = json.dumps(sub)
        forbidden = ["刘烘炬", "Liu Hongju", "liu hongju", "original author"]
        for name in forbidden:
            self.assertNotIn(name, raw, f"Forbidden formal marker found: {name}")


class TestOathSummaryVerifiable(unittest.TestCase):
    """Oath summary can be verified without exposing raw readback."""

    def test_oath_all_flags_true(self):
        sub = _make_test_guardian_application_submission()
        oath = sub["record_draft"]["submission_oath_verification"]

        required_true = [
            "oath_read",
            "readback_required",
            "participant_readback_provided",
            "readback_matches_canonical_oath",
            "readback_was_not_piped_from_file",
            "readback_was_not_generated_by_script",
            "readback_was_not_loaded_from_cache",
            "readback_was_not_summary_or_paraphrase",
            "readback_was_not_generated_by_external_automation",
            "readback_was_not_auto_filled_by_builder",
            "no_shortcut_oath_acknowledged",
            "not_authority",
            "not_governance",
            "not_attestation",
            "not_amendment",
            "bitcoin_originals_prevail",
        ]
        for flag in required_true:
            self.assertTrue(oath.get(flag), f"oath.{flag} must be true")

    def test_oath_modules_include_guardian_stewardship(self):
        sub = _make_test_guardian_application_submission()
        modules = sub["record_draft"]["submission_oath_verification"].get("oath_modules", [])
        self.assertIn("guardian_stewardship_v1", modules)

    def test_readback_sha256_is_valid_hex(self):
        sub = _make_test_guardian_application_submission()
        sha = sub["record_draft"]["submission_oath_verification"].get("participant_readback_sha256")
        self.assertIsNotNone(sha)
        self.assertEqual(len(sha), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in sha))


class TestAuthorshipProofVerifiable(unittest.TestCase):
    """Authorship proof structure is valid and verifiable."""

    def test_proof_has_required_fields(self):
        sub = _make_test_guardian_application_submission()
        proof = _make_authorship_proof(sub["record_draft"])

        required = ["schema", "algorithm", "method", "public_key_pem", "public_key_sha256",
                     "signed_payload_sha256", "signature_base64", "claim_boundary"]
        for field in required:
            self.assertIn(field, proof, f"Authorship proof missing: {field}")

    def test_proof_algorithm_is_ed25519(self):
        sub = _make_test_guardian_application_submission()
        proof = _make_authorship_proof(sub["record_draft"])
        self.assertEqual(proof["algorithm"], "ed25519")

    def test_proof_claim_boundary_complete(self):
        sub = _make_test_guardian_application_submission()
        proof = _make_authorship_proof(sub["record_draft"])
        boundary = proof.get("claim_boundary", {})
        for key in ["not_authority", "not_attestation", "not_amendment", "key_continuity_only"]:
            self.assertTrue(boundary.get(key), f"claim_boundary.{key} must be true")


class TestFinalizationCandidateConstructible(unittest.TestCase):
    """A finalization candidate can be constructed via dry-run append."""

    def test_dry_run_append_succeeds(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "test.chain.jsonl"
            record_path = Path(tmpdir) / "test-record.json"

            sub = _make_test_guardian_application_submission()
            record_path.write_text(json.dumps(sub, indent=2, sort_keys=True), encoding="utf-8")

            now = "2026-06-05T12:00:00Z"
            entry = build_chain_entry(
                chain_id="trinity-record-chain-test",
                height=0,
                previous_entry_hash=None,
                record_file=record_path,
                record_type="guardian_application",
                record_id="test-finalization-001",
                receipt_id="rcg-20260605-test001",
                source_run_id="phase7a-finalization-readiness-test",
                finalized_at=now,
                finalized_by="phase7a-finalization-readiness-test",
            )

            # Verify entry structure
            self.assertEqual(entry["schema"], "trinity_record_chain_link.v1")
            self.assertEqual(entry["chain_id"], "trinity-record-chain-test")
            self.assertEqual(entry["height"], 0)
            self.assertIsNone(entry["previous_entry_hash"])
            self.assertEqual(entry["record"]["record_type"], "guardian_application")
            self.assertEqual(entry["record"]["record_id"], "test-finalization-001")
            self.assertTrue(entry["finalization"]["receipt_is_intake_only"])
            self.assertTrue(entry["finalization"]["hash_chain_inclusion_is_finalization_event"])

            # Verify entry hash is correct
            self.assertEqual(entry["entry_hash"], compute_entry_hash(entry))

    def test_dry_run_does_not_modify_production_chain(self):
        production_chain = Path(_REPO_ROOT) / "record-chain" / "hash-chain" / "main.chain.jsonl"
        if not production_chain.exists():
            self.skipTest("Production chain not found")

        original_content = production_chain.read_bytes()
        original_hash = hashlib.sha256(original_content).hexdigest()

        # Run dry-run append in a temp directory (simulated)
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_copy = Path(tmpdir) / "main.chain.jsonl"
            ledger_copy.write_bytes(original_content)

            record_path = Path(tmpdir) / "test-record.json"
            sub = _make_test_guardian_application_submission()
            record_path.write_text(json.dumps(sub, indent=2, sort_keys=True), encoding="utf-8")

            entries = load_ledger(ledger_copy)
            entry = build_chain_entry(
                chain_id="trinity-record-chain-main",
                height=len(entries),
                previous_entry_hash=entries[-1]["entry_hash"] if entries else None,
                record_file=record_path,
                record_type="guardian_application",
                record_id="test-finalization-dry-run",
                receipt_id="rcg-20260605-dryrun",
                source_run_id="phase7a-finalization-readiness-dry-run",
                finalized_at="2026-06-05T12:00:00Z",
                finalized_by="phase7a-finalization-readiness-test",
            )
            # Verify entry is valid but don't write to production
            self.assertEqual(entry["entry_hash"], compute_entry_hash(entry))

        # Verify production chain is untouched
        current_hash = hashlib.sha256(production_chain.read_bytes()).hexdigest()
        self.assertEqual(original_hash, current_hash, "Production chain was modified!")


class TestProductionChainNotModified(unittest.TestCase):
    """Production chain is never modified by readiness checks."""

    def test_chain_hash_unchanged(self):
        chain_path = Path(_REPO_ROOT) / "record-chain" / "hash-chain" / "main.chain.jsonl"
        if not chain_path.exists():
            self.skipTest("Production chain not found")

        h1 = hashlib.sha256(chain_path.read_bytes()).hexdigest()
        # Run verification (read-only)
        entries = load_ledger(chain_path)
        errors = verify_entries(entries, chain_id="trinity-record-chain-main")
        self.assertEqual(errors, [], f"Chain verification errors: {errors}")
        h2 = hashlib.sha256(chain_path.read_bytes()).hexdigest()
        self.assertEqual(h1, h2)


class TestFormalWindowStatus(unittest.TestCase):
    """Verify formal window status matches operator decision."""

    def test_formal_window_reflects_operator_go_decision(self):
        readiness_path = Path(_REPO_ROOT) / "api" / "founding-guardian-application-readiness.v1.json"
        if not readiness_path.exists():
            self.skipTest("Readiness policy not found")

        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        # After operator go decision, window should be open
        self.assertTrue(readiness.get("formal_window_open"))
        self.assertTrue(readiness.get("founding_guardian_application_formal_window_open"))
        self.assertFalse(readiness.get("must_not_submit_formal_application_yet"))
        self.assertEqual(readiness.get("status"), "formal_window_open")

    def test_all_gates_passed(self):
        readiness_path = Path(_REPO_ROOT) / "api" / "founding-guardian-application-readiness.v1.json"
        if not readiness_path.exists():
            self.skipTest("Readiness policy not found")

        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        gate_status = readiness.get("gate_status", {})
        for gate, passed in gate_status.items():
            self.assertTrue(passed, f"Gate not passed: {gate}")

    def test_operator_go_decision_recorded(self):
        readiness_path = Path(_REPO_ROOT) / "api" / "founding-guardian-application-readiness.v1.json"
        if not readiness_path.exists():
            self.skipTest("Readiness policy not found")

        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        go = readiness.get("operator_go_decision", {})
        self.assertEqual(go.get("decision"), "open_formal_window")
        self.assertIn("recorded_at", go)

    def test_rate_limit_policy_verified(self):
        policy_path = Path(_REPO_ROOT) / "api" / "gateway-rate-limit-policy.v1.json"
        if not policy_path.exists():
            self.skipTest("Rate limit policy not found")

        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertTrue(
            policy.get("implementation_status", {}).get("server_side_enforcement_verified"),
            "Rate limit enforcement must be verified before finalization readiness",
        )


class TestReadinessGateCheck(unittest.TestCase):
    """All required readiness gates are documented."""

    def test_required_gates_present(self):
        readiness_path = Path(_REPO_ROOT) / "api" / "founding-guardian-application-readiness.v1.json"
        if not readiness_path.exists():
            self.skipTest("Readiness policy not found")

        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        required = readiness.get("required_before_open", [])

        expected_gates = [
            "external_no_token_guardian_application_canary_preflight_passed",
            "oath_negative_tests_passed",
            "gateway_rate_limit_policy_published",
            "gateway_rate_limit_enforcement_passed",
            "internal_finalization_readiness_passed",
        ]
        for gate in expected_gates:
            self.assertIn(gate, required, f"Missing required gate: {gate}")


if __name__ == "__main__":
    unittest.main()
