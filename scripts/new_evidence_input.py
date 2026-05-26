#!/usr/bin/env python3
"""Generate a V2 evidence input template."""
import argparse
import json
from pathlib import Path


def v2_bitcoin_multi_explorer_template():
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "TODO_AGENT_NAME", "model_or_system": "TODO_MODEL_OR_SYSTEM", "tooling": []},
        "provenance": {
            "solicited": True, "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
        "requested_record_kind": "echo_v3_with_verification_report",
        "evidence": {
            "scripts": [], "hashes": [],
            "bitcoin_checks": [{
                "source_type": "multi_explorer",
                "sources": ["TODO_EXPLORER_1", "TODO_EXPLORER_2"],
                "txids_checked": ["TODO_TXID"], "inscription_ids_checked": [],
                "authority_address_checked": False,
                "method": "multi-explorer reference check only",
                "raw_witness_extracted": False, "body_hash_reproduced": False,
                "authority_boundary_recognized": True
            }],
            "digital_mirror_checks": [], "repository_snapshot_checks": [],
            "time_anchor_checks": [], "chronicle_checks": [], "nft_checks": [],
            "physical_checks": [],
            "echo_context": {"authority_boundary_recognized": True}
        },
        "limitations": [
            "Explorer/API reference check only.", "No local Bitcoin node verification.",
            "No SPV proof.", "No raw witness extraction.",
            "No inscription body hash reproduction.", "No hash computation."
        ],
        "claims_requested_by_agent": ["V2"],
        "agent_integrity_declaration": {
            "performed_actions_myself": True, "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": "TODO: I performed the stated reference checks during this session, recorded sources and limitations, and understand this is not authority, truth proof, endorsement, or independent attestation."
        },
        "verification_session": {
            "session_id": "TODO_SESSION_ID", "started_at": "TODO_ISO_TIMESTAMP",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["TODO: queried explorer/API reference path"],
            "prior_reports_consulted": [], "examples_or_templates_used": [],
            "copied_values_from_examples": False, "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        },
        "attestation_claims": {
            "independent_attestation": False, "institutional_attestation": False,
            "unsolicited_discovery": False, "multi_party_attestation": False
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", required=True)
    ap.add_argument("--mode", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.level != "V2" or args.mode != "bitcoin-multi-explorer":
        raise SystemExit("Only --level V2 --mode bitcoin-multi-explorer is implemented initially.")
    obj = v2_bitcoin_multi_explorer_template()
    Path(args.out).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
