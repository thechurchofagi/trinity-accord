#!/usr/bin/env python3
"""Controlled external live write lifecycle canary — v24 zero-manual.

Gateway URL is discovered from public site contracts.
Write modes are gated by source-controlled canary policy + workflow confirmation input.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import hashlib
import json
import sys
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = "https://www.trinityaccord.org"
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
    gateway_base_url_discovered: str | None
    gateway_preflight_path: str | None
    gateway_submit_path: str | None
    canary_policy_loaded: bool
    write_gate_source: str


def fetch_public_json(site: str, path: str, timeout: int = 30) -> dict[str, Any]:
    url = site.rstrip("/") + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrinityExternalWriteLifecycleCanary/1.0",
            "Accept": "application/json,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_canary_policy(site: str, timeout: int) -> dict[str, Any]:
    return fetch_public_json(site, "/api/live-canary-policy.v1.json", timeout)


def discover_gateway_base_url(site: str, timeout: int) -> tuple[str, str, str]:
    submit_gateway = fetch_public_json(site, "/api/agent-submit-gateway.json", timeout)
    discovery = submit_gateway.get("gateway_discovery", {})

    candidates: list[str] = []
    if discovery.get("primary_base_url"):
        candidates.append(str(discovery["primary_base_url"]))
    candidates.extend(str(item) for item in discovery.get("base_url_candidates", []))

    preflight_path = discovery.get("preflight_path", "/gateway/preflight")
    submit_path = discovery.get("submit_path", "/gateway/submit")

    for base in candidates:
        base = base.rstrip("/")
        if not base.startswith("https://"):
            continue

        for health in discovery.get("health_paths", ["/healthz", "/readiness", "/"]):
            try:
                req = urllib.request.Request(
                    base + health,
                    headers={"User-Agent": "TrinityExternalWriteLifecycleCanary/1.0"},
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    if int(getattr(resp, "status", 200)) < 500:
                        return base, str(preflight_path), str(submit_path)
            except Exception:
                continue

    raise SystemExit("FAIL: no Gateway base URL discovered from public contracts")


def require_write_gate(mode: str, confirmation: str, policy: dict[str, Any]) -> None:
    if mode == "preflight-only":
        allowed = set(policy.get("scheduled_modes_allowed", [])) | set(policy.get("workflow_dispatch_modes_allowed", []))
        if mode not in allowed:
            raise SystemExit("FAIL: preflight-only is not allowed by live canary policy")
        return

    if mode not in set(policy.get("workflow_dispatch_modes_allowed", [])):
        raise SystemExit(f"FAIL: mode {mode!r} is not allowed by live canary policy")

    if policy.get("live_write_canary_enabled") is not True:
        raise SystemExit("FAIL: live write canary disabled by /api/live-canary-policy.v1.json")

    expected = policy.get("required_confirmation_for_write_modes")
    if confirmation != expected:
        raise SystemExit("FAIL: write mode requires --confirm-live-canary with exact policy phrase")


def validate_payload_against_policy(payload: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in policy.get("synthetic_payload_required_fields", []):
        if field not in payload:
            errors.append(f"payload missing required canary field {field}")

    for key, expected in policy.get("synthetic_payload_required_values", {}).items():
        if payload.get(key) != expected:
            errors.append(f"payload field {key} expected {expected!r}, got {payload.get(key)!r}")

    text = json.dumps(payload, sort_keys=True).lower()
    for forbidden in policy.get("must_not_claim", []):
        if forbidden.lower() in text:
            errors.append(f"payload contains forbidden claim phrase {forbidden!r}")

    return errors


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


def http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> tuple[int, dict[str, Any]]:
    data = None
    headers: dict[str, str] = {
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


def preflight(gateway_base: str, preflight_path: str, payload: dict[str, Any], timeout: int) -> tuple[str, dict[str, Any]]:
    status, body = http_json("POST", gateway_base + preflight_path, payload, timeout)
    if status >= 400:
        return "failed", body
    return "passed", body


def submit_canary(gateway_base: str, submit_path: str, payload: dict[str, Any], timeout: int) -> tuple[str, dict[str, Any]]:
    status, body = http_json("POST", gateway_base + submit_path, payload, timeout)
    if status >= 400:
        return "failed", body
    return "submitted", body


def read_public_status(site: str, nonce: str, timeout: int) -> tuple[bool, str | None]:
    candidates = [
        "/api/public-home-status.json",
        "/api/echo-index.json",
        "/api/agent-declared-verification-index.json",
    ]
    for path in candidates:
        try:
            _, body = http_json("GET", site.rstrip("/") + path, None, timeout)
            text = json.dumps(body, sort_keys=True)
            if nonce in text:
                return True, path
        except Exception:
            continue
    return False, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Trinity Accord external write lifecycle canary v24")
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--gateway", default="",
                        help="Local developer override for Gateway base URL (optional)")
    parser.add_argument("--mode", choices=["preflight-only", "single-write-canary", "duplicate-canary"],
                        default="preflight-only")
    parser.add_argument("--route", default="pure_echo")
    parser.add_argument("--confirm-live-canary", default="",
                        help="Required exact phrase for write modes")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--poll-seconds", type=int, default=180)
    args = parser.parse_args()

    # Load canary policy from public site
    try:
        policy = load_canary_policy(args.site, args.timeout)
        canary_policy_loaded = True
    except Exception as exc:
        print(f"FAIL: cannot load canary policy: {exc}")
        return 1

    # Discover Gateway URL from public contracts
    try:
        gateway_base, preflight_path, submit_path = discover_gateway_base_url(args.site, args.timeout)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"FAIL: Gateway discovery failed: {exc}")
        return 1

    if args.gateway:
        gateway_base = args.gateway.rstrip("/")

    print(f"gateway_base_url_discovered: {gateway_base}")

    # Gate writes by policy + confirmation
    require_write_gate(args.mode, args.confirm_live_canary, policy)

    nonce = uuid.uuid4().hex[:12]
    route_families = ROUTE_FAMILIES if args.mode == "preflight-only" else [args.route]

    payloads = {route: build_synthetic_canary_payload(route, nonce) for route in route_families}

    # Validate payloads against policy
    for route, payload in payloads.items():
        payload_errors = validate_payload_against_policy(payload, policy)
        if payload_errors:
            print(f"FAIL: canary payload violates /api/live-canary-policy.v1.json")
            for error in payload_errors:
                print("  -", error)
            return 1

    preflight_results: dict[str, tuple[str, dict[str, Any]]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(payloads))) as pool:
        future_map = {
            pool.submit(preflight, gateway_base, preflight_path, payload, args.timeout): route
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
            submission_result, submit_body = submit_canary(gateway_base, submit_path, payload, args.timeout)
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
            dup_result, dup_body = submit_canary(gateway_base, submit_path, payload, args.timeout)
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
        gateway_base_url_discovered=gateway_base,
        gateway_preflight_path=preflight_path,
        gateway_submit_path=submit_path,
        canary_policy_loaded=canary_policy_loaded,
        write_gate_source="api/live-canary-policy.v1.json + workflow input",
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
