#!/usr/bin/env python3
"""Concurrent external-agent preflight swarm smoke.

This is live/network. It must run in live-site group, not source-only p0-main.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import time
import urllib.request
from dataclasses import dataclass

DEFAULT_GATEWAY = "https://trinity-agent-issue-gateway.onrender.com"
PREFLIGHT_PATH = "/gateway/preflight"

@dataclass
class Result:
    index: int
    ok: bool
    status: int | None
    message: str

def payload(i: int) -> dict:
    return {
        "submission_type": "protocol_issue",
        "title": f"preflight swarm synthetic canary {i}",
        "body": "Synthetic preflight-only canary. Not formal Echo, not verification, not archive.",
        "labels": ["protocol-issue", "synthetic-canary", "preflight-only"],
        "source": {
            "kind": "external_agent_preflight_swarm",
            "agent_index": i,
            "timestamp": int(time.time())
        },
        "canary": {
            "preflight_only": True,
            "not_formal_submission": True,
            "not_archive": True,
            "not_verification": True,
            "not_guardian_status": True
        }
    }

def post_json(url: str, data: dict, timeout: int) -> tuple[int, str]:
    raw = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=raw,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "TrinityConcurrentPreflightSwarm/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")

def one(i: int, gateway: str, timeout: int) -> Result:
    url = gateway.rstrip("/") + PREFLIGHT_PATH
    try:
        status, body = post_json(url, payload(i), timeout)
        if status < 200 or status >= 300:
            return Result(i, False, status, f"non-2xx status: {body[:200]}")
        return Result(i, True, status, "ok")
    except Exception as exc:
        return Result(i, False, None, str(exc))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY)
    parser.add_argument("--agents", type=int, default=20)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--max-failures", type=int, default=0)
    args = parser.parse_args()

    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(one, i, args.gateway, args.timeout) for i in range(args.agents)]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            status = "PASS" if result.ok else "FAIL"
            print(f"{status}: agent={result.index} status={result.status} {result.message}")

    failures = [r for r in results if not r.ok]
    if len(failures) > args.max_failures:
        print(f"FAIL: concurrent preflight swarm failures: {len(failures)} > {args.max_failures}")
        return 1

    print("PASS: concurrent external-agent preflight swarm completed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
