"""Readiness and submit configuration checks must agree for each write mode."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

import app as app_module


def _set_repo_and_branch(monkeypatch) -> None:
    monkeypatch.setenv("TRINITY_REPO_FULL_NAME", "offline/test")
    monkeypatch.setenv("TRINITY_TARGET_BRANCH", "offline-audit")
    monkeypatch.delenv("TRINITY_GITHUB_TOKEN", raising=False)


def test_dry_run_config_does_not_require_unused_github_token(monkeypatch):
    _set_repo_and_branch(monkeypatch)
    monkeypatch.setattr(app_module, "_WRITE_MODE", "dry_run")
    app_module._check_config()


def test_github_write_mode_still_requires_token(monkeypatch):
    _set_repo_and_branch(monkeypatch)
    monkeypatch.setattr(app_module, "_WRITE_MODE", "github_contents_pending")
    with pytest.raises(HTTPException) as exc_info:
        app_module._check_config()
    assert exc_info.value.status_code == 503
    assert "TRINITY_GITHUB_TOKEN" in str(exc_info.value.detail)
