#!/usr/bin/env python3
"""Deploy the deeply verified Gateway without reverting its runtime contract.

This adapter keeps the mature exact-commit Render deployment machinery while
binding it to the current hardened entrypoint, runtime version, environment
attestation, and live health/readiness contract.
"""
from __future__ import annotations

from typing import Any

import render_protected_deploy as protected

EXPECTED_ENTRYPOINT = (
    "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
)
EXPECTED_START_COMMAND = (
    f"uvicorn {EXPECTED_ENTRYPOINT} --host 0.0.0.0 --port $PORT"
)
EXPECTED_RUNTIME_VERSION = "1.2.2-protected"

# Patch the shared exact-commit deployment engine before its main() executes.
protected.base.EXPECTED_GATEWAY_START_COMMAND = EXPECTED_START_COMMAND
protected.base.EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_RUNTIME_VERSION"] = (
    EXPECTED_RUNTIME_VERSION
)
protected.base.EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_PROTECTION_ENTRYPOINT"] = (
    EXPECTED_ENTRYPOINT
)
protected.base.EXPECTED_GATEWAY_READINESS["protection_entrypoint"] = (
    EXPECTED_ENTRYPOINT
)


def reconcile_gateway_config(
    service: dict[str, Any],
    token: str,
) -> dict[str, Any]:
    """Reconcile and attest the exact hardened production configuration."""
    service_id = str(service.get("id") or "")
    if not service_id:
        protected.base.fail(
            "Render service id missing during configuration reconciliation"
        )

    if protected.base.service_start_command(service) != EXPECTED_START_COMMAND:
        protected.base.request(
            f"/services/{service_id}",
            token,
            method="PATCH",
            body={
                "serviceDetails": {
                    "envSpecificDetails": {
                        "startCommand": EXPECTED_START_COMMAND,
                    }
                }
            },
        )
        print("RENDER_CONFIG_UPDATED field=startCommand")

    observed_health_path = protected.base.service_health_check_path(service)
    if observed_health_path != protected.EXPECTED_RENDER_HEALTH_PATH:
        protected.base.fail(
            "Render healthCheckPath must be the protected /healthz route; "
            f"observed {observed_health_path or 'missing'}"
        )

    for key, expected in protected.base.EXPECTED_GATEWAY_ENV.items():
        path = protected.base._env_var_path(service_id, key)
        current = protected.base.env_var_value(
            protected.base.request(path, token, allow_not_found=True)
        )
        if current != expected:
            protected.base.request(
                path,
                token,
                method="PUT",
                body={"value": expected},
            )
            print(f"RENDER_CONFIG_UPDATED env={key}")

    refreshed = protected.base.request(f"/services/{service_id}", token)
    if not isinstance(refreshed, dict):
        protected.base.fail("Render service readback did not return an object")
    if protected.base.service_start_command(refreshed) != EXPECTED_START_COMMAND:
        protected.base.fail(
            "Render startCommand readback does not match the hardened entrypoint"
        )
    if (
        protected.base.service_health_check_path(refreshed)
        != protected.EXPECTED_RENDER_HEALTH_PATH
    ):
        protected.base.fail(
            "Render healthCheckPath readback does not match protected /healthz"
        )
    for key, expected in protected.base.EXPECTED_GATEWAY_ENV.items():
        observed = protected.base.env_var_value(
            protected.base.request(
                protected.base._env_var_path(service_id, key),
                token,
            )
        )
        if observed != expected:
            protected.base.fail(
                f"Render environment readback mismatch for {key}"
            )

    print(
        "RENDER_CONFIG_ATTESTED hardened_entrypoint=true "
        f"entrypoint={EXPECTED_ENTRYPOINT} "
        "health_check_path=/healthz auxiliary_ready_path=/readyz "
        f"runtime_version={EXPECTED_RUNTIME_VERSION} "
        "request_max_bytes=98304 record_draft_max_bytes=49152 "
        "text_field_max_chars=4000"
    )
    return refreshed


def validate_hardened_route(
    *,
    route: str,
    status: int,
    payload: dict[str, Any],
) -> None:
    """Require live health routes to attest the exact hardened runtime."""
    if status != 200 or payload.get("ok") is not True:
        raise RuntimeError(f"protected {route} returned HTTP {status}")
    if payload.get("version") != EXPECTED_RUNTIME_VERSION:
        raise RuntimeError(
            f"protected {route} runtime version does not match deployed config"
        )
    if payload.get("protection_required") is not True:
        raise RuntimeError(f"protected {route} does not attest required protection")
    if payload.get("protection_layer_active") is not True:
        raise RuntimeError(f"protected {route} does not attest the protection layer")
    if payload.get("protection_entrypoint") != EXPECTED_ENTRYPOINT:
        raise RuntimeError(
            f"protected {route} does not attest the hardened entrypoint"
        )


# base.main() resolves these seams at execution time.
protected.reconcile_gateway_config = reconcile_gateway_config
protected.base.reconcile_gateway_config = reconcile_gateway_config
protected._validate_protected_route = validate_hardened_route


def main() -> int:
    return protected.main()


if __name__ == "__main__":
    raise SystemExit(main())
