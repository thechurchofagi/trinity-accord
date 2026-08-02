#!/usr/bin/env python3
"""Render manual deployment helper.

Uses the RENDER API key to list services and optionally trigger deployment.
Refuses the retired legacy Gateway unless ``--allow-legacy`` is specified.
A deployment is reported as triggered only when Render returns a real deploy ID.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

RENDER_API = "https://api.render.com/v1"
GATEWAY_SERVICE_NAME = "trinity-record-chain-gateway"
LEGACY_SERVICE_NAME = "trinity-agent-issue-gateway"
GATEWAY_PUBLIC_BASE_URL = "https://trinity-record-chain-gateway.onrender.com"
EXPECTED_GATEWAY_START_COMMAND = (
    "uvicorn apps.record_chain_intake_gateway.secure_entrypoint:app "
    "--host 0.0.0.0 --port $PORT"
)
EXPECTED_GATEWAY_HEALTH_CHECK_PATH = "/readyz"
EXPECTED_GATEWAY_ENV = {
    "TRINITY_GATEWAY_RUNTIME_VERSION": "1.2.1-protected",
    "TRINITY_MAX_SUBMISSION_BYTES": "98304",
    "TRINITY_RECORD_DRAFT_MAX_BYTES": "49152",
    "TRINITY_MAX_TEXT_FIELD_CHARS": "4000",
    "TRINITY_MAX_URL_CHARS": "2048",
    "TRINITY_MAX_JSON_DEPTH": "12",
    "TRINITY_MAX_ARRAY_ITEMS": "32",
    "TRINITY_MAX_REFERENCE_ITEMS": "16",
}
EXPECTED_GATEWAY_READINESS = {
    "max_submission_bytes": 98304,
    "record_draft_max_bytes": 49152,
    "max_text_field_chars": 4000,
    "protection_layer_active": True,
    "protection_entrypoint": "apps.record_chain_intake_gateway.secure_entrypoint:app",
}
DEPLOY_SUCCESS_STATUSES = frozenset({"live"})
DEPLOY_FAILURE_STATUSES = frozenset({
    "build_failed",
    "update_failed",
    "pre_deploy_failed",
    "canceled",
    "deactivated",
})
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _http_error_detail(exc: urllib.error.HTTPError) -> str:
    try:
        raw = exc.read().decode("utf-8", "replace")
    except Exception:
        return ""
    if not raw:
        return ""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw[:300]
    if isinstance(payload, dict):
        for key in ("message", "error", "detail"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value[:300]
    return json.dumps(payload, ensure_ascii=False)[:300]


def request(
    path: str,
    token: str,
    method: str = "GET",
    body: dict | None = None,
    *,
    allow_not_found: bool = False,
) -> Any:
    data = None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(f"{RENDER_API}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and allow_not_found:
            return None
        detail = _http_error_detail(exc)
        suffix = f": {detail}" if detail else ""
        fail(f"Render API HTTP {exc.code}{suffix}")
    except Exception as exc:
        fail(f"Render API error: {type(exc).__name__}")


def list_services(token: str) -> list[dict]:
    data = request("/services?limit=100", token)
    if not isinstance(data, list):
        fail("Render service list did not return list")
    return data


def find_service(token: str, name: str) -> dict:
    for item in list_services(token):
        svc = item.get("service") if isinstance(item, dict) else None
        if isinstance(svc, dict) and svc.get("name") == name:
            return svc
    fail(f"Render service not found: {name}")


def service_is_suspended(service: dict) -> bool:
    """Return whether Render reports that a service is intentionally suspended."""
    state = service.get("suspended")
    return state not in (None, False, "", "not_suspended")


def service_auto_deploy_is_disabled(service: dict) -> bool:
    """Return whether Render's actual service state disables autodeploys."""
    return service.get("autoDeploy") in ("no", False)


def service_start_command(service: dict[str, Any]) -> str:
    details = service.get("serviceDetails")
    if not isinstance(details, dict):
        return ""
    env_details = details.get("envSpecificDetails")
    if not isinstance(env_details, dict):
        return ""
    return str(env_details.get("startCommand") or "")


def service_health_check_path(service: dict[str, Any]) -> str:
    """Return the web-service health path across current and legacy API shapes."""
    value = service.get("healthCheckPath")
    if isinstance(value, str):
        return value
    details = service.get("serviceDetails")
    if isinstance(details, dict):
        value = details.get("healthCheckPath")
        if isinstance(value, str):
            return value
    return ""


def env_var_value(result: Any) -> str | None:
    """Return one Render env-var value without ever logging the response."""
    if not isinstance(result, dict):
        return None
    candidate = result.get("envVar")
    if not isinstance(candidate, dict):
        candidate = result
    value = candidate.get("value") if isinstance(candidate, dict) else None
    return value if isinstance(value, str) else None


def _env_var_path(service_id: str, key: str) -> str:
    return (
        f"/services/{urllib.parse.quote(service_id, safe='')}/env-vars/"
        f"{urllib.parse.quote(key, safe='')}"
    )


def reconcile_gateway_config(service: dict[str, Any], token: str) -> dict[str, Any]:
    """Update and then attest the non-secret production protection settings."""
    service_id = str(service.get("id") or "")
    if not service_id:
        fail("Render service id missing during configuration reconciliation")

    if service_start_command(service) != EXPECTED_GATEWAY_START_COMMAND:
        request(
            f"/services/{service_id}",
            token,
            method="PATCH",
            body={
                "serviceDetails": {
                    "envSpecificDetails": {
                        "startCommand": EXPECTED_GATEWAY_START_COMMAND,
                    }
                }
            },
        )
        print("RENDER_CONFIG_UPDATED field=startCommand")

    if service_health_check_path(service) != EXPECTED_GATEWAY_HEALTH_CHECK_PATH:
        # healthCheckPath is a web-service field in Render's Update Service API.
        request(
            f"/services/{service_id}",
            token,
            method="PATCH",
            body={"healthCheckPath": EXPECTED_GATEWAY_HEALTH_CHECK_PATH},
        )
        print("RENDER_CONFIG_UPDATED field=healthCheckPath")

    for key, expected in EXPECTED_GATEWAY_ENV.items():
        path = _env_var_path(service_id, key)
        current = env_var_value(request(path, token, allow_not_found=True))
        if current != expected:
            request(path, token, method="PUT", body={"value": expected})
            print(f"RENDER_CONFIG_UPDATED env={key}")

    refreshed = request(f"/services/{service_id}", token)
    if not isinstance(refreshed, dict):
        fail("Render service readback did not return an object")
    if service_start_command(refreshed) != EXPECTED_GATEWAY_START_COMMAND:
        fail("Render startCommand readback does not match the secure entrypoint")
    if service_health_check_path(refreshed) != EXPECTED_GATEWAY_HEALTH_CHECK_PATH:
        fail("Render healthCheckPath readback does not match the protected readiness endpoint")
    for key, expected in EXPECTED_GATEWAY_ENV.items():
        observed = env_var_value(request(_env_var_path(service_id, key), token))
        if observed != expected:
            fail(f"Render environment readback mismatch for {key}")

    print(
        "RENDER_CONFIG_ATTESTED secure_entrypoint=true health_check_path=/readyz "
        "runtime_version=1.2.1-protected request_max_bytes=98304 "
        "record_draft_max_bytes=49152 text_field_max_chars=4000"
    )
    return refreshed


def _public_json(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
) -> tuple[int, dict[str, Any]]:
    headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache, no-store, max-age=0",
        "Pragma": "no-cache",
        "User-Agent": "trinity-render-protection-attestation/1.0",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    request_obj = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request_obj, timeout=20) as response:
            status = int(response.status)
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read()
    try:
        payload = json.loads(raw.decode("utf-8")) if raw else {}
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"public Gateway returned non-JSON HTTP {status}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"public Gateway returned a non-object HTTP {status} payload")
    return status, payload


def _verify_public_gateway_protection_once(base_url: str) -> None:
    nonce = str(time.time_ns())

    protected_status, protected = _public_json(
        f"{base_url.rstrip('/')}/readyz?protection_attestation={nonce}"
    )
    if protected_status != 200 or protected.get("ok") is not True:
        raise RuntimeError(f"protected readiness returned HTTP {protected_status}")
    if protected.get("version") != EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_RUNTIME_VERSION"]:
        raise RuntimeError("protected readiness runtime version does not match deployed config")
    if protected.get("protection_layer_active") is not True:
        raise RuntimeError("protected readiness does not attest the protection layer")
    if protected.get("protection_entrypoint") != "apps.record_chain_intake_gateway.secure_entrypoint:app":
        raise RuntimeError("protected readiness does not attest the secure entrypoint")

    status, readiness = _public_json(
        f"{base_url.rstrip('/')}/record-chain/readiness?protection_attestation={nonce}"
    )
    if status != 200:
        raise RuntimeError(f"Gateway readiness returned HTTP {status}")
    if readiness.get("ok") is not True or readiness.get("submit_ready") is not True:
        raise RuntimeError("Gateway readiness is not submit-ready")
    for key, expected in EXPECTED_GATEWAY_READINESS.items():
        if readiness.get(key) != expected:
            raise RuntimeError(
                f"Gateway readiness mismatch for {key}: "
                f"expected {expected!r}, got {readiness.get(key)!r}"
            )
    cooldown = readiness.get("global_acceptance_cooldown_seconds")
    if cooldown != {"minimum": 3600, "maximum": 7200, "secret_keyed": True}:
        raise RuntimeError("Gateway readiness does not attest the secret-keyed 60-120 minute cooldown")

    oversized = b"{" + (b"x" * 99_999)
    status, payload = _public_json(
        f"{base_url.rstrip('/')}/record-chain/preflight",
        method="POST",
        data=oversized,
    )
    diagnostics = payload.get("diagnostics")
    code = diagnostics[0].get("code") if isinstance(diagnostics, list) and diagnostics else None
    if status != 413 or code != "REQUEST_BODY_TOO_LARGE":
        raise RuntimeError(
            f"100000-byte preflight was not rejected by the protection layer: "
            f"HTTP {status}, diagnostic={code!r}"
        )


def verify_public_gateway_protection(
    base_url: str = GATEWAY_PUBLIC_BASE_URL,
    *,
    attempts: int = 12,
    delay_seconds: float = 5.0,
) -> None:
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            _verify_public_gateway_protection_once(base_url)
        except Exception as exc:
            last_error = str(exc)
            if attempt < attempts:
                print(f"GATEWAY_PROTECTION_WAIT attempt={attempt}/{attempts} error={last_error}")
                time.sleep(max(0.0, delay_seconds))
                continue
            fail(f"public Gateway protection attestation failed: {last_error}")
        print(
            "GATEWAY_PROTECTION_ATTESTED protection_layer_active=true "
            "protected_readiness_http=200 runtime_version=1.2.1-protected "
            "request_max_bytes=98304 oversized_preflight_http=413 submit_called=false"
        )
        return


def deploy_id_from_response(result: Any) -> str | None:
    if not isinstance(result, dict):
        return None
    value = result.get("id")
    if isinstance(value, str) and value:
        return value
    nested = result.get("deploy")
    if isinstance(nested, dict):
        value = nested.get("id")
        if isinstance(value, str) and value:
            return value
    return None


def deploy_object(result: Any) -> dict[str, Any]:
    if not isinstance(result, dict):
        return {}
    nested = result.get("deploy")
    return nested if isinstance(nested, dict) else result


def deploy_commit_id(result: Any) -> str | None:
    deploy = deploy_object(result)
    commit = deploy.get("commit")
    if isinstance(commit, dict):
        value = commit.get("id") or commit.get("sha")
        if isinstance(value, str) and value:
            return value
    for key in ("commitId", "commit_id"):
        value = deploy.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def deploy_status(result: Any) -> str:
    value = deploy_object(result).get("status")
    return str(value or "").strip().lower()


def wait_for_deploy(
    *,
    service_id: str,
    deploy_id: str,
    token: str,
    expected_commit_id: str,
    timeout_seconds: int,
    poll_seconds: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_status = ""
    while True:
        result = request(f"/services/{service_id}/deploys/{deploy_id}", token)
        status = deploy_status(result)
        observed_commit = deploy_commit_id(result)
        if observed_commit and observed_commit != expected_commit_id:
            fail(
                f"Render deploy {deploy_id} commit mismatch: "
                f"expected {expected_commit_id}, got {observed_commit}"
            )
        if status != last_status:
            print(
                f"RENDER_DEPLOY_STATUS deploy_id={deploy_id} "
                f"status={status or 'unknown'}"
            )
            last_status = status
        if status in DEPLOY_SUCCESS_STATUSES:
            if observed_commit != expected_commit_id:
                fail(
                    f"Render deploy {deploy_id} is live without proving commit "
                    f"{expected_commit_id}"
                )
            return deploy_object(result)
        if status in DEPLOY_FAILURE_STATUSES:
            fail(f"Render deploy {deploy_id} ended with status={status}")
        if time.monotonic() >= deadline:
            fail(
                f"Render deploy {deploy_id} did not become live within "
                f"{timeout_seconds} seconds (last_status={status or 'unknown'})"
            )
        time.sleep(max(0.0, poll_seconds))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", default="trinity-record-chain-gateway")
    parser.add_argument("--deploy", action="store_true")
    parser.add_argument("--allow-legacy", action="store_true")
    parser.add_argument("--reconcile-config", action="store_true")
    parser.add_argument("--commit-id", default="")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--wait-timeout", type=int, default=900)
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    args = parser.parse_args()

    token = os.environ.get("RENDER", "").strip()
    if not token:
        fail("RENDER missing")

    if args.service == LEGACY_SERVICE_NAME and not args.allow_legacy:
        fail("Refusing to deploy legacy gateway without --allow-legacy")
    commit_id = args.commit_id.strip()
    if commit_id and not _COMMIT_RE.fullmatch(commit_id):
        fail("--commit-id must be a full 40-character lowercase Git commit SHA")
    if args.wait and not commit_id:
        fail("--wait requires --commit-id so the live source can be proven exactly")
    if args.wait_timeout < 1:
        fail("--wait-timeout must be at least 1 second")
    if args.poll_seconds < 0:
        fail("--poll-seconds must be non-negative")
    if args.reconcile_config and not args.deploy:
        fail("--reconcile-config requires --deploy")
    if args.reconcile_config and args.service != GATEWAY_SERVICE_NAME:
        fail("--reconcile-config is restricted to the production Record-Chain Gateway")

    svc = find_service(token, args.service)
    sid = svc.get("id")
    if not sid:
        fail("Render service id missing")

    suspended = service_is_suspended(svc)
    suspension_state = svc.get("suspended")
    suspenders = svc.get("suspenders") if isinstance(svc.get("suspenders"), list) else []
    print(
        f"PASS: found Render service name={args.service} id={sid} "
        f"suspended={str(suspended).lower()} state={suspension_state}"
    )

    if not args.deploy:
        suffix = f" commit_id={commit_id}" if commit_id else ""
        print(f"DRY_RUN: no deploy triggered{suffix}")
        return 0

    if suspended:
        actor = ",".join(str(value) for value in suspenders) or "unknown"
        fail(
            f"Render service is suspended (state={suspension_state}, suspenders={actor}); "
            "no deployment was created. Resume the service intentionally before deploying."
        )
    if commit_id and not service_auto_deploy_is_disabled(svc):
        fail(
            f"Refusing exact-commit deploy for {args.service}: Render reports "
            "autodeploys are enabled or unconfirmed"
        )
    if args.service == GATEWAY_SERVICE_NAME and not args.reconcile_config:
        fail(
            "Production Gateway deploys require --reconcile-config so a stale "
            "Render startCommand, healthCheckPath, or resource limit cannot survive a green deployment"
        )
    if args.reconcile_config:
        svc = reconcile_gateway_config(svc, token)

    body = {"clearCache": "do_not_clear"}
    if commit_id:
        body["commitId"] = commit_id
    result = request(f"/services/{sid}/deploys", token, method="POST", body=body)
    deploy_id = deploy_id_from_response(result)
    if not deploy_id:
        fail("Render accepted the deploy request without returning a deploy ID; deployment is unconfirmed")

    observed_commit = deploy_commit_id(result)
    if observed_commit and commit_id and observed_commit != commit_id:
        fail(
            f"Render created deploy {deploy_id} for unexpected commit "
            f"{observed_commit}; expected {commit_id}"
        )
    commit_suffix = f" commit_id={commit_id}" if commit_id else ""
    print(
        f"RENDER_DEPLOY_TRIGGERED service={args.service} "
        f"deploy_id={deploy_id}{commit_suffix}"
    )
    if args.wait:
        wait_for_deploy(
            service_id=str(sid),
            deploy_id=deploy_id,
            token=token,
            expected_commit_id=commit_id,
            timeout_seconds=args.wait_timeout,
            poll_seconds=args.poll_seconds,
        )
        print(
            f"RENDER_DEPLOY_LIVE service={args.service} deploy_id={deploy_id} "
            f"commit_id={commit_id}"
        )
        if args.service == GATEWAY_SERVICE_NAME:
            verify_public_gateway_protection()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
