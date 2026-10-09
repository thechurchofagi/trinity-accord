#!/usr/bin/env python3
"""Exact finite checks for the R201 robust orientation margin.

This verifies elementary probability inequalities on a declared rational grid.
It does not validate a marker, a human endpoint, actual route use, C1, or an
experience attribution.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path


def fs(x: Fraction) -> str:
    return str(x)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    grid = tuple(Fraction(i, 8) for i in range(9))
    signed_grid = tuple(Fraction(i, 8) for i in range(-8, 9))
    positive_rho = grid[1:]

    checked = 0
    certified = 0
    violations = []
    for p0, p1, rho, residual, q0, q1 in itertools.product(
        grid, grid, positive_rho, signed_grid, grid, grid
    ):
        delta_source = rho * (p1 - p0) + residual
        if not (-1 <= delta_source <= 1):
            continue
        beta = abs(residual)
        epsilon0 = abs(q0 - p0)
        epsilon1 = abs(q1 - p1)
        checked += 1
        if delta_source > beta + epsilon0 + epsilon1:
            certified += 1
            if not q1 - q0 > 0:
                violations.append({
                    "p0": fs(p0), "p1": fs(p1), "rho": fs(rho),
                    "residual": fs(residual), "q0": fs(q0), "q1": fs(q1),
                    "delta_source": fs(delta_source),
                })
                break

    equality_witness = {
        "beta": Fraction(1, 10),
        "epsilon0": Fraction(1, 10),
        "epsilon1": Fraction(1, 10),
        "rho": Fraction(1, 1),
        "p0": Fraction(2, 5),
        "p1": Fraction(3, 5),
        "residual": Fraction(1, 10),
        "q0": Fraction(1, 2),
        "q1": Fraction(1, 2),
    }
    equality_witness["delta_source"] = (
        equality_witness["rho"]
        * (equality_witness["p1"] - equality_witness["p0"])
        + equality_witness["residual"]
    )
    equality_witness["threshold"] = (
        equality_witness["beta"]
        + equality_witness["epsilon0"]
        + equality_witness["epsilon1"]
    )
    equality_witness["delta_target"] = equality_witness["q1"] - equality_witness["q0"]

    below_witness = {
        "beta": Fraction(1, 10),
        "epsilon0": Fraction(1, 10),
        "epsilon1": Fraction(1, 10),
        "rho": Fraction(1, 1),
        "p0": Fraction(2, 5),
        "p1": Fraction(11, 20),
        "residual": Fraction(1, 10),
        "q0": Fraction(1, 2),
        "q1": Fraction(9, 20),
    }
    below_witness["delta_source"] = (
        below_witness["rho"]
        * (below_witness["p1"] - below_witness["p0"])
        + below_witness["residual"]
    )
    below_witness["threshold"] = (
        below_witness["beta"]
        + below_witness["epsilon0"]
        + below_witness["epsilon1"]
    )
    below_witness["delta_target"] = below_witness["q1"] - below_witness["q0"]

    reversed_endpoint_witness = {
        "rho": Fraction(-1, 2),
        "p0": Fraction(1, 4),
        "p1": Fraction(3, 4),
        "residual": Fraction(0),
    }
    reversed_endpoint_witness["delta_source"] = (
        reversed_endpoint_witness["rho"]
        * (reversed_endpoint_witness["p1"] - reversed_endpoint_witness["p0"])
    )

    all_pass = (
        not violations
        and equality_witness["delta_source"] == equality_witness["threshold"]
        and equality_witness["delta_target"] == 0
        and below_witness["delta_source"] < below_witness["threshold"]
        and below_witness["delta_target"] < 0
        and reversed_endpoint_witness["delta_source"] < 0
    )
    result = {
        "schema": "uct-r201-robust-orientation-margin-check/1",
        "grid": {"denominator": 8, "checked_valid_instances": checked},
        "robust_sign_certificate": {
            "certified_instances": certified,
            "violations": violations,
            "statement": "If delta_source > beta + epsilon0 + epsilon1, rho is positive and at most one, |residual|<=beta, and each class-conditional target drift is bounded by epsilon_h, then delta_target>0.",
        },
        "strictness_witnesses": {
            "equality_can_reach_zero": {k: fs(v) for k, v in equality_witness.items()},
            "below_threshold_can_reverse": {k: fs(v) for k, v in below_witness.items()},
            "positive_endpoint_direction_is_required": {k: fs(v) for k, v in reversed_endpoint_witness.items()},
        },
        "all_exact_checks_pass": all_pass,
        "not_proved": [
            "that the adult comparative judgment is positively related to the intended H target",
            "that the residual-bias or cross-domain drift bounds hold in any population",
            "that a route-use test establishes actual same-episode route use",
            "that any marker constitutes experience or that C1 is empirically true",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "checked": checked,
        "certified": certified,
        "violations": len(violations),
        "all_exact_checks_pass": all_pass,
    }, sort_keys=True))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
