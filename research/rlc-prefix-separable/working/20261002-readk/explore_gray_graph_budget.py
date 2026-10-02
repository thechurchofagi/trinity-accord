#!/usr/bin/env python3
"""Replay translated-face pressure, or the retained exploratory genetic search.

The default mode exactly covers the specified one-parameter magnitude family.
--genetic replays an exploratory 12,000-draw search at each dimension 4--8;
it is not a chamber coverage claim and needs NumPy. It is intentionally not
rerun as part of ordinary verification.
"""

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from verify_gray_reflection_graph import (
    GRAY_CEILING_SEED, graph, optimize, order_and_scores,
)


def translated_pressure():
    start = time.monotonic()
    parent_scores = order_and_scores(GRAY_CEILING_SEED)[1]
    cuts = sorted({a - b for a in parent_scores for b in parent_scores if a > b})
    boundaries = [0] + cuts
    # Parent magnitudes are doubled. Probe t is twice the interval midpoint.
    probes = [a + b for a, b in zip(boundaries, boundaries[1:])]
    probes.append(2 * (cuts[-1] + 1))
    seen = {}
    best_energy = (-1000, None)
    best_surplus = (-1000, None)
    candidates = 0
    for t in probes:
        for weights in itertools.permutations(
                tuple(2 * a for a in GRAY_CEILING_SEED) + (t,)):
            candidates += 1
            result = order_and_scores(weights)
            assert result is not None
            order, scores = result
            if order in seen:
                continue
            seen[order] = weights
            certificate = graph(order, 6)
            maximum, phi = optimize(certificate, 6)
            net_energy = maximum - certificate["D"]
            surplus = certificate["W"] - certificate["D"]
            assert net_energy <= 24 and surplus <= 24
            if net_energy > best_energy[0]:
                best_energy = (net_energy, weights)
            if surplus > best_surplus[0]:
                best_surplus = (surplus, weights)
    assert len(cuts) == 48 and len(probes) == 49
    assert len(seen) == 34560
    assert best_energy[0] == best_surplus[0] == 24
    digest = hashlib.sha256()
    for order in sorted(seen):
        digest.update(bytes(order))
    result = {
        "state": "SPECIFIED_TRANSLATED_FAMILY_EXACT_CHECKS_PASS",
        "parent_magnitudes": GRAY_CEILING_SEED,
        "positive_parent_score_differences": cuts,
        "positive_translation_intervals": len(probes),
        "doubled_integer_translation_probes": probes,
        "all_coordinate_assignments_per_probe": 720,
        "generic_integer_vectors_evaluated": candidates,
        "distinct_positive_q6_chambers": len(seen),
        "sign_orbit_optimization": "exact graph formula; 16 spin states per chamber",
        "signed_sweep_orbits_covered": len(seen) * 64,
        "max_net_energy": best_energy[0],
        "max_net_energy_integer_witness": best_energy[1],
        "max_independent_edge_surplus": best_surplus[0],
        "min_cyclic_count_within_specified_family": 20,
        "sorted_chamber_digest": digest.hexdigest(),
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "scope": "All positive t at fixed five magnitudes, all six coordinate assignments and signs; not all Q6 or all parent-cone magnitudes.",
        "violations": 0,
    }
    Path(__file__).with_name("gray_translated_family_pressure.json").write_text(
        json.dumps(result, indent=2) + "\n")
    return result


def genetic_pressure():
    # Retained original search algorithm, seed, draw count and tie behavior.
    # Only exploratory results are claimed. No completeness is inferred.
    import numpy as np
    import random
    rng = random.Random(202610030618)
    receipts = []
    for n in range(4, 9):
        size = 1 << n
        xs = np.arange(size)
        bits = (xs[:, None] >> np.arange(n)) & 1
        gray_values = xs ^ (xs >> 1)

        def evaluate(weights):
            scores = bits @ weights
            if len(set(scores.tolist())) < size:
                return None
            order = np.argsort(scores)
            values = gray_values[order]
            signs = np.where(np.roll(values, -1) > values, 1, -1)
            difference = order ^ np.roll(order, -1)
            labels = np.floor(np.log2(difference)).astype(int)
            coupling = np.zeros((n, n), np.int64)
            a = np.minimum(labels, np.roll(labels, -1))
            b = np.maximum(labels, np.roll(labels, -1))
            np.add.at(coupling, (a, b), signs * np.roll(signs, -1))
            diagonal = int(np.trace(coupling))
            off = int(np.sum(abs(coupling)) - abs(np.diag(coupling)).sum())
            spins = 1 - 2 * bits
            energies = np.einsum("ij,jk,ik->i", spins, coupling, spins, optimize=True)
            best = int(max(energies))
            gap = off + diagonal - best
            return off + diagonal, best, gap, coupling, order

        first = None
        max_budget = (-1, None)
        best = (-size, None)
        population = []
        seeds = [[1, 14, 4, 12, 20]] if n == 5 else []
        if n >= 5:
            seeds.append([64 * (1 << j) for j in range(n - 5)]
                         + [1, 14, 4, 12, 20])
        accepted = 0
        for draw in range(12000):
            if draw < len(seeds):
                weights = seeds[draw]
            elif draw % 4 == 0 or not population:
                weights = [rng.randrange(1, 1000) for _ in range(n)]
                if draw % 8 == 0:
                    weights[rng.randrange(n)] = 1
            else:
                weights = list(rng.choice(population))
                k = rng.randrange(n)
                weights[k] = max(1, weights[k] + rng.randrange(
                    -max(2, weights[k] // 3), max(3, weights[k] // 3)))
            evaluated = evaluate(np.array(weights, dtype=np.int64))
            if evaluated is None:
                continue
            accepted += 1
            budget, maximum, gap, coupling, order = evaluated
            if gap and first is None:
                first = (weights, gap, coupling.tolist(), order.tolist())
            if budget > max_budget[0]:
                max_budget = budget, weights
            if maximum > best[0]:
                best = maximum, weights
            if len(population) < 24 or budget >= sorted(
                    evaluate(np.array(x))[0] for x in population)[5]:
                population.append(weights)
                if len(population) > 24:
                    population.sort(key=lambda x: evaluate(np.array(x))[0], reverse=True)
                    population = population[:24]
        receipts.append({
            "n": n, "draws": 12000, "generic_draws": accepted,
            "max_net_energy": best[0], "min_cyclic_density": (size - best[0]) / (2 * size),
            "best_weights": best[1], "max_W_minus_D": max_budget[0],
            "first_frustration": first,
        })
        print(json.dumps(receipts[-1]), flush=True)
    return {"seed": 202610030618, "scope": "exploratory; not chamber-complete",
            "dimensions": receipts}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--genetic", action="store_true")
    args = parser.parse_args()
    result = genetic_pressure() if args.genetic else translated_pressure()
    print(json.dumps(result, indent=2))
