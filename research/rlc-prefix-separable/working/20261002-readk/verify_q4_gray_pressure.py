#!/usr/bin/env python3
"""Finite Q4 pressure test for balanced-tree and forward-Gray candidates.

This regenerates the standard 5,376 labeled Q4 additive orders from the 14
positive sorted chamber representatives.  Its finite conclusions are not
used to extrapolate the all-dimensional theorem.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np


def subset_order(weights: tuple[int, ...]) -> tuple[int, ...] | None:
    scores = [sum(weights[j] * ((x >> j) & 1) for j in range(4)) for x in range(16)]
    if len(set(scores)) != 16:
        return None
    return tuple(sorted(range(16), key=scores.__getitem__))


def additive_orders() -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
    base: dict[tuple[int, ...], tuple[int, ...]] = {}
    for weights in itertools.combinations(range(1, 13), 4):
        order = subset_order(weights)
        if order is not None:
            base.setdefault(order, weights)
    assert len(base) == 14
    labeled = set()
    for weights in base.values():
        for permutation in itertools.permutations(range(4)):
            permuted = tuple(weights[permutation[j]] for j in range(4))
            for reflection in range(16):
                signed = tuple(
                    -permuted[j] if ((reflection >> j) & 1) else permuted[j]
                    for j in range(4)
                )
                order = subset_order(signed)
                assert order is not None
                labeled.add(order)
    assert len(labeled) == 5376
    return sorted(base.values()), sorted(labeled)


def tree_rank(code: int) -> tuple[int, ...]:
    rank = [-1] * 16
    position = 0

    def visit(depth: int, prefix: int, vertex: int) -> None:
        nonlocal position
        if depth == 4:
            rank[vertex] = position
            position += 1
            return
        coordinate = 3 - depth
        node = (1 << depth) - 1 + prefix
        first = (code >> node) & 1
        for bit in (first, 1 - first):
            visit(depth + 1, (prefix << 1) | bit, vertex | (bit << coordinate))

    visit(0, 0, 0)
    return tuple(rank)


def canonical(rank: tuple[int, ...]) -> tuple[int, ...]:
    variants = []
    for reflection in range(16):
        reflected = tuple(rank[x ^ reflection] for x in range(16))
        variants.append(reflected)
        variants.append(tuple(15 - value for value in reflected))
    return min(variants)


def metrics(rank: tuple[int, ...], orders: np.ndarray) -> tuple[int, int, int]:
    values = np.asarray(rank, dtype=np.int16)[orders]
    signs = values[:, 1:] > values[:, :-1]
    turns = np.sum(signs[:, 1:] != signs[:, :-1], axis=1)
    runs = 1 + turns
    boundary = ~(values[:, -1] > values[:, 0])
    endpoint = (signs[:, -1] != boundary).astype(np.int8) + (boundary != signs[:, 0]).astype(np.int8)
    adjusted = turns + endpoint
    return int(runs.min()), int(adjusted.min()), int(np.sum(runs == runs.min()))


def main() -> None:
    started = time.monotonic()
    base, order_tuples = additive_orders()
    orders = np.asarray(order_tuples, dtype=np.uint8)

    representatives: dict[tuple[int, ...], int] = {}
    code_classes = []
    for code in range(1 << 15):
        key = canonical(tree_rank(code))
        code_classes.append(key)
        representatives.setdefault(key, code)
    assert len(representatives) == 1088

    orbit_metrics = {}
    for key, code in representatives.items():
        orbit_metrics[key] = metrics(key, orders)
    full_run_histogram = Counter(orbit_metrics[key][0] for key in code_classes)
    full_adjusted_histogram = Counter(orbit_metrics[key][1] for key in code_classes)
    assert max(full_run_histogram) == 7
    assert full_run_histogram[7] == 832
    assert max(full_adjusted_histogram) == 8
    assert full_adjusted_histogram[8] == 768

    forward_gray = tuple(x ^ (x >> 1) for x in range(16))
    gray_runs, gray_adjusted, gray_minimizers = metrics(forward_gray, orders)
    assert (gray_runs, gray_adjusted, gray_minimizers) == (6, 6, 16)

    digest = hashlib.sha256()
    for order in order_tuples:
        digest.update(bytes(order))
    receipt = {
        "scope": "finite Q4 pressure test; not an all-dimensional extrapolation",
        "positive_sorted_representatives": [list(x) for x in base],
        "labeled_additive_orders": len(order_tuples),
        "tree_orientations": 1 << 15,
        "reflection_reversal_orbits": len(representatives),
        "tree_rlc_histogram": dict(sorted(full_run_histogram.items())),
        "maximum_tree_rlc": 7,
        "maximizing_tree_orientations": 832,
        "row_adjusted_histogram": dict(sorted(full_adjusted_histogram.items())),
        "maximum_row_adjusted_cost": 8,
        "forward_gray_rlc_q4": gray_runs,
        "forward_gray_row_adjusted_cost_q4": gray_adjusted,
        "forward_gray_minimizing_orders": gray_minimizers,
        "implication": "Q4 cannot improve the universal 1/2 tree ceiling, while Q4 already gives a 3/8 forward-Gray row lift; the Q5 certificate improves it to 5/16.",
        "order_digest": digest.hexdigest(),
        "violations": 0,
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    out = Path(__file__).with_name("q4_gray_pressure_verification.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
