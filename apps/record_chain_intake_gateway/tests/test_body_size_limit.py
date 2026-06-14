"""Part G: streaming body-size limit tests.

Tests both the middleware (Content-Length) path and the endpoint streaming
path (_read_limited_body) to ensure HTTP 413 is returned.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import _read_limited_body, RequestBodyTooLarge, _MAX_BODY_BYTES, _request_body_too_large_payload

client = TestClient(app_module.app)


# ---------------------------------------------------------------------------
# Fake request for unit testing _read_limited_body
# ---------------------------------------------------------------------------

class FakeRequest:
    """Fake ASGI request with async stream()."""
    def __init__(self, chunks: list[bytes]):
        self._chunks = iter(chunks)

    async def stream(self):
        for chunk in self._chunks:
            yield chunk


# ---------------------------------------------------------------------------
# Unit tests for _read_limited_body
# ---------------------------------------------------------------------------

class TestReadLimitedBody:
    @pytest.mark.asyncio
    async def test_small_body(self):
        req = FakeRequest([b"hello", b"world"])
        result = await _read_limited_body(req)
        assert result == b"helloworld"

    @pytest.mark.asyncio
    async def test_empty_body(self):
        req = FakeRequest([])
        result = await _read_limited_body(req)
        assert result == b""

    @pytest.mark.asyncio
    async def test_exact_limit(self):
        chunk = b"x" * _MAX_BODY_BYTES
        req = FakeRequest([chunk])
        result = await _read_limited_body(req)
        assert len(result) == _MAX_BODY_BYTES

    @pytest.mark.asyncio
    async def test_exceeds_limit_raises(self):
        chunk = b"x" * (_MAX_BODY_BYTES + 1)
        req = FakeRequest([chunk])
        with pytest.raises(RequestBodyTooLarge) as exc_info:
            await _read_limited_body(req)
        assert exc_info.value.size > _MAX_BODY_BYTES

    @pytest.mark.asyncio
    async def test_chunked_exceeds_limit(self):
        """Multiple small chunks that together exceed the limit."""
        chunk = b"x" * (_MAX_BODY_BYTES // 2 + 1)
        req = FakeRequest([chunk, chunk])
        with pytest.raises(RequestBodyTooLarge):
            await _read_limited_body(req)


# ---------------------------------------------------------------------------
# Endpoint tests — 413 returned (both middleware and endpoint paths)
# ---------------------------------------------------------------------------

class TestBodySizeLimitEndpoints:
    def test_preflight_413_for_oversized_body(self):
        """Middleware catches Content-Length > max → 413 with diagnostic payload."""
        big_body = b'{"x":"' + b"y" * (_MAX_BODY_BYTES + 100) + b'"}'
        resp = client.post(
            "/record-chain/preflight",
            content=big_body,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 413
        data = resp.json()
        assert data["accepted"] is False
        assert data["diagnostics"][0]["code"] == "REQUEST_BODY_TOO_LARGE"

    def test_submit_413_for_oversized_body(self):
        """Middleware catches Content-Length > max → 413 with diagnostic payload."""
        big_body = b'{"x":"' + b"y" * (_MAX_BODY_BYTES + 100) + b'"}'
        resp = client.post(
            "/record-chain/submit",
            content=big_body,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 413
        data = resp.json()
        assert data["accepted"] is False
        assert data["diagnostics"][0]["code"] == "REQUEST_BODY_TOO_LARGE"

    def test_preflight_413_via_endpoint_streaming(self, monkeypatch):
        """Endpoint streaming path returns 413 when body exceeds tiny limit.

        Monkeypatches _MAX_BODY_BYTES so both middleware and endpoint use the
        same small value. The 11-byte body exceeds the 10-byte limit.
        """
        tiny = 10
        monkeypatch.setattr(app_module, "_MAX_BODY_BYTES", tiny)
        body = b"x" * (tiny + 1)
        resp = client.post(
            "/record-chain/preflight",
            content=body,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 413

    def test_submit_413_via_endpoint_streaming(self, monkeypatch):
        """Submit endpoint streaming path returns 413."""
        tiny = 10
        monkeypatch.setattr(app_module, "_MAX_BODY_BYTES", tiny)
        body = b"x" * (tiny + 1)
        resp = client.post(
            "/record-chain/submit",
            content=body,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 413


# ---------------------------------------------------------------------------
# BLOCKER 2: Response payload shape tests
# ---------------------------------------------------------------------------

class TestRequestBodyTooLargePayload:
    def test_too_large_payload_submit_shape(self):
        """Submit 413 payload has accepted=False, submitted=False, correct diagnostic."""
        payload = _request_body_too_large_payload(_MAX_BODY_BYTES + 1, preflight=False)
        assert payload["accepted"] is False
        assert payload["submitted"] is False
        assert "preflight" not in payload
        assert payload["diagnostics"][0]["code"] == "REQUEST_BODY_TOO_LARGE"
        assert payload["diagnostics"][0]["retry_allowed"] is True

    def test_too_large_payload_preflight_shape(self):
        """Preflight 413 payload has accepted=False, preflight=True, route_detected=unknown."""
        payload = _request_body_too_large_payload(_MAX_BODY_BYTES + 1, preflight=True)
        assert payload["accepted"] is False
        assert payload["preflight"] is True
        assert payload["route_detected"] == "unknown"
        assert payload["diagnostics"][0]["code"] == "REQUEST_BODY_TOO_LARGE"
        assert "gateway_runtime" in payload
        assert "gateway_schema" in payload

    def test_preflight_413_is_jsonresponse_with_413(self, monkeypatch):
        """Preflight oversized body returns a JSONResponse with status_code 413,
        not a PreflightResponse model (which could default to 200)."""
        tiny = 10
        monkeypatch.setattr(app_module, "_MAX_BODY_BYTES", tiny)
        body = b"x" * (tiny + 1)
        resp = client.post(
            "/record-chain/preflight",
            content=body,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 413
        data = resp.json()
        # Middleware may catch it (ok/accepted/error) or endpoint may catch it
        # (accepted/preflight/diagnostics). Either way, 413 + accepted=False.
        assert data.get("accepted") is False

    def test_submit_413_is_jsonresponse_with_413(self, monkeypatch):
        """Submit oversized body returns a JSONResponse with status_code 413,
        not a SubmitResponse model (which could default to 200)."""
        tiny = 10
        monkeypatch.setattr(app_module, "_MAX_BODY_BYTES", tiny)
        body = b"x" * (tiny + 1)
        resp = client.post(
            "/record-chain/submit",
            content=body,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 413
        data = resp.json()
        # Middleware may catch it (ok/accepted/error) or endpoint may catch it
        # (accepted/submitted/diagnostics). Either way, 413 + accepted=False.
        assert data.get("accepted") is False
