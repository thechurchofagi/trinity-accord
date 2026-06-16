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
    def _make_receipt(self, receipt_id: str = "rcg-20260613-abcdef123456") -> dict:
        """Build a test receipt with valid receipt_sha256."""
        receipt = {"server_receipt_id": receipt_id, "accepted": True}
        from apps.record_chain_intake_gateway.gateway.receipts import compute_receipt_sha256
        receipt["receipt_sha256"] = compute_receipt_sha256(receipt)
        return receipt

    def test_durable_hit_returns_receipt(self, client: TestClient) -> None:
        receipt = self._make_receipt()
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new_callable=AsyncMock,
            return_value=json.dumps(receipt),
        ):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 200
        body = resp.json()
        assert body["receipt"]["server_receipt_id"] == "rcg-20260613-abcdef123456"
        assert body["receipt_hash_verified"] is True

    def test_durable_hit_updates_cache(self, client: TestClient) -> None:
        receipt = self._make_receipt()
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new_callable=AsyncMock,
            return_value=json.dumps(receipt),
        ):
            client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert _receipt_store.get("rcg-20260613-abcdef123456") is not None

    def test_durable_missing_hash_returns_500(self, client: TestClient) -> None:
        receipt = {"server_receipt_id": "rcg-20260613-abcdef123456", "accepted": True}  # no receipt_sha256
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
        assert any(
            w.get("code") == "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE"
            for w in body["receipt"].get("warnings", [])
        )

    def test_durable_none_no_cache_returns_404(self, client: TestClient) -> None:
        with patch(
            "apps.record_chain_intake_gateway.app.get_file_text",
            new_callable=AsyncMock,
            return_value=None,
        ):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 404
        body = resp.json()
        assert body["detail"]["code"] == "RECEIPT_NOT_FOUND"
        assert body["detail"]["retryable"] is False

    def test_invalid_receipt_id_returns_400(self, client: TestClient) -> None:
        resp = client.get("/record-chain/receipt/invalid-format")
        assert resp.status_code == 400
        body = resp.json()
        assert body["detail"]["code"] == "INVALID_RECEIPT_ID_FORMAT"
