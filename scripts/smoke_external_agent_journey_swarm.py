#!/usr/bin/env python3
"""Read-only external multi-agent first-contact journey smoke.

The smoke validates the currently published agent router and Record-Chain intake
journey. It deliberately follows only current public intents; historical V0-V5,
E2, V6+ and ``pure_echo`` labels are not treated as active routes.

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

# These families mirror api/agent-first-contact.json. Keep them semantic rather
# than version-taxonomy based so retired labels cannot silently return as current.
ROUTE_FAMILIES: dict[str, dict[str, Any]] = {
    "understand": {
        "intent": "understand",
        "required_reads": {
            "/agent-brief",
            "/agent-start",
            "/api/record-chain-status.json",
        },
        "required_flow_phrases": set(),
    },
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
    "echo": {
        "intent": "echo",
        "required_reads": {
            "/agent-echo",
            "/api/context-action-profiles.v1.json",
            "/api/record-chain-submission-schema.v1.json",
            "/api/record-chain-intake-gateway.v1.json",
            "/downloads/record-chain-builder.mjs",
        },
        "required_flow_phrases": set(),
    },
    "verify_current_model": {
        "intent": "verify_current_model",
        "required_reads": {
            "/agent-verify",
            "/api/verification-procedures.v1.json",
            "/api/verification-profiles.v1.json",
            "/api/verification-claim-model.v1.json",
            "/api/evidence-relationship-map.v1.json",
            "/api/record-chain-intake-gateway.v1.json",
        },
        "required_flow_phrases": set(),
    },
    "strict_evidence": {
        "intent": "physical_or_strict_evidence_verification",
        "required_reads": {
            "/agent-verify",
            "/verification-procedures",
            "/api/verification-procedures.v1.json",
            "/api/verification-profiles.v1.json",
            "/api/verification-claim-model.v1.json",
            "/api/evidence-relationship-map.v1.json",
            "/api/evidence-input-schema.v1.json",
            "/api/claim-gate-rules.json",
        },
        "required_flow_phrases": set(),
    },
}

RETIRED_ROUTE_INTENTS = {
    "verify_v0_v5_agent_declared",
    "verification_echo_e2",
    "verify_v6_plus_strict_evidence",
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


def normalize_route_path(value: str) -> str:
    """Normalize equivalent public route spellings for contract comparison."""
    if value == "/":
        return value
    return value.rstrip("/")


def normalized_path_set(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {
        normalize_route_path(value)
        for value in values
        if isinstance(value, str) and value.startswith("/")
    }


def result_object(
    fetched: dict[tuple[str, bool], FetchResult],
    path: str,
    cache_bust: bool,
    errors: list[str],
) -> dict[str, Any]:
    result = fetched.get((path, cache_bust))
    label = f"{path}{' cache-busted' if cache_bust else ' canonical'}"
    if result is None:
        errors.append(f"{label}: internal fetch result missing")
        return {}
    if result.error or result.status == 0 or result.status >= 400:
        return {}
    if not isinstance(result.data, dict):
        errors.append(f"{label}: JSON root must be an object")
        return {}
    return result.data


def canonical_cache_split_errors(
    fetched: dict[tuple[str, bool], FetchResult],
) -> list[str]:
    errors: list[str] = []
    for path in CORE_DISCOVERY_PATHS:
        canonical = fetched.get((path, False))
        busted = fetched.get((path, True))
        if canonical is None or busted is None:
            continue
        if canonical.error or busted.error:
            continue
        if canonical.status == 0 or busted.status == 0:
            continue
        if canonical.status >= 400 or busted.status >= 400:
            continue
        if canonical.digest != busted.digest:
            errors.append(
                f"{path} canonical/cache-busted content split: "
                f"{canonical.digest!r} vs {busted.digest!r}"
            )
    return errors


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


def fetch_json(
    site: str,
    path: str,
    agent_id: int,
    cache_token: str,
    timeout: int,
    cache_bust: bool,
) -> FetchResult:
    url = url_for(site, path, cache_token, agent_id, cache_bust)
    hostname = urllib.parse.urlsplit(site).hostname or "www.trinityaccord.org"
    ips = resolve_ips(hostname)
    headers = {
        "User-Agent": f"TrinityExternalAgentSwarm/3.0 agent={agent_id:02d}",
        "Accept": "application/json,*/*",
        "Cache-Control": "no-cache, no-store, max-age=0",
        "Pragma": "no-cache",
    }
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            status = int(getattr(resp, "status", 200))
            data = json.loads(body.decode("utf-8"))
            digest = hashlib.sha256(body).hexdigest()[:16]
            resp_headers = {key.lower(): value for key, value in resp.headers.items()}
            return FetchResult(path, url, status, digest, data, resp_headers, ips)
    except Exception as exc:
        return FetchResult(path, url, 0, "", None, {}, ips, error=str(exc))


def get_route(first_contact: dict[str, Any], intent: str) -> dict[str, Any] | None:
    for route in first_contact.get("choose_one", []):
        if isinstance(route, dict) and route.get("intent") == intent:
            return route
    return None


def route_contract_errors(
    first_contact: dict[str, Any],
    route_family: str,
) -> list[str]:
    family = ROUTE_FAMILIES[route_family]
    route = get_route(first_contact, family["intent"])
    if not route:
        return [f"first-contact missing current intent {family['intent']}"]

    errors: list[str] = []
    reads = normalized_path_set(route.get("read", []))
    required_reads = {
        normalize_route_path(value)
        for value in family["required_reads"]
    }
    missing_reads = sorted(required_reads - reads)
    if missing_reads:
        errors.append(f"{route_family}: route read list missing {missing_reads}")

    flow_text = json.dumps(route.get("flow", []), sort_keys=True)
    for phrase in sorted(family["required_flow_phrases"]):
        if phrase not in flow_text:
            errors.append(f"{route_family}: route flow missing {phrase!r}")
    return errors


def validate_agent(
    agent_id: int,
    route_family: str,
    site: str,
    timeout: int,
    cache_token: str,
) -> AgentResult:
    errors: list[str] = []
    digests: dict[str, str] = {}
    ip_candidates: list[str] = []

    fetched: dict[tuple[str, bool], FetchResult] = {}
    for path in CORE_DISCOVERY_PATHS:
        for cache_bust in (False, True):
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

    errors.extend(canonical_cache_split_errors(fetched))
    links = result_object(fetched, "/api/links.json", False, errors)
    links_busted = result_object(fetched, "/api/links.json", True, errors)
    well_known = result_object(fetched, "/.well-known/trinity-accord.json", False, errors)
    first_contact = result_object(fetched, "/api/agent-first-contact.json", False, errors)
    task_router = result_object(fetched, "/api/agent-task-router.v1.json", False, errors)
    output_policy = result_object(fetched, "/api/agent-output-policy.v1.json", False, errors)
    agent_start = result_object(fetched, "/api/agent-start.v2.json", False, errors)
    gateway = result_object(fetched, "/api/record-chain-intake-gateway.v1.json", False, errors)
    builder = result_object(fetched, "/api/record-chain-builder-bundles.v1.json", False, errors)

    repo_digest = repo_links_digest()
    if repo_digest:
        for label, obj in (("canonical", links), ("cache-busted", links_busted)):
            if obj.get("source_digest") != repo_digest:
                errors.append(
                    f"links.json {label} source_digest mismatch: "
                    f"live={obj.get('source_digest')!r}, repo={repo_digest!r}"
                )

    if links.get("source_digest") != links_busted.get("source_digest"):
        errors.append(
            "links.json canonical/cache-busted digest split: "
            f"{links.get('source_digest')!r} vs {links_busted.get('source_digest')!r}"
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
    for key in ("agent_first_contact", "agent_output_policy", "agent_task_router"):
        if key not in wk_api and key not in well_known:
            errors.append(f"well-known missing current key {key}")

    current_public_submission = well_known.get("current_public_submission")
    if not isinstance(current_public_submission, dict):
        errors.append("well-known missing current_public_submission")
    else:
        submission_text = json.dumps(current_public_submission, sort_keys=True)
        for required in (
            "/downloads/record-chain-builder.mjs",
            "/api/record-chain-intake-gateway.v1.json",
            "/api/record-chain-submission-schema.v1.json",
        ):
            if required not in submission_text:
                errors.append(f"well-known current_public_submission missing {required}")

    errors.extend(route_contract_errors(first_contact, route_family))

    current_submission_text = json.dumps(
        first_contact.get("current_public_submission_method", {}), sort_keys=True
    )
    for phrase in (
        "Record-Chain Intake Gateway",
        "/record-chain/preflight",
        "/record-chain/submit",
        "/downloads/record-chain-builder.mjs",
    ):
        if phrase not in current_submission_text:
            errors.append(f"first-contact current_public_submission_method missing {phrase!r}")

    protocol_text = json.dumps(agent_start.get("builder_usage_safety_protocol", {}), sort_keys=True)
    for phrase in (
        "BUILDER_USAGE_UNCLEAR",
        "doctor_submission",
        "preflight_submission",
        "submit_submission",
    ):
        if phrase not in protocol_text:
            errors.append(f"agent-start builder_usage_safety_protocol missing {phrase!r}")

    gateway_text = json.dumps(gateway, sort_keys=True)
    for phrase in ("/record-chain/preflight", "/record-chain/submit"):
        if phrase not in gateway_text:
            errors.append(f"record-chain intake gateway contract missing {phrase!r}")

    builder_text = json.dumps(builder, sort_keys=True)
    if "/downloads/record-chain-builder.mjs" not in builder_text:
        errors.append("builder bundle contract missing canonical builder download")

    output_text = json.dumps(output_policy, sort_keys=True)
    first_contact_text = json.dumps(first_contact, sort_keys=True)
    task_router_text = json.dumps(task_router, sort_keys=True)
    for phrase in ("post_submit_readback", "readback", "receipt"):
        if (
            phrase not in output_text
            and phrase not in first_contact_text
            and phrase not in task_router_text
        ):
            errors.append(
                f"{route_family}: missing journey phrase {phrase!r} "
                "in current output/route contracts"
            )

    return AgentResult(
        agent_id,
        route_family,
        not errors,
        errors,
        digests,
        sorted(set(ip_candidates)),
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
    cache_token = f"{repo_links_digest() or 'no-digest'}-{time.time_ns()}"

    all_results: list[AgentResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures: dict[concurrent.futures.Future[AgentResult], tuple[int, str]] = {}
        for round_id in range(args.rounds):
            for agent_id in range(args.agents):
                route_family = route_names[agent_id % len(route_names)]
                global_agent_id = round_id * args.agents + agent_id
                future = pool.submit(
                    validate_agent,
                    global_agent_id,
                    route_family,
                    args.site,
                    args.timeout,
                    cache_token,
                )
                futures[future] = (global_agent_id, route_family)

        for future in concurrent.futures.as_completed(futures):
            global_agent_id, route_family = futures[future]
            try:
                all_results.append(future.result())
            except Exception as exc:
                all_results.append(AgentResult(
                    global_agent_id,
                    route_family,
                    False,
                    [f"unhandled validator exception: {type(exc).__name__}: {exc}"],
                    {},
                    [],
                ))

    all_results.sort(key=lambda item: item.agent_id)
    failures = [result for result in all_results if not result.ok]
    print(f"External agent swarm results: {len(all_results) - len(failures)}/{len(all_results)} passed")

    seen_ips = sorted({ip for result in all_results for ip in result.ip_candidates})
    print("Resolved IP candidates:", ", ".join(seen_ips) if seen_ips else "(none)")

    for result in all_results:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status}: agent={result.agent_id:02d} route={result.route_family}")
        for error in result.errors:
            print(f"  - {error}")

    if failures:
        return 1
    print("PASS: external multi-agent full journey swarm smoke passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
