#!/usr/bin/env python3
"""Integer certificates for face-local consistency without a global sweep.

This checks a relaxation obstruction, NOT a counterexample to the RLC target.
All small-face orders share one positive integer vector. The full permutation
fails an explicit two-inequality additive certificate.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import defaultdict
from pathlib import Path

CASES = ((5, 2), (6, 3), (7, 4), (8, 5), (9, 6),
         (10, 3), (12, 3), (14, 3), (16, 3), (18, 3), (16, 4))


def gray(x):
    return x ^ (x >> 1)


def signed_sums(values, maximum_support):
    out = {0}
    for size in range(1, min(len(values), maximum_support) + 1):
        for chosen in itertools.combinations(values, size):
            sums = [0]
            for a in chosen:
                sums = [s + a for s in sums] + [s - a for s in sums]
            out.update(sums)
    return out


def weights_for(n, k):
    assert 2 <= k <= n - 3
    # The ONLY seed zero relation has support k+1.
    values = [1 << j for j in range(k)] + [(1 << k) - 1]
    decisions = []
    while len(values) < n:
        forbidden = signed_sums(values, k - 1)
        a = values[-1] + 1
        while a in forbidden:
            a += 1
        decisions.append({"coordinate": len(values), "value": a,
                          "forbidden_distinct_values": len(forbidden)})
        values.append(a)
    assert sum(values) <= (2 * n) ** (k + 1)
    return tuple(values), decisions


def subset_scores(values):
    out = [0]
    for a in values:
        out += [s + a for s in out]
    return out


def central_refinement(values):
    n = len(values)
    size = 1 << n
    total = sum(values)
    scores = subset_scores(values)
    buckets = defaultdict(list)
    for x, score in enumerate(scores):
        buckets[score].append(x)
    lower = []
    for score in sorted(buckets):
        if 2 * score < total:
            lower.extend(sorted(buckets[score], key=gray))
    center = []
    if total % 2 == 0 and total // 2 in buckets:
        left = sorted((x for x in buckets[total // 2]
                       if not (x >> (n - 1)) & 1), key=gray)
        center = left + [x ^ (size - 1) for x in reversed(left)]
    order = lower + center + [x ^ (size - 1) for x in reversed(lower)]
    assert len(order) == size and len(set(order)) == size
    return tuple(order), scores, len(buckets)


def direct_counts(values):
    signs = [1 if b > a else -1 for a, b in zip(values, values[1:])]
    linear = 1 + sum(a != b for a, b in zip(signs, signs[1:]))
    closing = 1 if values[0] > values[-1] else -1
    cyclic = (linear - 1 + int(signs[-1] != closing)
              + int(closing != signs[0]))
    return linear, cyclic


def verify_case(n, k, digest):
    values, decisions = weights_for(n, k)
    if k == 3:
        assert values == (1, 2) + tuple(3 * j - 2 for j in range(2, n))
    order, scores, buckets = central_refinement(values)
    size = 1 << n
    total = sum(values)
    positions = [0] * size
    for i, x in enumerate(order):
        positions[x] = i
    # Independent global strict-score audit certifies every non-tied pair.
    assert all(scores[a] <= scores[b] for a, b in zip(order, order[1:]))
    assert all(order[size - 1 - i] == (order[i] ^ (size - 1))
               for i in range(size))
    # Check all coordinate sets, using subset-sum genericity, independently
    # of the signed-sum avoidance generator. Every parallel face differs
    # by a score translation and is therefore covered by this certificate.
    coordinate_sets = 0
    face_subset_scores = 0
    for free in itertools.combinations(range(n), k):
        local = subset_scores([values[j] for j in free])
        assert len(set(local)) == 1 << k
        coordinate_sets += 1
        face_subset_scores += len(local)
    direct_pairs = 0
    if n <= 10:
        for r in range(1, k + 1):
            for support in itertools.combinations(range(n), r):
                mask = sum(1 << j for j in support)
                for x in range(size):
                    y = x ^ mask
                    if x < y:
                        assert scores[x] != scores[y]
                        assert (scores[x] < scores[y]) == (
                            positions[x] < positions[y])
                        direct_pairs += 1
    u, v, z = (1 << k) - 1, 1 << k, 1 << (k + 1)
    assert scores[u] == scores[v] == values[k]
    assert scores[u | z] == scores[v | z] == values[k] + values[k + 1]
    assert 2 * scores[u | z] < total
    assert gray(u) < gray(v) and gray(u | z) > gray(v | z)
    assert positions[u] < positions[v]
    assert positions[v | z] < positions[u | z]
    d = tuple(((v >> j) & 1) - ((u >> j) & 1) for j in range(n))
    opposite = tuple(((u | z) >> j & 1) - ((v | z) >> j & 1)
                     for j in range(n))
    assert all(a + b == 0 for a, b in zip(d, opposite))
    assert sum(bool(a) for a in d) == k + 1
    ranks = tuple(map(gray, order))
    linear, cyclic = direct_counts(ranks)
    assert linear == cyclic  # First and last edges use coordinate 0.
    assert cyclic <= 4 * buckets <= 4 * (total + 1)
    # Independent cyclic graph sums check the net-energy corollary.
    signs = [1 if ranks[(i + 1) % size] > ranks[i] else -1
             for i in range(size)]
    labels = [(order[i] ^ order[(i + 1) % size]).bit_length() - 1
              for i in range(size)]
    coupling = defaultdict(int)
    diagonal = 0
    for i in range(size):
        h, j = labels[i], labels[(i + 1) % size]
        product = signs[i] * signs[(i + 1) % size]
        coupling[tuple(sorted((h, j)))] += product
        if h == j:
            assert product == -1
            diagonal += 1
    assert all(v == 0 for (h, j), v in coupling.items()
               if h < j and j == n - 1)
    identity_energy = sum(v for (h, j), v in coupling.items() if h < j)
    assert identity_energy - diagonal == size - 2 * cyclic
    # Bucket refinement is globally unique, not a tie in the permutation.
    # It is its pair of opposite strict score inequalities that is invalid.
    record = {
        "n": n, "k": k, "weights": values, "extension_decisions": decisions,
        "vertices": size, "integer_score_range": total,
        "nonempty_score_buckets": buckets, "linear_runs": linear,
        "cyclic_runs": cyclic, "run_density": cyclic / size,
        "identity_net_graph_energy": identity_energy - diagonal,
        "top_couplings_cancel": True,
        "k_coordinate_sets_exhausted": coordinate_sets,
        "local_subset_scores_checked": face_subset_scores,
        "all_parallel_k_faces_certified": coordinate_sets * (1 << (n - k)),
        "direct_small_distance_pairs_checked": direct_pairs,
        "nonadditive_certificate": {
            "u": u, "v": v, "common_disjoint_translation": z,
            "ordered_pairs": [[u, v], [v | z, u | z]],
            "positions": [[positions[u], positions[v]],
                          [positions[v | z], positions[u | z]]],
            "difference_rows": [d, opposite],
            "positive_row_multipliers": [1, 1],
            "row_sum": [0] * n,
            "comparison_support": k + 1,
            "tied_primary_scores": [scores[u], scores[u | z]],
        },
        "order_sha256": hashlib.sha256(
            json.dumps(order, separators=(",", ":")).encode()).hexdigest(),
        "violations": 0,
    }
    digest.update(json.dumps(record, sort_keys=True).encode())
    return record


def main():
    start = time.monotonic()
    digest = hashlib.sha256()
    cases = [verify_case(n, k, digest) for n, k in CASES]
    out = {
        "state": "EXACT_FACE_LOCAL_RELAXATION_OBSTRUCTION_PASS",
        "arithmetic": "integer; no LP solver or floating feasibility",
        "cases": cases,
        "vertices_checked": sum(c["vertices"] for c in cases),
        "coordinate_sets_checked": sum(
            c["k_coordinate_sets_exhausted"] for c in cases),
        "direct_pairs_checked": sum(
            c["direct_small_distance_pairs_checked"] for c in cases),
        "scope": "Exact nonadditive refinements locally sharing one vector; "
                 "NOT actual additive sweeps and NOT RLC upper bounds.",
        "all_dimensional_results": {
            "parameters": "every n >= k+3, k >= 2",
            "score_range_bound": "(2*n)**(k+1)",
            "runs_bound": "4*(sum(weights)+1)",
            "local_face_dimension": "k",
            "subexponential_choice": "k=o(n/log(n)), k>=2",
            "positive_density_target": "OPEN",
        },
        "violations": 0,
        "digest": digest.hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "elapsed_seconds": round(time.monotonic() - start, 3),
    }
    target = Path(__file__).with_name("face_local_obstruction_verification.json")
    target.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "cases"}, indent=2))
    for c in cases:
        print(json.dumps({k: c[k] for k in
              ("n", "k", "integer_score_range", "nonempty_score_buckets",
               "cyclic_runs", "run_density")}))


if __name__ == "__main__":
    main()
