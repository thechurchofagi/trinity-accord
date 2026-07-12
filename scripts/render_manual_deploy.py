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
import sys
import urllib.error
import urllib.request
from typing import Any

RENDER_API = "https://api.render.com/v1"
LEGACY_SERVICE_NAME = "trinity-agent-issue-gateway"


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


def request(path: str, token: str, method: str = "GET", body: dict | None = None) -> Any:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", default="trinity-record-chain-gateway")
    parser.add_argument("--deploy", action="store_true")
    parser.add_argument("--allow-legacy", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("RENDER", "").strip()
    if not token:
        fail("RENDER missing")

    if args.service == LEGACY_SERVICE_NAME and not args.allow_legacy:
        fail("Refusing to deploy legacy gateway without --allow-legacy")

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
        print("DRY_RUN: no deploy triggered")
        return 0

    if suspended:
        actor = ",".join(str(value) for value in suspenders) or "unknown"
        fail(
            f"Render service is suspended (state={suspension_state}, suspenders={actor}); "
            "no deployment was created. Resume the service intentionally before deploying."
        )

    result = request(f"/services/{sid}/deploys", token, method="POST", body={"clearCache": "do_not_clear"})
    deploy_id = deploy_id_from_response(result)
    if not deploy_id:
        fail("Render accepted the deploy request without returning a deploy ID; deployment is unconfirmed")

    print(f"RENDER_DEPLOY_TRIGGERED service={args.service} deploy_id={deploy_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
