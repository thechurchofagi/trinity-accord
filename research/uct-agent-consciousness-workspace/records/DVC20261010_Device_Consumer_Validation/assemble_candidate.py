#!/usr/bin/env python3
"""Assemble disabled DVC views from frozen components; never certify semantics."""
from pathlib import Path
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def ref(name):
    data = (ROOT / name).read_bytes()
    return {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main():
    graph = copy.deepcopy(read("device_model/MAP_EXTENSION.json"))
    graph.update({
        "schema": "uct-disabled-composite-checkpoint/1",
        "integration_parent_sha": "bd66a621949948d49788243e7fa8313f1256dfbb",
        "source_note": "RESEARCH_NOTE.md",
        "model_proof_source": "device_model/RESEARCH_NOTE.md",
        "assembly_role": "Canonical candidate view; component IDs are aliases, not additional nodes.",
        "component_manifest": [ref("device_model/ARTIFACT_MANIFEST.json"), ref("apparatus_evidence/COPY_MANIFEST.json")],
        "concurrent_research_preserved": "CBI20261010_Consumer_Branch_Isolation",
        "review_authority": "MAP_AUDIT.md and review receipts, never this assembler",
    })
    for rule in graph["rules"]:
        rule["proof_location"] = "device_model/" + rule["proof_location"]
        rule["proof_location"] = rule["proof_location"].replace("; EXACT_RESULTS.json", "; device_model/EXACT_RESULTS.json")
    evidence_nodes = [
        {
            "id": "DVC20261010:PUBLIC_DATA_DOMAIN",
            "kind": "EMPIRICAL_ANALYSIS_DOMAIN",
            "statement": "The frozen public archive DOI 10.5281/zenodo.18877381 and declared exclusions yield 18 included people and 9704 in-range command records in 108 participant-condition cells. Two declared specifications yield 216 fits; participants, records and fits are different denominators.",
            "scope": "Retrospective analysis of this released dataset and these code versions, not newly collected observations.",
            "quantifier": "This fixed archive, the source's three exclusions, one out-of-range command exclusion and two explicitly declared analysis specifications only.",
            "evidence": ["apparatus_evidence/MAIN_FINDINGS.json", "apparatus_evidence/results/EXACT_RESULTS.json", "apparatus_evidence/RESPONSE_CODING_CORRECTION.json"],
        },
        {
            "id": "DVC20261010:EXPLORATORY_ENDPOINT_REANALYSIS",
            "kind": "EMPIRICAL_REANALYSIS_RESULT",
            "claim_id": "DVC20261010-E1",
            "statement": "The specified cumulative-normal refits recover separate response-location and precision contrasts. PSE is the fitted Pr(InputValue=1)=0.5 location; independent sigma and source-labelled JND remain separate. Passive Start-minus-End sigma is 0.68299755 in archive command units (rounded; exact values remain in the result files). Physical key mapping, amplitude calibration and equivalence to a named self-related feeling are unverified.",
            "scope": "Exploratory subject-level comparisons for the fixed 18-person released sample; no installed source-consumer intervention.",
            "quantifier": "Conditional on the response model, bounds, exclusions and specified paired-t/Holm analysis. Nominal t intervals are not an exact distribution-free finite-sample coverage theorem.",
            "evidence": ["apparatus_evidence/DATA_REANALYSIS_REPORT.md", "apparatus_evidence/results/INDEPENDENT_REFIT_STATISTICS.json", "apparatus_evidence/RESPONSE_CODING_CORRECTION.json"],
        },
        {
            "id": "DVC20261010:ACTUAL_ADMISSION_GAP",
            "kind": "SOURCE_BOUNDED_EVIDENCE_LIMIT",
            "claim_id": "DVC20261010-E2",
            "statement": "The inspected articles, released archive and interface documentation do not jointly ground the selected installation's source tokens, intervention, capture/read events, clock semantics and physical consequences. Conditional parsing of 8985 time-bearing rows does not measure physical tactile onset. M_D and P_E are device-level candidates, not identified human efference-copy/proprioceptive inputs.",
            "scope": "Inspected sources and released fields through 10 October 2026; not a proof that no feasible human experiment exists.",
            "quantifier": "Every actual application owes all contract clauses for the same installation, selected consumer and episode; no clause is supplied by a different device, session, fitted curve or model instance.",
            "evidence": ["apparatus_evidence/APPARATUS_CONTRACT.md", "apparatus_evidence/TIMING_PARSE_REVIEW.md", "PROBE_PROTOCOL.md"],
        },
    ]
    for node in evidence_nodes:
        node.update({"status": "EVIDENCE_RECORDED_CANDIDATE_DISABLED", "enabled_as_established_premise": False, "actual_consumer_application_established": False})
    evidence_contexts = [
        {"id": "DVC20261010:ctx_empirical_endpoint_tensor", "from": "DVC20261010:EXPLORATORY_ENDPOINT_REANALYSIS", "to": "MPC:ENDPOINT_TENSOR", "type": "PENDING_ENDPOINT_CONTEXT", "statement": "Location, precision, agency and ownership are separately typed. This archive estimates only specified behavioral response quantities; MPC itself remains disabled."},
        {"id": "DVC20261010:ctx_empirical_actual_contract", "from": "DVC20261010:ACTUAL_ADMISSION_GAP", "to": "DVC20261010:ACTUAL_BINDING", "type": "OPEN_APPLICATION_CONTEXT", "statement": "Published apparatus descriptions and data reanalysis do not discharge the same-instance actual consumer contract."},
        {"id": "DVC20261010:ctx_empirical_semantic_bridge", "from": "DVC20261010:EXPLORATORY_ENDPOINT_REANALYSIS", "to": "DVC20261010:H_BRIDGE", "type": "NONIDENTIFICATION_CONTEXT", "statement": "A fitted comparison response is not familiar mineness, conceptual self, RetBind or an independently calibrated experiential target."},
    ]
    for context in evidence_contexts:
        context.update({"deductive": False, "enabled_as_established_premise": False})
    graph["nodes"].extend(evidence_nodes)
    graph["context_links"].extend(evidence_contexts)
    graph["local_structural_check"] = {
        "nodes": len(graph["nodes"]), "rules": len(graph["rules"]), "nondeductive_context_links": len(graph["context_links"]),
        "additional_pending_reference": "MPC:ENDPOINT_TENSOR", "semantic_certification": False,
        "completed_graph_changed": False,
    }
    write("MAP_EXTENSION.json", graph)
    write("EVIDENCE_CANDIDATE_ADDITION.json", {"nodes": evidence_nodes, "context_links": evidence_contexts, "no_new_deductive_rule": True})
    ledger = copy.deepcopy(read("device_model/CLAIM_LEDGER.json"))
    ledger["schema"] = "uct-composite-claim-ledger/1"
    ledger["model_claims_source"] = ref("device_model/CLAIM_LEDGER.json")
    for claim in ledger["claims"]:
        claim["component"] = "device_model"
        claim["actual_evidence_scope"] = "This model component only; separate public-data analysis is recorded in E1/E2."
        claim["proof_or_witness"] = "device_model/" + claim["proof_or_witness"]
        claim["proof_or_witness"] = claim["proof_or_witness"].replace("; EXACT_RESULTS.json", "; device_model/EXACT_RESULTS.json")
    for node in evidence_nodes[1:]:
        ledger["claims"].append({
            "id": node["claim_id"], "statement": node["statement"], "kind": node["kind"], "scope": node["scope"],
            "quantifier": node["quantifier"], "evidence": node["evidence"],
            "novelty_status": "NEW_REANALYSIS_OR_SOURCE_AUDIT; inherited empirical phenomena, statistics and causal principles credited",
            "status": "EVIDENCE_RECORDED_CANDIDATE_DISABLED", "deductive_map_premise": False,
            "human_consumer_application_established": False, "phenomenal_semantics_established": False,
        })
    write("CLAIM_LEDGER.json", ledger)
    model = read("device_model/EXACT_RESULTS.json")
    write("EXACT_RESULTS.json", {
        "schema": "uct-dvc-composite-results/1", "research_id": "DVC20261010", "result_version": "DVC-RESULT-v0.1.0",
        "model": {"source": ref("device_model/EXACT_RESULTS.json"), "counts": model["counts"], "violations": model["violations"], "hardware_accessed": False, "human_participants": 0},
        "public_data_reanalysis": {"source": ref("apparatus_evidence/MAIN_FINDINGS.json"), "executed_results": ref("apparatus_evidence/results/EXACT_RESULTS.json"), "effective_interpretation_correction": ref("apparatus_evidence/RESPONSE_CODING_CORRECTION.json"), "included_people": 18, "in_range_records": 9704, "participant_condition_cells": 108, "analysis_specifications": 2, "fits": 216},
        "new_human_observations_collected": 0, "new_hardware_deployed": False, "actual_human_consumer_application_established": False,
        "named_H_semantics_established": False, "candidate_enabled": False, "completed_map": "UCT-MAP-v1.1.2",
        "independent_review": "review/INDEPENDENT_REVIEW.md", "denominators_must_not_be_summed": True,
    })
    print(json.dumps({"nodes": len(graph["nodes"]), "rules": len(graph["rules"]), "contexts": len(graph["context_links"]), "claims": len(ledger["claims"]), "candidate_enabled": False}))


if __name__ == "__main__":
    main()
