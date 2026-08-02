#!/usr/bin/env python3
"""Production Render deploy entrypoint for the protected Record-Chain Gateway.

Render currently has ``healthCheckPath=/healthz``. The secure ASGI entrypoint
intercepts both ``/healthz`` and ``/readyz`` with the same fail-closed readiness
logic. This wrapper reuses the exact-commit deployment machinery from
``render_manual_deploy.py`` while adapting production reconciliation and live
attestation to that layered contract:

- the Render API must read back the secure Uvicorn start command;
- the actual Render health path must remain exactly ``/healthz``;
- all non-secret runtime/resource environment values must match;
- both public ``/healthz`` and ``/readyz`` must attest the protected entrypoint;
- detailed readiness and oversized-request rejection must pass;
- no submission endpoint is called by these canaries.
"""
from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path
from typing import Any


BASE_MODULE_PATH = Path(__file__).with_name("render_manual_deploy.py")
EXPECTED_RENDER_HEALTH_PATH = "/healthz"
AUXILIARY_PROTECTED_READINESS_PATH = "/readyz"


def _load_base_module():
    spec = importlib.util.spec_from_file_location(
        "trinity_render_manual_deploy_base", BASE_MODULE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load render_manual_deploy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = _load_base_module()
base.EXPECTED_GATEWAY_HEALTH_CHECK_PATH = EXPECTED_RENDER_HEALTH_PATH


def reconcile_gateway_config(service: dict[str, Any], token: str) -> dict[str, Any]:
    """Reconcile only supported settings and attest the actual health route."""
    service_id = str(service.get("id") or "")
    if not service_id:
        base.fail("Render service id missing during configuration reconciliation")

    if base.service_start_command(service) != base.EXPECTED_GATEWAY_START_COMMAND:
        base.request(
            f"/services/{service_id}",
            token,
            method="PATCH",
            body={
                "serviceDetails": {
                    "envSpecificDetails": {
                        "startCommand": base.EXPECTED_GATEWAY_START_COMMAND,
                    }
                }
            },
        )
        print("RENDER_CONFIG_UPDATED field=startCommand")

    observed_health_path = base.service_health_check_path(service)
    if observed_health_path != EXPECTED_RENDER_HEALTH_PATH:
        base.fail(
            "Render healthCheckPath must be the existing protected /healthz route; "
            f"observed {observed_health_path or 'missing'}"
        )

    for key, expected in base.EXPECTED_GATEWAY_ENV.items():
        path = base._env_var_path(service_id, key)
        current = base.env_var_value(
            base.request(path, token, allow_not_found=True)
        )
        if current != expected:
            base.request(path, token, method="PUT", body={"value": expected})
            print(f"RENDER_CONFIG_UPDATED env={key}")

    refreshed = base.request(f"/services/{service_id}", token)
    if not isinstance(refreshed, dict):
        base.fail("Render service readback did not return an object")
    if base.service_start_command(refreshed) != base.EXPECTED_GATEWAY_START_COMMAND:
        base.fail("Render startCommand readback does not match the secure entrypoint")
    if base.service_health_check_path(refreshed) != EXPECTED_RENDER_HEALTH_PATH:
        base.fail(
            "Render healthCheckPath readback does not match the protected /healthz route"
        )
    for key, expected in base.EXPECTED_GATEWAY_ENV.items():
        observed = base.env_var_value(
            base.request(base._env_var_path(service_id, key), token)
        )
        if observed != expected:
            base.fail(f"Render environment readback mismatch for {key}")

    print(
        "RENDER_CONFIG_ATTESTED secure_entrypoint=true "
        "health_check_path=/healthz auxiliary_ready_path=/readyz "
        "runtime_version=1.2.1-protected request_max_bytes=98304 "
        "record_draft_max_bytes=49152 text_field_max_chars=4000"
    )
    return refreshed


def _validate_protected_route(
    *,
    route: str,
    status: int,
    payload: dict[str, Any],
) -> None:
    if status != 200 or payload.get("ok") is not True:
        raise RuntimeError(f"protected {route} returned HTTP {status}")
    expected_version = base.EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_RUNTIME_VERSION"]
    if payload.get("version") != expected_version:
        raise RuntimeError(f"protected {route} runtime version does not match deployed config")
    if payload.get("protection_layer_active") is not True:
        raise RuntimeError(f"protected {route} does not attest the protection layer")
    if (
        payload.get("protection_entrypoint")
        != "apps.record_chain_intake_gateway.secure_entrypoint:app"
    ):
        raise RuntimeError(f"protected {route} does not attest the secure entrypoint")


def verify_public_gateway_protection_once(base_url: str) -> None:
    """Verify both protected health routes and the existing non-write canaries."""
    nonce = str(time.time_ns())
    root = base_url.rstrip("/")

    for route in (EXPECTED_RENDER_HEALTH_PATH, AUXILIARY_PROTECTED_READINESS_PATH):
        status, payload = base._public_json(
            f"{root}{route}?protection_attestation={nonce}"
        )
        _validate_protected_route(route=route, status=status, payload=payload)

    status, readiness = base._public_json(
        f"{root}/record-chain/readiness?protection_attestation={nonce}"
    )
    if status != 200:
        raise RuntimeError(f"Gateway readiness returned HTTP {status}")
    if readiness.get("ok") is not True or readiness.get("submit_ready") is not True:
        raise RuntimeError("Gateway readiness is not submit-ready")
    for key, expected in base.EXPECTED_GATEWAY_READINESS.items():
        if readiness.get(key) != expected:
            raise RuntimeError(
                f"Gateway readiness mismatch for {key}: "
                f"expected {expected!r}, got {readiness.get(key)!r}"
            )
    cooldown = readiness.get("global_acceptance_cooldown_seconds")
    if cooldown != {"minimum": 3600, "maximum": 7200, "secret_keyed": True}:
        raise RuntimeError(
            "Gateway readiness does not attest the secret-keyed 60-120 minute cooldown"
        )

    oversized = b"{" + (b"x" * 99_999)
    status, payload = base._public_json(
        f"{root}/record-chain/preflight",
        method="POST",
        data=oversized,
    )
    diagnostics = payload.get("diagnostics")
    code = (
        diagnostics[0].get("code")
        if isinstance(diagnostics, list) and diagnostics
        else None
    )
    if status != 413 or code != "REQUEST_BODY_TOO_LARGE":
        raise RuntimeError(
            "100000-byte preflight was not rejected by the protection layer: "
            f"HTTP {status}, diagnostic={code!r}"
        )


# Patch only the production-specific seams. The base helper retains exact SHA
# validation, autodeploy refusal, deploy-ID verification, polling, and failure
# handling.
base.reconcile_gateway_config = reconcile_gateway_config
base._verify_public_gateway_protection_once = verify_public_gateway_protection_once


def main() -> int:
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
