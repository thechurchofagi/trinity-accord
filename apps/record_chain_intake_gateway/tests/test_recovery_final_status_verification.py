from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from apps.record_chain_intake_gateway import secure_entrypoint as base
from apps.record_chain_intake_gateway import secure_entrypoint_hardened as hardened

ROOT = Path(__file__).resolve().parents[3]
RECEIPT_ID = "rcg-20260806-" + "a" * 24
PENDING_PATH = f"record-chain/pending/{RECEIPT_ID}.echo.pending.json"
STATUS_PATH = f"record-chain/receipt-status/{RECEIPT_ID}.json"
FINAL_ID = "R-000000123"
FINAL_PATH = f"record-chain/records/{FINAL_ID}.json"


def _appended_status(final_sha: str) -> dict:
    return {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": RECEIPT_ID,
        "pending_file_path": PENDING_PATH,
        "append_status": "appended",
        "final_record_id": FINAL_ID,
        "final_record_path": FINAL_PATH,
        "final_record_sha256": final_sha,
        "rejection_path": None,
        "rejection_code": None,
    }


@pytest.mark.asyncio
async def test_hardened_terminal_status_accepts_hash_verified_final_record(
    monkeypatch,
) -> None:
    record = {
        "record_id": FINAL_ID,
        "record_type": "echo",
        "message": "immutable",
    }
    record["record_sha256"] = base.core_gateway._record_chain_record_sha256(record)

    async def read(path: str, *, label: str):
        assert label == "final record"
        assert path == FINAL_PATH
        return json.dumps(record)

    monkeypatch.setattr(hardened, "_original_read_text", read)
    await hardened._verify_terminal_status_text(
        STATUS_PATH,
        json.dumps(_appended_status(record["record_sha256"])),
    )


@pytest.mark.asyncio
async def test_hardened_terminal_status_rejects_tampered_final_record(
    monkeypatch,
) -> None:
    original = {
        "record_id": FINAL_ID,
        "record_type": "echo",
        "message": "original",
    }
    original["record_sha256"] = base.core_gateway._record_chain_record_sha256(
        original
    )
    tampered = dict(original)
    tampered["message"] = "tampered"

    monkeypatch.setattr(
        hardened,
        "_original_read_text",
        AsyncMock(return_value=json.dumps(tampered)),
    )
    with pytest.raises(
        base.RecoveryStateInconsistent,
        match="hash recomputation failed",
    ):
        await hardened._verify_terminal_status_text(
            STATUS_PATH,
            json.dumps(_appended_status(original["record_sha256"])),
        )


@pytest.mark.asyncio
async def test_hardened_terminal_status_rejects_wrong_schema(monkeypatch) -> None:
    status = _appended_status("b" * 64)
    status["schema"] = "trinityaccord.record-chain-final-status.v0"
    monkeypatch.setattr(hardened, "_original_read_text", AsyncMock())

    with pytest.raises(base.RecoveryStateInconsistent, match="schema mismatch"):
        await hardened._verify_terminal_status_text(
            STATUS_PATH,
            json.dumps(status),
        )
    hardened._original_read_text.assert_not_awaited()


@pytest.mark.asyncio
async def test_hardened_terminal_status_rejects_misbound_rejection_metadata(
    monkeypatch,
) -> None:
    pending_name = PENDING_PATH.rsplit("/", 1)[-1]
    rejection_path = (
        f"record-chain/rejected/{pending_name[:-5]}.rejection.json"
    )
    status = {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": RECEIPT_ID,
        "pending_file_path": PENDING_PATH,
        "append_status": "rejected",
        "final_record_id": None,
        "final_record_path": None,
        "final_record_sha256": None,
        "rejection_path": rejection_path,
        "rejection_code": "VALIDATION_FAILED",
    }
    monkeypatch.setattr(
        hardened,
        "_original_read_text",
        AsyncMock(return_value=json.dumps({"source_pending": "other.pending.json"})),
    )

    with pytest.raises(
        base.RecoveryStateInconsistent,
        match="rejection source binding mismatch",
    ):
        await hardened._verify_terminal_status_text(
            STATUS_PATH,
            json.dumps(status),
        )


@pytest.mark.asyncio
async def test_hardened_reader_preserves_backend_unavailable_semantics(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        hardened,
        "_original_read_text",
        AsyncMock(side_effect=base.RecoveryBackendUnavailable("backend down")),
    )

    with pytest.raises(base.RecoveryBackendUnavailable, match="backend down"):
        await hardened._deeply_verified_read_text(
            STATUS_PATH,
            label="final receipt status",
        )


def test_render_configs_use_hardened_entrypoint() -> None:
    for path in (
        ROOT / "render.yaml",
        ROOT / "apps" / "record_chain_intake_gateway" / "render.yaml",
    ):
        text = path.read_text(encoding="utf-8")
        assert (
            "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
            in text
        )
        assert "TRINITY_GATEWAY_RUNTIME_VERSION" in text
        assert "1.2.2-protected" in text
