"""Correction is author-only at Gateway and append boundaries."""
from __future__ import annotations

import asyncio
import json

import pytest

from apps.record_chain_intake_gateway import app as app_module
import scripts.trinity_record_chain as chain


TARGET_ID = "R-000000001"
TARGET_SHA = "b" * 64
AUTHOR_KEY = "a" * 64
OTHER_KEY = "c" * 64


def submission(signer_key: str) -> dict:
    return {
        "record_type": "correction",
        "record_draft": {
            "record_type": "correction",
            "correction_content": {
                "target_record_id": TARGET_ID,
                "target_record_sha256": TARGET_SHA,
            },
        },
        "authorship_proof": {"public_key_sha256": signer_key},
    }


def target(author_key: str | None = AUTHOR_KEY) -> dict:
    value = {
        "record_id": TARGET_ID,
        "record_type": "echo",
        "record_sha256": TARGET_SHA,
    }
    if author_key is not None:
        value["authorship_proof"] = {"public_key_sha256": author_key}
    return value


def codes(monkeypatch: pytest.MonkeyPatch, body: dict, target_record: dict) -> set[str]:
    async def fake_get_file_text(path: str) -> str | None:
        assert path == f"record-chain/records/{TARGET_ID}.json"
        return json.dumps(target_record)

    monkeypatch.setattr(app_module, "get_file_text", fake_get_file_text)
    result = asyncio.run(app_module._record_target_diagnostics(body))
    return {item.code for item in result}


def test_gateway_accepts_same_author_correction(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "CORRECTION_TARGET_AUTHOR_MISMATCH" not in codes(
        monkeypatch, submission(AUTHOR_KEY), target()
    )


def test_gateway_rejects_third_party_correction(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "CORRECTION_TARGET_AUTHOR_MISMATCH" in codes(
        monkeypatch, submission(OTHER_KEY), target()
    )


def test_gateway_fails_closed_without_target_authorship(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "CORRECTION_TARGET_AUTHORSHIP_UNAVAILABLE" in codes(
        monkeypatch, submission(AUTHOR_KEY), target(None)
    )


def test_append_enforces_same_author(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr(chain, "RECORDS", tmp_path)
    (tmp_path / f"{TARGET_ID}.json").write_text(
        json.dumps(target()), encoding="utf-8"
    )
    draft = submission(AUTHOR_KEY)["record_draft"]
    draft["authorship_proof"] = {"public_key_sha256": AUTHOR_KEY}
    chain.require_record_target_binding(draft)

    wrong = json.loads(json.dumps(draft))
    wrong["authorship_proof"]["public_key_sha256"] = OTHER_KEY
    with pytest.raises(ValueError, match="correction target author mismatch"):
        chain.require_record_target_binding(wrong)
