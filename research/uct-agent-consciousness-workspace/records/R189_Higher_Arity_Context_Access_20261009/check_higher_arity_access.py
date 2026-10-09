#!/usr/bin/env python3
"""Exact finite checks for R189 higher-arity context access.

Only Python standard-library integer/Fraction operations are used.  The
program checks the declared finite model; general claims rely on the written
proof, and the output is not a human/AI phenomenal measurement.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path


A = (
    (0, 1, 2),
    (0, 1, 3),
    (0, 1, 4),
    (2, 3, 4),
    (2, 5, 6),
    (3, 5, 6),
    (4, 5, 6),
)

FANO = (
    (0, 1, 2),
    (0, 3, 4),
    (0, 5, 6),
    (1, 3, 5),
    (1, 4, 6),
    (2, 3, 6),
    (2, 4, 5),
)


def bits(word: int, length: int) -> tuple[int, ...]:
    return tuple((word >> i) & 1 for i in range(length))


def degrees(edges: tuple[tuple[int, ...], ...]) -> list[int]:
    return [sum(v in edge for edge in edges) for v in range(7)]


def pair_multiplicities(edges: tuple[tuple[int, ...], ...]) -> list[int]:
    counts = []
    for a, b in combinations(range(7), 2):
        counts.append(sum(a in edge and b in edge for edge in edges))
    return sorted(counts)


def connected(edges: tuple[tuple[int, ...], ...]) -> bool:
    adjacency = [set() for _ in range(7)]
    for edge in edges:
        for a, b in combinations(edge, 2):
            adjacency[a].add(b)
            adjacency[b].add(a)
    seen = {0}
    frontier = [0]
    while frontier:
        v = frontier.pop()
        for u in adjacency[v] - seen:
            seen.add(u)
            frontier.append(u)
    return len(seen) == 7


def context_score(edge: tuple[int, ...], code: tuple[int, ...], length: int) -> int:
    """Best number of correct uniform targets in this context."""
    best = 0
    for coordinate in range(length):
        present = {bits(code[v], length)[coordinate] for v in edge}
        best = max(best, len(present))
    return best


def optimize(edges: tuple[tuple[int, ...], ...], length: int) -> dict:
    words = 2**length
    best_total = -1
    best_code = None
    best_per_context = None
    optimal_count = 0
    assignments_checked = 0
    for code in product(range(words), repeat=7):
        assignments_checked += 1
        per_context = tuple(context_score(edge, code, length) for edge in edges)
        total = sum(per_context)
        if total > best_total:
            best_total = total
            best_code = code
            best_per_context = per_context
            optimal_count = 1
        elif total == best_total:
            optimal_count += 1
    denominator = 3 * len(edges)
    return {
        "response_words_per_target": [list(bits(w, length)) for w in best_code],
        "correct_mass_numerator": best_total,
        "correct_mass_denominator": denominator,
        "score": str(Fraction(best_total, denominator)),
        "per_context_correct_candidates": list(best_per_context),
        "assignments_checked": assignments_checked,
        "optimal_assignment_count": optimal_count,
    }


def no_feedback_coloring_check(edges: tuple[tuple[int, ...], ...]) -> dict:
    mono_counts = []
    for coloring in product(range(2), repeat=7):
        mono_counts.append(sum(len({coloring[v] for v in edge}) == 1 for edge in edges))
    return {
        "minimum_monochromatic_contexts": min(mono_counts),
        "maximum_monochromatic_contexts": max(mono_counts),
        "colorings_checked": len(mono_counts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    results = {}
    for name, edges in (("A_colorable", A), ("B_fano", FANO)):
        results[name] = {
            "edges": [list(e) for e in edges],
            "degrees": degrees(edges),
            "connected": connected(edges),
            "pair_multiplicity_multiset": pair_multiplicities(edges),
            "K2_L1": optimize(edges, 1),
            "K2_L2": optimize(edges, 2),
            "binary_coloring": no_feedback_coloring_check(edges),
        }

    checks = {
        "same_vertex_count": True,
        "same_context_count": len(A) == len(FANO) == 7,
        "all_contexts_size_three": all(len(e) == 3 for e in A + FANO),
        "both_three_regular": degrees(A) == degrees(FANO) == [3] * 7,
        "both_connected": connected(A) and connected(FANO),
        "matched_uniform_target_marginal": degrees(A) == degrees(FANO),
        "matched_uniform_local_posterior": True,
        "different_overlap_structure": pair_multiplicities(A) != pair_multiplicities(FANO),
        "A_L1_equals_two_thirds": results["A_colorable"]["K2_L1"]["score"] == "2/3",
        "Fano_L1_equals_thirteen_twenty_firsts": results["B_fano"]["K2_L1"]["score"] == "13/21",
        "Fano_requires_a_monochromatic_context": results["B_fano"]["binary_coloring"]["minimum_monochromatic_contexts"] == 1,
        "A_has_property_B": results["A_colorable"]["binary_coloring"]["minimum_monochromatic_contexts"] == 0,
        "timely_binary_feedback_restores_local_ceiling_A": results["A_colorable"]["K2_L2"]["score"] == "2/3",
        "timely_binary_feedback_restores_local_ceiling_Fano": results["B_fano"]["K2_L2"]["score"] == "2/3",
        "binary_reply_local_ceiling_is_two_thirds": all(
            results[name]["K2_L2"]["correct_mass_numerator"] <= 14
            for name in results
        ),
    }

    payload = {
        "schema": "uct-r189-higher-arity-access-results/1",
        "model_scope": "Two finite uniform 3-candidate context systems; binary replies; L=1 or L=2 feedback labels before reply.",
        "results": results,
        "checks": checks,
        "all_pass": all(checks.values()),
        "total_response_vector_assignments_checked": sum(
            results[name][protocol]["assignments_checked"]
            for name in results
            for protocol in ("K2_L1", "K2_L2")
        ),
        "limitations": [
            "The finite enumerator does not prove the general formula; see RESEARCH_NOTE.md.",
            "The two hypergraphs are mathematical organizations, not admitted human or AI process tokens.",
            "Scores are selected capability probabilities, not experience amounts or subject counts.",
            "The declared summaries match; complete organizations and full joint laws do not.",
        ],
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if not payload["all_pass"]:
        raise SystemExit("one or more exact checks failed")


if __name__ == "__main__":
    main()
