from __future__ import annotations

import importlib.util
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


def _service(module, command: str) -> dict[str, Any]:
    return {
        "id": "srv-gateway",
        "name": module.GATEWAY_SERVICE_NAME,
        "autoDeploy": "no",
        "suspended": "not_suspended",
        "serviceDetails": {
            "envSpecificDetails": {
                "startCommand": command,
            }
        },
    }


def test_reconcile_updates_and_reads_back_start_command_and_limits(monkeypatch):
    module = load_module()
    service = _service(module, "uvicorn apps.record_chain_intake_gateway.app:app")
    current_command = service["serviceDetails"]["envSpecificDetails"]["startCommand"]
    env = {key: "stale" for key in module.EXPECTED_GATEWAY_ENV}
    calls: list[tuple[str, str, dict[str, Any]]] = []

    def fake_request(path: str, _token: str, method: str = "GET", body=None):
        nonlocal current_command
        calls.append((path, method, dict(body or {})))
        if path == "/services/srv-gateway" and method == "PATCH":
            current_command = body["serviceDetails"]["envSpecificDetails"]["startCommand"]
            return {}
        if path == "/services/srv-gateway" and method == "GET":
            return _service(module, current_command)
        key = path.rsplit("/", 1)[-1]
        if method == "PUT":
            env[key] = body["value"]
            return {"key": key, "value": env[key]}
        return {"key": key, "value": env[key]}

    monkeypatch.setattr(module, "request", fake_request)
    refreshed = module.reconcile_gateway_config(service, "render-token")

    assert module.service_start_command(refreshed) == module.EXPECTED_GATEWAY_START_COMMAND
    assert env == module.EXPECTED_GATEWAY_ENV
    assert any(method == "PATCH" for _path, method, _body in calls)
    assert sum(method == "PUT" for _path, method, _body in calls) == len(
        module.EXPECTED_GATEWAY_ENV
    )


def test_public_attestation_requires_runtime_marker_and_oversize_413(monkeypatch):
    module = load_module()
    calls = 0

    def fake_public_json(_url: str, *, method: str = "GET", data=None):
        nonlocal calls
        calls += 1
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
    assert calls == 2


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
