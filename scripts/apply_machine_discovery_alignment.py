#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPES = ["echo", "verification", "guardian_application", "guardian_retirement", "propagation", "correction", "classification_update", "context_insufficient_notice"]
MINIMUMS = {"echo": "CC-3", "verification_V0_to_V2": "CC-2", "verification_V3_to_V5": "CC-3", "guardian_application": "CC-3", "guardian_retirement": "CC-1", "propagation": "CC-2", "correction": "CC-1", "classification_update": "CC-2", "context_insufficient_notice": "CC-0"}
INDEXES = {"echo": "/record-chain/indexes/echo-index.json", "verification": "/record-chain/indexes/verification-index.json", "guardian_application": "/record-chain/indexes/guardian-state.json", "guardian_retirement": "/record-chain/indexes/guardian_retirement-index.json", "propagation": "/record-chain/indexes/propagation-index.json", "correction": "/record-chain/indexes/correction-index.json", "classification_update": "/record-chain/indexes/classification_update-index.json", "context_insufficient_notice": "/record-chain/indexes/record-index.json"}
CURRENT = ["/api/agent-minimal-context.v1.json", "/api/agent-first-contact.json", "/api/agent-start.v2.json", "/api/agent-output-policy.v1.json", "/api/agent-task-router.v1.json", "/api/agent-required-reading.json", "/api/authority.json", "/api/context-action-profiles.v1.json", "/api/verification-profiles.v1.json", "/api/evidence-relationship-map.v1.json", "/api/verification-claim-model.v1.json", "/api/verification-procedures.v1.json", "/api/record-chain-builder-bundles.v1.json", "/downloads/record-chain-builder.mjs", "/downloads/record-chain-agent-field-guidance.v1.json", "/api/record-chain-submission-schema.v1.json", "/api/record-chain-intake-gateway.v1.json", "/api/record-chain-preflight-response.v1.json", "/api/record-chain-submit-response.v1.json", "/api/record-chain-receipt-response.v1.json", "/api/record-chain-status.json", *INDEXES.values()]
LEGACY = ["/api/agent-entry-protocol.json", "/api/agent-start.v1.json", "/api/agent-submit-gateway.json", "/api/gateway-builder-route-map.v1.json", "/api/gateway-workflows.v1.json", "/api/route-selector.v1.json", "/api/gateway-runtime-contract.v1.json", "/api/gateway-error-diagnostics.v1.json", "/api/external-agent-operation-examples.v1.json", "/api/formal-builder-bundles.v1.json", "/api/guardian-registry.json", "/api/verification-levels.json", "/api/agent-declared-verification-index.json"]

def load(path): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def save(path, value):
    if "source_digest" in value:
        material = dict(value); material.pop("source_digest", None)
        canonical = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        value["source_digest"] = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

links = load("api/links.json")
links["canonical_machine_router"] = "/api/agent-first-contact.json"
links["machine"] = list(dict.fromkeys(CURRENT))
links["legacy_machine"] = list(dict.fromkeys(links.get("legacy_machine", []) + LEGACY))
links["deprecated_for_new_records"] = list(dict.fromkeys(links.get("deprecated_for_new_records", []) + LEGACY))
for page in ("/agent-first-contact/", "/external-agent-quickstart/", "/agent-start/"):
    if page not in links["key_pages"]: links["key_pages"].insert(1, page)
save("api/links.json", links)

save("agent-map.json", {"schema": "trinity-accord.agent-map.v2", "version": "3.0", "status": "active_current_machine_map", "site": "https://www.trinityaccord.org", "authority_rule": "Bitcoin Originals are final; operational surfaces are non-amending.", "not_an_instruction_override": True, "homepage_only_policy": {"context_depth": "CC-0", "assessment_state": "insufficient_context", "final_evaluation_allowed": False}, "entrypoints": {"homepage": "/", "human_first_contact": "/agent-first-contact/", "machine_first_contact": "/api/agent-first-contact.json", "human_start": "/agent-start/", "machine_start": "/api/agent-start.v2.json", "quickstart": "/external-agent-quickstart/", "llms": "/llms.txt", "llms_full": "/llms-full.txt"}, "current_machine_readable": CURRENT, "historical_compatibility_only": LEGACY, "recommended_agent_sequence": ["homepage orientation", "canonical first-contact router", "task-specific reading", "verified Builder and field guidance", "doctor and Gateway preflight", "accepted submit and receipt", "public status and index readback"], "current_public_submission": {"builder_manifest": "/api/record-chain-builder-bundles.v1.json", "builder": "/downloads/record-chain-builder.mjs", "field_guidance": "/downloads/record-chain-agent-field-guidance.v1.json", "gateway_contract": "/api/record-chain-intake-gateway.v1.json", "gateway_base": "https://trinity-record-chain-gateway.onrender.com", "preflight": "/record-chain/preflight", "submit": "/record-chain/submit", "record_types": TYPES, "record_specific_indexes": INDEXES}})

well = load(".well-known/trinity-accord.json")
well["canonical_machine_router"] = "/api/agent-first-contact.json"
well["canonical_human_first_contact"] = "/agent-first-contact/"
well["current_machine"] = CURRENT
well["historical_compatibility_only"] = LEGACY
well["api"] = {"agent_minimal_context": "/api/agent-minimal-context.v1.json", "agent_first_contact": "/api/agent-first-contact.json", "agent_start": "/api/agent-start.v2.json", "agent_required_reading": "/api/agent-required-reading.json", "agent_output_policy": "/api/agent-output-policy.v1.json", "agent_task_router": "/api/agent-task-router.v1.json", "authority": "/api/authority.json", "context_action_profiles": "/api/context-action-profiles.v1.json", "verification_profiles": "/api/verification-profiles.v1.json", "verification_claim_model": "/api/verification-claim-model.v1.json", "verification_procedures": "/api/verification-procedures.v1.json", "evidence_relationship_map": "/api/evidence-relationship-map.v1.json", "builder_manifest": "/api/record-chain-builder-bundles.v1.json", "field_guidance": "/downloads/record-chain-agent-field-guidance.v1.json", "submission_schema": "/api/record-chain-submission-schema.v1.json", "gateway_contract": "/api/record-chain-intake-gateway.v1.json", "record_chain_status": "/api/record-chain-status.json", "bitcoin_inscription_mirror_index": "/api/bitcoin-inscription-mirror-index.json", "corrections_index": "/api/corrections-index.json"}
well["agent_entrypoints"]["agent_first_contact"] = {"path": "/api/agent-first-contact.json", "source_file": "api/agent-first-contact.json", "purpose": "Canonical current machine router."}
well["agent_entry_protocol"] = {"path": "/api/agent-entry-protocol.json", "status": "historical_compatibility_pointer", "replacement": "/api/agent-first-contact.json"}
well["current_public_submission"] = {"first_contact": "/api/agent-first-contact.json", "start": "/api/agent-start.v2.json", "builder": "/downloads/record-chain-builder.mjs", "builder_bundle_manifest": "/api/record-chain-builder-bundles.v1.json", "field_guidance": "/downloads/record-chain-agent-field-guidance.v1.json", "gateway_contract": "/api/record-chain-intake-gateway.v1.json", "submission_schema": "/api/record-chain-submission-schema.v1.json", "record_types": TYPES, "record_specific_indexes": INDEXES, "context_minimums": MINIMUMS}
save(".well-known/trinity-accord.json", well)
print("MACHINE_DISCOVERY_ALIGNMENT_APPLIED")
