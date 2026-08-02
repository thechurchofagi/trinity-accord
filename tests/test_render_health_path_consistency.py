from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "reconcile_render_health_path.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "render_health_path_consistency_under_test", MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reconcile_waits_for_eventually_consistent_health_path(monkeypatch) -> None:
    module = load_module()
    service = {
        "id": "srv-gateway",
        "name": module.SERVICE_NAME,
        "healthCheckPath": "/healthz",
    }
    read_count = 0
    patch_bodies: list[dict[str, Any]] = []

    def fake_request(
        path: str,
        _token: str,
        *,
        method: str = "GET",
        body: dict[str, Any] | None = None,
    ) -> Any:
        nonlocal read_count
        if path == "/services?limit=100":
            return [{"service": dict(service)}]
        assert path == "/services/srv-gateway"
        if method == "PATCH":
            assert body is not None
            patch_bodies.append(dict(body))
            return dict(service)
        read_count += 1
        if read_count < 3:
            return dict(service)
        return {**service, "healthCheckPath": module.EXPECTED_HEALTH_PATH}

    sleeps: list[float] = []
    monkeypatch.setattr(module, "request", fake_request)
    monkeypatch.setattr(module.time, "sleep", sleeps.append)

    result = module.reconcile("token", attempts=5, delay_seconds=0.25)

    assert result["healthCheckPath"] == "/readyz"
    assert patch_bodies == [{"healthCheckPath": "/readyz"}]
    assert read_count == 3
    assert sleeps == [0.25, 0.25]


def test_reconcile_fails_closed_when_readback_never_converges(monkeypatch) -> None:
    module = load_module()
    service = {
        "id": "srv-gateway",
        "name": module.SERVICE_NAME,
        "healthCheckPath": "/healthz",
    }

    def fake_request(
        path: str,
        _token: str,
        *,
        method: str = "GET",
        body: dict[str, Any] | None = None,
    ) -> Any:
        del method, body
        if path == "/services?limit=100":
            return [{"service": dict(service)}]
        return dict(service)

    monkeypatch.setattr(module, "request", fake_request)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    with pytest.raises(SystemExit) as exc_info:
        module.reconcile("token", attempts=2, delay_seconds=0)
    assert exc_info.value.code == 1


def test_manual_and_one_time_workflows_use_consistency_helper() -> None:
    manual = (ROOT / ".github/workflows/render-manual-deploy.yml").read_text(
        encoding="utf-8"
    )
    once = (ROOT / ".github/workflows/render-gateway-deploy-once.yml").read_text(
        encoding="utf-8"
    )
    assert "python scripts/reconcile_render_health_path.py" in manual
    assert "python scripts/reconcile_render_health_path.py" in once
    assert "RENDER_HEALTH_PATH_ATTESTED" in once
