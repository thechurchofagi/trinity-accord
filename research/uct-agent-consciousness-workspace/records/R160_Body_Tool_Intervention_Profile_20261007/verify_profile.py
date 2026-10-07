#!/usr/bin/env python3
"""Exact finite checks for the R160 protocol-relative body/tool profile.

These checks verify only the declared finite classifier and latent-label
symmetry witness.  They are not physiological or phenomenal validation.
"""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path


EPSILON = Fraction(1, 4)
GRID = tuple(Fraction(i, 4) for i in range(5))


def classify(a, x, b, y):
    """a/x affect body-only readout; b/y affect tool-only readout.

    Columns are independently grounded body-afferent and tool-transform
    perturbations.  Off-diagonal effects x,b are explicitly permitted.
    """
    body = a > EPSILON and a - x > EPSILON
    tool = y > EPSILON and y - b > EPSILON
    if body and tool:
        return "overlap"
    if body:
        return "body_dominant_only"
    if tool:
        return "tool_dominant_only"
    return "neither"


def swapped_function(f):
    # pi(z)=1-z; f' = pi o f o pi^{-1}
    return tuple(1 - f[1 - z] for z in (0, 1))


def swapped_emission(e):
    # e' = e o pi^{-1}
    return tuple(e[1 - z] for z in (0, 1))


def trace(z0, transitions, emission, inputs):
    z = z0
    out = [emission[z]]
    for u in inputs:
        z = transitions[u][z]
        out.append(emission[z])
    return tuple(out)


def main():
    counts = {k: 0 for k in (
        "body_dominant_only", "tool_dominant_only", "overlap", "neither"
    )}
    coupled_counts = {k: 0 for k in counts}
    examples = {}
    for a, x, b, y in product(GRID, repeat=4):
        label = classify(a, x, b, y)
        counts[label] += 1
        if x > 0 and b > 0:
            coupled_counts[label] += 1
            examples.setdefault(label, [str(a), str(x), str(b), str(y)])

    assert sum(counts.values()) == len(GRID) ** 4 == 625
    assert all(counts[k] > 0 for k in counts)
    assert all(coupled_counts[k] > 0 for k in coupled_counts)
    assert classify(Fraction(4, 5), Fraction(2, 5),
                    Fraction(3, 10), Fraction(9, 10)) == "overlap"

    functions = list(product((0, 1), repeat=2))
    label_checks = 0
    for f_body, f_tool, emission, z0, inputs in product(
        functions, functions, functions, (0, 1), product((0, 1), repeat=3)
    ):
        transitions = (f_body, f_tool)
        swapped = (swapped_function(f_body), swapped_function(f_tool))
        lhs = trace(z0, transitions, emission, inputs)
        rhs = trace(1 - z0, swapped, swapped_emission(emission), inputs)
        assert lhs == rhs
        label_checks += 1
    assert label_checks == 1024

    result = {
        "schema": "UCT_R160_EXACT_CHECKS/v1",
        "epsilon": str(EPSILON),
        "grid": [str(x) for x in GRID],
        "effect_matrices_checked": 625,
        "category_counts": counts,
        "strictly_cross_modulated_category_counts": coupled_counts,
        "strictly_cross_modulated_examples_a_x_b_y": examples,
        "categories_jointly_nonempty": True,
        "overlap_allowed": True,
        "latent_label_swap_trace_checks": label_checks,
        "latent_label_swap_horizon": 3,
        "latent_label_swap_status": "PASS",
        "interpretation": (
            "Finite profile categories and a standard latent-state label symmetry "
            "were checked exactly. This does not establish actual human realization, "
            "anatomical membership, familiar ownership, C1, or semantic completeness."
        ),
    }
    out = Path(__file__).with_name("EXACT_CHECKS.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
