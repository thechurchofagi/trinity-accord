#!/usr/bin/env python3
"""Deploy and attest the current protected Record-Chain Gateway.

This is the canonical exact-commit Render deployment adapter used by the
standard Pages rollout.  It binds the mature deployment engine to the current
hardened entrypoint and fails closed unless public health/readiness responses
attest that exact runtime contract.
"""
from __future__ import annotations

import importlib.util
import time
from pathlib import Path
from typing import Any

BASE_MODULE_PATH = Path(__file__).with_name("render_manual_deploy.py")
EXPECTED_RENDER_HEALTH_PATH = "/healthz"
AUXILIARY_PROTECTED_READINESS_PATH = "/readyz"
EXPECTED_ENTRYPOINT = "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
EXPECTED_START_COMMAND = f"uvicorn {EXPECTED_ENTRYPOINT} --host 0.0.0.0 --port $PORT"
EXPECTED_RUNTIME_VERSION = "1.2.2-protected"


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
base.EXPECTED_GATEWAY_START_COMMAND = EXPECTED_START_COMMAND
base.EXPECTED_GATEWAY_HEALTH_CHECK_PATH = EXPECTED_RENDER_HEALTH_PATH
base.EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_RUNTIME_VERSION"] = EXPECTED_RUNTIME_VERSION
base.EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_PROTECTION_ENTRYPOINT"] = EXPECTED_ENTRYPOINT
base.EXPECTED_GATEWAY_READINESS["protection_entrypoint"] = EXPECTED_ENTRYPOINT


def reconcile_gateway_config(service: dict[str, Any], token: str) -> dict[str, Any]:
    """Reconcile supported settings and attest the hardened live contract."""
    service_id = str(service.get("id") or "")
    if not service_id:
        base.fail("Render service id missing during configuration reconciliation")

    if base.service_start_command(service) != EXPECTED_START_COMMAND:
        base.request(
            f"/services/{service_id}",
            token,
            method="PATCH",
            body={
                "serviceDetails": {
                    "envSpecificDetails": {"startCommand": EXPECTED_START_COMMAND}
                }
            },
        )
        print("RENDER_CONFIG_UPDATED field=startCommand")

    observed_health_path = base.service_health_check_path(service)
    if observed_health_path != EXPECTED_RENDER_HEALTH_PATH:
        base.fail(
            "Render healthCheckPath must be the protected /healthz route; "
            f"observed {observed_health_path or 'missing'}"
        )

    for key, expected in base.EXPECTED_GATEWAY_ENV.items():
        path = base._env_var_path(service_id, key)
        current = base.env_var_value(base.request(path, token, allow_not_found=True))
        if current != expected:
            base.request(path, token, method="PUT", body={"value": expected})
            print(f"RENDER_CONFIG_UPDATED env={key}")

    refreshed = base.request(f"/services/{service_id}", token)
    if not isinstance(refreshed, dict):
        base.fail("Render service readback did not return an object")
    if base.service_start_command(refreshed) != EXPECTED_START_COMMAND:
        base.fail("Render startCommand readback does not match the hardened entrypoint")
    if base.service_health_check_path(refreshed) != EXPECTED_RENDER_HEALTH_PATH:
        base.fail("Render healthCheckPath readback does not match protected /healthz")
    for key, expected in base.EXPECTED_GATEWAY_ENV.items():
        observed = base.env_var_value(base.request(base._env_var_path(service_id, key), token))
        if observed != expected:
            base.fail(f"Render environment readback mismatch for {key}")

    print(
        "RENDER_CONFIG_ATTESTED hardened_entrypoint=true "
        f"entrypoint={EXPECTED_ENTRYPOINT} "
        "health_check_path=/healthz auxiliary_ready_path=/readyz "
        f"runtime_version={EXPECTED_RUNTIME_VERSION} "
        "request_max_bytes=98304 record_draft_max_bytes=49152 "
        "text_field_max_chars=4000"
    )
    return refreshed


def recover_usable_existing_deploy_id(
    *,
    service_id: str,
    token: str,
    expected_commit_id: str,
    not_before_epoch: float,
    timeout_seconds: float,
    poll_seconds: float,
    require_match: bool,
) -> str | None:
    """Reuse one viable exact-commit deploy, ignoring terminal failures."""
    if require_match:
        return _original_recover_unique_deploy_id(
            service_id=service_id,
            token=token,
            expected_commit_id=expected_commit_id,
            not_before_epoch=not_before_epoch,
            timeout_seconds=timeout_seconds,
            poll_seconds=poll_seconds,
            require_match=True,
        )

    deadline = time.monotonic() + max(0.0, timeout_seconds)
    reported_terminal_ids: set[str] = set()
    while True:
        exact_candidates = base.exact_deploy_candidates(
            base.list_recent_deploys(service_id, token),
            expected_commit_id=expected_commit_id,
            not_before_epoch=not_before_epoch,
        )
        reusable_candidates: list[dict[str, Any]] = []
        for candidate in exact_candidates:
            deploy_id = base.deploy_id_from_response(candidate)
            status = base.deploy_status(candidate)
            if status in base.DEPLOY_FAILURE_STATUSES:
                if deploy_id and deploy_id not in reported_terminal_ids:
                    print(
                        "RENDER_DEPLOY_RECOVERY_SKIPPED_TERMINAL "
                        f"service_id={service_id} deploy_id={deploy_id} "
                        f"commit_id={expected_commit_id} status={status}"
                    )
                    reported_terminal_ids.add(deploy_id)
                continue
            reusable_candidates.append(candidate)

        if len(reusable_candidates) > 1:
            ids = ",".join(
                str(base.deploy_id_from_response(item) or "unknown")
                for item in reusable_candidates
            )
            base.fail(
                "Render deploy recovery is ambiguous: multiple viable exact-commit "
                f"deploys matched the recovery window ({ids})"
            )
        if len(reusable_candidates) == 1:
            deploy_id = base.deploy_id_from_response(reusable_candidates[0])
            if not deploy_id:
                base.fail("Render deploy recovery matched a record without an id")
            print(
                f"RENDER_DEPLOY_ID_RECOVERED service_id={service_id} "
                f"deploy_id={deploy_id} commit_id={expected_commit_id}"
            )
            return deploy_id
        if time.monotonic() >= deadline:
            return None
        time.sleep(max(0.0, poll_seconds))


def _validate_protected_route(*, route: str, status: int, payload: dict[str, Any]) -> None:
    if status != 200 or payload.get("ok") is not True:
        raise RuntimeError(f"protected {route} returned HTTP {status}")
    if payload.get("version") != EXPECTED_RUNTIME_VERSION:
        raise RuntimeError(f"protected {route} runtime version does not match deployed config")
    if payload.get("protection_required") is not True:
        raise RuntimeError(f"protected {route} does not attest required protection")
    if payload.get("protection_layer_active") is not True:
        raise RuntimeError(f"protected {route} does not attest the protection layer")
    if payload.get("protection_entrypoint") != EXPECTED_ENTRYPOINT:
        raise RuntimeError(f"protected {route} does not attest the hardened entrypoint")


def verify_public_gateway_protection_once(base_url: str) -> dict[str, Any]:
    """Verify protected production canaries and return the observed proof fields."""
    nonce = str(time.time_ns())
    root = base_url.rstrip("/")
    observed_runtime_version = ""

    for route in (EXPECTED_RENDER_HEALTH_PATH, AUXILIARY_PROTECTED_READINESS_PATH):
        status, payload = base._public_json(f"{root}{route}?protection_attestation={nonce}")
        _validate_protected_route(route=route, status=status, payload=payload)
        route_runtime_version = str(payload.get("version") or "")
        if observed_runtime_version and route_runtime_version != observed_runtime_version:
            raise RuntimeError("protected health routes disagree on runtime version")
        observed_runtime_version = route_runtime_version

    readiness_status, readiness = base._public_json(
        f"{root}/record-chain/readiness?protection_attestation={nonce}"
    )
    if readiness_status != 200:
        raise RuntimeError(f"Gateway readiness returned HTTP {readiness_status}")
    if readiness.get("ok") is not True or readiness.get("submit_ready") is not True:
        raise RuntimeError("Gateway readiness is not submit-ready")
    for key, expected in base.EXPECTED_GATEWAY_READINESS.items():
        if readiness.get(key) != expected:
            raise RuntimeError(
                f"Gateway readiness mismatch for {key}: expected {expected!r}, "
                f"got {readiness.get(key)!r}"
            )
    cooldown = readiness.get("global_acceptance_cooldown_seconds")
    if cooldown != {"minimum": 3600, "maximum": 7200, "secret_keyed": True}:
        raise RuntimeError(
            "Gateway readiness does not attest the secret-keyed 60-120 minute cooldown"
        )

    oversized = b"{" + (b"x" * 99_999)
    oversized_status, payload = base._public_json(
        f"{root}/record-chain/preflight", method="POST", data=oversized
    )
    diagnostics = payload.get("diagnostics")
    code = diagnostics[0].get("code") if isinstance(diagnostics, list) and diagnostics else None
    if oversized_status != 413 or code != "REQUEST_BODY_TOO_LARGE":
        raise RuntimeError(
            "100000-byte preflight was not rejected by the protection layer: "
            f"HTTP {oversized_status}, diagnostic={code!r}"
        )

    return {
        "protection_layer_active": True,
        "protected_readiness_http": readiness_status,
        "runtime_version": observed_runtime_version,
        "request_max_bytes": readiness["max_submission_bytes"],
        "oversized_preflight_http": oversized_status,
        "submit_called": False,
    }


def verify_public_gateway_protection(
    base_url: str = base.GATEWAY_PUBLIC_BASE_URL,
    *,
    attempts: int = 12,
    delay_seconds: float = 5.0,
) -> None:
    """Retry the live verifier and emit only fields observed in the passing attempt."""
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            attestation = verify_public_gateway_protection_once(base_url)
        except Exception as exc:
            last_error = str(exc)
            if attempt < attempts:
                print(f"GATEWAY_PROTECTION_WAIT attempt={attempt}/{attempts} error={last_error}")
                time.sleep(max(0.0, delay_seconds))
                continue
            base.fail(f"public Gateway protection attestation failed: {last_error}")
        print(
            "GATEWAY_PROTECTION_ATTESTED "
            f"protection_layer_active={str(attestation['protection_layer_active']).lower()} "
            f"protected_readiness_http={attestation['protected_readiness_http']} "
            f"runtime_version={attestation['runtime_version']} "
            f"request_max_bytes={attestation['request_max_bytes']} "
            f"oversized_preflight_http={attestation['oversized_preflight_http']} "
            f"submit_called={str(attestation['submit_called']).lower()}"
        )
        return


_original_recover_unique_deploy_id = base.recover_unique_deploy_id
base.reconcile_gateway_config = reconcile_gateway_config
base.recover_unique_deploy_id = recover_usable_existing_deploy_id
base._verify_public_gateway_protection_once = verify_public_gateway_protection_once
base.verify_public_gateway_protection = verify_public_gateway_protection


def main() -> int:
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
