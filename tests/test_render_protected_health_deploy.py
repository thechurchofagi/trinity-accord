from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_protected_deploy.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "render_protected_deploy_under_test", MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reconcile_keeps_healthz_and_updates_only_supported_settings(monkeypatch) -> None:
    module = load_module()
    service: dict[str, Any] = {
        "id": "srv-gateway",
        "name": module.base.GATEWAY_SERVICE_NAME,
        "healthCheckPath": "/healthz",
        "serviceDetails": {
            "envSpecificDetails": {
                "startCommand": "uvicorn apps.record_chain_intake_gateway.app:app"
            }
        },
    }
    env_values = dict(module.base.EXPECTED_GATEWAY_ENV)
    env_values["TRINITY_GATEWAY_RUNTIME_VERSION"] = "1.2.0-protected"
    calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def fake_request(
        path: str,
        _token: str,
        method: str = "GET",
        body: dict | None = None,
        *,
        allow_not_found: bool = False,
    ) -> Any:
        del allow_not_found
        calls.append((path, method, copy.deepcopy(body)))
        if path == "/services/srv-gateway":
            if method == "PATCH":
                assert body is not None
                assert "healthCheckPath" not in body
                details = body.get("serviceDetails")
                if isinstance(details, dict):
                    env_details = details.get("envSpecificDetails")
                    if isinstance(env_details, dict):
                        service["serviceDetails"]["envSpecificDetails"]["startCommand"] = env_details["startCommand"]
                return copy.deepcopy(service)
            return copy.deepcopy(service)
        marker = "/env-vars/"
        assert marker in path
        key = path.split(marker, 1)[1]
        if method == "PUT":
            assert body is not None and isinstance(body.get("value"), str)
            env_values[key] = body["value"]
        return {"envVar": {"key": key, "value": env_values.get(key)}}

    monkeypatch.setattr(module.base, "request", fake_request)
    refreshed = module.reconcile_gateway_config(service, "test-token")

    assert module.base.service_start_command(refreshed) == module.base.EXPECTED_GATEWAY_START_COMMAND
    assert module.base.service_health_check_path(refreshed) == "/healthz"
    assert env_values == module.base.EXPECTED_GATEWAY_ENV
    assert not any(
        method == "PATCH" and isinstance(body, dict) and "healthCheckPath" in body
        for _path, method, body in calls
    )


def test_reconcile_fails_closed_on_unexpected_health_path(monkeypatch) -> None:
    module = load_module()
    service = {
        "id": "srv-gateway",
        "name": module.base.GATEWAY_SERVICE_NAME,
        "healthCheckPath": "/unexpected",
        "serviceDetails": {
            "envSpecificDetails": {
                "startCommand": module.base.EXPECTED_GATEWAY_START_COMMAND
            }
        },
    }
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake_request(*args, **kwargs):
        calls.append((args, kwargs))
        return {}

    monkeypatch.setattr(module.base, "request", fake_request)
    with pytest.raises(SystemExit) as exc_info:
        module.reconcile_gateway_config(service, "test-token")
    assert exc_info.value.code == 1
    assert calls == []


def test_live_attestation_checks_healthz_readyz_readiness_and_oversize(monkeypatch) -> None:
    module = load_module()
    urls: list[str] = []

    def fake_public_json(
        url: str,
        *,
        method: str = "GET",
        data: bytes | None = None,
    ) -> tuple[int, dict[str, Any]]:
        urls.append(url)
        route = url.split("?", 1)[0]
        if route.endswith(("/healthz", "/readyz")):
            return 200, {
                "ok": True,
                "version": module.EXPECTED_RUNTIME_VERSION,
                "protection_required": True,
                "protection_layer_active": True,
                "protection_entrypoint": module.EXPECTED_ENTRYPOINT,
            }
        if route.endswith("/record-chain/readiness"):
            return 200, {
                "ok": True,
                "submit_ready": True,
                **module.base.EXPECTED_GATEWAY_READINESS,
                "global_acceptance_cooldown_seconds": {
                    "minimum": 3600,
                    "maximum": 7200,
                    "secret_keyed": True,
                },
            }
        assert method == "POST" and data is not None and len(data) == 100_000
        return 413, {"diagnostics": [{"code": "REQUEST_BODY_TOO_LARGE"}]}

    monkeypatch.setattr(module.base, "_public_json", fake_public_json)
    module.verify_public_gateway_protection_once("https://gateway.example")

    routes = [url.split("?", 1)[0] for url in urls]
    assert routes == [
        "https://gateway.example/healthz",
        "https://gateway.example/readyz",
        "https://gateway.example/record-chain/readiness",
        "https://gateway.example/record-chain/preflight",
    ]


def test_all_permanent_deployment_paths_use_protected_gateway_wrapper() -> None:
    secure = (ROOT / "apps/record_chain_intake_gateway/secure_entrypoint.py").read_text(
        encoding="utf-8"
    )
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    manual = (ROOT / ".github/workflows/render-manual-deploy.yml").read_text(
        encoding="utf-8"
    )
    pages = (ROOT / ".github/workflows/deploy-pages.yml").read_text(
        encoding="utf-8"
    )
    one_time = ROOT / ".github/workflows/render-gateway-deploy-once.yml"

    assert '_PROTECTED_HEALTH_PATHS = frozenset({"/healthz", "/readyz"})' in secure
    assert "healthCheckPath: /healthz" in render
    assert "TRINITY_ENFORCE_PROTECTION_LAYER" in render
    base_helper = (ROOT / "scripts/render_manual_deploy.py").read_text(encoding="utf-8")
    assert 'EXPECTED_GATEWAY_HEALTH_CHECK_PATH = "/healthz"' in base_helper
    assert "workflow_dispatch:" in manual
    assert "python scripts/render_hardened_deploy.py" in manual
    assert "python3 scripts/render_protected_deploy.py" in pages
    assert "scripts/render_(manual|protected)_deploy\\.py" in pages
    assert "python3 scripts/render_manual_deploy.py" not in pages
    assert not one_time.exists(), "temporary exact-main deployment bridge must be removed after LIVE evidence"
