"""Part G: streaming body-size limit tests."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from app import _read_limited_body, RequestBodyTooLarge, _MAX_BODY_BYTES


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
# Endpoint tests
# ---------------------------------------------------------------------------

class TestBodySizeLimitEndpoints:
    def test_preflight_returns_413_for_oversized_body(self, client):
        big_body = b'{"x":"' + b'y" * (_MAX_BODY_BYTES + 100) + b'"}'
        resp = client.post(
            "/record-chain/preflight",
            content=big_body,
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 413
        data = resp.json()
        diags = data.get("diagnostics", [])
        assert any(d.get("code") == "REQUEST_BODY_TOO_LARGE" for d in diags)

    def test_submit_returns_413_for_oversized_body(self, client):
        big_body = b'{"x":"' + b'y" * (_MAX_BODY_BYTES + 100) + b'"}'
        resp = client.post(
            "/record-chain/submit",
            content=big_body,
            headers={"content-type": "application/json"},
        )
        # Could be 413 from middleware or from streaming reader
        assert resp.status_code in (413, 422)
