"""The GitHub adapter must never emit token material to logs."""
from __future__ import annotations

import logging

from gateway import github_adapter


def test_token_is_returned_without_logging_any_fragment(monkeypatch, caplog):
    secret = "unit-test-secret-material-that-must-not-be-logged"
    monkeypatch.setenv("TRINITY_GITHUB_TOKEN", secret)
    caplog.set_level(logging.DEBUG)

    assert github_adapter._token() == secret
    assert secret not in caplog.text
    assert secret[:15] not in caplog.text
