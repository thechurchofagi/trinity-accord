#!/usr/bin/env python3
"""Controlled external live write lifecycle canary.

Default mode is preflight-only and must not create live issues.

Write modes require:
TRINITY_LIVE_CANARY_WRITE=I_UNDERSTAND_THIS_CREATES_A_LIVE_CANARY
"""
from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = "https://www.trinityaccord.org"
DEFAULT_GATEWAY = os.environ.get("TRINITY_GATEWAY_URL", "").rstrip("/")
WRITE_GATE_VALUE = "I_UNDERSTAND_THIS_CREATES_A_LIVE_CANARY"

ROUTE_FAMILIES = [
    "pure_echo",
    "guardian_signed_echo",
    "v0_v5",
    "e2",
    "v6_plus",
]

@dataclasses.dataclass
class LifecycleReport:
    mode: str
    nonce: str
    route_chosen: str
    builder_used: str | None
    payload_generated: bool
    preflight_attempted: bool
    preflight_result: str
    submission_attempted: bool
    submission_result: str
    gateway_receipt_id_if_any: str | None
    github_issue_url_if_any: str | None
    archive_status_if_known: str | None
    public_status_readback_performed: bool
    verification_state_by_this_agent: str
    remaining_uncertainty: str
    next_step_or_stop_reason: str

def require_write_gate(mode: str) -> None:
    if mode in {"single-write-canary", "duplicate-canary"}:
        if os.environ.get("TRINITY_LIVE_CANARY_WRITE") != WRITE_GATE_VALUE:
            raise SystemExit(
                "Refusing live write canary: set "
                "TRINITY_LIVE_CANARY_WRITE=I_UNDERSTAND_THIS_CREATES_A_LIVE_CANARY"
            )

def http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> tuple[int, dict[str, Any]]:
    data = None
    headers = {
        "User-Agent": "TrinityExternalWriteLifecycleCanary/1.0",
        "Accept": "application/json,*/*",
    }
    if payload is not None:
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        parsed = json.loads(body) if body.strip() else {}
        return int(getattr(resp, "status", 200)), parsed

def build_synthetic_canary_payload(route_family: str, nonce: str) -> dict[str, Any]:
    return {
        "synthetic_fixture": True,
        "canary": True,
        "test_only": True,
        "no_canonical_claim": True,
        "route_family": route_family,
        "nonce": nonce,
        "idempotency_key": f"trinity-live-canary-{nonce}",
        "agent_label": "external-lifecycle-canary",
        "title": f"[CANARY][AUTO-VERIFY][NO-AUTHORITY] {route_family} {nonce}",
        "summary": (
            "Synthetic live canary for Trinity Accord Gateway lifecycle. "
            "This is not verification, not archive status, and not canonical authority."
        ),
        "authority_boundary": "Bitcoin Originals only; this canary is non-authoritative.",
        "verification_state_by_this_agent": "unverified_by_this_agent",
    }

def preflight(gateway: str, payload: dict[str, Any], timeout: int) -> tuple[str, dict[str, Any]]:
    # Align endpoint names to deployed Gateway contract if different.
    status, body = http_json("POST", f"{gateway}/gateway/preflight", payload, timeout)
    if status >= 400:
        return "failed", body
    return "passed", body

def submit_canary(gateway: str, payload: dict[str, Any], timeout: int) -> tuple[str, dict[str, Any]]:
    status, body = http_json("POST", f"{gateway}/gateway/submit", payload, timeout)
    if status >= 400:
        return "failed", body
    return "submitted", body

def read_public_status(site: str, nonce: str, timeout: int) -> tuple[bool, str | None]:
    # First check common public indexes. Adjust if canary lands elsewhere.
    candidates = [
        "/api/public-home-status.json",
        "/api/echo-index.json",
        "/api/agent-declared-verification-index.json",
    ]
    for path in candidates:
        try:
            status, body = http_json("GET", site.rstrip("/") + path, None, timeout)
            text = json.dumps(body, sort_keys=True)
            if nonce in text:
                return True, path
        except Exception:
            continue
    return False, None

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY)
    parser.add_argument("--mode", choices=["preflight-only", "single-write-canary", "duplicate-canary"], default="preflight-only")
    parser.add_argument("--route", default="pure_echo")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--poll-seconds", type=int, default=180)
    args = parser.parse_args()

    if not args.gateway:
        print("FAIL: --gateway or TRINITY_GATEWAY_URL is required")
        return 1

    require_write_gate(args.mode)

    nonce = uuid.uuid4().hex[:12]
    route_families = ROUTE_FAMILIES if args.mode == "preflight-only" else [args.route]

    payloads = {route: build_synthetic_canary_payload(route, nonce) for route in route_families}

    preflight_results: dict[str, tuple[str, dict[str, Any]]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(payloads))) as pool:
        future_map = {
            pool.submit(preflight, args.gateway, payload, args.timeout): route
            for route, payload in payloads.items()
        }
        for future in concurrent.futures.as_completed(future_map):
            route = future_map[future]
            try:
                preflight_results[route] = future.result()
            except Exception as exc:
                preflight_results[route] = ("error", {"error": str(exc)})

    preflight_failures = {
        route: result
        for route, result in preflight_results.items()
        if result[0] != "passed"
    }

    submission_attempted = False
    submission_result = "not_attempted"
    receipt_id = None
    issue_url = None
    archive_status = None
    public_readback = False
    next_step = "preflight-only complete"

    if preflight_failures:
        next_step = "stop: preflight failed"
    elif args.mode in {"single-write-canary", "duplicate-canary"}:
        submission_attempted = True
        payload = payloads[args.route]
        try:
            submission_result, submit_body = submit_canary(args.gateway, payload, args.timeout)
            receipt_id = submit_body.get("receipt_id") or submit_body.get("gateway_receipt_id")
            issue_url = submit_body.get("issue_url") or submit_body.get("github_issue_url")
        except Exception as exc:
            submission_result = f"error: {exc}"
            submit_body = {}

        if submission_result == "submitted":
            deadline = time.time() + args.poll_seconds
            while time.time() < deadline:
                public_readback, path = read_public_status(args.site, nonce, args.timeout)
                if public_readback:
                    archive_status = f"observed_in:{path}"
                    break
                time.sleep(10)
            if not public_readback:
                archive_status = "not_observed_before_timeout"
            next_step = "write canary complete"

        if args.mode == "duplicate-canary" and submission_result == "submitted":
            # Re-submit same payload/idempotency key; Gateway should not create duplicate.
            dup_result, dup_body = submit_canary(args.gateway, payload, args.timeout)
            duplicate_issue_url = dup_body.get("issue_url") or dup_body.get("github_issue_url")
            if duplicate_issue_url and issue_url and duplicate_issue_url != issue_url:
                print("FAIL: duplicate canary created a different issue URL")
                return 1

    report = LifecycleReport(
        mode=args.mode,
        nonce=nonce,
        route_chosen=args.route if args.mode != "preflight-only" else "all_preflight_routes",
        builder_used="synthetic_fixture_payload_builder",
        payload_generated=True,
        preflight_attempted=True,
        preflight_result="passed" if not preflight_failures else json.dumps(preflight_failures, sort_keys=True),
        submission_attempted=submission_attempted,
        submission_result=submission_result,
        gateway_receipt_id_if_any=receipt_id,
        github_issue_url_if_any=issue_url,
        archive_status_if_known=archive_status,
        public_status_readback_performed=public_readback,
        verification_state_by_this_agent="unverified_by_this_agent",
        remaining_uncertainty=(
            "Canary is synthetic and non-authoritative; archive/public readback may be asynchronous."
        ),
        next_step_or_stop_reason=next_step,
    )

    print("before_leaving lifecycle report:")
    print(json.dumps(dataclasses.asdict(report), indent=2, sort_keys=True))

    if preflight_failures:
        return 1
    if args.mode in {"single-write-canary", "duplicate-canary"} and submission_result != "submitted":
        return 1

    print("PASS: external write lifecycle canary completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
