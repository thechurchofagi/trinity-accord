from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps.record_chain_intake_gateway.gateway import github_adapter
from apps.record_chain_intake_gateway.app import _build_agent_recovery
from apps.record_chain_intake_gateway.gateway.canonical import canonical_dumps, parse_json_strict
from apps.record_chain_intake_gateway.gateway.models import Diagnostic

ROOT = Path(__file__).resolve().parents[3]


def test_strict_json_rejects_non_finite_numbers_and_duplicate_keys() -> None:
    with pytest.raises(ValueError):
        parse_json_strict(b'{"x": NaN}')
    with pytest.raises(ValueError):
        parse_json_strict(b'{"x": 1, "x": 2}')
    with pytest.raises(ValueError):
        canonical_dumps({"x": float("inf")})


def test_non_retryable_diagnostic_stops_automatic_retry() -> None:
    recovery = _build_agent_recovery([
        Diagnostic(
            code="GUARDIAN_RETIREMENT_TARGET_KEY_MISMATCH",
            severity="error",
            message="wrong key",
            retry_allowed=False,
        )
    ])
    assert recovery.should_retry is False
    assert recovery.requires_human_attention is True


@pytest.mark.asyncio
async def test_confirmed_write_reconciles_timeout_after_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    async def ambiguous_put(*args, **kwargs):
        raise TimeoutError("response lost after commit")

    async def remote_text(path: str):
        return "exact-content"

    async def remote_sha(path: str):
        return "blob-sha"

    monkeypatch.setattr(github_adapter, "put_file", ambiguous_put)
    monkeypatch.setattr(github_adapter, "get_file_text", remote_text)
    monkeypatch.setattr(github_adapter, "get_file_sha", remote_sha)

    result = await github_adapter.put_file_confirmed("x.json", "exact-content", "write")
    assert result["content"]["sha"] == "blob-sha"
    assert result["reconciled_after_error"] is True


@pytest.mark.asyncio
async def test_confirmed_write_rejects_mismatched_remote_content(monkeypatch: pytest.MonkeyPatch) -> None:
    async def failed_put(*args, **kwargs):
        raise TimeoutError("ambiguous")

    async def remote_text(path: str):
        return "different-content"

    monkeypatch.setattr(github_adapter, "put_file", failed_put)
    monkeypatch.setattr(github_adapter, "get_file_text", remote_text)

    with pytest.raises(TimeoutError):
        await github_adapter.put_file_confirmed("x.json", "intended-content", "write")


def test_public_guidance_and_workflow_contracts_are_current() -> None:
    guidance = (ROOT / "agent-record-chain-guidance/index.html").read_text(encoding="utf-8")
    assert "--guardian-stewardship-oath" in guidance
    assert "<li><code>--oath</code>" not in guidance
    assert "do not handwrite the retired draft field <code>context_level</code>" in guidance

    waiting = (ROOT / ".github/workflows/waiting-heartbeat-status-sync.yml").read_text(encoding="utf-8")
    assert "schedule:" not in waiting
    assert "push:" not in waiting

    deploy = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
    assert "\n  push:\n" in deploy
    assert "Verify live machine contract after edge propagation" in deploy
    assert "smoke_live_discovery_contract_v2.py" in deploy
    assert "check_deployment_freshness_v2.py" in deploy
    assert "Confirm immutable verify/build handoff" in deploy
    assert "Confirm immutable build/deploy handoff" in deploy

    homepage = (ROOT / ".github/workflows/homepage-status-sync.yml").read_text(encoding="utf-8")
    assert "check_deployment_freshness_v2.py" in homepage
    assert "Record asynchronous deployment handoff" in homepage
    assert "Final live deployment contract check" not in homepage
    assert "Post-dispatch freshness probe" not in homepage
    assert 'latest_main="$(git rev-parse origin/main)"' in homepage
    assert "Waiting Heartbeat Submit" in homepage

    app_source = (ROOT / "apps/record_chain_intake_gateway/app.py").read_text(encoding="utf-8")
    atomic_source = (ROOT / "apps/record_chain_intake_gateway/gateway/github_atomic.py").read_text(encoding="utf-8")
    assert "create_files_atomic" in app_source
    assert "pending_written=True" in app_source
    assert "intake: materialize" in app_source
    assert "Write 1: intake submission" not in app_source
    assert "/git/trees" in atomic_source
    assert "/git/commits" in atomic_source
    assert '"force": False' in atomic_source
    assert "pending_written (non-fatal)" not in app_source
