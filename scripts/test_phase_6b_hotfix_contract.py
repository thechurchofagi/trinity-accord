"""Contract tests: Phase 6B schema hotfix.

Validates:
1. Submission schema if/then/else: formal records require oath, context_insufficient_notice does not.
2. Submit response schema accepts receipt_commit_sha, rejects receipt.commit_sha for immutable receipt.
3. external-agent-operation-examples does not contain active /gateway/preflight or /agent-submit.
4. links.json machine list contains no retired pointer files.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_SCHEMA = ROOT / "api" / "record-chain-submission-schema.v1.json"
SUBMIT_RESPONSE_API = ROOT / "api" / "record-chain-submit-response.v1.json"
SUBMIT_RESPONSE_APP = ROOT / "apps" / "record_chain_intake_gateway" / "schemas" / "submit_response.schema.json"
SERVER_RECEIPT_APP = ROOT / "apps" / "record_chain_intake_gateway" / "schemas" / "server_receipt.schema.json"
SERVER_RECEIPT_API = ROOT / "api" / "record-chain-server-receipt.v1.json"
EXTERNAL_EXAMPLES = ROOT / "api" / "external-agent-operation-examples.v1.json"
LINKS = ROOT / "api" / "links.json"


@pytest.fixture(scope="module")
def submission_schema() -> dict:
    return json.loads(SUBMISSION_SCHEMA.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def submit_response_api() -> dict:
    return json.loads(SUBMIT_RESPONSE_API.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def submit_response_app() -> dict:
    return json.loads(SUBMIT_RESPONSE_APP.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def server_receipt_app() -> dict:
    return json.loads(SERVER_RECEIPT_APP.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def server_receipt_api() -> dict:
    return json.loads(SERVER_RECEIPT_API.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def external_examples() -> dict:
    return json.loads(EXTERNAL_EXAMPLES.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def links() -> dict:
    return json.loads(LINKS.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. Submission schema if/then/else
# ---------------------------------------------------------------------------

class TestSubmissionSchemaIfThenElse:
    """Submission schema must distinguish formal records from context_insufficient_notice."""

    def test_has_if_then_else(self, submission_schema):
        assert "if" in submission_schema, "Missing top-level 'if'"
        assert "then" in submission_schema, "Missing top-level 'then'"
        assert "else" in submission_schema, "Missing top-level 'else'"

    def test_then_requires_oath_for_formal(self, submission_schema):
        then = submission_schema["then"]
        # Top-level then should require client_oath_readback
        assert "client_oath_readback" in then.get("required", []), (
            "then clause must require client_oath_readback"
        )
        # record_draft.then should require submission_oath_verification
        rd_then = then.get("properties", {}).get("record_draft", {})
        assert "submission_oath_verification" in rd_then.get("required", []), (
            "then.record_draft must require submission_oath_verification"
        )

    def test_else_no_oath_for_context_insufficient(self, submission_schema):
        else_clause = submission_schema["else"]
        rd_else = else_clause.get("properties", {}).get("record_draft", {})
        # The else clause should use "not.required" to forbid submission_oath_verification
        not_clause = rd_else.get("not", {})
        assert "submission_oath_verification" in not_clause.get("required", []), (
            "else.record_draft.not must forbid submission_oath_verification"
        )

    def test_oath_not_in_base_required(self, submission_schema):
        """submission_oath_verification should NOT be in record_draft.required
        (handled by if/then/else)."""
        rd_required = (
            submission_schema
            .get("properties", {})
            .get("record_draft", {})
            .get("required", [])
        )
        assert "submission_oath_verification" not in rd_required, (
            "submission_oath_verification must not be in base record_draft.required; "
            "it is handled by if/then/else"
        )

    def test_actor_identity_deprecated(self, submission_schema):
        actor = (
            submission_schema
            .get("properties", {})
            .get("record_draft", {})
            .get("properties", {})
            .get("actor_identity", {})
        )
        assert actor.get("deprecated") is True, "actor_identity must be marked deprecated"

    def test_boundary_deprecated(self, submission_schema):
        boundary = (
            submission_schema
            .get("properties", {})
            .get("record_draft", {})
            .get("properties", {})
            .get("boundary", {})
        )
        assert boundary.get("deprecated") is True, "boundary must be marked deprecated"


# ---------------------------------------------------------------------------
# 2. Submit response schema: receipt_commit_sha + no receipt.commit_sha
# ---------------------------------------------------------------------------

class TestSubmitResponseReceiptCommitSha:
    """Submit response must have receipt_commit_sha at envelope level."""

    def test_api_has_receipt_commit_sha(self, submit_response_api):
        props = submit_response_api.get("properties", {})
        assert "receipt_commit_sha" in props, "api response must have receipt_commit_sha"

    def test_api_receipt_commit_sha_in_required(self, submit_response_api):
        assert "receipt_commit_sha" in submit_response_api.get("required", []), (
            "receipt_commit_sha must be required in api response"
        )

    def test_app_has_receipt_commit_sha(self, submit_response_app):
        props = submit_response_app.get("properties", {})
        assert "receipt_commit_sha" in props, "app response must have receipt_commit_sha"

    def test_app_receipt_body_no_commit_sha(self, submit_response_app):
        receipt_props = (
            submit_response_app
            .get("properties", {})
            .get("receipt", {})
            .get("properties", {})
        )
        assert "commit_sha" not in receipt_props, (
            "receipt body must NOT contain commit_sha (immutable receipt); "
            "use receipt_commit_sha at envelope level"
        )

    def test_app_receipt_has_new_fields(self, submit_response_app):
        receipt_props = (
            submit_response_app
            .get("properties", {})
            .get("receipt", {})
            .get("properties", {})
        )
        for field in ["original_submission_sha256", "stored_submission_sha256",
                       "raw_readback_redacted", "oath_verification"]:
            assert field in receipt_props, f"receipt body must have '{field}'"

    def test_app_receipt_required_has_new_fields(self, submit_response_app):
        receipt_required = (
            submit_response_app
            .get("properties", {})
            .get("receipt", {})
            .get("required", [])
        )
        for field in ["original_submission_sha256", "stored_submission_sha256",
                       "raw_readback_redacted"]:
            assert field in receipt_required, f"receipt.required must include '{field}'"


# ---------------------------------------------------------------------------
# 3. Server receipt schema aligned with make_receipt()
# ---------------------------------------------------------------------------

class TestServerReceiptSchema:
    """Server receipt schema must match make_receipt() output."""

    def test_no_commit_sha_in_receipt(self, server_receipt_app):
        assert "commit_sha" not in server_receipt_app.get("properties", {}), (
            "server receipt must NOT contain commit_sha"
        )

    def test_has_new_fields(self, server_receipt_app):
        props = server_receipt_app.get("properties", {})
        for field in ["original_submission_sha256", "stored_submission_sha256",
                       "raw_readback_redacted", "oath_verification",
                       "receipt_is_not_final_chain_record"]:
            assert field in props, f"server receipt must have '{field}'"

    def test_api_mirror_exists(self, server_receipt_api):
        assert server_receipt_api.get("properties"), "api mirror must have properties"

    def test_api_mirror_no_commit_sha(self, server_receipt_api):
        assert "commit_sha" not in server_receipt_api.get("properties", {}), (
            "api server receipt mirror must NOT contain commit_sha"
        )


# ---------------------------------------------------------------------------
# 4. external-agent-operation-examples: no active /gateway/preflight or /agent-submit
# ---------------------------------------------------------------------------

class TestExternalExamplesRetired:
    """external-agent-operation-examples must be historical_archive_only."""

    def test_status_is_historical(self, external_examples):
        assert external_examples.get("status") == "historical_archive_only", (
            "external-agent-operation-examples must be historical_archive_only"
        )

    def test_has_replacement(self, external_examples):
        assert external_examples.get("replacement") == "/api/agent-first-contact.json", (
            "replacement must point to /api/agent-first-contact.json"
        )

    def test_gateway_status_historical(self, external_examples):
        gw = external_examples.get("gateway", {})
        assert gw.get("status") == "historical_archive_only", (
            "gateway section must be historical_archive_only"
        )

    def test_minimal_sections_mark_historical(self, external_examples):
        for section in ["pure_echo_minimal_recognition",
                        "v0_agent_declared_verification_minimal",
                        "guardian_stage_1_minimal_application"]:
            entry = external_examples.get(section, {})
            assert entry.get("preflight_status") == "historical_archive_only", (
                f"{section}.preflight_status must be historical_archive_only"
            )
            assert entry.get("submit_status") == "historical_archive_only", (
                f"{section}.submit_status must be historical_archive_only"
            )


# ---------------------------------------------------------------------------
# 5. links.json: machine list contains no retired pointers
# ---------------------------------------------------------------------------

class TestLinksMachineNoRetired:
    """links.json machine list must not contain retired pointer files."""

    RETIRED_PATHS = [
        "/api/route-selector.v1.json",
        "/api/gateway-runtime-contract.v1.json",
        "/api/gateway-error-diagnostics.v1.json",
    ]

    @pytest.mark.parametrize("retired", RETIRED_PATHS)
    def test_retired_not_in_machine(self, links, retired):
        machine = links.get("machine", [])
        assert retired not in machine, (
            f"'{retired}' must NOT be in machine list; it belongs in legacy_machine"
        )

    @pytest.mark.parametrize("retired", RETIRED_PATHS)
    def test_retired_in_legacy_machine(self, links, retired):
        legacy = links.get("legacy_machine", [])
        assert retired in legacy, (
            f"'{retired}' must be in legacy_machine list"
        )

    @pytest.mark.parametrize("retired", RETIRED_PATHS)
    def test_retired_in_deprecated(self, links, retired):
        deprecated = links.get("deprecated_for_new_records", [])
        assert retired in deprecated, (
            f"'{retired}' must be in deprecated_for_new_records list"
        )
