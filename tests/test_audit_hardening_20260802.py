from __future__ import annotations

import json
from pathlib import Path

from apps.record_chain_intake_gateway.gateway import rate_limit


ROOT = Path(__file__).resolve().parents[1]


def test_render_healthcheck_is_intercepted_by_secure_entrypoint() -> None:
    secure = (ROOT / "apps/record_chain_intake_gateway/secure_entrypoint.py").read_text(
        encoding="utf-8"
    )
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert '_PROTECTED_HEALTH_PATHS = frozenset({"/healthz", "/readyz"})' in secure
    assert "class ProtectedProductionApp" in secure
    assert "scope.get(\"path\") in _PROTECTED_HEALTH_PATHS" in secure
    assert "healthCheckPath: /healthz" in render
    assert (
        "startCommand: uvicorn apps.record_chain_intake_gateway.secure_entrypoint:app"
        in render
    )


def test_retired_issue_gateway_profile_cannot_look_current() -> None:
    profile = json.loads(
        (ROOT / "api/agent-gateway-production-profile.json").read_text(encoding="utf-8")
    )

    assert profile["status"] == "historical_archive_only"
    assert profile["do_not_use_for_new_public_submissions"] is True
    assert profile["replacement"] == "/api/record-chain-intake-gateway.v1.json"
    assert profile["current_public_submission"]["external_agents_do_not_need_github"] is True
    assert (
        profile["current_public_submission"]
        ["external_agents_must_not_open_github_issues_for_submission"]
        is True
    )


def test_submit_participant_counter_cardinality_is_bounded(monkeypatch) -> None:
    rate_limit.reset()
    monkeypatch.setattr(rate_limit, "MAX_TRACKED_PARTICIPANTS", 3)

    for index in range(12):
        submission = {
            "record_draft": {
                "submitting_participant_identity": {
                    "participant_public_key_sha256": f"key-{index}"
                }
            }
        }
        assert rate_limit.check_rate_limit(submission) is None

    assert rate_limit.state_cardinality()["participants"] <= 3
    rate_limit.reset()


def test_preflight_client_counter_cardinality_is_bounded(monkeypatch) -> None:
    rate_limit.reset()
    monkeypatch.setattr(rate_limit, "MAX_TRACKED_PREFLIGHT_CLIENTS", 4)

    for index in range(20):
        assert rate_limit.check_preflight_rate_limit(f"client-{index}") is None

    assert rate_limit.state_cardinality()["preflight_clients"] <= 4
    rate_limit.reset()


def test_secure_entrypoint_bounds_blocked_client_guidance_state() -> None:
    secure = (ROOT / "apps/record_chain_intake_gateway/secure_entrypoint.py").read_text(
        encoding="utf-8"
    )
    assert "_MAX_BLOCKED_CLIENT_KEYS = 10_000" in secure
    assert "_BLOCKED_CLIENT_TARGET = 8_000" in secure
    assert "entries_by_client.pop(key, None)" in secure
