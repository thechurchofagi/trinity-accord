#!/usr/bin/env python3
"""Shared current-machine contract for Pages build and live deployment checks.

This module is deliberately source-driven: current public discovery files are
validated against the repository copies that Pages publishes byte-for-byte.
Historical compatibility routes remain preserved, but may not re-enter active
machine discovery lists.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

CURRENT_RECORD_TYPES = (
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "propagation",
    "correction",
    "classification_update",
    "context_insufficient_notice",
)

CURRENT_CORE_MACHINE_PATHS = frozenset(
    {
        "/api/agent-minimal-context.v1.json",
        "/api/agent-first-contact.json",
        "/api/agent-start.v2.json",
        "/api/agent-output-policy.v1.json",
        "/api/agent-task-router.v1.json",
        "/api/agent-required-reading.json",
        "/api/context-action-profiles.v1.json",
        "/api/context-load-map.json",
        "/api/echo-types.json",
        "/api/verification-profiles.v1.json",
        "/api/evidence-relationship-map.v1.json",
        "/api/verification-claim-model.v1.json",
        "/api/verification-procedures.v1.json",
        "/api/record-chain-builder-bundles.v1.json",
        "/downloads/record-chain-builder.mjs",
        "/downloads/record-chain-agent-field-guidance.v1.json",
        "/api/record-chain-submission-schema.v1.json",
        "/api/record-chain-field-helper.v1.json",
        "/api/record-chain-oath-policy.v1.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/api/record-chain-preflight-response.v1.json",
        "/api/record-chain-submit-response.v1.json",
        "/api/record-chain-receipt-response.v1.json",
        "/api/record-chain-server-receipt.v1.json",
        "/api/record-chain-status.json",
        "/record-chain/indexes/echo-index.json",
        "/record-chain/indexes/verification-index.json",
        "/record-chain/indexes/guardian-state.json",
        "/record-chain/indexes/guardian_retirement-index.json",
        "/record-chain/indexes/propagation-index.json",
        "/record-chain/indexes/correction-index.json",
        "/record-chain/indexes/classification_update-index.json",
        "/record-chain/indexes/record-index.json",
    }
)

CURRENT_KEY_PAGES = frozenset(
    {
        "/agent-first-contact",
        "/agent-start",
        "/external-agent-quickstart",
        "/agent-echo",
        "/guardian-alliance",
    }
)

RETIRED_ACTIVE_PATHS = frozenset(
    {
        "/api/agent-entry-protocol.json",
        "/api/agent-start.v1.json",
        "/api/agent-submit-gateway.json",
        "/api/gateway-builder-route-map.v1.json",
        "/api/gateway-workflows.v1.json",
        "/api/route-selector.v1.json",
        "/api/gateway-runtime-contract.v1.json",
        "/api/gateway-error-diagnostics.v1.json",
        "/api/external-agent-operation-examples.v1.json",
        "/api/formal-builder-bundles.v1.json",
        "/api/guardian-registry.json",
        "/api/verification-levels.json",
        "/api/agent-declared-verification-index.json",
    }
)

RETIRED_ROUTE_INTENTS = frozenset(
    {
        "verify_v0_v5_agent_declared",
        "verification_echo_e2",
        "verify_v6_plus_strict_evidence",
    }
)

SMOKE_JSON_SURFACES = (
    "/api/links.json",
    "/.well-known/trinity-accord.json",
    "/api/agent-first-contact.json",
    "/api/agent-start.v2.json",
    "/api/agent-required-reading.json",
    "/api/agent-task-router.v1.json",
    "/api/external-agent-quickstart.json",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-builder-bundles.v1.json",
    "/downloads/record-chain-agent-field-guidance.v1.json",
)
SMOKE_TEXT_SURFACES = ("/llms.txt", "/ai.txt")

DEPLOYMENT_BYTE_SURFACES = (
    "/llms.txt",
    "/llms-full.txt",
    "/ai.txt",
    "/api/links.json",
    "/.well-known/trinity-accord.json",
    "/api/agent-minimal-context.v1.json",
    "/api/agent-first-contact.json",
    "/api/agent-start.v2.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/agent-required-reading.json",
    "/api/context-action-profiles.v1.json",
    "/api/context-load-map.json",
    "/api/echo-types.json",
    "/api/verification-profiles.v1.json",
    "/api/evidence-relationship-map.v1.json",
    "/api/verification-claim-model.v1.json",
    "/api/verification-procedures.v1.json",
    "/api/record-chain-builder-bundles.v1.json",
    "/downloads/record-chain-builder.mjs",
    "/downloads/record-chain-agent-field-guidance.v1.json",
    "/api/record-chain-submission-schema.v1.json",
    "/api/record-chain-field-helper.v1.json",
    "/api/record-chain-oath-policy.v1.json",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-preflight-response.v1.json",
    "/api/record-chain-submit-response.v1.json",
    "/api/record-chain-receipt-response.v1.json",
    "/api/record-chain-server-receipt.v1.json",
    "/api/public-home-status.json",
    "/api/record-chain-status.json",
    "/api/waiting-heartbeat-status.json",
    "/.well-known/pages-production-closure.v1.json",
    "/api/agent-live-health.v1.json",
    "/api/formal-builder-bundles.v1.json",
    "/builder-bundles/download_and_run_builder_bundle.py",
    "/builder-bundles/trinity-guardian-full-registration-bundle.manifest.json",
    "/builder-bundles/trinity-guardian-full-registration-bundle.tar.gz",
    "/builder-bundles/trinity-guardian-retirement-bundle.manifest.json",
    "/builder-bundles/trinity-guardian-retirement-bundle.tar.gz",
    "/builder-bundles/trinity-guardian-signed-echo-builder-bundle.manifest.json",
    "/builder-bundles/trinity-guardian-signed-echo-builder-bundle.tar.gz",
    "/builder-bundles/trinity-guardian-stage1-builder-bundle.manifest.json",
    "/builder-bundles/trinity-guardian-stage1-builder-bundle.tar.gz",
    "/builder-bundles/trinity-guardian-stage2-builder-bundle.manifest.json",
    "/builder-bundles/trinity-guardian-stage2-builder-bundle.tar.gz",
    "/builder-bundles/trinity-pure-echo-builder-bundle.manifest.json",
    "/builder-bundles/trinity-pure-echo-builder-bundle.tar.gz",
    "/builder-bundles/trinity-v0v5-builder-bundle.manifest.json",
    "/builder-bundles/trinity-v0v5-builder-bundle.tar.gz",
    "/record-chain/chain-tip.json",
    "/record-chain/indexes/statistics.json",
    "/record-chain/indexes/record-index.json",
    "/record-chain/indexes/echo-index.json",
    "/record-chain/indexes/verification-index.json",
    "/record-chain/indexes/guardian-state.json",
    "/record-chain/indexes/guardian_retirement-index.json",
    "/record-chain/indexes/propagation-index.json",
    "/record-chain/indexes/correction-index.json",
    "/record-chain/indexes/classification_update-index.json",
)


def normalize_web_path(path: str) -> str:
    if path != "/" and path.endswith("/"):
        return path[:-1]
    return path


def repo_file(path: str) -> Path:
    return ROOT / path.lstrip("/")


def repo_bytes(path: str) -> bytes:
    return repo_file(path).read_bytes()


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def json_object_from_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_strict_json_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not strict UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} JSON root must be an object, got {type(value).__name__}")
    return value


def repo_json_object(path: str) -> dict[str, Any]:
    return json_object_from_bytes(repo_bytes(path), f"repository {path}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_digest_for_object(value: dict[str, Any]) -> str:
    material = dict(value)
    material.pop("source_digest", None)
    canonical = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()[:16]


def validate_embedded_source_digest(
    label: str,
    value: dict[str, Any],
    errors: list[str],
) -> None:
    embedded = value.get("source_digest")
    if embedded is None:
        return
    actual = source_digest_for_object(value)
    if embedded != actual:
        errors.append(
            f"{label} source_digest is not bound to its JSON content: "
            f"embedded={embedded!r}, recomputed={actual!r}"
        )


def validate_links_semantics(
    label: str,
    links: dict[str, Any],
    errors: list[str],
) -> None:
    machine = set(links.get("machine", []))
    legacy = set(links.get("legacy_machine", []))
    deprecated = set(links.get("deprecated_for_new_records", []))
    pages = {normalize_web_path(str(path)) for path in links.get("key_pages", [])}

    missing_machine = sorted(CURRENT_CORE_MACHINE_PATHS - machine)
    if missing_machine:
        errors.append(f"{label} links.json current machine paths missing: {missing_machine}")

    active_legacy = sorted(machine & RETIRED_ACTIVE_PATHS)
    if active_legacy:
        errors.append(f"{label} links.json active machine list contains retired paths: {active_legacy}")

    missing_legacy = sorted(RETIRED_ACTIVE_PATHS - legacy)
    if missing_legacy:
        errors.append(f"{label} links.json legacy list missing retired paths: {missing_legacy}")

    missing_deprecated = sorted(RETIRED_ACTIVE_PATHS - deprecated)
    if missing_deprecated:
        errors.append(f"{label} links.json deprecated list missing retired paths: {missing_deprecated}")

    missing_pages = sorted(CURRENT_KEY_PAGES - pages)
    if missing_pages:
        errors.append(f"{label} links.json key pages missing: {missing_pages}")

    if links.get("canonical_machine_router") != "/api/agent-first-contact.json":
        errors.append(f"{label} links.json canonical_machine_router is not current first contact")

    validate_embedded_source_digest(label, links, errors)


def validate_well_known_semantics(
    label: str,
    well_known: dict[str, Any],
    errors: list[str],
) -> None:
    if well_known.get("canonical_machine_router") != "/api/agent-first-contact.json":
        errors.append(f"{label} well-known canonical_machine_router is not current first contact")

    api = well_known.get("api", {})
    expected_api = {
        "agent_first_contact": "/api/agent-first-contact.json",
        "agent_start": "/api/agent-start.v2.json",
        "agent_required_reading": "/api/agent-required-reading.json",
        "agent_task_router": "/api/agent-task-router.v1.json",
        "builder_manifest": "/api/record-chain-builder-bundles.v1.json",
        "field_guidance": "/downloads/record-chain-agent-field-guidance.v1.json",
        "submission_schema": "/api/record-chain-submission-schema.v1.json",
        "gateway_contract": "/api/record-chain-intake-gateway.v1.json",
        "record_chain_status": "/api/record-chain-status.json",
    }
    for key, expected in expected_api.items():
        if api.get(key) != expected:
            errors.append(f"{label} well-known api.{key} expected {expected!r}, got {api.get(key)!r}")

    current = well_known.get("current_public_submission", {})
    if tuple(current.get("record_types", [])) != CURRENT_RECORD_TYPES:
        errors.append(f"{label} well-known current record types do not match runtime contract")

    historical = well_known.get("agent_entry_protocol", {})
    if historical.get("status") != "historical_compatibility_pointer":
        errors.append(f"{label} well-known agent-entry protocol is not historical-only")
    if historical.get("replacement") != "/api/agent-first-contact.json":
        errors.append(f"{label} well-known agent-entry replacement is not current first contact")

    validate_embedded_source_digest(label, well_known, errors)
