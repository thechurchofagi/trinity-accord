from __future__ import annotations

import pytest

from apps.record_chain_intake_gateway import secure_entrypoint
from apps.record_chain_intake_gateway.gateway.runtime import get_runtime_info


def test_keyed_cooldown_is_stable_bounded_and_secret_dependent():
    commit_sha = "a" * 40
    first = secure_entrypoint.keyed_cooldown_seconds(commit_sha, secret=b"server-secret-one")
    repeated = secure_entrypoint.keyed_cooldown_seconds(commit_sha, secret=b"server-secret-one")
    other_secret = secure_entrypoint.keyed_cooldown_seconds(commit_sha, secret=b"server-secret-two")

    assert first == repeated
    assert 3600 <= first <= 7200
    assert 3600 <= other_secret <= 7200
    assert first != other_secret


def test_production_secret_prefers_dedicated_secret(monkeypatch):
    monkeypatch.setenv("TRINITY_GITHUB_TOKEN", "github-fallback")
    monkeypatch.setenv("TRINITY_COOLDOWN_SECRET", "dedicated-secret")
    assert secure_entrypoint._server_cooldown_secret() == b"dedicated-secret"


def test_production_secret_falls_back_to_existing_gateway_token(monkeypatch):
    monkeypatch.delenv("TRINITY_COOLDOWN_SECRET", raising=False)
    monkeypatch.setenv("TRINITY_GITHUB_TOKEN", "github-fallback")
    assert secure_entrypoint._server_cooldown_secret() == b"github-fallback"


def test_production_secret_fails_closed_when_no_server_secret_exists(monkeypatch):
    monkeypatch.delenv("TRINITY_COOLDOWN_SECRET", raising=False)
    monkeypatch.delenv("TRINITY_GITHUB_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="required for unpredictable durable intake cooldowns"):
        secure_entrypoint._server_cooldown_secret()


def test_render_configs_use_secure_entrypoint():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    expected = "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
    for path in [
        root / "render.yaml",
        root / "apps/record_chain_intake_gateway/render.yaml",
    ]:
        text = path.read_text(encoding="utf-8")
        assert expected in text
        assert "TRINITY_COOLDOWN_SECRET" in text


def test_secure_entrypoint_marks_runtime_protection_active():
    info = get_runtime_info()
    assert info["protection_layer_active"] is True
    assert info["protection_entrypoint"] == "apps.record_chain_intake_gateway.secure_entrypoint:app"
    assert info["max_submission_bytes"] == 98304
    assert info["record_draft_max_bytes"] == 49152
    assert info["max_text_field_chars"] == 4000
    assert info["global_acceptance_cooldown_seconds"] == {
        "minimum": 3600,
        "maximum": 7200,
        "secret_keyed": True,
    }
