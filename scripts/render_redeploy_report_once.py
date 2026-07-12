#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

API = "https://api.render.com/v1"
BASE = "https://trinity-record-chain-gateway.onrender.com"


def api_json(path: str):
    token = os.environ["RENDER"].strip()
    request = urllib.request.Request(
        API + path,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def public_json(path: str, *, post: bool = False):
    request = urllib.request.Request(
        BASE + path,
        data=b"{}" if post else None,
        headers={"Content-Type": "application/json"} if post else {},
        method="POST" if post else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def main() -> int:
    services = api_json("/services?limit=100")
    service = next(
        (
            item.get("service")
            for item in services
            if isinstance(item, dict)
            and isinstance(item.get("service"), dict)
            and item["service"].get("name") == "trinity-record-chain-gateway"
        ),
        None,
    )
    if not service:
        raise SystemExit("service not found")

    deploy_data = api_json(f"/services/{service['id']}/deploys?limit=10")
    raw_deploys = deploy_data if isinstance(deploy_data, list) else deploy_data.get("deploys", [])
    latest_raw = raw_deploys[0] if raw_deploys else {}
    latest = latest_raw.get("deploy", latest_raw) if isinstance(latest_raw, dict) else {}

    preflight_status, preflight = public_json("/record-chain/preflight", post=True)
    health_status, health = public_json("/healthz")
    readiness_status, readiness = public_json("/record-chain/readiness")

    report = {
        "service_id": service.get("id"),
        "service_name": service.get("name"),
        "service_updated_at": service.get("updatedAt"),
        "latest_deploy": {
            key: latest.get(key)
            for key in (
                "id",
                "status",
                "createdAt",
                "updatedAt",
                "finishedAt",
                "commit",
                "commitId",
                "trigger",
                "clearCache",
            )
            if latest.get(key) is not None
        },
        "gateway_runtime": preflight.get("gateway_runtime"),
        "preflight_http_status": preflight_status,
        "health_http_status": health_status,
        "health": health,
        "readiness_http_status": readiness_status,
        "readiness": readiness,
    }
    print("RENDER_REDEPLOY_REPORT=" + json.dumps(report, ensure_ascii=False, sort_keys=True))

    healthy = (
        health_status == 200
        and health.get("ok") is True
        and readiness_status == 200
        and readiness.get("ok") is True
        and readiness.get("submit_ready") is True
        and bool(report["latest_deploy"].get("id"))
    )
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
