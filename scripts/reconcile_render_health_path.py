#!/usr/bin/env python3
"""Reconcile and attest the protected Render Gateway health-check path.

Render configuration updates and subsequent service reads can be briefly
inconsistent. This helper updates only the non-secret web-service
``healthCheckPath`` field, then performs a bounded readback loop. It exits
successfully only after the API returns the exact protected ``/readyz`` path.
No deploy is triggered here; the exact-commit deploy remains owned by
``render_manual_deploy.py``.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

RENDER_API = "https://api.render.com/v1"
SERVICE_NAME = "trinity-record-chain-gateway"
EXPECTED_HEALTH_PATH = "/readyz"
READBACK_ATTEMPTS = 15
READBACK_DELAY_SECONDS = 2.0


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def request(
    path: str,
    token: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
) -> Any:
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        f"{RENDER_API}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", "replace")[:300]
        except Exception:
            detail = ""
        suffix = f": {detail}" if detail else ""
        fail(f"Render API HTTP {exc.code}{suffix}")
    except Exception as exc:
        fail(f"Render API error: {type(exc).__name__}")


def service_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    nested = value.get("service")
    return nested if isinstance(nested, dict) else value


def health_check_path(service: dict[str, Any]) -> str:
    value = service.get("healthCheckPath")
    if isinstance(value, str):
        return value
    details = service.get("serviceDetails")
    if isinstance(details, dict):
        value = details.get("healthCheckPath")
        if isinstance(value, str):
            return value
    return ""


def find_service(token: str) -> dict[str, Any]:
    result = request("/services?limit=100", token)
    if not isinstance(result, list):
        fail("Render service list did not return a list")
    for item in result:
        service = service_object(item)
        if service.get("name") == SERVICE_NAME:
            return service
    fail(f"Render service not found: {SERVICE_NAME}")


def reconcile(
    token: str,
    *,
    attempts: int = READBACK_ATTEMPTS,
    delay_seconds: float = READBACK_DELAY_SECONDS,
) -> dict[str, Any]:
    if attempts < 1:
        fail("readback attempts must be at least one")
    service = find_service(token)
    service_id = str(service.get("id") or "")
    if not service_id:
        fail("Render service id missing")

    if health_check_path(service) != EXPECTED_HEALTH_PATH:
        request(
            f"/services/{service_id}",
            token,
            method="PATCH",
            body={"healthCheckPath": EXPECTED_HEALTH_PATH},
        )
        print("RENDER_CONFIG_UPDATED field=healthCheckPath")

    observed = ""
    for attempt in range(1, attempts + 1):
        refreshed = service_object(request(f"/services/{service_id}", token))
        observed = health_check_path(refreshed)
        if observed == EXPECTED_HEALTH_PATH:
            print(
                "RENDER_HEALTH_PATH_ATTESTED "
                f"service={SERVICE_NAME} health_check_path={EXPECTED_HEALTH_PATH} "
                f"readback_attempt={attempt}"
            )
            return refreshed
        if attempt < attempts:
            print(
                "RENDER_HEALTH_PATH_WAIT "
                f"attempt={attempt}/{attempts} observed={observed or 'missing'}"
            )
            time.sleep(max(0.0, delay_seconds))

    fail(
        "Render healthCheckPath readback did not converge to "
        f"{EXPECTED_HEALTH_PATH} after {attempts} attempts; "
        f"last observed={observed or 'missing'}"
    )


def main() -> int:
    token = os.environ.get("RENDER", "").strip()
    if not token:
        fail("RENDER missing")
    reconcile(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
