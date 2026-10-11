#!/usr/bin/env python3
"""Finite checks for the A4L same-bearer 2x2 installation criterion."""

import hashlib
import json
from collections import defaultdict

LEVELS = {(0, 0), (0, 1), (1, 0), (1, 1)}
INVARIANTS = ("bearer", "event", "consumer", "route", "response_code")


def token(cell, actual, invariant="K0", witness=None, independent=True):
    r, f = actual
    wr, wf = witness if witness is not None else actual
    return {
        "assigned": list(cell),
        "actual": [r, f],
        **{key: invariant for key in INVARIANTS},
        "witness": [wr, wf],
        "pre_outcome": True,
        "witness_independent_of_assignment_and_response": independent,
    }


def slice_key(t):
    return tuple(t[k] for k in INVARIANTS)


def valid_token(t):
    return (
        tuple(t["assigned"]) == tuple(t["actual"])
        and tuple(t["witness"]) == tuple(t["actual"])
        and t["pre_outcome"]
        and t["witness_independent_of_assignment_and_response"]
    )


def assess(tokens):
    slices = defaultdict(list)
    for t in tokens:
        slices[slice_key(t)].append(t)
    per_slice = []
    for key, rows in sorted(slices.items()):
        actual_image = {tuple(t["actual"]) for t in rows}
        valid_image = {tuple(t["actual"]) for t in rows if valid_token(t)}
        per_slice.append({
            "invariant_key": list(key),
            "token_count": len(rows),
            "actual_image": sorted(map(list, actual_image)),
            "valid_image": sorted(map(list, valid_image)),
            "actual_image_size": len(actual_image),
            "valid_image_size": len(valid_image),
            "full_actual_cross": actual_image == LEVELS,
            "full_valid_cross": valid_image == LEVELS,
        })
    return {
        "slice_count": len(slices),
        "any_full_actual_cross": any(x["full_actual_cross"] for x in per_slice),
        "any_full_valid_cross": any(x["full_valid_cross"] for x in per_slice),
        "per_slice": per_slice,
    }


assignments = sorted(LEVELS)
scenarios = {
    "free_cross_with_independent_fidelity": [token(c, c) for c in assignments],
    "structural_coupling_fit_equals_relation": [token(c, (c[0], c[0])) for c in assignments],
    "label_echo_without_actual_manipulation": [token(c, (0, 0), witness=c, independent=False) for c in assignments],
    "comparison_breaking_compensator": [token(c, c, invariant=f"K{c[1]}") for c in assignments],
    "admissible_invariant_preserving_compensator": [token(c, c, invariant="K0") for c in assignments],
}

results = {
    "schema": "a4l-factorial-installability/1",
    "scope": "Finite same-bearer invariant-slice and fidelity checks; no physical, human, AI, or phenomenal installation.",
    "criterion": "A valid same-bearer 2x2 exists only if one frozen invariant slice contains independently witnessed valid tokens for all four actual (relation_use,present_fit) values.",
    "scenarios": {name: assess(rows) for name, rows in scenarios.items()},
    "current_repository_application": {
        "physical_same_bearer_tokens_admitted": 0,
        "valid_actual_cells": [],
        "decision": "NOT_INSTALLED_TERMINATE_CURRENT_CANDIDATE_COMPARISON",
        "reason": "A4A and A4H-A4K provide formation, finite-model, question, prediction and interval contracts, but no one actual bearer supplies four invariant-preserving cells with independent pre-outcome relation-use and fit witnesses.",
    },
    "phenomenal_assignments": 0,
}

assert results["scenarios"]["free_cross_with_independent_fidelity"]["any_full_valid_cross"]
assert not results["scenarios"]["structural_coupling_fit_equals_relation"]["any_full_actual_cross"]
assert not results["scenarios"]["label_echo_without_actual_manipulation"]["any_full_valid_cross"]
assert results["scenarios"]["comparison_breaking_compensator"]["slice_count"] == 2
assert not results["scenarios"]["comparison_breaking_compensator"]["any_full_valid_cross"]
assert results["scenarios"]["admissible_invariant_preserving_compensator"]["any_full_valid_cross"]

canonical = json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
results["canonical_payload_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
