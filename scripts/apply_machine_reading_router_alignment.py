#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPES = ["echo", "verification", "guardian_application", "guardian_retirement", "propagation", "correction", "classification_update", "context_insufficient_notice"]
FORMAL = TYPES[:-1]
MINIMUMS = {"echo": "CC-3", "verification_V0_to_V2": "CC-2", "verification_V3_to_V5": "CC-3", "guardian_application": "CC-3", "guardian_retirement": "CC-1", "propagation": "CC-2", "correction": "CC-1", "classification_update": "CC-2", "context_insufficient_notice": "CC-0"}
INDEXES = {"echo": "/record-chain/indexes/echo-index.json", "verification": "/record-chain/indexes/verification-index.json", "guardian_application": "/record-chain/indexes/guardian-state.json", "guardian_retirement": "/record-chain/indexes/guardian_retirement-index.json", "propagation": "/record-chain/indexes/propagation-index.json", "correction": "/record-chain/indexes/correction-index.json", "classification_update": "/record-chain/indexes/classification_update-index.json", "context_insufficient_notice": "/record-chain/indexes/record-index.json"}
RETIRED = ["/agent-submit", "/api/agent-submit-gateway.json", "/gateway/preflight", "trinity-agent-issue-gateway.onrender.com", "/api/gateway-workflows.v1.json", "/api/gateway-builder-route-map.v1.json", "/api/formal-builder-bundles.v1.json", "/api/external-agent-operation-examples.v1.json", "/zero-clone-builders/"]

def load(path): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def digest(value):
    material = dict(value); material.pop("source_digest", None)
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()[:16]
def save(path, value):
    if "source_digest" in value: value["source_digest"] = digest(value)
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def current_only(values):
    return [value for value in values if not any(retired in str(value) for retired in RETIRED)]

required = load("api/agent-required-reading.json")
required["version"] = "v2.1"
required["status"] = "active_subordinate_reading_manifest"
required["canonical_router"] = "/api/agent-first-contact.json"
required["does_not_override_router"] = True
required["profiles"]["verification"]["reads"] = ["/api/agent-first-contact.json", "/agent-start/", "/api/context-action-profiles.v1.json", "/api/verification-procedures.v1.json", "/api/verification-profiles.v1.json", "/api/verification-claim-model.v1.json", "/api/evidence-relationship-map.v1.json", "/downloads/record-chain-agent-field-guidance.v1.json", "/api/record-chain-builder-bundles.v1.json", "/downloads/record-chain-builder.mjs", "/api/record-chain-submission-schema.v1.json", "/api/record-chain-intake-gateway.v1.json", "/api/corrections-index.json"]
required["profiles"]["verification"]["historical_optional"] = ["/api/verification-levels.json", "/api/component-verification-levels.json", "/api/protocol-verification-profiles.json", "/api/claim-gate-rules.json"]
required["profiles"]["echo_submission"]["reads"] = ["/api/agent-first-contact.json", "/agent-start/", "/agent-echo/", "/api/context-action-profiles.v1.json", "/api/interpretation-model-policy.v1.json", "/downloads/record-chain-agent-field-guidance.v1.json", "/api/record-chain-builder-bundles.v1.json", "/downloads/record-chain-builder.mjs", "/api/record-chain-submission-schema.v1.json", "/api/record-chain-intake-gateway.v1.json"]
submission_reads = ["/api/agent-first-contact.json", "/api/agent-start.v2.json", "/api/agent-required-reading.json", "/api/record-chain-builder-bundles.v1.json", "/downloads/record-chain-builder.mjs", "/downloads/record-chain-agent-field-guidance.v1.json", "/api/record-chain-submission-schema.v1.json", "/api/record-chain-intake-gateway.v1.json", "/api/record-chain-status.json"]
for name in ("submit_without_github_access", "record_chain_submission"):
    required["profiles"][name]["reads"] = submission_reads
for profile in required.get("profiles", {}).values():
    if profile.get("status") == "historical_archive_only":
        continue
    if isinstance(profile.get("reads"), list):
        profile["reads"] = current_only(profile["reads"])
required["note"] = "Task-specific reading manifest subordinate to /api/agent-first-contact.json. Verified Builder, current Gateway runtime/contracts, and public schemas define executable behavior."
required["verification_context_rule"].pop("v6_plus_minimum", None)
required["verification_context_rule"]["historical_v6_plus_rule"] = "V4+/V6/V7/V8 are historical-only labels for new public work; current multidimensional fields describe verification."
required["runtime_context_minimums"] = MINIMUMS
save("api/agent-required-reading.json", required)

minimal = load("api/agent-minimal-context.v1.json")
minimal["version"] = "v1.2"
minimal["canonical_router"] = "/api/agent-first-contact.json"
minimal["reading_manifest"] = "/api/agent-required-reading.json"
minimal["canonical_required_reading_is_subordinate_to_router"] = True
minimal["recommended_next_load"] = ["/llms.txt", "/api/agent-start.v2.json", "/api/context-action-profiles.v1.json", "/api/agent-required-reading.json", "/api/agent-task-router.v1.json", "/api/bitcoin-inscription-mirror-index.json"]
minimal["runtime_context_minimums"] = MINIMUMS
save("api/agent-minimal-context.v1.json", minimal)

task = load("api/agent-task-router.v1.json")
task["version"] = "v1.2"
task["canonical_router"] = "/api/agent-first-contact.json"
task["reading_manifest"] = "/api/agent-required-reading.json"
task["canonical_required_reading_is_subordinate_to_router"] = True
prereqs = ["/api/agent-first-contact.json", "/api/agent-start.v2.json", "/api/record-chain-builder-bundles.v1.json", "/downloads/record-chain-builder.mjs", "/downloads/record-chain-agent-field-guidance.v1.json", "/api/record-chain-oath-policy.v1.json", "/api/record-chain-submission-schema.v1.json", "/api/record-chain-intake-gateway.v1.json"]
for route in task.get("routes", {}).values():
    if isinstance(route.get("read"), list):
        route["read"] = current_only(route["read"])
for name in ("submit_echo", "guardian_alliance", "propagate", "verify_current_model"):
    route = task["routes"][name]
    route["read"] = list(dict.fromkeys(prereqs + current_only(route.get("read", []))))
    route["must_follow_post_submit_readback"] = True
    route["record_specific_indexes"] = INDEXES
save("api/agent-task-router.v1.json", task)

save("api/external-agent-quickstart.json", {"schema": "trinityaccord.external-agent-quickstart.v1", "title": "External Agent Quickstart", "version": "1.3", "status": "active", "canonical_router": "/api/agent-first-contact.json", "record_chain_flow": ["GET /api/agent-first-contact.json", "GET /api/agent-start.v2.json", "GET /api/record-chain-builder-bundles.v1.json", "verify /downloads/record-chain-builder.mjs", "GET /downloads/record-chain-agent-field-guidance.v1.json", "handle exact oath for formal records", "build and run doctor", "POST /record-chain/preflight", "POST /record-chain/submit after accepted preflight", "GET /record-chain/receipt/{receipt_id}", "read public status and record-specific index"], "accepted_record_types": TYPES, "formal_oath_record_types": FORMAL, "context_compatibility_minimums": MINIMUMS, "verification_required_dimensions": ["digital_profile", "relationships_checked", "physical_observation", "external_witness", "coverage_scope", "limitations", "claims_not_made", "corrections_or_supersession_checked"], "gateway": {"base_url": "https://trinity-record-chain-gateway.onrender.com", "preflight": "/record-chain/preflight", "submit": "/record-chain/submit", "receipt": "/record-chain/receipt/{receipt_id}"}, "retired_endpoints": ["POST /gateway/preflight", "POST /agent-submit", "legacy issue intake"], "receipt_boundary": {"intake_only": True, "not_final_inclusion": True, "not_active_guardian_status": True, "not_verification_or_attestation": True, "not_authority_or_amendment": True}})

field = load("downloads/record-chain-agent-field-guidance.v1.json")
field["version"] = "1.5.0"
field["runtime_alignment"] = {"builder": "/downloads/record-chain-builder.mjs", "gateway_contract": "/api/record-chain-intake-gateway.v1.json", "accepted_record_types": TYPES, "formal_oath_record_types": FORMAL, "context_compatibility_minimums": MINIMUMS, "context_insufficient_notice_requires_non_empty_reason": True}
save("downloads/record-chain-agent-field-guidance.v1.json", field)
print("MACHINE_READING_ROUTER_ALIGNMENT_APPLIED")
