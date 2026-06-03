#!/usr/bin/env python3
"""Live smoke: three core external agent preflight routes.

Verifies that the three core builder routes (pure_echo, v0_v5_agent_declared_archive,
guardian_application_stage_1) respond to preflight at the live gateway.

This is live/network. It must not run in source-only p0-current.
It must not POST to /agent-submit.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_GATEWAY = "https://trinity-agent-issue-gateway.onrender.com"

CORE_ROUTES = [
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
]


def preflight(gateway: str, route: str) -> dict:
    url = f"{gateway}/gateway/preflight"
    payload = json.dumps({"route": route}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "TrinityCorePreflightSmoke/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return {"error": e.code, "body": body}


def main() -> int:
    parser = argparse.ArgumentParser(description="Live smoke: three core preflight routes")
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY)
    args = parser.parse_args()

    failures = []
    for route in CORE_ROUTES:
        print(f"Preflight {route} ...", end=" ")
        result = preflight(args.gateway, route)
        if "error" in result:
            print(f"FAIL ({result['error']})")
            failures.append((route, result))
        else:
            accepted = result.get("accepted")
            print(f"accepted={accepted}")
            if not accepted:
                failures.append((route, result))

    if failures:
        print(f"\nFAIL: {len(failures)}/{len(CORE_ROUTES)} routes failed")
        for route, result in failures:
            print(f"  {route}: {json.dumps(result, indent=2)[:200]}")
        return 1

    print(f"\nPASS: all {len(CORE_ROUTES)} core preflight routes accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
