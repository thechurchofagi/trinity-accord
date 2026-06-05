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

DEFAULT_GATEWAY = "https://trinity-record-chain-gateway.onrender.com"

# Route name → record_type for /record-chain/preflight
CORE_ROUTES = [
    ("pure_echo", "echo"),
    ("v0_v5_agent_declared_archive", "verification"),
    ("guardian_application_stage_1", "guardian_application"),
]


def preflight(gateway: str, route_label: str, record_type: str) -> dict:
    url = f"{gateway}/record-chain/preflight"
    payload = json.dumps({"record_type": record_type}).encode()
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
    for route_label, record_type in CORE_ROUTES:
        print(f"Preflight {route_label} ({record_type}) ...", end=" ")
        result = preflight(args.gateway, route_label, record_type)
        if "error" in result:
            print(f"FAIL ({result['error']})")
            failures.append((route_label, result))
        else:
            preflight_ok = result.get("preflight")
            route_detected = result.get("route_detected")
            accepted = result.get("accepted")
            print(f"preflight={preflight_ok} route_detected={route_detected} accepted={accepted}")
            if not preflight_ok:
                failures.append((route_label, result))

    if failures:
        print(f"\nFAIL: {len(failures)}/{len(CORE_ROUTES)} routes failed")
        for route_label, result in failures:
            print(f"  {route_label}: {json.dumps(result, indent=2)[:300]}")
        return 1

    print(f"\nPASS: all {len(CORE_ROUTES)} core preflight routes responded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
