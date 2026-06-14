"""Tests for linked Guardian auto-creation disabled at preflight/submit time."""
from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app import app

# In-memory receipt store (same as test_receipt.py)
from apps.record_chain_intake_gateway.app import _receipt_store


@pytest.fixture
def client() -> TestClient:
    _receipt_store.clear()
    return TestClient(app)


def test_preflight_rejects_linked_guardian_request(client, signed_echo_submission):
    payload = deepcopy(signed_echo_submission)
    payload["record_draft"]["optional_linked_guardian_application_request"] = {
        "does_participant_request_guardian_application_with_this_record": True,
        "guardian_public_key_sha256": payload["authorship_proof"]["public_key_sha256"],
    }

    resp = client.post("/record-chain/preflight", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["accepted"] is False
    assert any(d["code"] == "LINKED_GUARDIAN_AUTO_CREATION_DISABLED" for d in data["diagnostics"])


def test_submit_rejects_linked_guardian_request_before_write_config(client, signed_echo_submission, monkeypatch):
    payload = deepcopy(signed_echo_submission)
    payload["record_draft"]["optional_linked_guardian_application_request"] = {
        "does_participant_request_guardian_application_with_this_record": True,
        "guardian_public_key_sha256": payload["authorship_proof"]["public_key_sha256"],
    }

    for key in ("TRINITY_REPO_FULL_NAME", "TRINITY_TARGET_BRANCH", "TRINITY_GITHUB_TOKEN"):
        monkeypatch.delenv(key, raising=False)

    resp = client.post("/record-chain/submit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["accepted"] is False
    assert any(d["code"] == "LINKED_GUARDIAN_AUTO_CREATION_DISABLED" for d in data["diagnostics"])
