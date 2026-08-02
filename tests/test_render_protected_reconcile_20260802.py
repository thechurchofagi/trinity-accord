from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_manual_deploy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_manual_deploy_reconcile_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reconcile_updates_health_path_runtime_and_secure_entrypoint(monkeypatch) -> None:
    module = load_module()
    service: dict[str, Any] = {
        "id": "srv-gateway",
        "name": module.GATEWAY_SERVICE_NAME,
        "healthCheckPath": "/healthz",
        "serviceDetails": {
            "envSpecificDetails": {
                "startCommand": "uvicorn apps.record_chain_intake_gateway.app:app"
            }
        },
    }
    env_values = dict(module.EXPECTED_GATEWAY_ENV)
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
                if "healthCheckPath" in body:
                    service["healthCheckPath"] = body["healthCheckPath"]
                details = body.get("serviceDetails")
                if isinstance(details, dict):
                    env_details = details.get("envSpecificDetails")
                    if isinstance(env_details, dict) and "startCommand" in env_details:
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

    monkeypatch.setattr(module, "request", fake_request)
    refreshed = module.reconcile_gateway_config(service, "test-token")

    assert module.service_start_command(refreshed) == module.EXPECTED_GATEWAY_START_COMMAND
    assert module.service_health_check_path(refreshed) == "/readyz"
    assert env_values["TRINITY_GATEWAY_RUNTIME_VERSION"] == "1.2.1-protected"
    assert any(
        method == "PATCH" and body == {"healthCheckPath": "/readyz"}
        for _path, method, body in calls
    )


def test_live_attestation_checks_protected_readyz_first(monkeypatch) -> None:
    module = load_module()
    urls: list[str] = []

    def fake_public_json(
        url: str,
        *,
        method: str = "GET",
        data: bytes | None = None,
    ) -> tuple[int, dict[str, Any]]:
        urls.append(url)
        if url.split("?", 1)[0].endswith("/readyz"):
            return 200, {
                "ok": True,
                "version": "1.2.1-protected",
                "protection_layer_active": True,
                "protection_entrypoint": "apps.record_chain_intake_gateway.secure_entrypoint:app",
            }
        if url.split("?", 1)[0].endswith("/record-chain/readiness"):
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
        assert method == "POST" and data is not None
        return 413, {"diagnostics": [{"code": "REQUEST_BODY_TOO_LARGE"}]}

    monkeypatch.setattr(module, "_public_json", fake_public_json)
    module._verify_public_gateway_protection_once("https://gateway.example")

    assert urls[0].split("?", 1)[0].endswith("/readyz")
    assert urls[1].split("?", 1)[0].endswith("/record-chain/readiness")
    assert urls[2].endswith("/record-chain/preflight")
