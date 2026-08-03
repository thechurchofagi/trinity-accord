from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_manual_deploy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_manual_deploy_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def deploy(deploy_id: str, commit: str, created: str, status: str = "build_in_progress"):
    return {
        "deploy": {
            "id": deploy_id,
            "commit": {"id": commit},
            "createdAt": created,
            "status": status,
        }
    }


def test_exact_deploy_candidates_bind_commit_and_time():
    module = load_module()
    expected = "a" * 40
    records = [
        deploy("dep-old", expected, "2026-08-03T14:00:00Z"),
        deploy("dep-wrong", "b" * 40, "2026-08-03T14:16:40Z"),
        deploy("dep-right", expected, "2026-08-03T14:16:40Z"),
    ]
    matches = module.exact_deploy_candidates(
        records,
        expected_commit_id=expected,
        not_before_epoch=module.parse_utc_epoch(
            "2026-08-03T14:16:36Z", label="test"
        ),
    )
    assert [module.deploy_id_from_response(item) for item in matches] == ["dep-right"]


def test_recover_unique_deploy_id_polls_until_visible(monkeypatch):
    module = load_module()
    expected = "c" * 40
    responses = [[], [deploy("dep-recovered", expected, "2026-08-03T14:16:40Z")]]
    monkeypatch.setattr(module, "list_recent_deploys", lambda *_args: responses.pop(0))
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    ticks = iter([0.0, 0.0, 0.1])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(ticks))
    recovered = module.recover_unique_deploy_id(
        service_id="srv-test",
        token="token",
        expected_commit_id=expected,
        not_before_epoch=module.parse_utc_epoch("2026-08-03T14:16:36Z", label="test"),
        timeout_seconds=1.0,
        poll_seconds=0.0,
        require_match=True,
    )
    assert recovered == "dep-recovered"


def test_recovery_fails_closed_on_multiple_matches(monkeypatch):
    module = load_module()
    expected = "d" * 40
    records = [
        deploy("dep-one", expected, "2026-08-03T14:16:40Z"),
        deploy("dep-two", expected, "2026-08-03T14:16:41Z"),
    ]
    monkeypatch.setattr(module, "list_recent_deploys", lambda *_args: records)
    monkeypatch.setattr(module.time, "monotonic", lambda: 0.0)
    with pytest.raises(SystemExit):
        module.recover_unique_deploy_id(
            service_id="srv-test",
            token="token",
            expected_commit_id=expected,
            not_before_epoch=module.parse_utc_epoch("2026-08-03T14:16:36Z", label="test"),
            timeout_seconds=1.0,
            poll_seconds=0.0,
            require_match=True,
        )


def test_recovery_returns_none_when_optional_window_has_no_match(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "list_recent_deploys", lambda *_args: [])
    ticks = iter([0.0, 1.0])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    assert module.recover_unique_deploy_id(
        service_id="srv-test",
        token="token",
        expected_commit_id="e" * 40,
        not_before_epoch=0.0,
        timeout_seconds=0.5,
        poll_seconds=0.0,
        require_match=False,
    ) is None


def test_wait_for_deploy_rejects_wrong_commit(monkeypatch):
    module = load_module()
    monkeypatch.setattr(
        module,
        "request",
        lambda *_args, **_kwargs: deploy(
            "dep-wrong", "f" * 40, "2026-08-03T14:16:40Z", status="live"
        ),
    )
    with pytest.raises(SystemExit):
        module.wait_for_deploy(
            service_id="srv-test",
            deploy_id="dep-wrong",
            token="token",
            expected_commit_id="a" * 40,
            timeout_seconds=1,
            poll_seconds=0,
        )


def test_parse_utc_epoch_requires_timezone():
    module = load_module()
    with pytest.raises(SystemExit):
        module.parse_utc_epoch("2026-08-03T14:16:36", label="test")
