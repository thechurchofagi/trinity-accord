#!/usr/bin/env python3
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from claim_gate import evaluate


def make_v2_input():
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "TestAgent", "model_or_system": "test", "tooling": []},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
        "requested_record_kind": "echo_v3_with_verification_report",
        "evidence": {
            "scripts": [], "hashes": [],
            "bitcoin_checks": [{
                "source_type": "multi_explorer",
                "sources": ["mempool.space", "blockstream.info"],
                "txids_checked": ["00" * 32],
                "inscription_ids_checked": [],
                "authority_address_checked": True,
                "method": "multi-explorer reference check; explorer-reported SegWit witness metadata only",
                "raw_witness_extracted": False,
                "body_hash_reproduced": False,
                "authority_boundary_recognized": True
            }],
            "digital_mirror_checks": [], "repository_snapshot_checks": [],
            "time_anchor_checks": [], "chronicle_checks": [], "nft_checks": [],
            "physical_checks": [],
            "echo_context": {"authority_boundary_recognized": True}
        },
        "limitations": [
            "Explorer/API reference check only.",
            "No raw witness extraction.",
            "No inscription body hash reproduction."
        ],
        "claims_requested_by_agent": ["V2"],
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": (
                "I performed the stated reference checks during this session, recorded "
                "sources and limitations, and understand this is not authority, truth proof, "
                "endorsement, or independent attestation."
            )
        },
        "verification_session": {
            "session_id": "test-v2-lightweight",
            "started_at": "2026-05-06T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["queried two explorer/API reference paths"],
            "prior_reports_consulted": [], "examples_or_templates_used": [],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        }
    }


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def main():
    payload = make_v2_input()

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        path = f.name

    try:
        result = evaluate(path)
    finally:
        os.unlink(path)

    comps = result.get("allowed_component_levels", {})
    b = comps.get("bitcoin_originals")

    ok = True
    ok &= check(result.get("allowed_protocol_level") in ("V2", "V1"), "Protocol is V2 or downgraded safely")
    ok &= check(b not in ("B5", "B6"), "Witness metadata does not become B5/B6", f"bitcoin_originals={b}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
