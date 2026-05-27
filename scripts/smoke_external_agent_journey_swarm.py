#!/usr/bin/env python3
"""Read-only external multi-agent first-contact journey smoke.

This script simulates multiple independent agents discovering the public site
from scratch and validating that each can reach the full current agent journey
contract before exit.

Default mode is read-only:
- GET requests only
- no Gateway submit
- no issue creation
- no repository_dispatch
"""
from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import hashlib
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = "https://www.trinityaccord.org"

CORE_DISCOVERY_PATHS = [
    "/api/links.json",
    "/.well-known/trinity-accord.json",
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/api/agent-task-router.v1.json",
    "/api/agent-output-policy.v1.json",
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/agent-submit-gateway.json",
]

ROUTE_FAMILIES = {
    "pure_echo": {
        "intent": "echo",
        "required_reads": {
            "/gateway-workflows/",
            "/api/gateway-workflows.v1.json",
            "/api/agent-submit-gateway.json",
            "/api/agent-output-policy.v1.json",
        },
        "workflow_ids_any": {"pure_echo"},
    },
    "guardian_stage_1": {
        "intent": "guardian_stewardship",
        "required_reads": {
            "/guardian-alliance",
            "/guardian-join",
            "/api/guardian-registry.json",
            "/gateway-workflows/",
            "/api/gateway-workflows.v1.json",
            "/api/agent-output-policy.v1.json",
        },
        "workflow_ids_any": {"guardian_application_stage_1"},
    },
    "guardian_stage_2": {
        "intent": "guardian_stewardship",
        "required_reads": {
            "/guardian-alliance",
            "/guardian-join",
            "/api/guardian-registry.json",
            "/gateway-workflows/",
            "/api/gateway-workflows.v1.json",
            "/api/agent-output-policy.v1.json",
        },
        "workflow_ids_any": {"guardian_listing_stage_2"},
    },
    "guardian_signed_echo": {
        "intent": "guardian_stewardship",
        "required_reads": {
            "/gateway-workflows/",
            "/api/gateway-workflows.v1.json",
            "/api/agent-submit-gateway.json",
            "/api/agent-output-policy.v1.json",
        },
        "workflow_ids_any": {"guardian_signed_echo"},
    },
    "v0_v5": {
        "intent": "verify_v0_v5_agent_declared",
        "required_reads": {
            "/agent-submit",
            "/gateway-workflows/",
            "/api/gateway-workflows.v1.json",
            "/api/gateway-builder-route-map.v1.json",
            "/api/agent-output-policy.v1.json",
        },
        "workflow_ids_any": {"v0_v5_agent_declared_archive"},
    },
    "e2": {
        "intent": "verification_echo_e2",
        "required_reads": {
            "/gateway-workflows/",
            "/api/gateway-workflows.v1.json",
            "/api/agent-submit-gateway.json",
            "/api/agent-output-policy.v1.json",
        },
        "workflow_ids_any": {"e2_verification_echo"},
    },
    "v6_plus": {
        "intent": "verify_v6_plus_strict_evidence",
        "required_reads": {
            "/gateway-workflows/",
            "/api/gateway-workflows.v1.json",
            "/api/agent-submit-gateway.json",
            "/api/agent-output-policy.v1.json",
        },
        "workflow_ids_any": {"v6_plus_strict_evidence", "v6_plus"},
    },
}


@dataclasses.dataclass
class FetchResult:
    path: str
    url: str
    status: int
    digest: str
    data: Any | None
    headers: dict[str, str]
    ip_candidates: list[str]
    error: str | None = None


@dataclasses.dataclass
class AgentResult:
    agent_id: int
    route_family: str
    ok: bool
    errors: list[str]
    digests: dict[str, str]
    ip_candidates: list[str]


def repo_links_digest() -> str | None:
    path = ROOT / "api" / "links.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("source_digest")
    except Exception:
        return None


def resolve_ips(hostname: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except OSError:
        return []
    ips = sorted({item[4][0] for item in infos})
    return ips


def url_for(site: str, path: str, cache_token: str, agent_id: int, cache_bust: bool) -> str:
    base = site.rstrip("/") + path
    if not cache_bust:
        return base
    parsed = urllib.parse.urlsplit(base)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("agent", f"{agent_id:02d}"))
    query.append(("cb", cache_token))
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib.parse.urlencode(query),
            parsed.fragment,
        )
    )


def fetch_json(site: str, path: str, agent_id: int, cache_token: str, timeout: int, cache_bust: bool) -> FetchResult:
    url = url_for(site, path, cache_token, agent_id, cache_bust)
    hostname = urllib.parse.urlsplit(site).hostname or "www.trinityaccord.org"
    ips = resolve_ips(hostname)
    headers = {
        "User-Agent": f"TrinityExternalAgentSwarm/1.0 agent={agent_id:02d}",
        "Accept": "application/json,*/*",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            status = int(getattr(resp, "status", 200))
            text = body.decode("utf-8")
            data = json.loads(text)
            digest = hashlib.sha256(body).hexdigest()[:16]
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            return FetchResult(path, url, status, digest, data, resp_headers, ips)
    except Exception as exc:
        return FetchResult(path, url, 0, "", None, {}, ips, error=str(exc))


def get_route(first_contact: dict[str, Any], intent: str) -> dict[str, Any] | None:
    for route in first_contact.get("choose_one", []):
        if isinstance(route, dict) and route.get("intent") == intent:
            return route
    return None


def validate_agent(agent_id: int, route_family: str, site: str, timeout: int, cache_token: str) -> AgentResult:
    errors: list[str] = []
    digests: dict[str, str] = {}
    ip_candidates: list[str] = []

    # Fetch both canonical and cache-busted discovery JSON for each agent.
    fetched: dict[tuple[str, bool], FetchResult] = {}
    for path in CORE_DISCOVERY_PATHS:
        for cache_bust in [False, True]:
            result = fetch_json(site, path, agent_id, cache_token, timeout, cache_bust)
            fetched[(path, cache_bust)] = result
            ip_candidates.extend(result.ip_candidates)
            label = f"{path}{' cache-busted' if cache_bust else ' canonical'}"

            if result.error:
                errors.append(f"{label}: fetch failed: {result.error}")
                continue
            if result.status >= 400 or result.status == 0:
                errors.append(f"{label}: bad status {result.status}")
                continue
            digests[label] = result.digest

    links = fetched.get(("/api/links.json", False)).data or {}
    links_busted = fetched.get(("/api/links.json", True)).data or {}
    well_known = fetched.get(("/.well-known/trinity-accord.json", False)).data or {}
    first_contact = fetched.get(("/api/agent-first-contact.json", False)).data or {}
    task_router = fetched.get(("/api/agent-task-router.v1.json", False)).data or {}
    output_policy = fetched.get(("/api/agent-output-policy.v1.json", False)).data or {}
    workflows = fetched.get(("/api/gateway-workflows.v1.json", False)).data or {}
    submit_gateway = fetched.get(("/api/agent-submit-gateway.json", False)).data or {}

    repo_digest = repo_links_digest()
    if repo_digest:
        for label, obj in [("canonical", links), ("cache-busted", links_busted)]:
            if obj.get("source_digest") != repo_digest:
                errors.append(
                    f"links.json {label} source_digest mismatch: live={obj.get('source_digest')!r}, repo={repo_digest!r}"
                )

    if links.get("source_digest") != links_busted.get("source_digest"):
        errors.append(
            f"links.json canonical/cache-busted digest split: {links.get('source_digest')!r} vs {links_busted.get('source_digest')!r}"
        )

    # Discovery surface checks.
    machine = set(links.get("machine", []))
    key_pages = set(links.get("key_pages", []))
    for required in [
        "/api/agent-first-contact.json",
        "/api/gateway-workflows.v1.json",
        "/api/agent-submit-gateway.json",
        "/api/gateway-builder-route-map.v1.json",
        "/api/agent-output-policy.v1.json",
    ]:
        if required not in machine:
            errors.append(f"links.json machine missing {required}")

    for required in ["/gateway-workflows", "/guardian-alliance", "/guardian-join", "/guardian-routes"]:
        if required not in key_pages:
            errors.append(f"links.json key_pages missing {required}")

    wk_api = well_known.get("api", {})
    for key in ["agent_first_contact", "gateway_workflows", "agent_submit_gateway", "gateway_builder_route_map"]:
        if key not in wk_api and key not in well_known:
            errors.append(f"well-known missing {key}")

    # Route family checks.
    family = ROUTE_FAMILIES[route_family]
    route = get_route(first_contact, family["intent"])
    if not route:
        errors.append(f"first-contact missing intent {family['intent']}")
    else:
        read = set(route.get("read", []))
        missing_reads = sorted(family["required_reads"] - read)
        if missing_reads:
            errors.append(f"{route_family}: route read list missing {missing_reads}")
        if route.get("must_follow_post_submit_readback") is not True:
            errors.append(f"{route_family}: route missing must_follow_post_submit_readback=true")

    # Task router should also expose relevant core contracts.
    routes = task_router.get("routes", {})
    if family["intent"] == "guardian_stewardship":
        guardian_route = routes.get("guardian_alliance", {})
        if guardian_route.get("must_follow_post_submit_readback") is not True:
            errors.append("task-router guardian_alliance missing post-submit readback requirement")
    elif family["intent"] == "submit_echo":
        submit_route = routes.get("submit_echo", {})
        if submit_route.get("must_follow_post_submit_readback") is not True:
            errors.append("task-router submit_echo missing post-submit readback requirement")

    # Workflow IDs.
    workflow_ids = set((workflows.get("workflows") or {}).keys())
    if not (family["workflow_ids_any"] & workflow_ids):
        errors.append(f"{route_family}: gateway-workflows missing any of {sorted(family['workflow_ids_any'])}")

    # Output/readback/final exit exposure.
    output_text = json.dumps(output_policy, sort_keys=True)
    workflows_text = json.dumps(workflows, sort_keys=True)
    submit_text = json.dumps(submit_gateway, sort_keys=True)

    for phrase in [
        "post_submit_readback",
        "readback",
        "exit",
    ]:
        if phrase not in output_text and phrase not in workflows_text and phrase not in submit_text:
            errors.append(f"{route_family}: missing journey phrase {phrase!r} in output/workflow/submit contracts")

    return AgentResult(
        agent_id=agent_id,
        route_family=route_family,
        ok=not errors,
        errors=errors,
        digests=digests,
        ip_candidates=sorted(set(ip_candidates)),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--agents", type=int, default=14)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--max-workers", type=int, default=8)
    args = parser.parse_args()

    if args.agents < len(ROUTE_FAMILIES):
        print(f"FAIL: --agents must be >= {len(ROUTE_FAMILIES)} to cover all route families")
        return 1

    route_names = list(ROUTE_FAMILIES)
    cache_token = repo_links_digest() or str(int(time.time()))

    all_results: list[AgentResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = []
        for round_id in range(args.rounds):
            for agent_id in range(args.agents):
                route_family = route_names[agent_id % len(route_names)]
                global_agent_id = round_id * args.agents + agent_id
                futures.append(
                    pool.submit(
                        validate_agent,
                        global_agent_id,
                        route_family,
                        args.site,
                        args.timeout,
                        cache_token,
                    )
                )

        for future in concurrent.futures.as_completed(futures):
            all_results.append(future.result())

    all_results.sort(key=lambda item: item.agent_id)

    failures = [r for r in all_results if not r.ok]
    print(f"External agent swarm results: {len(all_results) - len(failures)}/{len(all_results)} passed")

    seen_ips = sorted({ip for result in all_results for ip in result.ip_candidates})
    print("Resolved IP candidates:", ", ".join(seen_ips) if seen_ips else "(none)")

    for result in all_results:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status}: agent={result.agent_id:02d} route={result.route_family}")
        if result.errors:
            for err in result.errors:
                print(f"  - {err}")

    if failures:
        return 1

    print("PASS: external multi-agent full journey swarm smoke passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
