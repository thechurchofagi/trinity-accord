#!/usr/bin/env python3
"""Exact finite witnesses for R192's signature-relative invariance claims.

The script does not test consciousness.  It enumerates Boolean predicates over a
declared four-bit toy signature and verifies extensionality, projection limits,
label-swap invariance, bridge underdetermination, and the logical separation of
installed use from positive diagnostic evidence.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


FEATURES = (
    "online_authorization",
    "actual_retained_revision",
    "bearer_directed_coupling",
    "actual_consumer_use",
)
STATES = tuple(itertools.product((0, 1), repeat=len(FEATURES)))
CURRENT_COORDS = (0, 2, 3)


def truth(mask: int, index: int) -> int:
    return (mask >> index) & 1


def state_index(state: tuple[int, ...]) -> int:
    return sum(bit << i for i, bit in enumerate(state))


def projection(state: tuple[int, ...], coords: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(state[i] for i in coords)


def projection_index(projected: tuple[int, ...]) -> int:
    return sum(bit << i for i, bit in enumerate(projected))


def main() -> None:
    complete_functions = range(1 << len(STATES))
    projected_states = tuple(itertools.product((0, 1), repeat=len(CURRENT_COORDS)))
    projection_functions = range(1 << len(projected_states))

    frozen = (1, 0, 1, 1)
    formed = (1, 1, 1, 1)
    identical_a = (1, 1, 1, 1)
    identical_b = tuple(identical_a)

    # Every complete-signature predicate is extensional: the same complete
    # state receives the same result irrespective of an external source label.
    complete_twin_checks = 0
    complete_twin_invariant = True
    label_swap_invariant = True
    for mask in complete_functions:
        va = truth(mask, state_index(identical_a))
        vb = truth(mask, state_index(identical_b))
        complete_twin_checks += 1
        complete_twin_invariant &= va == vb
        # Labels "adaptive_reflex" and "experienced_endorsement" are not
        # inputs to an admissible complete-signature predicate.
        label_swap_invariant &= va == vb

    frozen_projection = projection(frozen, CURRENT_COORDS)
    formed_projection = projection(formed, CURRENT_COORDS)
    projection_checks = 0
    projection_cannot_separate = True
    for mask in projection_functions:
        vf = truth(mask, projection_index(frozen_projection))
        vg = truth(mask, projection_index(formed_projection))
        projection_checks += 1
        projection_cannot_separate &= vf == vg

    # The history coordinate itself separates the pair after signature
    # expansion.  This repairs the projection collision but does not name an
    # experiential quality.
    history_predicate_separates = frozen[1] != formed[1]

    # Two sparse external target labels leave 14 of 16 truth-table entries
    # unconstrained.  This counts compatible complete-signature bridges; it is
    # a finite underdetermination witness, not an empirical estimate.
    sample = {
        state_index((0, 0, 0, 0)): 0,
        state_index((1, 1, 1, 1)): 1,
    }
    compatible_masks = [
        mask
        for mask in complete_functions
        if all(truth(mask, idx) == value for idx, value in sample.items())
    ]

    # Actual route use and positive test evidence are distinct variables.
    # All four pairs are logically representable; neither direction follows
    # without an additional reliability premise.
    use_test_pairs = list(itertools.product((0, 1), repeat=2))
    positive_test_without_use = (0, 1) in use_test_pairs
    use_without_positive_test = (1, 0) in use_test_pairs

    checks = {
        "complete_twin_invariance_all_boolean_predicates": complete_twin_invariant,
        "external_source_label_swap_changes_no_internal_predicate": label_swap_invariant,
        "current_projection_collision_is_exact": frozen_projection == formed_projection,
        "all_current_projection_predicates_fail_to_separate_pair": projection_cannot_separate,
        "history_expansion_separates_declared_pair": history_predicate_separates,
        "complete_pair_is_not_a_complete_twin_after_history_expansion": frozen != formed,
        "sparse_named_targets_leave_multiple_compatible_bridges": len(compatible_masks) > 1,
        "compatible_bridge_count_matches_2_pow_14": len(compatible_masks) == 2**14,
        "positive_test_does_not_entail_actual_use_in_declared_epistemic_model": positive_test_without_use,
        "actual_use_does_not_entail_positive_test_without_reliability_premise": use_without_positive_test,
    }

    output = {
        "schema": "uct-r192-complete-twin-check/1",
        "research_id": "R192-CTBI-20261009",
        "signature": {"features": FEATURES, "state_count": len(STATES)},
        "current_projection": {
            "coordinates": [FEATURES[i] for i in CURRENT_COORDS],
            "state_count": len(projected_states),
            "predicate_count": 1 << len(projected_states),
        },
        "complete_predicate_count": 1 << len(STATES),
        "complete_twin_predicate_evaluations": complete_twin_checks,
        "projection_predicate_evaluations": projection_checks,
        "declared_pair": {
            "frozen_reflex": dict(zip(FEATURES, frozen)),
            "formed_controller": dict(zip(FEATURES, formed)),
            "equal_current_projection": frozen_projection == formed_projection,
            "equal_complete_signature": frozen == formed,
        },
        "sparse_target_sample_size": len(sample),
        "compatible_complete_bridge_count": len(compatible_masks),
        "use_test_pairs": [
            {"actual_use": use, "positive_test": test} for use, test in use_test_pairs
        ],
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation_boundary": (
            "Enumeration proves only the displayed finite extensional/projection facts. "
            "The general complete-twin result is ordinary isomorphism/extensionality reasoning. "
            "No row establishes actual installation, a named feeling, report accuracy, or consciousness."
        ),
    }
    canonical = json.dumps(output, sort_keys=True, separators=(",", ":")).encode()
    output["content_sha256_without_this_field"] = hashlib.sha256(canonical).hexdigest()
    target = Path(__file__).with_name("EXACT_RESULTS.json")
    target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_checks_pass": output["all_checks_pass"], "checks": len(checks), "compatible_bridges": len(compatible_masks)}))
    if not output["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
