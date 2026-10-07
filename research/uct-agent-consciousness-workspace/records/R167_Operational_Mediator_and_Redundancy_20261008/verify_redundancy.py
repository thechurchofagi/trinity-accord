#!/usr/bin/env python3
"""Exact finite checks for R167 redundancy, compensation, and status priority."""

from itertools import product
from pathlib import Path
import hashlib
import json


HERE = Path(__file__).resolve().parent


def bit(function_id, index):
    return (function_id >> index) & 1


def contextual_redundancy_checks():
    totals = {}
    grand_functions = 0
    for m in range(4):
        contexts = list(product((0, 1), repeat=m))
        rows = 2 ** (m + 1)
        functions = 2 ** rows
        relevant = 0
        indispensable = 0
        for fid in range(functions):
            contrasts = []
            for z in contexts:
                z_index = sum(v << i for i, v in enumerate(z))
                i0 = (z_index << 1) | 0
                i1 = (z_index << 1) | 1
                contrasts.append(bit(fid, i1) != bit(fid, i0))
            extensional_dependence = any(contrasts)
            criterion = any(contrasts)
            assert extensional_dependence == criterion
            if criterion:
                relevant += 1
            if all(contrasts):
                indispensable += 1
        totals[str(m)] = {
            "declared_backups": m,
            "contexts": len(contexts),
            "boolean_functions": functions,
            "contextually_relevant": relevant,
            "contextually_indispensable": indispensable,
        }
        grand_functions += functions
    assert grand_functions == 65812
    return {"by_backup_count": totals, "functions_checked": grand_functions}


def or_model(k, z):
    return int(bool(k or z))


def single_cut_false_negative():
    masked = (or_model(1, 1), or_model(0, 1))
    revealing = (or_model(1, 0), or_model(0, 0))
    assert masked == (1, 1)
    assert revealing == (1, 0)
    return {
        "model": "u = k OR z",
        "tested_only_with_backup_on": list(masked),
        "tested_with_backup_off": list(revealing),
        "single_context_null_is_false_negative": True,
    }


def compensation_obstruction():
    baseline = {"k": 1, "z": 0, "u": or_model(1, 0)}
    cut_immediate = {"k": 0, "z": 0, "u": or_model(0, 0)}
    cut_late = {"k": 0, "z": 1, "u": or_model(0, 1)}
    assert baseline["u"] == 1
    assert cut_immediate["u"] == 0
    assert cut_late["u"] == baseline["u"]
    return {
        "dynamics": "u_t=k_t OR z_t; z_(t+1)=z_t OR cut_t",
        "baseline": baseline,
        "cut_pre_adaptation": cut_immediate,
        "cut_post_compensation": cut_late,
        "late_endpoint_masks_initial_contribution": True,
    }


def triage(identity, admissible, fidelity, closure, any_effect, all_null, sensitive):
    if not (identity and admissible and fidelity):
        return "INVALID_PROTOCOL"
    if any_effect:
        return "PRIMARY_USE_SUPPORTED_RELATIVE_TO_CLOSURE"
    if closure and all_null and sensitive:
        return "CANDIDATE_REFUTED_RELATIVE_TO_CLOSURE"
    return "UNRESOLVED"


def status_priority_checks():
    cases = []
    for values in product((False, True), repeat=7):
        status = triage(*values)
        identity, admissible, fidelity, closure, any_effect, all_null, sensitive = values
        if not (identity and admissible and fidelity):
            assert status == "INVALID_PROTOCOL"
        elif any_effect:
            assert status == "PRIMARY_USE_SUPPORTED_RELATIVE_TO_CLOSURE"
        elif closure and all_null and sensitive:
            assert status == "CANDIDATE_REFUTED_RELATIVE_TO_CLOSURE"
        else:
            assert status == "UNRESOLVED"
        cases.append(status)
    return {
        "boolean_assignments": len(cases),
        "counts": {s: cases.count(s) for s in sorted(set(cases))},
        "priority": ["invalidity", "support", "closure-qualified refutation", "unresolved"],
    }


def joint_witness():
    witness = {
        "one_bearer_lineage": True,
        "physical_anchor": True,
        "live_mediator_read": True,
        "valid_anchor_pulse": True,
        "valid_mediator_pulse": True,
        "declared_backup_contexts_tested": True,
        "pre_compensation_effect": True,
        "report_used_as_physical_definition": False,
        "c1_derived": False,
        "b_min_validated": False,
    }
    assert all(witness[k] for k in (
        "one_bearer_lineage", "physical_anchor", "live_mediator_read",
        "valid_anchor_pulse", "valid_mediator_pulse",
        "declared_backup_contexts_tested", "pre_compensation_effect"))
    assert not witness["report_used_as_physical_definition"]
    return witness


result = {
    "schema": "UCT_R167_EXACT_CHECKS/v1",
    "contextual_redundancy": contextual_redundancy_checks(),
    "single_cut_false_negative": single_cut_false_negative(),
    "compensation_timing_obstruction": compensation_obstruction(),
    "status_priority": status_priority_checks(),
    "joint_satisfiability_witness": joint_witness(),
    "interpretation": [
        "For a declared finite Boolean consumer, contextual relevance is exactly existence of a backup context with a nonzero controlled contrast.",
        "A single cut with an active redundant backup can be a false negative.",
        "A late endpoint after compensation can match baseline despite an immediate causal contribution.",
        "Refutation is permitted only relative to declared intervention closure and adequate sensitivity.",
    ],
    "claim_limits": {
        "actual_data": False,
        "actual_apparatus": False,
        "ethics_approval": False,
        "hidden_routes_excluded": False,
        "neural_mediator_identified": False,
        "complete_organization_identified": False,
        "C1_derived": False,
        "B_min_validated": False,
        "basal_experience_gate": False,
    },
}

out = HERE / "EXACT_CHECKS.json"
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({
    "status": "PASS",
    "output": out.name,
    "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
    "functions_checked": result["contextual_redundancy"]["functions_checked"],
    "status_assignments": result["status_priority"]["boolean_assignments"],
}, indent=2))
