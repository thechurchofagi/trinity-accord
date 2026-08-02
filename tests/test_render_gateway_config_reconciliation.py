from __future__ import annotations

import io
import importlib.util
import urllib.error
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_manual_deploy.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "render_manual_deploy_config_under_test", MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _service(module, command: str, health_path: str | None = None) -> dict[str, Any]:
    return {
        "id": "srv-gateway",
        "name": module.GATEWAY_SERVICE_NAME,
        "autoDeploy": "no",
        "suspended": "not_suspended",
        "healthCheckPath": (
            module.EXPECTED_GATEWAY_HEALTH_CHECK_PATH
            if health_path is None
            else health_path
        ),
        "serviceDetails": {
            "envSpecificDetails": {
                "startCommand": command,
            }
        },
    }


def test_reconcile_updates_and_reads_back_start_command_health_and_limits(monkeypatch):
    module = load_module()
    service = _service(
        module,
        "uvicorn apps.record_chain_intake_gateway.app:app",
        health_path="/healthz",
    )
    current_command = service["serviceDetails"]["envSpecificDetails"]["startCommand"]
    current_health_path = service["healthCheckPath"]
    env = {key: "stale" for key in module.EXPECTED_GATEWAY_ENV}
    calls: list[tuple[str, str, dict[str, Any]]] = []

    def fake_request(
        path: str,
        _token: str,
        method: str = "GET",
        body=None,
        *,
        allow_not_found: bool = False,
    ):
        del allow_not_found
        nonlocal current_command, current_health_path
        calls.append((path, method, dict(body or {})))
        if path == "/services/srv-gateway" and method == "PATCH":
            if "serviceDetails" in body:
                current_command = body["serviceDetails"]["envSpecificDetails"]["startCommand"]
            if "healthCheckPath" in body:
                current_health_path = body["healthCheckPath"]
            return {}
        if path == "/services/srv-gateway" and method == "GET":
            return _service(module, current_command, health_path=current_health_path)
        key = path.rsplit("/", 1)[-1]
        if method == "PUT":
            env[key] = body["value"]
            return {"key": key, "value": env[key]}
        return {"key": key, "value": env[key]}

    monkeypatch.setattr(module, "request", fake_request)
    refreshed = module.reconcile_gateway_config(service, "render-token")

    assert module.service_start_command(refreshed) == module.EXPECTED_GATEWAY_START_COMMAND
    assert module.service_health_check_path(refreshed) == "/readyz"
    assert env == module.EXPECTED_GATEWAY_ENV
    assert any(
        method == "PATCH" and body == {"healthCheckPath": "/readyz"}
        for _path, method, body in calls
    )
    assert sum(method == "PUT" for _path, method, _body in calls) == len(
        module.EXPECTED_GATEWAY_ENV
    )


def test_reconcile_creates_missing_environment_limits(monkeypatch):
    module = load_module()
    service = _service(module, module.EXPECTED_GATEWAY_START_COMMAND)
    env: dict[str, str] = {}
    missing_reads: list[str] = []

    def fake_request(
        path: str,
        _token: str,
        method: str = "GET",
        body=None,
        *,
        allow_not_found: bool = False,
    ):
        if path == "/services/srv-gateway":
            return service
        key = path.rsplit("/", 1)[-1]
        if method == "PUT":
            env[key] = body["value"]
            return {"key": key, "value": env[key]}
        if key not in env:
            assert allow_not_found is True
            missing_reads.append(key)
            return None
        return {"key": key, "value": env[key]}

    monkeypatch.setattr(module, "request", fake_request)
    module.reconcile_gateway_config(service, "render-token")

    assert set(missing_reads) == set(module.EXPECTED_GATEWAY_ENV)
    assert env == module.EXPECTED_GATEWAY_ENV


def test_request_can_treat_only_an_expected_404_as_missing(monkeypatch):
    module = load_module()

    def missing(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://api.render.com/v1/services/srv/env-vars/NEW_LIMIT",
            404,
            "Not Found",
            {},
            io.BytesIO(b'{"message":"not found: NEW_LIMIT"}'),
        )

    monkeypatch.setattr(module.urllib.request, "urlopen", missing)

    assert (
        module.request(
            "/services/srv/env-vars/NEW_LIMIT",
            "render-token",
            allow_not_found=True,
        )
        is None
    )
    with pytest.raises(SystemExit) as exc_info:
        module.request("/services/srv/env-vars/NEW_LIMIT", "render-token")
    assert exc_info.value.code == 1


def test_public_attestation_requires_protected_readyz_runtime_and_oversize_413(monkeypatch):
    module = load_module()
    calls: list[str] = []

    def fake_public_json(url: str, *, method: str = "GET", data=None):
        calls.append(url)
        if url.split("?", 1)[0].endswith("/readyz"):
            return 200, {
                "ok": True,
                "version": module.EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_RUNTIME_VERSION"],
                "protection_layer_active": True,
                "protection_entrypoint": "apps.record_chain_intake_gateway.secure_entrypoint:app",
            }
        if method == "GET":
            return 200, {
                "ok": True,
                "submit_ready": True,
                **module.EXPECTED_GATEWAY_READINESS,
                "global_acceptance_cooldown_seconds": {
                    "minimum": 3600,
                    "maximum": 7200,
                    "secret_keyed": True,
                },
            }
        assert data is not None and len(data) == 100_000
        return 413, {"diagnostics": [{"code": "REQUEST_BODY_TOO_LARGE"}]}

    monkeypatch.setattr(module, "_public_json", fake_public_json)
    module.verify_public_gateway_protection(
        "https://gateway.example", attempts=1, delay_seconds=0
    )
    assert len(calls) == 3
    assert calls[0].split("?", 1)[0].endswith("/readyz")


def test_public_attestation_fails_if_core_entrypoint_claims_ready(monkeypatch):
    module = load_module()

    monkeypatch.setattr(
        module,
        "_public_json",
        lambda *_args, **_kwargs: (
            200,
            {
                "ok": True,
                "submit_ready": True,
                "max_submission_bytes": 98304,
                "record_draft_max_bytes": 49152,
                "max_text_field_chars": 4000,
                "protection_layer_active": False,
                "protection_entrypoint": "core_app_without_protection_wrapper",
                "global_acceptance_cooldown_seconds": None,
            },
        ),
    )
    with pytest.raises(SystemExit) as exc_info:
        module.verify_public_gateway_protection(
            "https://gateway.example", attempts=1, delay_seconds=0
        )
    assert exc_info.value.code == 1
