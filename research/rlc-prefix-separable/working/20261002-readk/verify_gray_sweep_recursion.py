#!/usr/bin/env python3
"""Integer checks of Gray signed-lex counts, endpoints and row lifting."""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import time
from collections import Counter
from pathlib import Path

import numpy as np


SEED = 202610030543


def gray(x: int) -> int:
    return x ^ (x >> 1)


def linear_and_cyclic(values: list[int]) -> tuple[int, int, list[int]]:
    signs = [1 if b > a else -1 for a, b in zip(values, values[1:])]
    runs = 1 + sum(a != b for a, b in zip(signs, signs[1:]))
    boundary = 1 if values[0] > values[-1] else -1
    cyclic = sum(a != b for a, b in zip(signs, signs[1:]))
    cyclic += int(signs[-1] != boundary) + int(boundary != signs[0])
    assert abs(runs - cyclic) <= 1
    return runs, cyclic, signs


def generic_order(weights: list[int] | tuple[int, ...]) -> list[int] | None:
    n = len(weights)
    scores = [sum(w * ((x >> j) & 1) for j, w in enumerate(weights))
              for x in range(1 << n)]
    if len(set(scores)) != len(scores):
        return None
    return sorted(range(1 << n), key=scores.__getitem__)


def check_comparison_rule() -> int:
    checks = 0
    for n in range(1, 7):
        for x in range(1 << n):
            for y in range(1 << n):
                if x == y:
                    continue
                h = (x ^ y).bit_length() - 1
                direction = ((y >> h) & 1) - ((x >> h) & 1)
                prediction = direction * (-1 if ((x >> (h + 1)) & 1) else 1)
                actual = 1 if gray(y) > gray(x) else -1
                assert actual == prediction
                checks += 1
    return checks


def check_signed_lex(digest: hashlib._Hash) -> list[dict[str, object]]:
    receipts = []
    for n in range(1, 8):
        size = 1 << n
        counter = np.arange(size, dtype=np.int64)
        gray_values = counter ^ (counter >> 1)
        reflections = counter[:, None]
        histogram: Counter[int] = Counter()
        scans = boundary_checks = pair_checks = 0
        for permutation in itertools.permutations(range(n)):
            unreflected = np.zeros(size, dtype=np.int64)
            for t, coordinate in enumerate(permutation):
                unreflected |= ((counter >> t) & 1) << coordinate
            orders = unreflected[None, :] ^ reflections
            values = gray_values[orders]
            signs = values[:, 1:] > values[:, :-1]
            runs = 1 + np.sum(signs[:, 1:] != signs[:, :-1], axis=1)
            closing = values[:, 0] > values[:, -1]
            cycle_signs = np.concatenate((signs, closing[:, None]), axis=1)
            cyclic = np.sum(cycle_signs != np.roll(cycle_signs, -1, axis=1), axis=1)
            fastest = permutation[0]
            if fastest == n - 1:
                expected = size - 1
                assert np.all(cyclic == size)
            else:
                ell = next(t for t in range(1, n) if permutation[t] > fastest)
                block_size = 1 << ell
                blocks = size // block_size
                expected = size - blocks
                assert np.all(cyclic == expected)
                q = permutation.index(fastest + 1)
                boundary_indices = np.arange(block_size - 1, size, block_size)
                boundary_costs = (
                    (cycle_signs[:, (boundary_indices - 1) % size]
                     != cycle_signs[:, boundary_indices]).astype(np.int8)
                    + (cycle_signs[:, boundary_indices]
                       != cycle_signs[:, (boundary_indices + 1) % size]).astype(np.int8)
                )
                assert np.all(np.sum(boundary_costs, axis=1) == blocks)
                for b, index in enumerate(boundary_indices):
                    index = int(index)
                    carry = n if index == size - 1 else ((index + 1) & -(index + 1)).bit_length() - 1
                    if carry >= q:
                        assert np.all(boundary_costs[:, b] == 1)
                    else:
                        partner_index = index ^ (1 << q)
                        partner_block = (partner_index + 1) // block_size - 1
                        assert np.all(boundary_costs[:, b]
                                      + boundary_costs[:, partner_block] == 2)
                        pair_checks += size
                    boundary_checks += size
            assert np.all(runs == expected)
            if n <= 5:
                # Independently realize every reflected order by actual
                # integer subset scores, rather than only a counter map.
                scores = np.zeros_like(orders)
                for t, coordinate in enumerate(permutation):
                    signed_weight = (1 - 2 * ((counter >> coordinate) & 1)) * (1 << t)
                    scores += signed_weight[:, None] * ((orders >> coordinate) & 1)
                assert np.all(np.diff(scores, axis=1) == 1)
            histogram.update(map(int, runs))
            scans += size
            digest.update(bytes(permutation))
            digest.update(int(expected).to_bytes(2, "little"))
        assert min(histogram) == (1 if n == 1 else size // 2)
        receipts.append({
            "n": n,
            "coordinate_permutations": scans // size,
            "reflections_each": size,
            "scans": scans,
            "run_histogram": dict(sorted(histogram.items())),
            "boundary_cost_checks": boundary_checks,
            "paired_boundary_checks": pair_checks,
            "integer_score_realizations": scans if n <= 5 else 0,
            "violations": 0,
        })
    return receipts


def check_endpoint_and_face_identity(rng: random.Random) -> dict[str, int]:
    endpoint_checks = face_checks = 0
    for n in range(2, 11):
        done = 0
        while done < 128:
            weights = [rng.randint(-100_000, 100_000) for _ in range(n)]
            order = generic_order(weights)
            if order is None:
                continue
            values = [gray(x) for x in order]
            runs, cyclic, signs = linear_and_cyclic(values)
            fastest = min(range(n), key=lambda j: abs(weights[j]))
            expected_penalty = int(fastest == n - 1)
            assert cyclic == runs + expected_penalty
            assert (signs[0] == signs[-1]) == (fastest == n - 1)
            endpoint_checks += 1
            parent = generic_order(weights[:-1])
            assert parent is not None
            parent_values = [gray(x) for x in parent]
            upper_values = [gray(x + (1 << (n - 1))) for x in parent]
            assert upper_values == [v + (1 << (n - 1)) for v in reversed(parent_values)]
            face_checks += 1
            done += 1
    return {"endpoint_checks": endpoint_checks, "translated_face_identity_checks": face_checks}


def check_q3_and_nonlex_witness() -> dict[str, object]:
    q3_orders = set()
    for seed in ((1, 2, 4), (2, 3, 4)):
        for permutation in itertools.permutations(range(3)):
            for reflection in range(8):
                weights = [seed[permutation[j]] * (-1 if (reflection >> j) & 1 else 1)
                           for j in range(3)]
                order = generic_order(weights)
                assert order is not None
                q3_orders.add(tuple(order))
    assert len(q3_orders) == 96
    minimum = min(linear_and_cyclic([gray(x) for x in order])[0] for order in q3_orders)
    assert minimum == 4
    weights = (1, 6, 4, 8)
    order = generic_order(weights)
    assert order is not None
    values = [gray(x) for x in order]
    runs, cyclic, _ = linear_and_cyclic(values)
    assert runs == cyclic == 6
    return {"q3_generic_orders": 96, "q3_minimum": minimum,
            "q4_nonlex_witness": {"weights": list(weights), "order": order,
                                  "rank_values": values, "runs": runs,
                                  "signed_lex_minimum": 8}}


def check_counterexamples() -> list[dict[str, object]]:
    receipts = []
    for d in range(2, 16):
        parent_weights = [4 << j for j in range(d - 1)] + [1]
        child_weights = parent_weights + [2]
        parent_order = generic_order(parent_weights)
        child_order = generic_order(child_weights)
        assert parent_order is not None and child_order is not None
        rp = linear_and_cyclic([gray(x) for x in parent_order])[0]
        rc = linear_and_cyclic([gray(x) for x in child_order])[0]
        assert rp == (1 << d) - 1
        assert rc == (1 << d)
        receipts.append({"parent_dimension": d, "child_dimension": d + 1,
                         "parent_weights": parent_weights, "new_weight": 2,
                         "parent_runs": rp, "child_runs": rc,
                         "doubling_loss": 2 * rp - rc, "violations": 0})
    return receipts


def randomized_tree_rank(top_rank: list[int], d: int, m: int, rng: random.Random) -> list[int]:
    """Use independent lower tree orientations, not a Gray implementation."""
    row_count = 1 << m
    full = [-1] * (1 << (d + m))
    for top_vertex in range(1 << d):
        position = 0
        def visit(depth: int, vertex: int) -> None:
            nonlocal position
            if depth == m:
                full[top_vertex * row_count + vertex] = top_rank[top_vertex] * row_count + position
                position += 1
                return
            coordinate = m - 1 - depth
            first = rng.randrange(2)
            for bit in (first, 1 - first):
                visit(depth + 1, vertex | (bit << coordinate))
        visit(0, 0)
    return full


def check_row_lifts(rng: random.Random) -> dict[str, int]:
    gray_checks = independent_lower_checks = 0
    for d in range(1, 6):
        for m in range(1, 5):
            for _ in range(16):
                while True:
                    weights = [rng.randint(-100, 100) for _ in range(d)]
                    top_order = generic_order(weights)
                    if top_order is not None:
                        break
                top_rank = [gray(x) for x in range(1 << d)]
                top_values = [top_rank[x] for x in top_order]
                top_r, top_c, signs = linear_and_cyclic(top_values)
                b = 1 if top_values[0] > top_values[-1] else -1
                endpoint = int(signs[-1] != b) + int(b != signs[0])
                row_count = 1 << m
                separation = 1 + sum(abs(w) for w in weights)
                full_weights = [separation << j for j in range(m)] + weights
                order = generic_order(full_weights)
                assert order is not None
                expected_order = [z * row_count + y for y in range(row_count) for z in top_order]
                assert order == expected_order
                r, c, _ = linear_and_cyclic([gray(x) for x in order])
                assert c == row_count * top_c
                assert r == 1 + row_count * (top_r - 1) + (row_count - 1) * endpoint
                gray_checks += 1
                tree_rank = randomized_tree_rank(top_rank, d, m, rng)
                other_r, other_c, _ = linear_and_cyclic([tree_rank[x] for x in order])
                assert (other_r, other_c) == (r, c)
                independent_lower_checks += 1
    return {"gray_row_lifts": gray_checks,
            "arbitrary_lower_tree_orientation_row_lifts": independent_lower_checks}


def main() -> None:
    started = time.monotonic()
    rng = random.Random(SEED)
    digest = hashlib.sha256()
    lex = check_signed_lex(digest)
    receipt = {
        "state": "GRAY_SWEEP_RECURSION_CHECKS_PASS",
        "seed": SEED,
        "comparison_rule_checks": check_comparison_rule(),
        "signed_lex_exhaustive": lex,
        "signed_lex_scan_count": sum(row["scans"] for row in lex),
        "generic_sweep_identities": check_endpoint_and_face_identity(rng),
        "minimal_nonlex_obstruction": check_q3_and_nonlex_witness(),
        "scalar_doubling_counterexamples": check_counterexamples(),
        "cyclic_row_lifts": check_row_lifts(rng),
        "proof_scope": "signed-lex formula, recurrence counterexample, and cyclic density limit; no general positive-density lower bound",
        "arithmetic": "integer",
        "violations": 0,
        "digest": digest.hexdigest(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    output = Path(__file__).with_name("gray_sweep_recursion_verification.json")
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
