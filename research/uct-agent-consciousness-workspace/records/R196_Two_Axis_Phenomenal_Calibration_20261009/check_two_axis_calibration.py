#!/usr/bin/env python3
"""Exact finite checks for R196's structure x value calibration boundary."""

from __future__ import annotations

import itertools
import json


CELLS = tuple(itertools.product((0, 1), repeat=2))  # (A, V)


def table(bits: tuple[int, int, int, int]) -> dict[tuple[int, int], int]:
    return {cell: bits[index] for index, cell in enumerate(CELLS)}


def structural_sensitive(t: dict[tuple[int, int], int]) -> bool:
    return all(t[(0, v)] != t[(1, v)] for v in (0, 1))


def value_invariant(t: dict[tuple[int, int], int]) -> bool:
    return all(t[(a, 0)] == t[(a, 1)] for a in (0, 1))


def value_sensitive(t: dict[tuple[int, int], int]) -> bool:
    return all(t[(a, 0)] != t[(a, 1)] for a in (0, 1))


def bits_of(t: dict[tuple[int, int], int]) -> str:
    return "".join(str(t[cell]) for cell in CELLS)


def main() -> None:
    functions = [table(bits) for bits in itertools.product((0, 1), repeat=4)]
    structure_only = [t for t in functions if structural_sensitive(t) and value_invariant(t)]
    crossed_outcomes = [t for t in functions if structural_sensitive(t) and value_sensitive(t)]
    stable_targets = [t for t in functions if structural_sensitive(t) and value_invariant(t)]

    constrained_triples = [
        (m, y, f)
        for m in functions
        for y in functions
        for f in functions
        if m in structure_only and y in crossed_outcomes and f in stable_targets
    ]

    marker_anchor = table((0, 0, 1, 1))  # M=A.
    outcome_rule = table((0, 1, 1, 0))  # Y=A xor V.
    observed_anchored = [
        (m, y, f)
        for m, y, f in constrained_triples
        if m == marker_anchor and y == outcome_rule
    ]
    endpoint_anchored = [
        triple for triple in observed_anchored if triple[2][(1, 0)] == 1
    ]

    assert len(functions) == 16
    assert sorted(bits_of(t) for t in structure_only) == ["0011", "1100"]
    assert sorted(bits_of(t) for t in crossed_outcomes) == ["0110", "1001"]
    assert len(constrained_triples) == 8
    assert len(observed_anchored) == 2
    assert sorted(bits_of(f) for _, _, f in observed_anchored) == ["0011", "1100"]
    assert len(endpoint_anchored) == 1
    assert bits_of(endpoint_anchored[0][2]) == "0011"

    # Outcome reversal at fixed A flips Y while M and each admissible F stay fixed.
    for m, y, f in constrained_triples:
        for a in (0, 1):
            assert y[(a, 0)] != y[(a, 1)]
            assert m[(a, 0)] == m[(a, 1)]
            assert f[(a, 0)] == f[(a, 1)]

    result = {
        "research_id": "R196-TPD-20261009",
        "cell_order": ["A0V0", "A0V1", "A1V0", "A1V1"],
        "all_boolean_tables": len(functions),
        "structure_sensitive_tables": sum(structural_sensitive(t) for t in functions),
        "structure_sensitive_and_value_invariant_tables": len(structure_only),
        "structure_only_tables": sorted(bits_of(t) for t in structure_only),
        "structure_and_value_sensitive_tables": len(crossed_outcomes),
        "crossed_outcome_tables": sorted(bits_of(t) for t in crossed_outcomes),
        "all_marker_outcome_target_triples": len(functions) ** 3,
        "triples_after_two_axis_constraints": len(constrained_triples),
        "triples_after_numeric_marker_and_outcome_anchors": len(observed_anchored),
        "remaining_target_tables": sorted(bits_of(f) for _, _, f in observed_anchored),
        "triples_after_independent_positive_endpoint": len(endpoint_anchored),
        "selected_target_table": bits_of(endpoint_anchored[0][2]),
        "checks": {
            "full_factorial_identifies_each_declared_truth_table": True,
            "structure_tracking_excludes_value_and_interaction_dependence": True,
            "value_reversal_leaves_marker_and_stable_target_fixed": True,
            "numeric_marker_and_functional_outcome_do_not_orient_target": True,
            "one_independent_phenomenal_endpoint_orients_the_pair": True,
        },
        "interpretive_boundary": (
            "The endpoint condition is exactly the still-open phenomenal-direction premise; "
            "the enumeration does not supply or measure it."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
