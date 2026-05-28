#!/usr/bin/env python3
"""Agent submit Gateway contract must expose Gateway discovery for zero-manual canary."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
GATEWAY_PATH = ROOT / "api" / "agent-submit-gateway.json"
CANARY_POLICY_PATH = ROOT / "api" / "live-canary-policy.v1.json"
PAYLOAD_SCHEMA_PATH = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"

EXPECTED_BASE = "https://trinity-agent-issue-gateway.onrender.com"
EXPECTED_PREFLIGHT_PATH = "/gateway/preflight"
EXPECTED_SUBMIT_PATH = "/agent-submit"
EXPECTED_CANARY_POLICY = "/api/live-canary-policy.v1.json"
EXPECTED_PAYLOAD_SCHEMA = "/api/agent-issue-gateway-payload-schema.v1.json"


def is_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def main() -> int:
    data = json.loads(GATEWAY_PATH.read_text(encoding="utf-8"))
    discovery = data.get("gateway_discovery", {})
    errors: list[str] = []

    if not isinstance(discovery, dict):
        errors.append("gateway_discovery must be an object")
    else:
        candidates: list[str] = []

        primary = discovery.get("primary_base_url")
        if primary:
            candidates.append(primary)

        base_url_candidates = discovery.get("base_url_candidates", [])
        if not isinstance(base_url_candidates, list):
            errors.append("base_url_candidates must be a list when present")
        else:
            candidates.extend(base_url_candidates)

        if not candidates:
            errors.append("gateway_discovery must expose primary_base_url or base_url_candidates")

        if EXPECTED_BASE not in candidates:
            errors.append(f"gateway_discovery must include expected Render base URL: {EXPECTED_BASE}")

        for url in candidates:
            if not isinstance(url, str) or not is_https_url(url):
                errors.append(f"Gateway candidate must be https URL: {url!r}")

        if discovery.get("preflight_path") != EXPECTED_PREFLIGHT_PATH:
            errors.append(f"preflight_path must be {EXPECTED_PREFLIGHT_PATH}")

        if discovery.get("submit_path") != EXPECTED_SUBMIT_PATH:
            errors.append(f"submit_path must be {EXPECTED_SUBMIT_PATH}")

        if discovery.get("submit_path") == "/gateway/submit":
            errors.append("submit_path must not use stale /gateway/submit")

        if discovery.get("method") != "POST":
            errors.append("method must be POST")

        if discovery.get("content_type") != "application/json":
            errors.append("content_type must be application/json")

        if discovery.get("payload_schema") != EXPECTED_PAYLOAD_SCHEMA:
            errors.append(f"payload_schema must be {EXPECTED_PAYLOAD_SCHEMA}")

        if discovery.get("canary_supported") is not True:
            errors.append("canary_supported must be true")

        if discovery.get("canary_policy") != EXPECTED_CANARY_POLICY:
            errors.append(f"canary_policy must point to {EXPECTED_CANARY_POLICY}")

        route = discovery.get("synthetic_canary_route", {})
        if not isinstance(route, dict):
            errors.append("synthetic_canary_route must be an object")
        else:
            if route.get("submission_type") != "protocol_issue":
                errors.append("synthetic_canary_route.submission_type must be protocol_issue")
            if route.get("builder_required") is not False:
                errors.append("synthetic_canary_route.builder_required must be false")
            for boundary in [
                "not_formal_echo",
                "not_archive",
                "not_attestation",
                "not_verification",
                "not_guardian_status",
                "not_canonical_amendment",
            ]:
                if route.get(boundary) is not True:
                    errors.append(f"synthetic_canary_route.{boundary} must be true")

    if not CANARY_POLICY_PATH.exists():
        errors.append("canary_policy target file is missing: api/live-canary-policy.v1.json")

    if not PAYLOAD_SCHEMA_PATH.exists():
        errors.append("payload schema target file is missing: api/agent-issue-gateway-payload-schema.v1.json")

    # Cross-check related endpoint fields stay aligned.
    base = EXPECTED_BASE

    v0v5 = data.get("v0_v5_archive_submission", {})
    if v0v5.get("preflight_endpoint") != base + EXPECTED_PREFLIGHT_PATH:
        errors.append("v0_v5_archive_submission.preflight_endpoint does not match gateway_discovery")
    if v0v5.get("submit_endpoint") != base + EXPECTED_SUBMIT_PATH:
        errors.append("v0_v5_archive_submission.submit_endpoint does not match gateway_discovery")

    submission_endpoint = data.get("submission_endpoint", {})
    if submission_endpoint.get("public_url") != base + EXPECTED_SUBMIT_PATH:
        errors.append("submission_endpoint.public_url does not match gateway_discovery submit path")

    if "/gateway/submit" in json.dumps(data, sort_keys=True):
        errors.append("stale /gateway/submit must not appear in active agent-submit-gateway contract")

    if errors:
        print("FAIL: Gateway discovery canary contract errors:")
        for e in errors:
            print("  -", e)
        return 1

    print("PASS: Gateway discovery for zero-manual canary is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
