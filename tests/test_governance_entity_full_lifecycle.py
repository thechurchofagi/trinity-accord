from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
GATEWAY_ROOT = ROOT / "apps" / "record_chain_intake_gateway"
if str(GATEWAY_ROOT) not in sys.path:
    sys.path.insert(0, str(GATEWAY_ROOT))

import app as app_module  # noqa: E402
from scripts.test_agent_e2e_journey_matrix import build_formal_journeys  # noqa: E402


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_governance_entity_builder_gateway_and_retirement_lifecycle(monkeypatch, tmp_path):
    """Exercise the public Builder and both current gateway routes as one actor.

    The matrix builds echo, verification, Guardian application, Guardian
    retirement, propagation, and correction records with one durable Ed25519
    identity. This test then carries the Guardian lifecycle through HTTP
    preflight, dry-run submit, receipt retrieval, target binding, and a tamper
    rejection without writing to GitHub or the production Record-Chain.
    """
    build_formal_journeys(tmp_path)

    application = _load(tmp_path / "guardian.json")
    retirement = _load(tmp_path / "guardian-retirement.json")
    app_content = application["record_draft"]["guardian_application_content"]
    retirement_draft = retirement["record_draft"]

    assert retirement_draft["guardian_id"] == app_content["requested_guardian_identifier"]
    assert retirement_draft["guardian_public_key_sha256"] == app_content["guardian_public_key_sha256"]
    assert retirement_draft["guardian_id"].startswith("guardian_ed25519_")

    target_id = retirement_draft["target_guardian_application_record_id"]
    target_sha = retirement_draft["target_guardian_application_record_sha256"]
    final_application = {
        "record_id": target_id,
        "record_type": "guardian_application",
        "record_sha256": target_sha,
        "guardian_application_content": app_content,
    }

    async def get_file_text(path: str) -> str | None:
        if path == f"record-chain/records/{target_id}.json":
            return json.dumps(final_application)
        return None

    async def no_existing_idempotency(_submission_sha256: str):
        return None

    monkeypatch.setattr(app_module, "get_file_text", get_file_text)
    monkeypatch.setattr(app_module, "_read_idempotency_index", no_existing_idempotency)
    monkeypatch.setattr(app_module, "check_preflight_rate_limit", lambda _key: None)
    monkeypatch.setattr(app_module, "check_rate_limit", lambda _body: None)
    monkeypatch.setattr(app_module, "_WRITE_MODE", "dry_run")
    monkeypatch.setenv("TRINITY_REPO_FULL_NAME", "offline/test")
    monkeypatch.setenv("TRINITY_TARGET_BRANCH", "offline-audit")
    monkeypatch.setenv("TRINITY_GITHUB_TOKEN", "offline-not-used")

    client = TestClient(app_module.app)

    for payload in (application, retirement):
        preflight = client.post("/record-chain/preflight", json=payload)
        assert preflight.status_code == 200
        assert preflight.json()["accepted"] is True, preflight.json().get("diagnostics")

        submitted = client.post("/record-chain/submit", json=payload)
        assert submitted.status_code == 200
        response = submitted.json()
        assert response["accepted"] is True
        assert response["submitted"] is True
        assert response["append_status"] == "dry_run"
        assert response["boundary"]["receipt_is_not_final_chain_record"] is True
        assert response["receipt"]["receipt_is_not_final_chain_record"] is True

        receipt = client.get(f"/record-chain/receipt/{response['receipt_id']}")
        assert receipt.status_code == 200
        receipt_envelope = receipt.json()
        assert receipt_envelope["receipt_id"] == response["receipt_id"]
        assert receipt_envelope["receipt"]["server_receipt_id"] == response["receipt_id"]
        assert receipt_envelope["receipt_hash_verified"] is True

    tampered = copy.deepcopy(retirement)
    tampered["record_draft"]["guardian_id"] = "auto"
    rejected = client.post("/record-chain/preflight", json=tampered)
    assert rejected.status_code == 200
    assert rejected.json()["accepted"] is False
    codes = {item["code"] for item in rejected.json()["diagnostics"]}
    assert "INVALID_GUARDIAN_ID" in codes
    assert "AUTHORSHIP_PAYLOAD_SHA_MISMATCH" in codes
