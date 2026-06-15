"""Phase 6B Contract Hotfix I tests.

Tests:
  1. context_insufficient_notice minimal schema pass (no oath/readback/formal blocks).
  2. formal echo missing oath/readback → schema fail.
  3. formal echo with oath/readback → schema pass.
  4. links current machine files must not have status historical_archive_only.
  5. external-agent-operation-examples must not be in current machine list.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_SCHEMA = ROOT / "api" / "record-chain-submission-schema.v1.json"
LINKS = ROOT / "api" / "links.json"
EXTERNAL_EXAMPLES = ROOT / "api" / "external-agent-operation-examples.v1.json"
FIELD_HELPER = ROOT / "api" / "record-chain-field-helper.v1.json"

FORMAL_RECORD_TYPES = [
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "propagation",
    "correction",
    "classification_update",
]


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _validate_submission(schema: dict, submission: dict) -> list[str]:
    """Minimal JSON Schema validation using stdlib only.

    Returns list of error messages. Empty = valid.
    """
    errors = []

    # Check top-level required
    for field in schema.get("required", []):
        if field not in submission:
            errors.append(f"missing top-level required: {field}")

    # Check if/then/else
    if_clause = schema.get("if")
    then_clause = schema.get("then")
    else_clause = schema.get("else")

    if if_clause and then_clause and else_clause:
        rt = submission.get("record_type", "")
        is_formal = rt != "context_insufficient_notice"

        clause = then_clause if is_formal else else_clause

        # Check clause top-level required
        for field in clause.get("required", []):
            if field not in submission:
                errors.append(f"missing clause-required ({'formal' if is_formal else 'cin'}): {field}")

        # Check clause record_draft required
        rd_clause = clause.get("properties", {}).get("record_draft", {})
        draft = submission.get("record_draft", {})
        for field in rd_clause.get("required", []):
            if field not in draft:
                errors.append(f"missing record_draft clause-required ({'formal' if is_formal else 'cin'}): {field}")

        # Check not.required
        not_clause = rd_clause.get("not", {})
        for field in not_clause.get("required", []):
            if field in draft:
                errors.append(f"forbidden field in record_draft ({'formal' if is_formal else 'cin'}): {field}")

    # Check base record_draft required
    rd_schema = schema.get("properties", {}).get("record_draft", {})
    draft = submission.get("record_draft", {})
    for field in rd_schema.get("required", []):
        if field not in draft:
            errors.append(f"missing base record_draft required: {field}")

    return errors


def _minimal_cin_submission() -> dict:
    """Minimal context_insufficient_notice submission."""
    return {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "client_generated_at": "2026-06-03T00:00:00Z",
        "record_type": "context_insufficient_notice",
        "record_draft": {
            "record_type": "context_insufficient_notice",
            "submitting_participant_identity": {
                "participant_public_display_label": "test-agent",
                "participant_type": "agent",
            },
            "submission_execution_context": {
                "who_executed_the_submission": "self",
                "execution_operator_type": "agent",
            },
            "context_readiness": {
                "declared_context_level": "CC-0",
                "minimum_required_for_action": "CC-0",
                "context_sufficient_for_selected_action": False,
            },
            "authorization_context": {
                "authorization_scope": "create_context_insufficient_notice_record",
                "authorization_status": "not_required",
            },
        },
        "builder": {
            "name": "test-builder",
            "version": "1.0.0",
            "source_url": "https://example.com/builder",
        },
        "client_context": {
            "site_entry_url": "https://www.trinityaccord.org/",
            "declared_context_level": "CC-0",
        },
        "authorship_proof": {
            "schema": "trinityaccord.agent-authorship-proof.v1",
            "method": "public_key_signature",
            "algorithm": "ed25519",
            "public_key_pem": "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
            "public_key_sha256": "0" * 64,
            "signed_payload_sha256": "1" * 64,
            "signature_base64": "dGVzdA==",
            "signed_message": "test",
            "claim_boundary": {
                "not_authority": True,
                "not_attestation": True,
                "not_amendment": True,
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
    }


def _echo_submission(*, with_oath: bool = True) -> dict:
    """Echo submission (formal record type)."""
    sub = _minimal_cin_submission()
    sub["record_type"] = "echo"
    sub["record_draft"]["record_type"] = "echo"
    sub["record_draft"]["context_readiness"]["declared_context_level"] = "CC-3"
    sub["record_draft"]["context_readiness"]["minimum_required_for_action"] = "CC-3"
    sub["record_draft"]["context_readiness"]["context_sufficient_for_selected_action"] = True
    sub["record_draft"]["discovery_and_introduction_context"] = {
        "how_participant_first_discovered_trinity_accord": "self_discovered",
        "was_discovery_self_initiated": True,
        "was_discovery_introduced_by_someone_else": False,
        "introducing_party_type": "none",
        "discovery_intent_category": "open_exploration",
    }
    sub["record_draft"]["decision_autonomy_context"] = {
        "who_decided_to_create_this_record": "self",
        "was_record_creation_self_decided": True,
        "participant_declares_free_choice": True,
    }
    sub["record_draft"]["authorization_context"] = {
        "was_external_authorization_required": False,
        "authorization_status": "self_authorized",
        "authorization_scope": "create_echo_record",
    }
    sub["record_draft"]["non_authority_boundary_acknowledgement"] = {
        "not_authority": True,
        "not_governance": True,
        "not_attestation": True,
        "not_successor_reception": True,
        "not_amendment": True,
        "bitcoin_originals_prevail": True,
    }
    if with_oath:
        sub["record_draft"]["submission_oath_verification"] = {
            "oath_read": True,
            "readback_required": True,
            "participant_readback_provided": True,
            "readback_matches_canonical_oath": True,
            "readback_method_declared": "participant_generated_in_current_context",
        }
        sub["client_oath_readback"] = {
            "readback_text": "test oath text",
            "readback_text_sha256": "abc123",
        }
    return sub


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestContextInsufficientNoticeMinimal:
    """context_insufficient_notice with minimal fields must pass schema."""

    def test_minimal_cin_passes(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _minimal_cin_submission()
        errors = _validate_submission(schema, sub)
        assert not errors, f"minimal CIN should pass: {errors}"

    def test_cin_without_discovery_passes(self):
        """discovery_and_introduction_context not required for CIN."""
        schema = _load(SUBMISSION_SCHEMA)
        sub = _minimal_cin_submission()
        # Ensure no discovery context
        sub["record_draft"].pop("discovery_and_introduction_context", None)
        errors = _validate_submission(schema, sub)
        assert not errors, f"CIN without discovery should pass: {errors}"

    def test_cin_without_decision_autonomy_passes(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _minimal_cin_submission()
        sub["record_draft"].pop("decision_autonomy_context", None)
        errors = _validate_submission(schema, sub)
        assert not errors, f"CIN without decision_autonomy should pass: {errors}"

    def test_cin_without_authorization_fails(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _minimal_cin_submission()
        sub["record_draft"].pop("authorization_context", None)
        errors = _validate_submission(schema, sub)
        assert errors, "CIN without authorization_context should fail"

    def test_cin_without_boundary_ack_passes(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _minimal_cin_submission()
        sub["record_draft"].pop("non_authority_boundary_acknowledgement", None)
        errors = _validate_submission(schema, sub)
        assert not errors, f"CIN without boundary_ack should pass: {errors}"

    def test_cin_without_oath_passes(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _minimal_cin_submission()
        sub["record_draft"].pop("submission_oath_verification", None)
        errors = _validate_submission(schema, sub)
        assert not errors, f"CIN without oath should pass: {errors}"

    def test_cin_without_client_oath_readback_passes(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _minimal_cin_submission()
        sub.pop("client_oath_readback", None)
        errors = _validate_submission(schema, sub)
        assert not errors, f"CIN without client_oath_readback should pass: {errors}"

    def test_cin_forbids_oath_in_draft(self):
        """CIN must NOT have submission_oath_verification in record_draft."""
        schema = _load(SUBMISSION_SCHEMA)
        sub = _minimal_cin_submission()
        sub["record_draft"]["submission_oath_verification"] = {"oath_read": True}
        errors = _validate_submission(schema, sub)
        assert any("forbidden" in e for e in errors), (
            f"CIN with oath in draft should fail: {errors}"
        )


class TestFormalEchoOathRequired:
    """Formal echo must require oath/readback."""

    def test_echo_without_oath_fails(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _echo_submission(with_oath=False)
        errors = _validate_submission(schema, sub)
        assert any("submission_oath_verification" in e for e in errors), (
            f"echo without oath should fail: {errors}"
        )

    def test_echo_without_client_readback_fails(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _echo_submission(with_oath=True)
        sub.pop("client_oath_readback", None)
        errors = _validate_submission(schema, sub)
        assert any("client_oath_readback" in e for e in errors), (
            f"echo without client_oath_readback should fail: {errors}"
        )

    def test_echo_with_oath_passes(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _echo_submission(with_oath=True)
        errors = _validate_submission(schema, sub)
        assert not errors, f"echo with oath should pass: {errors}"

    def test_echo_missing_discovery_fails(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _echo_submission(with_oath=True)
        sub["record_draft"].pop("discovery_and_introduction_context", None)
        errors = _validate_submission(schema, sub)
        assert any("discovery_and_introduction_context" in e for e in errors), (
            f"echo without discovery should fail: {errors}"
        )

    def test_echo_missing_boundary_ack_fails(self):
        schema = _load(SUBMISSION_SCHEMA)
        sub = _echo_submission(with_oath=True)
        sub["record_draft"].pop("non_authority_boundary_acknowledgement", None)
        errors = _validate_submission(schema, sub)
        assert any("non_authority_boundary_acknowledgement" in e for e in errors), (
            f"echo without boundary_ack should fail: {errors}"
        )


class TestLinksMachineClean:
    """links.json current machine list must be clean."""

    def test_no_historical_in_machine(self):
        links = _load(LINKS)
        machine = links.get("machine", [])
        for entry in machine:
            # Check if this entry has a status marker in the links metadata
            pass  # structural check below

        # Check metadata sections at bottom
        for section_key in ["route_selector", "gateway_runtime_contract", "gateway_error_diagnostics"]:
            section = links.get(section_key, {})
            if section.get("status") == "historical_archive_only":
                url = section.get("url", "")
                assert url not in machine, (
                    f"'{url}' has status historical_archive_only but is still in machine list"
                )

    def test_external_examples_not_in_machine(self):
        links = _load(LINKS)
        machine = links.get("machine", [])
        assert "/api/external-agent-operation-examples.v1.json" not in machine, (
            "external-agent-operation-examples.v1.json must not be in current machine list"
        )

    def test_external_examples_in_legacy(self):
        links = _load(LINKS)
        assert "/api/external-agent-operation-examples.v1.json" in links.get("legacy_machine", []), (
            "external-agent-operation-examples.v1.json must be in legacy_machine"
        )

    def test_external_examples_in_deprecated(self):
        links = _load(LINKS)
        assert "/api/external-agent-operation-examples.v1.json" in links.get("deprecated_for_new_records", []), (
            "external-agent-operation-examples.v1.json must be in deprecated_for_new_records"
        )

    def test_retired_not_in_machine(self):
        links = _load(LINKS)
        machine = links.get("machine", [])
        retired = [
            "/api/route-selector.v1.json",
            "/api/gateway-runtime-contract.v1.json",
            "/api/gateway-error-diagnostics.v1.json",
        ]
        for r in retired:
            assert r not in machine, f"'{r}' must not be in machine list"


class TestFieldHelperFormalOnly:
    """Field helper must mark formal-only fields correctly."""

    def test_discovery_marked_formal_only(self):
        helper = _load(FIELD_HELPER)
        for fg in helper["field_groups"]:
            if fg["field"].startswith("discovery_and_introduction_context."):
                assert fg.get("formal_record_types_only") is True, (
                    f"'{fg['field']}' must be formal_record_types_only"
                )
                assert "context_insufficient_notice" in fg.get("not_required_for", []), (
                    f"'{fg['field']}' must list context_insufficient_notice in not_required_for"
                )

    def test_decision_autonomy_marked_formal_only(self):
        helper = _load(FIELD_HELPER)
        for fg in helper["field_groups"]:
            if fg["field"].startswith("decision_autonomy_context."):
                assert fg.get("formal_record_types_only") is True, (
                    f"'{fg['field']}' must be formal_record_types_only"
                )

    def test_authorization_marked_formal_only(self):
        helper = _load(FIELD_HELPER)
        for fg in helper["field_groups"]:
            if fg["field"].startswith("authorization_context."):
                assert fg.get("formal_record_types_only") is True, (
                    f"'{fg['field']}' must be formal_record_types_only"
                )

    def test_boundary_ack_marked_formal_only(self):
        helper = _load(FIELD_HELPER)
        for fg in helper["field_groups"]:
            if fg["field"] == "non_authority_boundary_acknowledgement":
                assert fg.get("formal_record_types_only") is True, (
                    "non_authority_boundary_acknowledgement must be formal_record_types_only"
                )
