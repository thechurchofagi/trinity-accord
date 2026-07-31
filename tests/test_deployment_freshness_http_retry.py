from __future__ import annotations

import sys
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_deployment_freshness as freshness  # noqa: E402


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def test_read_live_retries_transient_connection_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def fake_urlopen(request, timeout):
        nonlocal calls
        calls += 1
        assert timeout == 7
        assert "freshness=token" in request.full_url
        if calls < 3:
            raise ConnectionResetError(104, "Connection reset by peer")
        return FakeResponse(b"current")

    sleeps: list[float] = []
    monkeypatch.setattr(freshness.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(freshness.time, "sleep", sleeps.append)

    assert freshness.read_live("https://example.test", "/status/", "token", 7) == b"current"
    assert calls == 3
    assert sleeps == [1.0, 2.0]


def test_read_live_does_not_retry_nontransient_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def fake_urlopen(request, timeout):
        nonlocal calls
        calls += 1
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)

    sleeps: list[float] = []
    monkeypatch.setattr(freshness.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(freshness.time, "sleep", sleeps.append)

    with pytest.raises(urllib.error.HTTPError) as exc_info:
        freshness.read_live("https://example.test", "/missing", "token", 7)

    assert exc_info.value.code == 404
    assert calls == 1
    assert sleeps == []
