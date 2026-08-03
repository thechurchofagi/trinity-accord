from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_protected_deploy.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "render_protected_deploy_test", MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def deploy(deploy_id: str, commit: str, created: str, status: str):
    return {
        "deploy": {
            "id": deploy_id,
            "commit": {"id": commit},
            "createdAt": created,
            "status": status,
        }
    }


def recover(module, *, require_match: bool) -> str | None:
    return module.recover_usable_existing_deploy_id(
        service_id="srv-test",
        token="token",
        expected_commit_id="a" * 40,
        not_before_epoch=module.base.parse_utc_epoch(
            "2026-08-03T14:16:36Z", label="test"
        ),
        timeout_seconds=0.0,
        poll_seconds=0.0,
        require_match=require_match,
    )


def test_optional_recovery_skips_terminal_failure(monkeypatch, capsys):
    module = load_module()
    records = [
        deploy(
            "dep-terminal",
            "a" * 40,
            "2026-08-03T14:16:40Z",
            "deactivated",
        )
    ]
    monkeypatch.setattr(module.base, "list_recent_deploys", lambda *_args: records)
    assert recover(module, require_match=False) is None
    output = capsys.readouterr().out
    assert (
        "RENDER_DEPLOY_RECOVERY_SKIPPED_TERMINAL "
        "service_id=srv-test deploy_id=dep-terminal "
        f"commit_id={'a' * 40} status=deactivated"
    ) in output


def test_optional_recovery_reuses_only_viable_candidate(monkeypatch):
    module = load_module()
    records = [
        deploy(
            "dep-terminal",
            "a" * 40,
            "2026-08-03T14:16:40Z",
            "build_failed",
        ),
        deploy(
            "dep-viable",
            "a" * 40,
            "2026-08-03T14:16:41Z",
            "build_in_progress",
        ),
    ]
    monkeypatch.setattr(module.base, "list_recent_deploys", lambda *_args: records)
    assert recover(module, require_match=False) == "dep-viable"


def test_optional_recovery_fails_closed_on_multiple_viable_candidates(monkeypatch):
    module = load_module()
    records = [
        deploy(
            "dep-one",
            "a" * 40,
            "2026-08-03T14:16:40Z",
            "build_in_progress",
        ),
        deploy(
            "dep-two",
            "a" * 40,
            "2026-08-03T14:16:41Z",
            "live",
        ),
    ]
    monkeypatch.setattr(module.base, "list_recent_deploys", lambda *_args: records)
    with pytest.raises(SystemExit):
        recover(module, require_match=False)


def test_required_post_request_recovery_keeps_terminal_candidate(monkeypatch):
    module = load_module()
    records = [
        deploy(
            "dep-new-terminal",
            "a" * 40,
            "2026-08-03T14:16:40Z",
            "deactivated",
        )
    ]
    monkeypatch.setattr(module.base, "list_recent_deploys", lambda *_args: records)
    assert recover(module, require_match=True) == "dep-new-terminal"
