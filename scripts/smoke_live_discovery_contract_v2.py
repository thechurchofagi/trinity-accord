#!/usr/bin/env python3
"""Cache-safe live smoke for the current public machine contract."""
from __future__ import annotations

import argparse
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from public_machine_deployment_contract import (
    CURRENT_RECORD_TYPES,
    RETIRED_ROUTE_INTENTS,
    SMOKE_JSON_SURFACES,
    SMOKE_TEXT_SURFACES,
    json_object_from_bytes,
    repo_bytes,
    sha256,
    validate_embedded_source_digest,
    validate_links_semantics,
    validate_well_known_semantics,
)

DEFAULT_SITE = "https://www.trinityaccord.org"
CURRENT_INTENTS = {
    "stop",
    "understand",
    "submit_record",
    "echo",
    "verify_current_model",
    "physical_or_strict_evidence_verification",
}
FORBIDDEN_GUIDANCE = (
    "/agent-submit",
    "/gateway/preflight",
    "/api/agent-start.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/gateway-workflows.v1.json",
)


def busted(url: str, token: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("cb", token))
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment)
    )


def fetch(url: str, timeout: int) -> tuple[bytes, dict[str, str]]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "trinity-accord-live-discovery-smoke/2.0",
            "Accept": "application/json,text/plain,*/*",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), {k.lower(): v for k, v in response.headers.items()}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} from {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc.reason}") from exc


def fetch_pair(site: str, path: str, token: str, timeout: int) -> tuple[bytes, bytes]:
    url = site.rstrip("/") + path
    canonical, canonical_headers = fetch(url, timeout)
    cache_busted, busted_headers = fetch(busted(url, token), timeout)
    for label, headers in (("canonical", canonical_headers), ("cache-busted", busted_headers)):
        diagnostics = ", ".join(
            f"{key}={headers[key]}"
            for key in ("cache-control", "etag", "last-modified", "age", "x-cache", "via")
            if key in headers
        )
        print(f"{label} {path} cache: {diagnostics or 'no diagnostic headers'}")
    return canonical, cache_busted


def compare_pair(
    path: str,
    canonical: bytes,
    cache_busted: bytes,
    strict: bool,
    errors: list[str],
) -> None:
    canonical_sha = sha256(canonical)
    busted_sha = sha256(cache_busted)
    print(f"{path}: canonical={canonical_sha} cache_busted={busted_sha}")
    if canonical != cache_busted:
        errors.append(
            f"{path} canonical/cache-busted mismatch: {canonical_sha} != {busted_sha}"
        )
    if strict:
        expected = repo_bytes(path)
        expected_sha = sha256(expected)
        if canonical != expected:
            errors.append(f"{path} canonical differs from repo: {canonical_sha} != {expected_sha}")
        if cache_busted != expected:
            errors.append(f"{path} cache-busted differs from repo: {busted_sha} != {expected_sha}")


def validate_entrypoints(
    objects: dict[str, dict[str, Any]], texts: dict[str, str], errors: list[str]
) -> None:
    first = objects.get("/api/agent-first-contact.json", {})
    start = objects.get("/api/agent-start.v2.json", {})
    required = objects.get("/api/agent-required-reading.json", {})
    task = objects.get("/api/agent-task-router.v1.json", {})
    quick = objects.get("/api/external-agent-quickstart.json", {})
    gateway = objects.get("/api/record-chain-intake-gateway.v1.json", {})
    guidance = objects.get("/downloads/record-chain-agent-field-guidance.v1.json", {})

    intents = {
        str(item.get("intent"))
        for item in first.get("choose_one", [])
        if isinstance(item, dict) and item.get("intent")
    }
    missing = sorted(CURRENT_INTENTS - intents)
    if missing:
        errors.append(f"first-contact missing current intents: {missing}")
    retired = sorted(intents & RETIRED_ROUTE_INTENTS)
    if retired:
        errors.append(f"first-contact exposes retired intents: {retired}")

    submit = next(
        (
            item
            for item in first.get("choose_one", [])
            if isinstance(item, dict) and item.get("intent") == "submit_record"
        ),
        {},
    )
    if tuple(submit.get("supported_record_types", [])) != CURRENT_RECORD_TYPES:
        errors.append("first-contact submit_record types drifted")
    if tuple(first.get("runtime_alignment", {}).get("accepted_record_types", [])) != CURRENT_RECORD_TYPES:
        errors.append("first-contact runtime record types drifted")
    indexes = first.get("post_submit_observation_protocol", {}).get("record_specific_indexes", {})
    if set(indexes) != set(CURRENT_RECORD_TYPES):
        errors.append("first-contact indexes do not cover all record types")

    if tuple(start.get("runtime_alignment", {}).get("accepted_record_types", [])) != CURRENT_RECORD_TYPES:
        errors.append("agent-start runtime record types drifted")
    commands = start.get("builder_usage_safety_protocol", {}).get("record_type_commands", {})
    if set(commands) != set(CURRENT_RECORD_TYPES):
        errors.append("agent-start Builder commands do not cover all record types")

    if required.get("canonical_router") != "/api/agent-first-contact.json":
        errors.append("required-reading canonical router drifted")
    if required.get("does_not_override_router") is not True:
        errors.append("required-reading is not explicitly subordinate")
    if task.get("canonical_router") != "/api/agent-first-contact.json":
        errors.append("task-router canonical router drifted")
    task_dump = json.dumps(task, sort_keys=True)
    for intent in RETIRED_ROUTE_INTENTS:
        if intent in task_dump:
            errors.append(f"task-router contains retired intent {intent}")

    safe = quick.get("default_safe_mode", {})
    if safe.get("submission_type") != "record_chain_entry_candidate":
        errors.append("external quickstart safe submission type drifted")
    if safe.get("preflight_required") is not True:
        errors.append("external quickstart no longer requires preflight")
    if tuple(quick.get("accepted_record_types", [])) != CURRENT_RECORD_TYPES:
        errors.append("external quickstart record types drifted")

    if tuple(gateway.get("runtime_alignment", {}).get("accepted_record_types", [])) != CURRENT_RECORD_TYPES:
        errors.append("Gateway contract record types drifted")
    expected_endpoints = {
        "health": "/healthz",
        "readiness": "/record-chain/readiness",
        "preflight": "/record-chain/preflight",
        "submit": "/record-chain/submit",
        "receipt": "/record-chain/receipt/{receipt_id}",
    }
    for name, expected in expected_endpoints.items():
        if gateway.get("endpoints", {}).get(name, {}).get("path") != expected:
            errors.append(f"Gateway endpoint {name} drifted")

    if tuple(guidance.get("runtime_alignment", {}).get("accepted_record_types", [])) != CURRENT_RECORD_TYPES:
        errors.append("field guidance record types drifted")

    for path, text in texts.items():
        if "/api/agent-first-contact.json" not in text:
            errors.append(f"{path} missing canonical router")
        for forbidden in FORBIDDEN_GUIDANCE:
            if forbidden in text:
                errors.append(f"{path} contains retired active route {forbidden}")


def validate_builder(
    site: str,
    token: str,
    timeout: int,
    strict: bool,
    manifest: dict[str, Any],
    errors: list[str],
) -> None:
    builder = manifest.get("canonical_builder", {})
    path = builder.get("url")
    if path != "/downloads/record-chain-builder.mjs":
        errors.append(f"unexpected Builder URL: {path!r}")
        return
    try:
        canonical, cache_busted = fetch_pair(site, path, token, timeout)
        compare_pair(path, canonical, cache_busted, strict, errors)
        mirror, mirror_busted = fetch_pair(
            site, "/builder-bundles/record-chain-builder.mjs", token, timeout
        )
    except RuntimeError as exc:
        errors.append(str(exc))
        return
    for label, data in (("canonical", canonical), ("cache-busted", cache_busted)):
        if builder.get("sha256") != sha256(data):
            errors.append(f"{label} Builder SHA-256 does not match manifest")
        if builder.get("size_bytes") != len(data):
            errors.append(f"{label} Builder size does not match manifest")
    if mirror != canonical or mirror_busted != canonical:
        errors.append("Builder mirror differs from canonical Builder")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--strict-digest", action="store_true")
    args = parser.parse_args()

    site = args.site.rstrip("/")
    hostname = urllib.parse.urlsplit(site).hostname or site
    try:
        print(f"Resolved {hostname} -> {socket.gethostbyname(hostname)}")
    except socket.gaierror as exc:
        print(f"DNS resolution failed for {hostname}: {exc}")

    repo_links = json_object_from_bytes(repo_bytes("/api/links.json"), "repository links")
    token = f"{repo_links.get('source_digest', 'none')}-{time.time_ns()}"
    errors: list[str] = []
    objects: dict[str, dict[str, Any]] = {}
    texts: dict[str, str] = {}

    for path in SMOKE_JSON_SURFACES:
        try:
            canonical, cache_busted = fetch_pair(site, path, token, args.timeout)
            compare_pair(path, canonical, cache_busted, args.strict_digest, errors)
            current = json_object_from_bytes(canonical, f"live {path}")
            cache_current = json_object_from_bytes(cache_busted, f"cache-busted live {path}")
            validate_embedded_source_digest(f"live {path}", current, errors)
            validate_embedded_source_digest(f"cache-busted live {path}", cache_current, errors)
            objects[path] = current
        except (RuntimeError, ValueError) as exc:
            errors.append(str(exc))

    for path in SMOKE_TEXT_SURFACES:
        try:
            canonical, cache_busted = fetch_pair(site, path, token, args.timeout)
            compare_pair(path, canonical, cache_busted, args.strict_digest, errors)
            texts[path] = canonical.decode("utf-8")
        except (RuntimeError, UnicodeDecodeError) as exc:
            errors.append(f"{path} fetch/decode failed: {exc}")

    if "/api/links.json" in objects:
        validate_links_semantics("live", objects["/api/links.json"], errors)
    if "/.well-known/trinity-accord.json" in objects:
        validate_well_known_semantics("live", objects["/.well-known/trinity-accord.json"], errors)
    validate_entrypoints(objects, texts, errors)

    manifest = objects.get("/api/record-chain-builder-bundles.v1.json")
    if manifest:
        validate_builder(site, token, args.timeout, args.strict_digest, manifest, errors)
    else:
        errors.append("Builder manifest unavailable")

    if errors:
        print("FAIL: live discovery contract errors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("PASS: live machine discovery, Builder, Gateway, and cache parity are current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
