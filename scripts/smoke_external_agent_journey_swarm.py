#!/usr/bin/env python3
"""Read-only external multi-agent first-contact journey smoke.

This script simulates multiple independent agents discovering the public site
from scratch and validating that each can reach the current Record-Chain
Intake Gateway journey before exit.

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
    "/api/agent-start.v2.json",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-submission-schema.v1.json",
    "/api/record-chain-builder-bundles.v1.json",
    "/api/record-chain-status.json",
]

ROUTE_FAMILIES = {
    "submit_record": {
        "intent": "submit_record",
        "required_reads": set(),
        "required_flow_phrases": {
            "download /downloads/record-chain-builder.mjs",
            "POST to /record-chain/preflight",
            "POST to /record-chain/submit if accepted",
            "save receipt",
        },
    },
    "pure_echo": {
        "intent": "echo",
        "required_reads": {
            "/agent-echo",
            "/api/echo-record-schema.v3.1.json",
            "/api/record-chain-intake-gateway.v1.json",
            "/downloads/record-chain-builder.mjs",
        },
        "required_flow_phrases": set(),
    },
    "v0_v5": {
        "intent": "verify_v0_v5_agent_declared",
        "required_reads": {
            "/agent-verify",
            "/api/claim-gate-rules.json",
            "/api/agent-declared-verification-template.v1.json",
            "/api/evidence-input-schema.v1.json",
            "/api/record-chain-intake-gateway.v1.json",
        },
        "required_flow_phrases": set(),
    },
    "e2": {
        "intent": "verification_echo_e2",
        "required_reads": {
            "/agent-verify",
            "/api/claim-gate-rules.json",
            "/api/echo-record-schema.v3.1.json",
            "/api/verification-report-schema.v2.json",
        },
        "required_flow_phrases": set(),
    },
    "v6_plus": {
        "intent": "verify_v6_plus_strict_evidence",
        "required_reads": {
            "/agent-verify",
            "/api/protocol-verification-profiles.json",
            "/api/claim-gate-rules.json",
            "/api/evidence-input-schema.v1.json",
        },
        "required_flow_phrases": set(),
    },
}

CURRENT_MACHINE_REQUIRED = {
    "/api/agent-first-contact.json",
    "/api/agent-start.v2.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-submission-schema.v1.json",
    "/api/record-chain-builder-bundles.v1.json",
    "/api/record-chain-status.json",
    "/downloads/record-chain-builder.mjs",
}

CURRENT_KEY_PAGES_REQUIRED = {
    "/agent-start",
    "/agent-brief",
    "/agent-echo",
}

LEGACY_NOT_CURRENT = {
    "/api/agent-submit-gateway.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/gateway-workflows.v1.json",
    "/gateway-workflows",
    "/guardian-routes",
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
    return sorted({item[4][0] for item in infos})


def url_for(site: str, path: str, cache_token: str, agent_id: int, cache_bust: bool) -> str:
    base = site.rstrip("/") + path
    if not cache_bust:
        return base
    parsed = urllib.parse.urlsplit(base)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("agent", f"{agent_id:02d}"))
    query.append(("cb", cache_token))
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment)
    )


def fetch_json(site: str, path: str, agent_id: int, cache_token: str, timeout: int, cache_bust: bool) -> FetchResult:
    url = url_for(site, path, cache_token, agent_id, cache_bust)
    hostname = urllib.parse.urlsplit(site).hostname or "www.trinityaccord.org"
    ips = resolve_ips(hostname)
    headers = {
        "User-Agent": f"TrinityExternalAgentSwarm/2.0 agent={agent_id:02d}",
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
    agent_start = fetched.get(("/api/agent-start.v2.json", False)).data or {}
    gateway = fetched.get(("/api/record-chain-intake-gateway.v1.json", False)).data or {}
    builder = fetched.get(("/api/record-chain-builder-bundles.v1.json", False)).data or {}

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

    machine = set(links.get("machine", []))
    key_pages = set(links.get("key_pages", []))
    legacy = set(links.get("legacy_machine", []))
    deprecated = set(links.get("deprecated_for_new_records", []))

    for required in sorted(CURRENT_MACHINE_REQUIRED):
        if required not in machine:
            errors.append(f"links.json machine missing {required}")

    for required in sorted(CURRENT_KEY_PAGES_REQUIRED):
        if required not in key_pages and required + "/" not in key_pages:
            errors.append(f"links.json key_pages missing {required}")

    for legacy_path in sorted(LEGACY_NOT_CURRENT):
        if legacy_path in machine:
            errors.append(f"links.json machine still exposes retired current path {legacy_path}")
        if legacy_path not in legacy and legacy_path not in deprecated:
            errors.append(f"links.json legacy/deprecated missing retired path {legacy_path}")

    wk_api = well_known.get("api", {})
    for key in ["agent_first_contact", "agent_output_policy", "agent_task_router"]:
        if key not in wk_api and key not in well_known:
            errors.append(f"well-known missing current key {key}")
    if "current_public_submission" not in well_known:
        errors.append("well-known missing current_public_submission")
    else:
        cps = well_known.get("current_public_submission", {})
        for required in [
            "/downloads/record-chain-builder.mjs",
            "/api/record-chain-intake-gateway.v1.json",
            "/api/record-chain-submission-schema.v1.json",
        ]:
            if required not in json.dumps(cps, sort_keys=True):
                errors.append(f"well-known current_public_submission missing {required}")

    family = ROUTE_FAMILIES[route_family]
    route = get_route(first_contact, family["intent"])
    if not route:
        errors.append(f"first-contact missing intent {family['intent']}")
    else:
        read = set(route.get("read", []))
        missing_reads = sorted(family["required_reads"] - read)
        if missing_reads:
            errors.append(f"{route_family}: route read list missing {missing_reads}")
        flow_text = json.dumps(route.get("flow", []), sort_keys=True)
        for phrase in sorted(family["required_flow_phrases"]):
            if phrase not in flow_text:
                errors.append(f"{route_family}: route flow missing {phrase!r}")

    current_submission_text = json.dumps(first_contact.get("current_public_submission_method", {}), sort_keys=True)
    for phrase in [
        "Record-Chain Intake Gateway",
        "/record-chain/preflight",
        "/record-chain/submit",
        "/downloads/record-chain-builder.mjs",
    ]:
        if phrase not in current_submission_text:
            errors.append(f"first-contact current_public_submission_method missing {phrase!r}")

    protocol_text = json.dumps(agent_start.get("builder_usage_safety_protocol", {}), sort_keys=True)
    for phrase in ["BUILDER_USAGE_UNCLEAR", "doctor_submission", "preflight_submission", "submit_submission"]:
        if phrase not in protocol_text:
            errors.append(f"agent-start builder_usage_safety_protocol missing {phrase!r}")

    gateway_text = json.dumps(gateway, sort_keys=True)
    for phrase in ["/record-chain/preflight", "/record-chain/submit"]:
        if phrase not in gateway_text:
            errors.append(f"record-chain intake gateway contract missing {phrase!r}")

    builder_text = json.dumps(builder, sort_keys=True)
    if "/downloads/record-chain-builder.mjs" not in builder_text:
        errors.append("builder bundle contract missing canonical builder download")

    output_text = json.dumps(output_policy, sort_keys=True)
    first_contact_text = json.dumps(first_contact, sort_keys=True)
    task_router_text = json.dumps(task_router, sort_keys=True)
    for phrase in ["post_submit_readback", "readback", "receipt"]:
        if phrase not in output_text and phrase not in first_contact_text and phrase not in task_router_text:
            errors.append(f"{route_family}: missing journey phrase {phrase!r} in current output/route contracts")

    return AgentResult(agent_id, route_family, not errors, errors, digests, sorted(set(ip_candidates)))


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
                futures.append(pool.submit(validate_agent, global_agent_id, route_family, args.site, args.timeout, cache_token))

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
        for err in result.errors:
            print(f"  - {err}")

    if failures:
        return 1
    print("PASS: external multi-agent full journey swarm smoke passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
