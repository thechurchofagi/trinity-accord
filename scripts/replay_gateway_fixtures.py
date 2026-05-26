#!/usr/bin/env python3
"""Replay Gateway fixtures against a deployed Gateway.

Uses /gateway/preflight by default and does not create GitHub Issues.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_FIXTURES = [
    "tests/fixtures/gateway/valid_pure_echo.json",
    "tests/fixtures/gateway/valid_agent_declared_v4.json",
]


def request_json(method, url, timeout, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "content-type": "application/json",
            "user-agent": "trinity-gateway-smoke/1.0",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return err.code, parsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--endpoint", default="/gateway/preflight")
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--require-readiness", action="store_true")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    failures = []

    for path in ["/healthz", "/gateway/version", "/gateway/capabilities"]:
        status, body = request_json("GET", base + path, args.timeout)
        print(f"{path}: HTTP {status}")
        if status >= 400:
            failures.append(f"{path} failed: HTTP {status}: {body}")

    status, readiness = request_json("GET", base + "/readiness", args.timeout)
    print(f"/readiness: HTTP {status}")
    if args.require_readiness and status != 200:
        failures.append(f"/readiness failed: HTTP {status}: {readiness}")

    fixtures = args.fixture or DEFAULT_FIXTURES
    for rel in fixtures:
        fixture_path = ROOT / rel
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))

        status, body = request_json("POST", base + args.endpoint, args.timeout, payload=payload)
        print(f"{rel} -> {args.endpoint}: HTTP {status}")

        if status != 200:
            failures.append(f"{rel}: expected HTTP 200, got {status}: {body}")
            continue

        if body.get("accepted") is not True:
            failures.append(f"{rel}: accepted is not true: {body}")

        if body.get("issue_created") is not False:
            failures.append(f"{rel}: preflight must not create issue: {body}")

        if "guardian_verification_result" not in body:
            failures.append(f"{rel}: missing guardian_verification_result")

        if "idempotency_key" not in body:
            failures.append(f"{rel}: missing idempotency_key")

        if "request_id" not in body:
            failures.append(f"{rel}: missing request_id")

    if failures:
        print("GATEWAY_FIXTURE_REPLAY_FAIL")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(1)

    print("GATEWAY_FIXTURE_REPLAY_OK")


if __name__ == "__main__":
    main()
