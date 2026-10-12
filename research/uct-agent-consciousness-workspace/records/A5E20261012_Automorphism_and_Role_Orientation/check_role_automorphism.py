#!/usr/bin/env python3
"""Exact two-object audit for A5E's role-automorphism boundary.

This checks a finite witness family.  It does not prove C1, identify a
phenomenal target, or establish the converse from invariance to definability.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def swapped_structure(bits: tuple[int, ...]) -> tuple[int, ...]:
    # A(0), A(1), R(0,0), R(0,1), R(1,0), R(1,1)
    a0, a1, r00, r01, r10, r11 = bits
    return (a1, a0, r11, r10, r01, r00)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()

    structures = list(itertools.product((0, 1), repeat=6))
    automorphic = [s for s in structures if swapped_structure(s) == s]
    asymmetric = [s for s in structures if swapped_structure(s) != s]

    predicates = list(itertools.product((0, 1), repeat=2))
    invariant_predicates = [h for h in predicates if h[0] == h[1]]
    reversing_predicates = [h for h in predicates if h[0] != h[1]]

    true_automorphism_pairs = [(s, h) for s in automorphic for h in predicates]
    preserved_pairs = [(s, h) for s, h in true_automorphism_pairs if h[0] == h[1]]
    reversal_pairs = [(s, h) for s, h in true_automorphism_pairs if h[0] != h[1]]

    # Parameter transport check: H(x) := (x=p) is covariant only if p is moved.
    parameter_worlds = []
    for p in (0, 1):
        h = tuple(int(x == p) for x in (0, 1))
        p_prime = 1 - p
        h_prime = tuple(int(x == p_prime) for x in (0, 1))
        transported = tuple(h[1 - x] for x in (0, 1))
        parameter_worlds.append(
            {
                "p": p,
                "H": list(h),
                "transported_p": p_prime,
                "H_after_parameter_transport": list(h_prime),
                "swap_of_H": list(transported),
                "covariant": h_prime == transported,
            }
        )

    result = {
        "schema": "uct-a5e-exact-role-automorphism/1",
        "model": {
            "domain": [0, 1],
            "signature": ["unary A", "binary R"],
            "transformation": "swap 0 and 1",
        },
        "counts": {
            "all_structures": len(structures),
            "swap_automorphism_structures": len(automorphic),
            "swap_nonautomorphism_structures": len(asymmetric),
            "all_unary_target_predicates": len(predicates),
            "invariant_target_predicates": len(invariant_predicates),
            "reversing_target_predicates": len(reversing_predicates),
            "true_automorphism_structure_target_pairs": len(true_automorphism_pairs),
            "preserved_pairs": len(preserved_pairs),
            "reversal_pairs": len(reversal_pairs),
        },
        "equalities": {
            "automorphism_conditions": ["A0=A1", "R00=R11", "R01=R10"],
            "parameter_free_definability_necessity": "Any parameter-free definable H must be preserved by every automorphism.",
            "reversal_implication": "If H reverses under the swap, then H is not parameter-free definable from this K on a swap-automorphic structure.",
        },
        "parameter_transport": parameter_worlds,
        "assertions": {
            "automorphism_count_is_8": len(automorphic) == 8,
            "nonautomorphism_count_is_56": len(asymmetric) == 56,
            "preserved_and_reversal_split_is_16_16": (len(preserved_pairs), len(reversal_pairs)) == (16, 16),
            "all_parameter_transports_covary": all(w["covariant"] for w in parameter_worlds),
        },
        "scope_limit": "Finite enumeration verifies the declared witness counts and parameter covariance. The definability-to-invariance implication is standard model theory, not inferred from these counts.",
    }

    assert all(result["assertions"].values())
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
