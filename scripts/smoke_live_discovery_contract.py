#!/usr/bin/env python3
"""Smoke-test live public discovery surfaces after Pages deployment.

This is an external live smoke. It should be run manually or on schedule,
not as a normal PR/P0 source-only check.

It verifies that the public site exposes the current full agent journey:
discovery -> first-contact -> workflow manual/API -> submit gateway ->
builder route map -> output/readback policy.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SITE = "https://www.trinityaccord.org"

REQUIRED_LINKS_MACHINE = {
    "/api/agent-minimal-context.v1.json",
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/api/agent-start.v1.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/context-load-map.json",
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/public-home-status.json",
    "/api/guardian-registry.json",
    "/api/echo-index.json",
    "/api/agent-declared-verification-index.json",
}

REQUIRED_LINKS_PAGES = {
    "/agent-start",
    "/agent-echo",
    "/gateway-workflows",
    "/guardian-alliance",
    "/guardian-join",
    "/guardian-routes",
}

REQUIRED_WELL_KNOWN_API = {
    "agent_minimal_context": "/api/agent-minimal-context.v1.json",
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
    "agent_output_policy": "/api/agent-output-policy.v1.json",
    "agent_task_router": "/api/agent-task-router.v1.json",
    "gateway_workflows": "/api/gateway-workflows.v1.json",
    "agent_submit_gateway": "/api/agent-submit-gateway.json",
    "gateway_builder_route_map": "/api/gateway-builder-route-map.v1.json",
}

REQUIRED_WELL_KNOWN_ALIASES = {
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
    "gateway_workflows": "/gateway-workflows/",
    "gateway_workflows_json": "/api/gateway-workflows.v1.json",
    "agent_submit_gateway": "/api/agent-submit-gateway.json",
    "gateway_builder_route_map": "/api/gateway-builder-route-map.v1.json",
}


def fetch_json(url: str, timeout: int) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "trinity-accord-live-discovery-smoke/1.0",
            "Accept": "application/json,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            status = getattr(resp, "status", None)
            if status and status >= 400:
                raise RuntimeError(f"HTTP {status} from {url}")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} from {url}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch {url}: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from {url}: {e}") from e


def local_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def norm(path: str) -> str:
    if path != "/" and path.endswith("/"):
        return path[:-1]
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument(
        "--strict-digest",
        action="store_true",
        help="Require live api/links.json source_digest to match repository source_digest.",
    )
    args = parser.parse_args()

    site = args.site.rstrip("/")
    errors: list[str] = []

    links_url = f"{site}/api/links.json"
    well_known_url = f"{site}/.well-known/trinity-accord.json"

    print(f"Fetching live links: {links_url}")
    live_links = fetch_json(links_url, args.timeout)

    print(f"Fetching live well-known: {well_known_url}")
    live_well_known = fetch_json(well_known_url, args.timeout)

    # Print live metadata for diagnostics
    print(f"Live links source_digest: {live_links.get('source_digest')!r}")
    print(f"Live links version: {live_links.get('version')!r}")
    print(f"Live well-known site: {live_well_known.get('site')!r}")

    machine = set(live_links.get("machine", []))
    key_pages = set(live_links.get("key_pages", []))
    key_pages_norm = {norm(p) for p in key_pages}

    missing_machine = sorted(REQUIRED_LINKS_MACHINE - machine)
    if missing_machine:
        errors.append(f"live links.json machine missing: {missing_machine}")

    missing_pages = sorted(
        p for p in REQUIRED_LINKS_PAGES
        if p not in key_pages and norm(p) not in key_pages_norm
    )
    if missing_pages:
        errors.append(f"live links.json key_pages missing: {missing_pages}")

    wk_api = live_well_known.get("api", {})
    for key, expected in REQUIRED_WELL_KNOWN_API.items():
        if wk_api.get(key) != expected:
            errors.append(
                f"live well-known api.{key} expected {expected!r}, got {wk_api.get(key)!r}"
            )

    for key, expected in REQUIRED_WELL_KNOWN_ALIASES.items():
        if live_well_known.get(key) != expected:
            errors.append(
                f"live well-known top-level {key} expected {expected!r}, got {live_well_known.get(key)!r}"
            )

    entrypoints = live_well_known.get("agent_entrypoints", {})
    for key in [
        "agent_first_contact",
        "agent_required_reading",
        "gateway_workflows",
        "agent_submit_gateway",
        "gateway_builder_route_map",
    ]:
        if key not in entrypoints:
            errors.append(f"live well-known agent_entrypoints missing {key}")

    if args.strict_digest:
        repo_links = local_json("api/links.json")
        live_digest = live_links.get("source_digest")
        repo_digest = repo_links.get("source_digest")
        if live_digest != repo_digest:
            errors.append(
                "live links.json source_digest mismatch: "
                f"live={live_digest!r}, repo={repo_digest!r}; "
                "this usually means Pages/CDN/custom-domain is serving an older artifact"
            )

    if errors:
        print("FAIL: live discovery contract errors:")
        for e in errors:
            print("  -", e)
        return 1

    print("PASS: live public discovery exposes full agent journey contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
