"""Tests for receipt retrieval: durable-first lookup, error semantics, format validation."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.record_chain_intake_gateway.app import _receipt_path_from_id, _receipt_store, app


@pytest.fixture()
def client() -> TestClient:
    _receipt_store.clear()
    return TestClient(app)


# ---------------------------------------------------------------------------
# _receipt_path_from_id format validation
# ---------------------------------------------------------------------------

class TestReceiptPathFromId:
    def test_accepts_sha12(self) -> None:
        path = _receipt_path_from_id("rcg-20260613-abcdef123456")
        assert path == "record-chain/intake/receipts/2026/06/rcg-20260613-abcdef123456.receipt.json"

    def test_accepts_sha24(self) -> None:
        path = _receipt_path_from_id("rcg-20260613-abcdef123456abcdef123456")
        assert path == "record-chain/intake/receipts/2026/06/rcg-20260613-abcdef123456abcdef123456.receipt.json"

    def test_rejects_too_short(self) -> None:
        with pytest.raises(Exception):
            _receipt_path_from_id("rcg-20260613-abcdef12345")

    def test_rejects_too_long(self) -> None:
        with pytest.raises(Exception):
            _receipt_path_from_id("rcg-20260613-abcdef1234567")

    def test_rejects_old_suffix(self) -> None:
        with pytest.raises(Exception):
            _receipt_path_from_id("rcg-20260613-abcdef123456-01")

    def test_rejects_20_hex(self) -> None:
        with pytest.raises(Exception):
            _receipt_path_from_id("rcg-20260613-abcdef123456abcdef1234")

    def test_rejects_bad_date(self) -> None:
        with pytest.raises(Exception):
            _receipt_path_from_id("rcg-20261399-abcdef123456")


# ---------------------------------------------------------------------------
# GET /record-chain/receipt/{receipt_id}
# ---------------------------------------------------------------------------

class TestGetReceipt:
    def _make_stored_submission(self) -> dict:
        return {
            "schema": "trinityaccord.record-chain-submission.v2",
            "submission_type": "record_chain_entry",
            "record_type": "echo",
            "record_draft": {"record_type": "echo", "message": "test"},
        }

    def _make_receipt(self, receipt_id: str = "rcg-20260613-abcdef123456") -> dict:
        """Build a canonically path-bound receipt and matching stored hash."""
        from apps.record_chain_intake_gateway.gateway.canonical import sha256_canonical_json
        from apps.record_chain_intake_gateway.gateway.receipts import compute_receipt_sha256

        stored_submission = self._make_stored_submission()
        receipt = {
            "server_receipt_id": receipt_id,
            "accepted": True,
            "record_type": "echo",
            "receipt_path": (
                f"record-chain/intake/receipts/2026/06/{receipt_id}.receipt.json"
            ),
            "intake_submission_path": (
                f"record-chain/intake/submissions/2026/06/{receipt_id}.submission.json"
            ),
            "pending_file_path": f"record-chain/pending/{receipt_id}.echo.pending.json",
            "stored_submission_sha256": sha256_canonical_json(stored_submission),
        }
        receipt["receipt_sha256"] = compute_receipt_sha256(receipt)
        return receipt

    def _durable_reader(self, receipt: dict, *, tampered: bool = False):
        stored_submission = self._make_stored_submission()
        if tampered:
            stored_submission = {**stored_submission, "tampered": True}

        async def read(path: str):
            if path == receipt["receipt_path"]:
                return json.dumps(receipt)
            if path == receipt["intake_submission_path"]:
                return json.dumps(stored_submission)
            return None

        return read

    def test_durable_hit_returns_receipt(self, client: TestClient) -> None:
        receipt = self._make_receipt()
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new=AsyncMock(side_effect=self._durable_reader(receipt)),
        ):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 200
        body = resp.json()
        assert body["receipt"]["server_receipt_id"] == "rcg-20260613-abcdef123456"
        assert body["receipt_hash_verified"] is True
        assert body["receipt_url_binding_verified"] is True
        assert body["stored_submission_hash_verified"] is True

    def test_durable_stored_submission_hash_mismatch_fails_closed(self, client: TestClient) -> None:
        receipt = self._make_receipt()
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new=AsyncMock(side_effect=self._durable_reader(receipt, tampered=True)),
        ):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 500
        assert resp.json()["detail"]["code"] == "RECEIPT_STORED_SUBMISSION_HASH_MISMATCH"

    def test_durable_hit_updates_cache(self, client: TestClient) -> None:
        receipt = self._make_receipt()
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new=AsyncMock(side_effect=self._durable_reader(receipt)),
        ):
            client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert _receipt_store.get("rcg-20260613-abcdef123456") is not None

    def test_durable_missing_hash_returns_500(self, client: TestClient) -> None:
        receipt = {"server_receipt_id": "rcg-20260613-abcdef123456", "accepted": True}
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new_callable=AsyncMock,
            return_value=json.dumps(receipt),
        ):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 500
        assert resp.json()["detail"]["code"] == "RECEIPT_INTEGRITY_MISSING_HASH"

    def test_durable_backend_error_no_cache_returns_503(self, client: TestClient) -> None:
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new_callable=AsyncMock,
            side_effect=RuntimeError("GitHub API timeout"),
        ):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 503
        body = resp.json()
        assert body["detail"]["code"] == "RECEIPT_BACKEND_UNAVAILABLE"
        assert body["detail"]["retryable"] is True

    def test_durable_backend_error_with_cache_returns_cache_and_warning(self, client: TestClient) -> None:
        cached = self._make_receipt()
        _receipt_store["rcg-20260613-abcdef123456"] = cached
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new_callable=AsyncMock,
            side_effect=RuntimeError("GitHub API timeout"),
        ):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 200
        body = resp.json()
        assert body["receipt"]["server_receipt_id"] == "rcg-20260613-abcdef123456"
        # Warnings are now in the envelope, not inside the immutable receipt body
        assert any(
            w.get("code") == "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE"
            for w in body.get("envelope_warnings", [])
        )
        assert body["receipt_url_binding_verified"] is True
        assert body["stored_submission_hash_verified"] is False

    def test_durable_none_no_cache_returns_404(self, client: TestClient) -> None:
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new_callable=AsyncMock,
            return_value=None,
        ):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 404
        body = resp.json()
        assert body["found"] is False
        assert body["diagnostics"][0]["code"] == "RECEIPT_NOT_FOUND"
        assert body["diagnostics"][0]["retry_allowed"] is False

    def test_invalid_receipt_id_returns_400(self, client: TestClient) -> None:
        resp = client.get("/record-chain/receipt/invalid-format")
        assert resp.status_code == 400
        body = resp.json()
        assert body["detail"]["code"] == "INVALID_RECEIPT_ID_FORMAT"


    def test_success_envelope_declares_found_true(self, client: TestClient) -> None:
        receipt = self._make_receipt()

        async def read(path: str):
            if path == receipt["receipt_path"]:
                return json.dumps(receipt)
            if path == receipt["intake_submission_path"]:
                return json.dumps(self._make_stored_submission())
            return None

        with patch("apps.record_chain_intake_gateway.app.get_file_text", new=AsyncMock(side_effect=read)):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 200
        assert resp.json()["found"] is True

    def test_invalid_final_status_is_unknown_not_pending(self, client: TestClient) -> None:
        receipt = self._make_receipt()
        receipt["pending_file_path"] = "record-chain/pending/rcg-20260613-abcdef123456.echo.pending.json"
        from apps.record_chain_intake_gateway.gateway.receipts import compute_receipt_sha256
        receipt["receipt_sha256"] = compute_receipt_sha256(receipt)

        async def read(path: str):
            if path == receipt["receipt_path"]:
                return json.dumps(receipt)
            if path == receipt["intake_submission_path"]:
                return json.dumps(self._make_stored_submission())
            if path.startswith("record-chain/receipt-status/"):
                return json.dumps({"schema": "wrong"})
            return None

        with patch("apps.record_chain_intake_gateway.app.get_file_text", new=AsyncMock(side_effect=read)):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 200
        body = resp.json()
        assert body["final_status"]["append_status"] == "unknown"
        assert any(
            warning.get("code") == "RECEIPT_FINAL_STATUS_UNAVAILABLE"
            for warning in body.get("envelope_warnings", [])
            if isinstance(warning, dict)
        )
