#!/usr/bin/env python3
"""Live smoke for external heterogeneous agent entrypoint journeys.

This script simulates multiple external agents entering through public entrypoints
and verifies that they can discover first-contact, route, policy, workflow, and
before_leaving contracts.

This is a live smoke. Do not run it in source-only p0-main.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import dataclass
from typing import Any

DEFAULT_SITE = "https://www.trinityaccord.org"

ENTRYPOINTS = [
    "/",
    "/robots.txt",
    "/llms.txt",
    "/ai.txt",
    "/.well-known/trinity-accord.json",
    "/api/links.json",
    "/agent-start",
    "/agent-echo",
    "/gateway-workflows/",
]

REQUIRED_PUBLIC_CONTRACTS = [
    "/api/links.json",
    "/.well-known/trinity-accord.json",
    "/api/agent-first-contact.json",
    "/api/agent-submit-gateway.json",
    "/api/agent-output-policy.v1.json",
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
]


@dataclass
class Result:
    entrypoint: str
    ok: bool
    message: str


def fetch(site: str, path: str, timeout: int) -> bytes:
    url = site.rstrip("/") + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrinityExternalAgentJourneySmoke/1.0",
            "Accept": "application/json,text/plain,text/html,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_json(site: str, path: str, timeout: int) -> dict[str, Any]:
    return json.loads(fetch(site, path, timeout).decode("utf-8"))


def check_entrypoint(site: str, entrypoint: str, timeout: int) -> Result:
    try:
        body = fetch(site, entrypoint, timeout)
        if not body:
            return Result(entrypoint, False, "empty response")
        return Result(entrypoint, True, "reachable")
    except Exception as exc:
        return Result(entrypoint, False, f"fetch failed: {exc}")


def check_contracts(site: str, timeout: int) -> list[str]:
    errors: list[str] = []

    for path in REQUIRED_PUBLIC_CONTRACTS:
        try:
            fetch(site, path, timeout)
        except Exception as exc:
            errors.append(f"{path}: fetch failed: {exc}")

    try:
        first_contact = fetch_json(site, "/api/agent-first-contact.json", timeout)
        text = json.dumps(first_contact, sort_keys=True)
        for required in [
            "/api/agent-submit-gateway.json",
            "/api/agent-output-policy.v1.json",
            "/api/gateway-workflows.v1.json",
            "/api/gateway-builder-route-map.v1.json",
            "before_leaving",
        ]:
            if required not in text:
                errors.append(f"first-contact missing {required}")
    except Exception as exc:
        errors.append(f"first-contact parse failed: {exc}")

    try:
        submit = fetch_json(site, "/api/agent-submit-gateway.json", timeout)
        text = json.dumps(submit, sort_keys=True)
        if "/gateway/submit" in text:
            errors.append("agent-submit-gateway contains stale /gateway/submit")
        if "/agent-submit" not in text:
            errors.append("agent-submit-gateway missing /agent-submit")
        if "/gateway/preflight" not in text:
            errors.append("agent-submit-gateway missing /gateway/preflight")
    except Exception as exc:
        errors.append(f"submit gateway parse failed: {exc}")

    try:
        output_policy = fetch_json(site, "/api/agent-output-policy.v1.json", timeout)
        if "before_leaving" not in json.dumps(output_policy, sort_keys=True):
            errors.append("output policy missing before_leaving")
    except Exception as exc:
        errors.append(f"output policy parse failed: {exc}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    results = [check_entrypoint(args.site, entrypoint, args.timeout) for entrypoint in ENTRYPOINTS]
    errors = []

    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status}: entrypoint={result.entrypoint} {result.message}")
        if not result.ok:
            errors.append(f"{result.entrypoint}: {result.message}")

    errors.extend(check_contracts(args.site, args.timeout))

    if errors:
        print("FAIL: external agent entrypoint journey smoke errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: external heterogeneous agent entrypoint journeys passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
