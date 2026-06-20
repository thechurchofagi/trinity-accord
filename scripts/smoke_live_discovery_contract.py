#!/usr/bin/env python3
"""Smoke-test live public discovery surfaces after Pages deployment.

This is an external live smoke. It should be run manually or on schedule,
not as a normal PR/P0 source-only check.

It verifies that the public site exposes the current full agent journey:
discovery -> first-contact -> workflow manual/API -> submit gateway ->
builder route map -> output/readback policy.

v19: adds cache/edge diagnostics — fetches both canonical and cache-busted
live JSON, prints HTTP cache headers, detects CDN/edge inconsistency.
"""
from __future__ import annotations

import argparse
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

REQUIRED_LINKS_MACHINE = {
    "/api/agent-minimal-context.v1.json",
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/api/agent-start.v2.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/context-load-map.json",
    "/api/public-home-status.json",
    "/api/echo-index.json",
    "/api/agent-declared-verification-index.json",
}

REQUIRED_LINKS_PAGES = {
    "/agent-start",
    "/agent-echo",
    "/guardian-alliance",
}

REQUIRED_WELL_KNOWN_API = {
    "agent_minimal_context": "/api/agent-minimal-context.v1.json",
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
    "agent_output_policy": "/api/agent-output-policy.v1.json",
    "agent_task_router": "/api/agent-task-router.v1.json",
}

REQUIRED_WELL_KNOWN_ALIASES = {
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
}


def fetch_json_with_headers(url: str, timeout: int) -> tuple[Any, dict[str, str]]:
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
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return json.loads(body), headers
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} from {url}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch {url}: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from {url}: {e}") from e


def fetch_json(url: str, timeout: int) -> Any:
    data, _headers = fetch_json_with_headers(url, timeout)
    return data


def fetch_text(url: str, timeout: int) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "trinity-accord-live-discovery-smoke/1.0",
            "Accept": "text/plain,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", None)
            if status and status >= 400:
                raise RuntimeError(f"HTTP {status} from {url}")
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} from {url}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch {url}: {e.reason}") from e


def with_cache_bust(url: str, token: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("cb", token))
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib.parse.urlencode(query),
            parsed.fragment,
        )
    )


def print_cache_headers(label: str, headers: dict[str, str]) -> None:
    interesting = [
        "cache-control",
        "etag",
        "last-modified",
        "age",
        "x-cache",
        "via",
        "server",
        "cf-cache-status",
    ]
    print(f"{label} response cache headers:")
    for key in interesting:
        if key in headers:
            print(f"  {key}: {headers[key]}")


def local_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def norm(path: str) -> str:
    if path != "/" and path.endswith("/"):
        return path[:-1]
    return path


def validate_links_contract(label: str, links: dict[str, Any], errors: list[str]) -> None:
    machine = set(links.get("machine", []))
    key_pages = set(links.get("key_pages", []))
    key_pages_norm = {norm(p) for p in key_pages}

    missing_machine = sorted(REQUIRED_LINKS_MACHINE - machine)
    if missing_machine:
        errors.append(f"{label} links.json machine missing: {missing_machine}")

    missing_pages = sorted(
        p for p in REQUIRED_LINKS_PAGES
        if p not in key_pages and norm(p) not in key_pages_norm
    )
    if missing_pages:
        errors.append(f"{label} links.json key_pages missing: {missing_pages}")



def validate_links_legacy_contract(label: str, links: dict[str, Any], errors: list[str]) -> None:
    """Ensure guardian-registry is in legacy_machine/deprecated, not in machine."""
    machine = set(links.get("machine", []))
    legacy = set(links.get("legacy_machine", []))
    deprecated = set(links.get("deprecated_for_new_records", []))

    if "/api/guardian-registry.json" in machine:
        errors.append(f"{label} links.json machine still contains legacy item: /api/guardian-registry.json")
    if "/api/guardian-registry.json" not in legacy:
        errors.append(f"{label} links.json legacy_machine missing: /api/guardian-registry.json")
    if "/api/guardian-registry.json" not in deprecated:
        errors.append(f"{label} links.json deprecated_for_new_records missing: /api/guardian-registry.json")


def validate_well_known_contract(label: str, well_known: dict[str, Any], errors: list[str]) -> None:
    wk_api = well_known.get("api", {})
    for key, expected in REQUIRED_WELL_KNOWN_API.items():
        if wk_api.get(key) != expected:
            errors.append(
                f"{label} well-known api.{key} expected {expected!r}, got {wk_api.get(key)!r}"
            )

    for key, expected in REQUIRED_WELL_KNOWN_ALIASES.items():
        if well_known.get(key) != expected:
            errors.append(
                f"{label} well-known top-level {key} expected {expected!r}, got {well_known.get(key)!r}"
            )

    entrypoints = well_known.get("agent_entrypoints", {})
    for key in [
        "agent_first_contact",
        "agent_required_reading",
    ]:
        if key not in entrypoints:
            errors.append(f"{label} well-known agent_entrypoints missing {key}")



def validate_builder_contract(label: str, site: str, timeout: int, errors: list[str]) -> None:
    """Verify live canonical builder matches API contract."""
    contract_url = f"{site}/api/record-chain-builder-bundles.v1.json"
    try:
        contract = fetch_json(contract_url, timeout)
    except RuntimeError as e:
        errors.append(f"{label} builder contract fetch failed: {e}")
        return

    builder = contract.get("canonical_builder", {})
    canonical_url = builder.get("url")
    if not canonical_url:
        errors.append(f"{label} builder contract missing canonical_builder.url")
        return

    if canonical_url != "/downloads/record-chain-builder.mjs":
        errors.append(f"{label} unexpected canonical builder URL: {canonical_url!r}")
        return

    expected_sha = builder.get("sha256")
    expected_size = builder.get("size_bytes")

    # Fetch canonical builder
    full_url = f"{site}{canonical_url}"
    try:
        req = urllib.request.Request(
            full_url,
            headers={"User-Agent": "trinity-accord-live-discovery-smoke/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        errors.append(f"{label} canonical builder fetch failed: {e}")
        return

    actual_sha = hashlib.sha256(body).hexdigest()
    actual_size = len(body)

    if expected_sha and actual_sha != expected_sha:
        errors.append(
            f"{label} canonical builder SHA-256 mismatch: "
            f"expected={expected_sha!r}, actual={actual_sha!r}"
        )
    if expected_size and actual_size != expected_size:
        errors.append(
            f"{label} canonical builder size mismatch: "
            f"expected={expected_size}, actual={actual_size}"
        )

    # Optionally verify mirror
    mirror_url = f"{site}/builder-bundles/record-chain-builder.mjs"
    try:
        req2 = urllib.request.Request(
            mirror_url,
            headers={"User-Agent": "trinity-accord-live-discovery-smoke/1.0"},
        )
        with urllib.request.urlopen(req2, timeout=timeout) as resp2:
            mirror_body = resp2.read()
        if mirror_body != body:
            errors.append(f"{label} builder mirror differs from canonical")
    except (urllib.error.HTTPError, urllib.error.URLError):
        pass  # mirror is optional


def validate_live_agent_entrypoints(
    first_contact: dict[str, Any],
    agent_start: dict[str, Any],
    field_helper: dict[str, Any],
    task_router: dict[str, Any],
    quickstart: dict[str, Any],
    llms_text: str,
    ai_text: str,
    errors: list[str],
) -> None:
    submit_action = None
    for item in first_contact.get("choose_one", []):
        if isinstance(item, dict) and item.get("intent") == "submit_record":
            submit_action = item
            break

    if not isinstance(submit_action, dict):
        errors.append("live first-contact missing submit_record action")
        return

    if "classification_update" not in submit_action.get("supported_record_types", []):
        errors.append("live first-contact supported_record_types missing classification_update")

    zc = first_contact.get("zero_clone_formal_builder_policy", {})
    if "classification_update" not in zc.get("supported_zero_clone_routes", []):
        errors.append("live first-contact zero_clone routes missing classification_update")

    observation = first_contact.get("post_submit_observation_protocol", {})
    record_indexes = observation.get("record_specific_indexes", {})
    if record_indexes.get("guardian_application") != "/record-chain/indexes/guardian-state.json":
        errors.append("live first-contact guardian_application index is not guardian-state")

    claim = observation.get("claim_discipline", {})
    if claim.get("guardian_active_status_requires_record_chain_guardian_state_readback") is not True:
        errors.append("live first-contact must require record-chain guardian-state readback")
    if claim.get("guardian_active_status_requires_registry_readback") is not False:
        errors.append("live first-contact must not require legacy registry readback for active Guardian status")

    commands = agent_start.get("builder_usage_safety_protocol", {}).get("record_type_commands", {})
    supported = set(submit_action.get("supported_record_types", []))
    missing_commands = sorted(supported - set(commands))
    if missing_commands:
        errors.append(f"live agent-start record_type_commands missing supported record types: {missing_commands}")

    # Guardian command flag checks
    guardian_application_cmd = commands.get("guardian_application", {}).get("build_command", "")
    for required in ["--guardian-id", "--guardian-key-sha"]:
        if required not in guardian_application_cmd:
            errors.append(f"live guardian_application build_command missing {required}")
    # --oath is now a legacy alias; Builder uses canonical default when omitted
    for forbidden in [
        "--requested-guardian-identifier",
        "--guardian-public-key-sha256",
        "--guardian-application-statement",
    ]:
        if forbidden in guardian_application_cmd:
            errors.append(f"live guardian_application build_command uses unsupported flag {forbidden}")

    guardian_retirement_cmd = commands.get("guardian_retirement", {}).get("build_command", "")
    for required in ["--guardian-id", "--guardian-key-sha", "--body"]:
        if required not in guardian_retirement_cmd:
            errors.append(f"live guardian_retirement build_command missing {required}")
    for forbidden in ["--guardian-public-key-sha256", "--reason"]:
        if forbidden in guardian_retirement_cmd:
            errors.append(f"live guardian_retirement build_command uses unsupported flag {forbidden}")

    if field_helper.get("current_public_phase") != "production_live":
        errors.append("live field helper current_public_phase is not production_live")

    for code in [
        "AUTHORSHIP_CLAIM_BOUNDARY_INVALID",
        "CLIENT_SUPPLIED_UNSIGNED_PROJECTION_FIELD",
        "MISSING_CLASSIFICATION_UPDATE_CONTENT",
        "INVALID_CLASSIFICATION_TARGET_SHA",
    ]:
        if code not in field_helper.get("diagnostic_code_help", {}):
            errors.append(f"live field helper missing diagnostic help for {code}")

    for label, text in [("llms.txt", llms_text), ("ai.txt", ai_text)]:
        if "/record-chain/indexes/guardian-state.json" not in text:
            errors.append(f"live {label} missing current guardian-state source")
        if "Guardian application → `/api/guardian-registry.json`" in text:
            errors.append(f"live {label} presents legacy registry as active Guardian application index")

    # Task-router guardian route checks
    guardian_route = task_router.get("routes", {}).get("guardian_alliance", {})
    if guardian_route.get("active_guardian_status_requires_record_chain_guardian_state_readback") is not True:
        errors.append("live task-router guardian_alliance must require guardian-state readback")
    if guardian_route.get("legacy_guardian_registry_is_historical_archive_only") is not True:
        errors.append("live task-router guardian_alliance must mark legacy registry historical-only")
    if "/api/guardian-registry.json" in guardian_route.get("post_submit_readback", []):
        errors.append("live task-router guardian_alliance uses legacy registry as active post-submit readback")

    # External-agent-quickstart checks
    if quickstart.get("default_safe_mode", {}).get("submission_type") != "record_chain_entry_candidate":
        errors.append("live external-agent-quickstart default_safe_mode is not record_chain_entry_candidate")
    if "verification_report_candidate" in json.dumps(quickstart, sort_keys=True):
        errors.append("live external-agent-quickstart still contains verification_report_candidate")


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

    # DNS resolution for vantage diagnostics
    hostname = site.split("://")[-1].split("/")[0].split(":")[0]
    try:
        resolved_ip = socket.gethostbyname(hostname)
        print(f"Resolved {hostname} -> {resolved_ip}")
    except socket.gaierror as e:
        print(f"DNS resolution failed for {hostname}: {e}")
        resolved_ip = "unknown"

    links_url = f"{site}/api/links.json"
    well_known_url = f"{site}/.well-known/trinity-accord.json"

    repo_links_for_token = local_json("api/links.json")
    cache_token = str(repo_links_for_token.get("source_digest") or int(time.time()))

    links_busted_url = with_cache_bust(links_url, cache_token)
    well_known_busted_url = with_cache_bust(well_known_url, cache_token)

    print(f"Fetching live links: {links_url}")
    live_links, links_headers = fetch_json_with_headers(links_url, args.timeout)
    print_cache_headers("canonical links.json", links_headers)

    print(f"Fetching cache-busted live links: {links_busted_url}")
    live_links_busted, links_busted_headers = fetch_json_with_headers(links_busted_url, args.timeout)
    print_cache_headers("cache-busted links.json", links_busted_headers)

    print(f"Fetching live well-known: {well_known_url}")
    live_well_known, wk_headers = fetch_json_with_headers(well_known_url, args.timeout)
    print_cache_headers("canonical well-known", wk_headers)

    print(f"Fetching cache-busted live well-known: {well_known_busted_url}")
    live_well_known_busted, wk_busted_headers = fetch_json_with_headers(well_known_busted_url, args.timeout)
    print_cache_headers("cache-busted well-known", wk_busted_headers)

    # Print diagnostics
    print(f"Live canonical links source_digest: {live_links.get('source_digest')!r}")
    print(f"Live cache-busted links source_digest: {live_links_busted.get('source_digest')!r}")
    print(f"Repo links source_digest: {repo_links_for_token.get('source_digest')!r}")
    print(f"Live links version: {live_links.get('version')!r}")
    print(f"Live well-known site: {live_well_known.get('site')!r}")

    # Compare canonical vs cache-busted
    if live_links.get("source_digest") != live_links_busted.get("source_digest"):
        errors.append(
            "canonical and cache-busted live links.json source_digest differ: "
            f"canonical={live_links.get('source_digest')!r}, "
            f"cache_busted={live_links_busted.get('source_digest')!r}; "
            "this indicates CDN/edge/cache inconsistency"
        )

    # Validate both canonical and cache-busted
    validate_links_contract("canonical", live_links, errors)
    validate_links_contract("cache-busted", live_links_busted, errors)
    validate_links_legacy_contract("canonical", live_links, errors)
    validate_links_legacy_contract("cache-busted", live_links_busted, errors)
    validate_well_known_contract("canonical", live_well_known, errors)
    validate_well_known_contract("cache-busted", live_well_known_busted, errors)

    if args.strict_digest:
        repo_digest = repo_links_for_token.get("source_digest")
        for label, links in [
            ("canonical", live_links),
            ("cache-busted", live_links_busted),
        ]:
            live_digest = links.get("source_digest")
            if live_digest != repo_digest:
                errors.append(
                    f"{label} live links.json source_digest mismatch: "
                    f"live={live_digest!r}, repo={repo_digest!r}; "
                    "this usually means Pages/CDN/custom-domain is serving an older artifact"
                )

    # Verify builder contract
    validate_builder_contract("canonical", site, args.timeout, errors)

    # Fetch and validate live active entrypoints
    print(f"Fetching live agent entrypoints...")
    try:
        first_contact = fetch_json(f"{site}/api/agent-first-contact.json", args.timeout)
        agent_start = fetch_json(f"{site}/api/agent-start.v2.json", args.timeout)
        field_helper = fetch_json(f"{site}/api/record-chain-field-helper.v1.json", args.timeout)
        task_router = fetch_json(f"{site}/api/agent-task-router.v1.json", args.timeout)
        quickstart = fetch_json(f"{site}/api/external-agent-quickstart.json", args.timeout)
        llms_text = fetch_text(f"{site}/llms.txt", args.timeout)
        ai_text = fetch_text(f"{site}/ai.txt", args.timeout)

        validate_live_agent_entrypoints(
            first_contact,
            agent_start,
            field_helper,
            task_router,
            quickstart,
            llms_text,
            ai_text,
            errors,
        )
    except RuntimeError as e:
        errors.append(f"live agent entrypoint fetch failed: {e}")

    if errors:
        print("FAIL: live discovery contract errors:")
        for e in errors:
            print("  -", e)
        return 1

    print("PASS: live public discovery exposes full agent journey contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
