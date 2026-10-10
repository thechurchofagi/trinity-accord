#!/usr/bin/env python3
"""Exact finite witnesses for the area-3a double-selectivity audit.

This is ordinary linear algebra over rational numbers plus exhaustive binary
enumeration. It is not a neural model and supplies no experiential evidence.
"""
from fractions import Fraction
from itertools import product
import json


PACKAGES = {
    # latent order: selected->3a, collateral->3a,
    #               selected->neighbour, collateral->neighbour
    "pooled": [[1, 1, 1, 1]],
    "consumer_only": [[1, 1, 0, 0]],
    "source_only": [[1, 0, 1, 0]],
    "crossed_but_no_interaction": [[1, 1, 0, 0], [1, 0, 1, 0]],
    "target_selective": [[1, 0, 0, 0]],
}


def rref(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    if not a:
        return a, []
    rows, cols, pivot_cols = len(a), len(a[0]), []
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = a[r][c]
        a[r] = [v / scale for v in a[r]]
        for i in range(rows):
            if i != r and a[i][c]:
                factor = a[i][c]
                a[i] = [x - factor * y for x, y in zip(a[i], a[r])]
        pivot_cols.append(c)
        r += 1
        if r == rows:
            break
    return a, pivot_cols


def rank(matrix):
    return len(rref(matrix)[1])


def target_identifiable(matrix):
    e = [1, 0, 0, 0]
    return rank(matrix) == rank(matrix + [e])


def observation(matrix, latent):
    return tuple(sum(a * b for a, b in zip(row, latent)) for row in matrix)


def binary_twins(matrix):
    groups = {}
    for latent in product((0, 1), repeat=4):
        groups.setdefault(observation(matrix, latent), []).append(latent)
    witnesses = []
    for obs, rows in groups.items():
        for x in rows:
            for y in rows:
                if x[0] != y[0]:
                    witnesses.append({"observation": obs, "target_0": x, "target_1": y})
                    break
            if witnesses:
                break
        if witnesses:
            break
    return witnesses


def main():
    results = {}
    for name, matrix in PACKAGES.items():
        results[name] = {
            "matrix": matrix,
            "rank": rank(matrix),
            "target_coordinate_in_row_span": target_identifiable(matrix),
            "binary_target_switch_twin": (binary_twins(matrix) or [None])[0],
        }
    assertions = {
        "pooled_fails": not results["pooled"]["target_coordinate_in_row_span"],
        "consumer_axis_alone_fails": not results["consumer_only"]["target_coordinate_in_row_span"],
        "source_axis_alone_fails": not results["source_only"]["target_coordinate_in_row_span"],
        "two_margins_still_fail": not results["crossed_but_no_interaction"]["target_coordinate_in_row_span"],
        "target_selective_succeeds": results["target_selective"]["target_coordinate_in_row_span"],
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)
    print(json.dumps({"latent_order": ["S_to_A3a", "Q_to_A3a", "S_to_N", "Q_to_N"],
                      "packages": results, "assertions": assertions}, indent=2))


if __name__ == "__main__":
    main()
