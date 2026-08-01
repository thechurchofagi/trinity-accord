"""Regression tests for Guardian semantic idempotency and append safety."""
from __future__ import annotations

import copy
import json
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import app as app_module
from conftest import _sign_draft
from gateway.canonical import sha256_canonical_json
from gateway.guardian_uniqueness import (
    GUARDIAN_STATE_PATH,
    build_guardian_uniqueness_claim,
    guardian_uniqueness_claim_paths,
)


client = TestClient(app_module.app)


def _identity(submission: dict) -> tuple[str, str]:
    content = submission["record_draft"]["guardian_application_content"]
    return content["requested_guardian_identifier"], content["guardian_public_key_sha256"]


def _empty_guardian_state() -> str:
    return json.dumps({
        "schema": "trinityaccord.derived-guardian-state.v1",
        "guardians": [],
    })


def _claim_files(submission: dict, submission_sha256: str) -> dict[str, str]:
    guardian_id, public_key_sha256 = _identity(submission)
    paths = guardian_uniqueness_claim_paths(guardian_id, public_key_sha256)
    receipt_id = "rcg-20260731-111111111111111111111111"
    receipt_path = f"record-chain/intake/receipts/2026/07/{receipt_id}.receipt.json"
    pending_path = f"record-chain/pending/{receipt_id}.guardian_application.pending.json"
    intake_path = f"record-chain/intake/submissions/2026/07/{receipt_id}.submission.json"
    return {
        path: json.dumps(build_guardian_uniqueness_claim(
            claim_kind=kind,
            guardian_id=guardian_id,
            public_key_sha256=public_key_sha256,
            submission_sha256=submission_sha256,
            receipt_id=receipt_id,
            receipt_path=receipt_path,
            pending_file_path=pending_path,
            intake_submission_path=intake_path,
            created_at="2026-07-31T00:00:00Z",
        ))
        for kind, path in paths.items()
    }


def _differently_signed_same_guardian(submission: dict) -> dict:
    duplicate = copy.deepcopy(submission)
    duplicate["record_draft"]["guardian_application_content"][
        "guardian_stewardship_oath"
    ] += " I preserve this distinct signed application attempt for testing."
    duplicate["authorship_proof"] = _sign_draft(duplicate["record_draft"])
    return duplicate


def test_preflight_rejects_identity_already_in_final_guardian_state(
    valid_guardian_application_submission,
    monkeypatch,
):
    guardian_id, public_key_sha256 = _identity(valid_guardian_application_submission)
    state = json.dumps({
        "schema": "trinityaccord.derived-guardian-state.v1",
        "guardians": [{
            "guardian_id": guardian_id,
            "guardian_public_key_sha256": public_key_sha256,
            "source_record_id": "R-000000123",
            "current_derived_status": "retired_guardian",
        }],
    })

    async def read(path: str):
        return state if path == GUARDIAN_STATE_PATH else None

    monkeypatch.setattr(app_module, "get_file_text", read)
    monkeypatch.setattr(app_module, "check_preflight_rate_limit", lambda _key: None)

    data = client.post(
        "/record-chain/preflight",
        json=valid_guardian_application_submission,
    ).json()
    assert data["accepted"] is False
    assert {item["code"] for item in data["diagnostics"]} == {
        "GUARDIAN_APPLICATION_DUPLICATE_ID",
        "GUARDIAN_APPLICATION_DUPLICATE_PUBLIC_KEY",
    }


def test_preflight_rejects_different_envelope_with_same_pending_guardian_claims(
    valid_guardian_application_submission,
    monkeypatch,
):
    duplicate = _differently_signed_same_guardian(valid_guardian_application_submission)
    first_sha = sha256_canonical_json(valid_guardian_application_submission)
    claims = _claim_files(valid_guardian_application_submission, first_sha)

    async def read(path: str):
        if path == GUARDIAN_STATE_PATH:
            return _empty_guardian_state()
        return claims.get(path)

    monkeypatch.setattr(app_module, "get_file_text", read)
    monkeypatch.setattr(app_module, "check_preflight_rate_limit", lambda _key: None)

    data = client.post("/record-chain/preflight", json=duplicate).json()
    assert data["accepted"] is False
    assert {item["code"] for item in data["diagnostics"]} == {
        "GUARDIAN_APPLICATION_DUPLICATE_ID",
        "GUARDIAN_APPLICATION_DUPLICATE_PUBLIC_KEY",
    }


def test_new_guardian_submit_atomically_materializes_both_semantic_claims(
    valid_guardian_application_submission,
    monkeypatch,
):
    atomic = AsyncMock(return_value={"commit": {"sha": "guardian-atomic-commit"}})

    async def read(path: str):
        if path == GUARDIAN_STATE_PATH:
            return _empty_guardian_state()
        return None

    monkeypatch.setenv("TRINITY_REPO_FULL_NAME", "test/repo")
    monkeypatch.setenv("TRINITY_TARGET_BRANCH", "main")
    monkeypatch.setenv("TRINITY_GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(app_module, "get_file_text", read)
    monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))
    monkeypatch.setattr(app_module, "create_files_atomic", atomic)
    monkeypatch.setattr(app_module, "dispatch_workflow", AsyncMock(return_value=None))
    monkeypatch.setattr(app_module, "check_rate_limit", lambda _body: None)

    data = client.post(
        "/record-chain/submit",
        json=valid_guardian_application_submission,
    ).json()
    assert data["accepted"] is True
    files = atomic.await_args.args[0]
    assert len(files) == 6

    guardian_id, public_key_sha256 = _identity(valid_guardian_application_submission)
    claim_paths = guardian_uniqueness_claim_paths(guardian_id, public_key_sha256)
    assert set(claim_paths.values()).issubset(files)
    for kind, path in claim_paths.items():
        claim = json.loads(files[path])
        assert claim["claim_kind"] == kind
        assert claim["submission_sha256"] == data["submission_sha256"]
        assert claim["receipt_id"] == data["receipt_id"]

    idempotency_path = next(path for path in files if "by-submission-sha256" in path)
    idempotency = json.loads(files[idempotency_path])
    assert idempotency["guardian_uniqueness_claims_written"] is True
    assert idempotency["guardian_uniqueness_claim_paths"] == claim_paths


def test_concurrent_different_guardian_application_loser_gets_semantic_rejection(
    valid_guardian_application_submission,
    monkeypatch,
):
    loser = _differently_signed_same_guardian(valid_guardian_application_submission)
    winner_sha = sha256_canonical_json(valid_guardian_application_submission)
    winner_claims = _claim_files(valid_guardian_application_submission, winner_sha)
    winner_visible = False

    async def read(path: str):
        if path == GUARDIAN_STATE_PATH:
            return _empty_guardian_state()
        if winner_visible:
            return winner_claims.get(path)
        return None

    async def lose_atomic_race(*_args, **_kwargs):
        nonlocal winner_visible
        winner_visible = True
        raise app_module.AtomicCreateConflict("concurrent semantic claim won")

    dispatch = AsyncMock()
    monkeypatch.setenv("TRINITY_REPO_FULL_NAME", "test/repo")
    monkeypatch.setenv("TRINITY_TARGET_BRANCH", "main")
    monkeypatch.setenv("TRINITY_GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(app_module, "get_file_text", read)
    monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))
    monkeypatch.setattr(app_module, "create_files_atomic", lose_atomic_race)
    monkeypatch.setattr(app_module, "dispatch_workflow", dispatch)
    monkeypatch.setattr(app_module, "check_rate_limit", lambda _body: None)

    data = client.post("/record-chain/submit", json=loser).json()
    assert data["accepted"] is False
    assert data["submitted"] is False
    assert {item["code"] for item in data["diagnostics"]} == {
        "GUARDIAN_APPLICATION_DUPLICATE_ID",
        "GUARDIAN_APPLICATION_DUPLICATE_PUBLIC_KEY",
    }
    dispatch.assert_not_awaited()


def test_guardian_uniqueness_state_lookup_fails_closed(
    valid_guardian_application_submission,
    monkeypatch,
):
    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=None))
    monkeypatch.setattr(app_module, "check_preflight_rate_limit", lambda _key: None)

    data = client.post(
        "/record-chain/preflight",
        json=valid_guardian_application_submission,
    ).json()
    assert data["accepted"] is False
    assert {item["code"] for item in data["diagnostics"]} == {
        "GUARDIAN_APPLICATION_UNIQUENESS_LOOKUP_FAILED",
    }
