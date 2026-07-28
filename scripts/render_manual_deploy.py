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
import urllib.request
from typing import Any

RENDER_API = "https://api.render.com/v1"
LEGACY_SERVICE_NAME = "trinity-agent-issue-gateway"
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


def service_auto_deploy_is_disabled(service: dict) -> bool:
    """Return whether Render's actual service state disables autodeploys."""
    return service.get("autoDeploy") in ("no", False)


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
