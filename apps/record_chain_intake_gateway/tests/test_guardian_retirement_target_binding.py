"""Guardian retirement preflight/submit must bind to the final application."""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import app as app_module


client = TestClient(app_module.app)


TARGET_ID = "R-000000054"
TARGET_SHA = "a" * 64
GUARDIAN_KEY = "b" * 64
GUARDIAN_ID = "guardian_ed25519_bbbbbbbbbbbbbbbb"


def retirement_submission() -> dict:
    return {
        "record_type": "guardian_retirement",
        "record_draft": {
            "record_type": "guardian_retirement",
            "guardian_id": GUARDIAN_ID,
            "guardian_public_key_sha256": GUARDIAN_KEY,
            "target_guardian_application_record_id": TARGET_ID,
            "target_guardian_application_record_sha256": TARGET_SHA,
        },
    }


def target_application(**overrides: object) -> dict:
    target = {
        "record_id": TARGET_ID,
        "record_type": "guardian_application",
        "record_sha256": TARGET_SHA,
        "guardian_application_content": {
            "requested_guardian_identifier": GUARDIAN_ID,
            "guardian_public_key_sha256": GUARDIAN_KEY,
        },
    }
    target.update(overrides)
    return target


@pytest.mark.asyncio
async def test_matching_target_is_accepted(monkeypatch):
    async def get_file_text(path: str) -> str:
        assert path == f"record-chain/records/{TARGET_ID}.json"
        return json.dumps(target_application())

    monkeypatch.setattr(app_module, "get_file_text", get_file_text)
    assert await app_module._guardian_retirement_target_diagnostics(retirement_submission()) == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("target", "expected_code"),
    [
        (None, "GUARDIAN_RETIREMENT_TARGET_NOT_FOUND"),
        (target_application(record_type="echo"), "GUARDIAN_RETIREMENT_TARGET_WRONG_TYPE"),
        (target_application(record_sha256="c" * 64), "GUARDIAN_RETIREMENT_TARGET_SHA_MISMATCH"),
        (
            target_application(guardian_application_content={
                "requested_guardian_identifier": GUARDIAN_ID,
                "guardian_public_key_sha256": "c" * 64,
            }),
            "GUARDIAN_RETIREMENT_TARGET_KEY_MISMATCH",
        ),
        (
            target_application(guardian_application_content={
                "requested_guardian_identifier": "guardian_ed25519_cccccccccccccccc",
                "guardian_public_key_sha256": GUARDIAN_KEY,
            }),
            "GUARDIAN_RETIREMENT_TARGET_ID_MISMATCH",
        ),
    ],
)
async def test_invalid_target_fails_closed(monkeypatch, target, expected_code):
    async def get_file_text(_path: str) -> str | None:
        return None if target is None else json.dumps(target)

    monkeypatch.setattr(app_module, "get_file_text", get_file_text)
    diagnostics = await app_module._guardian_retirement_target_diagnostics(retirement_submission())
    assert expected_code in {diagnostic.code for diagnostic in diagnostics}


@pytest.mark.asyncio
async def test_target_lookup_failure_is_retryable_diagnostic(monkeypatch):
    async def get_file_text(_path: str) -> str:
        raise RuntimeError("temporary GitHub read failure")

    monkeypatch.setattr(app_module, "get_file_text", get_file_text)
    diagnostics = await app_module._guardian_retirement_target_diagnostics(retirement_submission())
    assert [diagnostic.code for diagnostic in diagnostics] == ["GUARDIAN_RETIREMENT_TARGET_LOOKUP_FAILED"]
    assert diagnostics[0].retry_allowed is True


@pytest.mark.parametrize("endpoint", ["/record-chain/preflight", "/record-chain/submit"])
def test_http_routes_apply_target_binding_before_acceptance(monkeypatch, endpoint):
    monkeypatch.setattr(app_module, "validate_submission", lambda _body: [])
    monkeypatch.setattr(app_module, "_client_projection_diagnostics", lambda _body: [])

    async def get_file_text(_path: str) -> str:
        return json.dumps(target_application(record_sha256="c" * 64))

    monkeypatch.setattr(app_module, "get_file_text", get_file_text)
    response = client.post(endpoint, json=retirement_submission())
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is False
    assert "GUARDIAN_RETIREMENT_TARGET_SHA_MISMATCH" in {
        diagnostic["code"] for diagnostic in data["diagnostics"]
    }
