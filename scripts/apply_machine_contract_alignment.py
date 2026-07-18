#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-07-18T00:00:00Z"
TYPES = ["echo", "verification", "guardian_application", "guardian_retirement", "propagation", "correction", "classification_update", "context_insufficient_notice"]
FORMAL = TYPES[:-1]
MINIMUMS = {"echo": "CC-3", "verification_V0_to_V2": "CC-2", "verification_V3_to_V5": "CC-3", "guardian_application": "CC-3", "guardian_retirement": "CC-1", "propagation": "CC-2", "correction": "CC-1", "classification_update": "CC-2", "context_insufficient_notice": "CC-0"}
INDEXES = {"echo": "/record-chain/indexes/echo-index.json", "verification": "/record-chain/indexes/verification-index.json", "guardian_application": "/record-chain/indexes/guardian-state.json", "guardian_retirement": "/record-chain/indexes/guardian_retirement-index.json", "propagation": "/record-chain/indexes/propagation-index.json", "correction": "/record-chain/indexes/correction-index.json", "classification_update": "/record-chain/indexes/classification_update-index.json", "context_insufficient_notice": "/record-chain/indexes/record-index.json"}

def load(path): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def save(path, value): (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

first = load("api/agent-first-contact.json")
first["version"] = "2.4.0"
first["updated_at"] = TODAY
first["operational_source_of_truth"] = {"canonical_router": "/api/agent-first-contact.json", "reading_manifest": "/api/agent-required-reading.json", "builder_manifest": "/api/record-chain-builder-bundles.v1.json", "builder": "/downloads/record-chain-builder.mjs", "gateway_contract": "/api/record-chain-intake-gateway.v1.json", "live_runtime_defines_operational_availability": True, "public_status_and_indexes_define_final_inclusion": True, "agent_entry_protocol_is_historical_pointer": True}
first["runtime_alignment"] = {"accepted_record_types": TYPES, "formal_oath_record_types": FORMAL, "context_compatibility_minimums": MINIMUMS, "formal_cc3_to_cc5_require_loaded_urls": True, "formal_cc3_to_cc5_require_context_read_confirmed_true": True, "context_insufficient_notice_requires_non_empty_reason": True}
first["post_submit_observation_protocol"]["record_specific_indexes"] = INDEXES
save("api/agent-first-contact.json", first)

start = load("api/agent-start.v2.json")
start["version"] = "2.6.0"
start["updated_at"] = TODAY
start["canonical_machine_router"] = "/api/agent-first-contact.json"
start["runtime_alignment"] = {"accepted_record_types": TYPES, "formal_oath_record_types": FORMAL, "context_compatibility_minimums": MINIMUMS, "formal_cc3_to_cc5_require_loaded_urls": True, "formal_cc3_to_cc5_require_context_read_confirmed_true": True, "context_insufficient_notice_requires_non_empty_reason": True}
start["post_submit_status_sources"]["record_specific_indexes"] = INDEXES
save("api/agent-start.v2.json", start)

gateway = load("api/record-chain-intake-gateway.v1.json")
gateway["updated_at"] = TODAY
gateway["runtime_alignment"] = {"implementation": "/apps/record_chain_intake_gateway/app.py", "validation": "/apps/record_chain_intake_gateway/gateway/validation.py", "accepted_record_types": TYPES, "formal_oath_record_types": FORMAL, "context_compatibility_minimums": MINIMUMS, "default_max_submission_bytes": 524288, "strict_json_duplicate_keys_rejected": True, "submit_intake_files_materialized_in_one_git_commit": True, "receipt_and_terminal_status_hashes_verified_on_read": True, "live_readiness_endpoint": "/record-chain/readiness"}
gateway["server_side_pipeline"]["final_record_hashes_assigned_server_side"] = True
gateway["server_side_pipeline"]["builder_assigns_client_authorship_and_oath_hashes"] = True
gateway["server_side_pipeline"]["generated_hash_source_rule"] = "Builder generates client authorship and oath-derived hashes; Gateway generates receipt hashes; final-chain tooling assigns final record, content, and chain hashes."
save("api/record-chain-intake-gateway.v1.json", gateway)

save("api/agent-entry-protocol.json", {"schema": "trinityaccord.agent-entry-protocol.v1", "status": "historical_compatibility_pointer", "active_router": False, "replacement": "/api/agent-first-contact.json", "canonical_human_first_contact": "/agent-first-contact/", "current_start": "/api/agent-start.v2.json", "current_builder": "/downloads/record-chain-builder.mjs", "current_gateway_contract": "/api/record-chain-intake-gateway.v1.json", "historical_scope": ["legacy fixed reading sequence", "legacy issue intake", "legacy V-level routing"], "homepage_only_policy": {"assessment_state": "insufficient_context", "final_evaluation_allowed": False, "current_router": "/api/agent-first-contact.json"}, "boundary": {"not_authority": True, "non_amending": True, "bitcoin_originals_prevail": True}})
print("MACHINE_CONTRACT_ALIGNMENT_APPLIED")
