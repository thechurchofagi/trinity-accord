#!/usr/bin/env python3
"""Render manual deployment helper.

Uses RENDER API key to list services and optionally trigger deployment.
Refuses legacy gateway deploy unless --allow-legacy is specified.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

RENDER_API = "https://api.render.com/v1"
LEGACY_SERVICE_NAME = "trinity-agent-issue-gateway"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def request(path: str, token: str, method: str = "GET", body: dict | None = None):
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
        fail(f"Render API HTTP {exc.code}")
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

    print(f"PASS: found Render service name={args.service} id={sid}")

    if not args.deploy:
        print("DRY_RUN: no deploy triggered")
        return 0

    result = request(f"/services/{sid}/deploys", token, method="POST", body={"clearCache": "do_not_clear"})
    deploy_id = result.get("id") or result.get("deploy", {}).get("id")
    print(f"RENDER_DEPLOY_TRIGGERED service={args.service} deploy_id={deploy_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
