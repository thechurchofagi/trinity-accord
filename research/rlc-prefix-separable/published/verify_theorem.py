#!/usr/bin/env python3
"""Finite independent checks for the prefix-separable run-complexity proof.

Complete enumeration of all leaf permutations and all tree signs in dimensions
1--3 checks the analytic ingredients. Larger separator checks are explicitly
sampled. This program does not prove the all-dimensional theorem or priority.
Requires Python 3 and NumPy; uses no floating-point feasibility solver.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

import numpy as np


def tree_rank(n, signs):
    """Construct the full vertex order recursively, without an LCA formula."""
    def visit(node, left, right):
        if right - left == 1:
            return [left]
        middle = (left + right) // 2
        a = visit(2 * node + 1, left, middle)
        b = visit(2 * node + 2, middle, right)
        return a + b if signs[node] == 1 else b + a
    order = visit(0, 0, 1 << n)
    rank = [0] * len(order)
    for i, vertex in enumerate(order):
        rank[vertex] = i
    return rank


def signs_from_codes(codes, nodes):
    return np.array([[1 if (code >> j) & 1 else -1 for j in range(nodes)]
                     for code in codes], dtype=np.int8)


def lca_label(a, b, n):
    j = (a ^ b).bit_length() - 1
    node = (1 << (n - 1 - j)) - 1 + (a >> (j + 1))
    direction = ((b >> j) & 1) - ((a >> j) & 1)
    return node, direction


def scalar_runs(values):
    signs = [1 if b > a else -1 for a, b in zip(values, values[1:])]
    return 1 + sum(a != b for a, b in zip(signs, signs[1:]))


def alternating_length(values):
    up, down = [1] * len(values), [1] * len(values)
    for j in range(len(values)):
        for i in range(j):
            if values[i] < values[j]:
                up[j] = max(up[j], down[i] + 1)
            else:
                down[j] = max(down[j], up[i] + 1)
    return max(up + down)


def check_all_permutations():
    rows = []
    for n in range(1, 4):
        size, nodes = 1 << n, (1 << n) - 1
        codes = np.arange(1 << nodes, dtype=np.int32)
        spins = signs_from_codes(codes, nodes)
        ranks = np.array([tree_rank(n, signs) for signs in spins], dtype=np.int16)
        count, tail_checks, flip_checks = 0, 0, 0
        for permutation in itertools.permutations(range(size)):
            actual_signs = np.sign(np.diff(ranks[:, permutation], axis=1))
            labels = [lca_label(a, b, n) for a, b in zip(permutation, permutation[1:])]
            indices = np.array([u for u, _ in labels], dtype=np.int32)
            eta = np.array([direction for _, direction in labels], dtype=np.int8)
            predicted_signs = spins[:, indices] * eta
            assert np.array_equal(actual_signs, predicted_signs)
            runs = 1 + np.count_nonzero(actual_signs[:, 1:] != actual_signs[:, :-1], axis=1)
            repeats = int(np.count_nonzero(indices[1:] == indices[:-1]))
            assert 2 * int(runs.sum()) == len(codes) * (size + repeats)
            multiplicities = np.bincount(indices, minlength=nodes)
            assert np.all(runs >= int(multiplicities.max()))
            for node in range(nodes):
                flipped = runs[codes ^ (1 << node)]
                assert np.all(np.abs(flipped - runs) <= 2 * multiplicities[node])
                flip_checks += len(codes)
            for threshold in range(1, size // 2):
                bad = int(np.count_nonzero(runs <= threshold))
                if int(multiplicities.max()) > threshold:
                    assert bad == 0
                else:
                    exponent = Fraction((size - 2 * threshold) ** 2,
                                        8 * threshold * (size - 1))
                    # All exponents in the tested dimensions are below one.
                    # exp(-a) >= 1-a, so this rational stronger check certifies
                    # the finite instance without floating-point exponentials.
                    assert exponent < 1
                    assert Fraction(bad, len(codes)) <= 1 - exponent
                tail_checks += 1
            count += 1
        rows.append({"dimension": n, "vertices": size, "tree_sign_assignments": len(codes),
                     "leaf_permutations": count, "rank_sequences_checked": count * len(codes),
                     "spin_flip_comparisons": flip_checks, "finite_tail_checks": tail_checks,
                     "coverage": "exhaustive"})
    return rows


def check_prefix_separators():
    rng = random.Random(20261002)
    rows = []
    for n in range(1, 7):
        size, nodes = 1 << n, (1 << n) - 1
        codes = list(range(1 << nodes)) if n <= 3 else [rng.getrandbits(nodes) for _ in range(64)]
        spins = signs_from_codes(codes, nodes)
        vertices = np.arange(size, dtype=np.int64)
        bits = np.array([[(int(x) >> j) & 1 for j in range(n)] for x in vertices], dtype=np.int64)
        checked = 0
        for signs in spins:
            rank = np.array(tree_rank(n, signs), dtype=np.int64)
            order = np.argsort(rank)
            for length in range(1, size):
                z = int(order[length])
                coefficients = np.array([3 ** j * int(signs[(1 << (n - 1 - j)) - 1 + (z >> (j + 1))])
                                         for j in range(n)], dtype=np.int64)
                scores = (bits - bits[z]) @ coefficients
                assert np.all(scores[rank < length] <= -1)
                assert np.all(scores[rank >= length] >= 0)
                assert np.array_equal(scores < Fraction(-1, 2), rank < length)
                checked += 1
        rows.append({"dimension": n, "sign_assignments_checked": len(codes),
                     "prefixes_checked": checked,
                     "coverage": "all signs" if n <= 3 else "64 reproducibly sampled signs"})
    return rows


def check_statistic_and_counterexamples():
    count = 0
    for size in range(2, 8):
        for permutation in itertools.permutations(range(size)):
            assert alternating_length(permutation) == scalar_runs(permutation) + 1
            count += 1
    rank = [0, 2, 3, 1]
    assert tuple(x + 1 for x in rank) not in {(2, 4, 1, 3), (3, 1, 4, 2)}
    prefix = sorted(range(4), key=lambda x: rank[x])[:2]
    assert prefix == [0, 3]
    def bits(x): return (x & 1, (x >> 1) & 1)
    assert tuple(sum(bits(x)[j] for x in [0, 3]) for j in range(2)) == (1, 1)
    assert tuple(sum(bits(x)[j] for x in [1, 2]) for j in range(2)) == (1, 1)
    sweep = sorted(range(4), key=lambda x: -2 * bits(x)[0] + bits(x)[1])
    assert sweep == [1, 3, 0, 2]
    assert [x + 1 for x in sweep] == [2, 4, 1, 3]
    return {"statistic_identity_permutations_checked": count,
            "separable_rank_with_inseparable_cube_prefix": [1, 3, 4, 2],
            "admissible_identity_rank_after_generic_sweep": [2, 4, 1, 3]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=Path(__file__).with_name("verification-receipt.json"))
    args = parser.parse_args()
    started = time.monotonic()
    result = {"state": "FINITE_THEOREM_CHECKS_PASS", "report_number": "TA-TR-2026-22",
              "version": "1.0", "all_leaf_orders": check_all_permutations(),
              "strict_prefix_separators": check_prefix_separators(),
              "literature_connections": check_statistic_and_counterexamples(),
              "numpy_version": np.__version__,
              "verification_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "scope": "Finite independent implementation checks; analytic all-dimensional proof is in the manuscript.",
              "external_peer_review": False}
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    args.receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
