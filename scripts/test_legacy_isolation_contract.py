#!/usr/bin/env python3
"""Phase 6B Legacy Isolation Contract Test.

Ensures legacy/historical surfaces are properly isolated from current
discovery and submission paths.

Checks:
  1. api/links.json: no /external-agent-copy-paste-examples in key_pages.
  2. api/links.json: formal-builder-bundles and guardian-registry in legacy_machine.
  3. api/links.json: current machine list contains required record-chain endpoints.
  4. .well-known/trinity-accord.json: current_public_submission block exists.
  5. .well-known/trinity-accord.json: legacy entries removed from agent_entrypoints.
  6. .well-known/trinity-accord.json: submission_gate renamed to legacy_internal_submission_gate.
  7. api/guardian-registry.json: marked historical_archive_only.
  8. api/guardian-registry.json: no status=active (replaced with historical_legacy_listing).
  9. api/external-agent-operation-examples.v1.json: still historical_archive_only.
  10. Current discovery surfaces do not reference external-agent-operation-examples as current.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def load_json(rel: str):
    p = ROOT / rel
    if not p.exists():
        fail(f"missing {rel}")
    return json.loads(p.read_text(encoding="utf-8"))


# ------------------------------------------------------------------
# 1. links.json: no /external-agent-copy-paste-examples in key_pages
# ------------------------------------------------------------------
def check_links_no_copy_paste_examples():
    d = load_json("api/links.json")
    key_pages = d.get("key_pages", [])
    for p in key_pages:
        if "external-agent-copy-paste-examples" in p:
            fail(f"links.json key_pages still contains: {p}")
    ok("links.json: no external-agent-copy-paste-examples in key_pages")


# ------------------------------------------------------------------
# 2. links.json: formal-builder-bundles and guardian-registry in legacy
# ------------------------------------------------------------------
def check_links_legacy_machine():
    d = load_json("api/links.json")
    legacy = d.get("legacy_machine", [])
    deprecated = d.get("deprecated_for_new_records", [])
    for item in ["/api/formal-builder-bundles.v1.json", "/api/guardian-registry.json"]:
        if item not in legacy:
            fail(f"links.json legacy_machine missing: {item}")
        if item not in deprecated:
            fail(f"links.json deprecated_for_new_records missing: {item}")
        machine = d.get("machine", [])
        if item in machine:
            fail(f"links.json machine still contains legacy item: {item}")
    ok("links.json: formal-builder-bundles and guardian-registry in legacy")


# ------------------------------------------------------------------
# 3. links.json: current machine list has required endpoints
# ------------------------------------------------------------------
def check_links_required_endpoints():
    d = load_json("api/links.json")
    machine = d.get("machine", [])
    required = [
        "/api/agent-first-contact.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/api/record-chain-submission-schema.v1.json",
        "/api/record-chain-field-helper.v1.json",
        "/api/record-chain-oath-policy.v1.json",
        "/api/record-chain-builder-bundles.v1.json",
        "/api/record-chain-status.json",
        "/api/record-chain-server-receipt.v1.json",
        "/api/public-home-status.json",
    ]
    for r in required:
        if r not in machine:
            fail(f"links.json machine missing required endpoint: {r}")
    ok("links.json: all required record-chain endpoints present in machine")


# ------------------------------------------------------------------
# 4. .well-known: current_public_submission block exists
# ------------------------------------------------------------------
def check_well_known_current_submission():
    d = load_json(".well-known/trinity-accord.json")
    block = d.get("current_public_submission")
    if not block:
        fail(".well-known/trinity-accord.json missing current_public_submission")
    for key in [
        "first_contact", "builder", "builder_bundle_manifest",
        "gateway_contract", "submission_schema", "field_helper", "oath_policy"
    ]:
        if key not in block:
            fail(f"current_public_submission missing key: {key}")
    ok(".well-known: current_public_submission block present")


# ------------------------------------------------------------------
# 5. .well-known: legacy entries removed from agent_entrypoints
# ------------------------------------------------------------------
def check_well_known_entrypoints():
    d = load_json(".well-known/trinity-accord.json")
    entrypoints = d.get("agent_entrypoints", {})
    for legacy_key in ["formal_builder_bundles", "external_agent_operation_examples"]:
        if legacy_key in entrypoints:
            fail(f".well-known agent_entrypoints still contains legacy: {legacy_key}")
    ok(".well-known: legacy entries removed from agent_entrypoints")


# ------------------------------------------------------------------
# 6. .well-known: submission_gate renamed
# ------------------------------------------------------------------
def check_well_known_submission_gate():
    d = load_json(".well-known/trinity-accord.json")
    if "submission_gate" in d:
        fail(".well-known still has 'submission_gate' (should be legacy_internal_submission_gate)")
    legacy_gate = d.get("legacy_internal_submission_gate")
    if not legacy_gate:
        fail(".well-known missing legacy_internal_submission_gate")
    status = legacy_gate.get("status", "")
    if "historical" not in status and "internal" not in status:
        fail(f"legacy_internal_submission_gate status not historical/internal: {status}")
    ok(".well-known: submission_gate renamed to legacy_internal_submission_gate")


# ------------------------------------------------------------------
# 7. guardian-registry: marked historical
# ------------------------------------------------------------------
def check_guardian_registry_historical():
    d = load_json("api/guardian-registry.json")
    if not d.get("historical_archive_only"):
        fail("guardian-registry.json missing historical_archive_only=true")
    if not d.get("not_current_record_chain_guardian_status"):
        fail("guardian-registry.json missing not_current_record_chain_guardian_status=true")
    ok("guardian-registry: marked historical_archive_only")


# ------------------------------------------------------------------
# 8. guardian-registry: no status=active
# ------------------------------------------------------------------
def check_guardian_registry_no_active():
    d = load_json("api/guardian-registry.json")
    for g in d.get("guardians", []):
        if g.get("status") == "active":
            fail(f"guardian {g.get('guardian_registry_number')} still has status=active")
    ok("guardian-registry: no status=active entries")


# ------------------------------------------------------------------
# 9. external-agent-operation-examples: still historical
# ------------------------------------------------------------------
def check_external_examples_historical():
    d = load_json("api/external-agent-operation-examples.v1.json")
    if d.get("status") != "historical_archive_only":
        fail(f"external-agent-operation-examples status={d.get('status')}, expected historical_archive_only")
    ok("external-agent-operation-examples: historical_archive_only")


# ------------------------------------------------------------------
# 10. Current surfaces don't reference external examples as current
# ------------------------------------------------------------------
def check_current_surfaces_no_external_examples():
    # Check that agent-task-router uses example_historical (not example)
    router = load_json("api/agent-task-router.v1.json")
    router_text = json.dumps(router)
    # Should have example_historical but not example pointing to external-agent-operation-examples
    if '"example": "/api/external-agent-operation-examples' in router_text:
        fail("agent-task-router.v1.json uses 'example' (not 'example_historical') for external-agent-operation-examples")
    if 'external_agent_examples":' in router_text and 'external_agent_examples_historical' not in router_text:
        # Check agent-live-health
        pass

    # Check agent-live-health
    health = load_json("api/agent-live-health.v1.json")
    if "external_agent_examples" in health:
        fail("agent-live-health.v1.json still has external_agent_examples (should be _historical)")

    ok("current discovery surfaces properly mark external examples as historical")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main() -> int:
    check_links_no_copy_paste_examples()
    check_links_legacy_machine()
    check_links_required_endpoints()
    check_well_known_current_submission()
    check_well_known_entrypoints()
    check_well_known_submission_gate()
    check_guardian_registry_historical()
    check_guardian_registry_no_active()
    check_external_examples_historical()
    check_current_surfaces_no_external_examples()

    print("\n=== ALL LEGACY ISOLATION CONTRACT TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
