#!/usr/bin/env python3
"""Exact checks of the Gray reflection graph and its first frustrated chamber.

All proof certificates use integers. Finite chamber completeness through Q4
uses the explicitly cited Maclagan region counts, not a sampling claim.
The graph bound needed for a positive density remains unproved.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import time
from collections import Counter, defaultdict
from pathlib import Path

SEED = 202610030618
FRUSTRATED_SEED = (2, 20, 16, 5, 12)
GRAY_CEILING_SEED = (1, 14, 4, 12, 20)


def gray(x):
    return x ^ (x >> 1)


def order_and_scores(weights):
    scores = [0]
    for w in weights:
        scores += [s + w for s in scores]
    if len(set(scores)) != len(scores):
        return None
    order = tuple(sorted(range(len(scores)), key=scores.__getitem__))
    return order, tuple(scores[x] for x in order)


def counts(values):
    n = len(values)
    signs = tuple(1 if values[(i + 1) % n] > values[i] else -1
                  for i in range(n))
    cyclic = sum(signs[i] != signs[(i + 1) % n] for i in range(n))
    linear = 1 + sum(signs[i] != signs[i + 1] for i in range(n - 2))
    return linear, cyclic, signs


def graph(order, n):
    size = 1 << n
    assert len(order) == size and len(set(order)) == size
    values = tuple(map(gray, order))
    _, _, signs = counts(values)
    labels = tuple((order[i] ^ order[(i + 1) % size]).bit_length() - 1
                   for i in range(size))
    coupling = defaultdict(int)
    same = 0
    for i in range(size):
        a, b = labels[i], labels[(i + 1) % size]
        coupling[tuple(sorted((a, b)))] += signs[i] * signs[(i + 1) % size]
        if a == b:
            assert signs[i] == -signs[(i + 1) % size]
            same += 1
    diagonal = sum(v for (a, b), v in coupling.items() if a == b)
    assert diagonal == -same
    edges = tuple((a, b, v) for (a, b), v in sorted(coupling.items())
                  if a < b and v)
    weight = sum(abs(v) for _, _, v in edges)
    return {"labels": labels, "signs": signs, "edges": edges,
            "diagonal": tuple((a, v) for (a, b), v in sorted(coupling.items())
                              if a == b and v),
            "D": same, "W": weight}


def energy(edges, mask):
    return sum(v * (-1 if ((mask >> a) ^ (mask >> b)) & 1 else 1)
               for a, b, v in edges)


def optimize(certificate, n):
    # The top coordinate is isolated; global spin inversion is redundant.
    # Fix spin 0 and the top spin positive. n=1 has no off-diagonal edges.
    masks = [x << 1 for x in range(1 << max(0, n - 2))]
    best = max(energy(certificate["edges"], mask) for mask in masks)
    assert (certificate["W"] - best) % 2 == 0
    phi = (certificate["W"] - best) // 2
    return best, phi


def inverse_gray(x):
    result = 0
    while x:
        result ^= x
        x >>= 1
    return result


def check_orbit(weights, reflections, digest, realize=False):
    n = len(weights)
    size = 1 << n
    result = order_and_scores(weights)
    assert result is not None and all(w > 0 for w in weights)
    order, scores = result
    assert all(order[size - 1 - i] == (order[i] ^ (size - 1))
               for i in range(size))
    certificate = graph(order, n)
    assert all(b < n - 1 for a, b, v in certificate["edges"])
    best, phi = optimize(certificate, n)
    expected_min = (size + certificate["D"] - best) // 2
    assert 2 * expected_min == size + certificate["D"] - best
    fastest = min(range(n), key=weights.__getitem__)
    actual_min = size
    checked = 0
    for z in reflections:
        reflected = tuple(x ^ z for x in order)
        linear, cyclic, actual_signs = counts(tuple(map(gray, reflected)))
        mask = gray(z)
        predicted_signs = tuple(
            e * (-1 if (mask >> h) & 1 else 1)
            for e, h in zip(certificate["signs"], certificate["labels"]))
        assert predicted_signs == actual_signs
        prediction = (size + certificate["D"]
                      - energy(certificate["edges"], mask)) // 2
        assert cyclic == prediction
        assert linear == cyclic - int(fastest == n - 1)
        if realize:
            signed = tuple(-w if (z >> j) & 1 else w
                           for j, w in enumerate(weights))
            assert order_and_scores(signed)[0] == reflected
        actual_min = min(actual_min, cyclic)
        checked += 1
        digest.update(bytes.fromhex(hashlib.sha256(
            json.dumps((n, weights, z, linear, cyclic)).encode()).hexdigest()))
    if checked == size:
        assert actual_min == expected_min
    # Check that the optimizer corresponds to a real signed weight choice.
    minimizing_mask = next(mask << 1 for mask in range(1 << max(0, n - 2))
                           if energy(certificate["edges"], mask << 1) == best)
    z = inverse_gray(minimizing_mask)
    actual_linear, actual_cyclic, _ = counts(tuple(gray(x ^ z) for x in order))
    assert actual_cyclic == expected_min
    assert actual_linear == expected_min - int(fastest == n - 1)
    return certificate, phi, checked


def positive_chambers(n):
    if n == 1:
        seeds = [(1,)]
    elif n == 2:
        seeds = [(1, 2)]
    elif n == 3:
        seeds = [(1, 2, 4), (2, 3, 4)]
    else:
        assert n == 4
        seeds_by_order = {}
        for weights in itertools.combinations(range(1, 13), 4):
            result = order_and_scores(weights)
            if result:
                seeds_by_order.setdefault(result[0], weights)
        assert len(seeds_by_order) == 14
        seeds = list(seeds_by_order.values())
    by_order = {}
    for weights in seeds:
        for permuted in itertools.permutations(weights):
            by_order.setdefault(order_and_scores(permuted)[0], permuted)
    expected_positive = {1: 1, 2: 2, 3: 12, 4: 336}[n]
    assert len(by_order) == expected_positive
    # The positive orthant gives one of 2^n sign-reflection copies.
    expected_total = {1: 2, 2: 8, 3: 96, 4: 5376}[n]
    signed_orders = {tuple(x ^ z for x in order)
                     for order in by_order for z in range(1 << n)}
    assert len(signed_orders) == expected_total
    return sorted(by_order.values())


def check_small_chambers(digest):
    receipts = []
    for n in range(1, 5):
        edges_histogram = Counter()
        minimum = 1 << n
        reflections = 0
        weights_list = positive_chambers(n)
        for weights in weights_list:
            certificate, phi, checked = check_orbit(
                weights, range(1 << n), digest, realize=True)
            assert phi == 0
            edges_histogram[len(certificate["edges"])] += 1
            if n == 4:
                assert len(certificate["edges"]) <= 2
            best, _ = optimize(certificate, n)
            minimum = min(minimum, ((1 << n) + certificate["D"] - best) // 2)
            reflections += checked
        receipts.append({"n": n, "positive_chambers": len(weights_list),
                         "all_signed_sweeps_checked": reflections,
                         "frustrated_chambers": 0,
                         "off_diagonal_edge_histogram": dict(edges_histogram),
                         "cyclic_minimum": minimum, "violations": 0})
    return receipts


def check_first_frustration(digest):
    weights = FRUSTRATED_SEED
    order, scores = order_and_scores(weights)
    certificate, phi, checked = check_orbit(weights, range(32), digest, realize=True)
    assert certificate["edges"] == ((0, 2, -2), (0, 3, 4), (2, 3, 2))
    assert certificate["diagonal"] == ((3, -4), (4, -8))
    assert certificate["D"] == 12 and certificate["W"] == 8 and phi == 2
    # Negative triangle: at least one edge must be unsatisfied, weight >= 2.
    assert (-2) * 4 * 2 < 0
    best, _ = optimize(certificate, 5)
    assert best == 4
    histogram = Counter()
    for z in range(32):
        linear, cyclic, _ = counts(tuple(gray(x ^ z) for x in order))
        assert linear == cyclic
        histogram[cyclic] += 1
    assert dict(histogram) == {20: 16, 22: 8, 26: 8}
    return {"weights": weights, "ordered_vertices": order,
            "ordered_scores": scores, "graph": certificate,
            "weighted_frustration": phi, "max_off_diagonal_energy": best,
            "independent_edge_relaxation": 18, "true_orbit_minimum": 20,
            "all_reflections": checked, "cyclic_histogram": dict(histogram),
            "minimal_obstruction_dimension": 5, "violations": 0}


def check_row_lift(digest):
    rows = []
    for n in range(5, 15):
        m = n - 5
        lift = 1 << m
        weights = tuple(64 * (1 << j) for j in range(m)) + FRUSTRATED_SEED
        order, scores = order_and_scores(weights)
        certificate = graph(order, n)
        expected_edges = tuple((m + a, m + b, lift * v)
                               for a, b, v in ((0, 2, -2), (0, 3, 4), (2, 3, 2)))
        assert certificate["edges"] == expected_edges
        assert certificate["D"] == 12 * lift
        assert certificate["W"] == 8 * lift
        best, phi = optimize(certificate, n)
        assert best == 4 * lift and phi == 2 * lift
        assert ((1 << n) + certificate["D"] - best) // 2 == 20 * lift
        actual_histogram = Counter()
        for top_reflection in range(32):
            z = top_reflection << m
            linear, cyclic, _ = counts(tuple(gray(x ^ z) for x in order))
            assert linear == cyclic
            actual_histogram[cyclic] += 1
        assert dict(actual_histogram) == {20 * lift: 16, 22 * lift: 8, 26 * lift: 8}
        # Lower reflections have no effect: every edge changes a high bit.
        assert min(certificate["labels"]) >= m
        digest.update(json.dumps((n, expected_edges, phi)).encode())
        rows.append({"n": n, "row_factor": lift, "weighted_frustration": phi,
                     "independent_edge_relaxation": 18 * lift,
                     "true_orbit_minimum": 20 * lift, "gap": 2 * lift,
                     "explicit_reflections_checked": 32, "violations": 0})
    return rows


def check_generic_sample(digest):
    rng = random.Random(SEED)
    receipts = []
    for n in range(5, 13):
        count = 16 if n <= 9 else 8
        checks = 0
        frustrated = 0
        accepted = 0
        while accepted < count:
            weights = tuple(rng.randrange(1, 1000000) for _ in range(n))
            if order_and_scores(weights) is None:
                continue
            reflections = range(1 << n) if n <= 9 else (
                0, (1 << n) - 1, *[rng.randrange(1 << n) for _ in range(14)])
            certificate, phi, checked = check_orbit(
                weights, reflections, digest, realize=n <= 6)
            accepted += 1
            checks += checked
            frustrated += int(phi > 0)
        receipts.append({"n": n, "positive_weight_samples": accepted,
                         "reflections_checked": checks,
                         "frustrated_samples": frustrated,
                         "coverage": "all reflections of sampled magnitudes"
                                     if n <= 9 else "16 sampled reflections per vector",
                         "violations": 0})
    return receipts


def check_central_symmetry_relaxation(digest):
    receipts = []
    for n in range(2, 13):
        size = 1 << n
        half = tuple(inverse_gray(x) for x in range(size // 2))
        order = half + tuple(x ^ (size - 1) for x in reversed(half))
        assert len(set(order)) == size
        assert all(order[size - 1 - i] == order[i] ^ (size - 1)
                   for i in range(size))
        linear, cyclic, _ = counts(tuple(map(gray, order)))
        assert linear == cyclic == 2
        certificate = graph(order, n)
        assert all(b < n - 1 for a, b, v in certificate["edges"])
        best, phi = optimize(certificate, n)
        assert (size + certificate["D"] - best) // 2 == 2
        if n >= 3:
            # The face restriction requires 0 < 1 and 3 < 2, contradictory
            # signs for coordinate 0 in an additive score.
            assert order.index(0) < order.index(1) < order.index(3) < order.index(2)
        digest.update(json.dumps((n, certificate["D"], best, phi)).encode())
        receipts.append({"n": n, "cyclic_runs": 2, "linear_runs": 2,
                         "additive_impossibility_certified": n >= 3})
    return receipts


def main():
    started = time.monotonic()
    digest = hashlib.sha256()
    result = {
        "state": "EXACT_GRAY_REFLECTION_GRAPH_CHECKS_PASS",
        "seed": SEED, "arithmetic": "integer",
        "small_chambers": check_small_chambers(digest),
        "first_frustration": check_first_frustration(digest),
        "all_dimensional_counterexample_row_lifts": check_row_lift(digest),
        "generic_integer_pressure": check_generic_sample(digest),
        "central_symmetry_only_counterexamples": check_central_symmetry_relaxation(digest),
        "literature_count_dependency": {
            "paper": "Maclagan, Boolean Term Orders and the Root System B_n",
            "section": "4", "source": "https://arxiv.org/pdf/math/9809134",
            "region_counts_n1_to_n4": [2, 8, 96, 5376]},
        "scope": "Exact sign-orbit formula, minimal frustrated chamber, growing relaxation gap; no positive-density proof.",
        "violations": 0,
    }
    result["digest"] = digest.hexdigest()
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    path = Path(__file__).with_name("gray_reflection_graph_verification.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
