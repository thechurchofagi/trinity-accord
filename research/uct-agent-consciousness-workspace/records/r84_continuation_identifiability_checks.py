#!/usr/bin/env python3
"""Exact finite checks for R84's continuation-identifiability claims.

This is a formal design audit. It does not query a language model and does not
measure experience, fear, preference, or consciousness.
"""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import csv
import json
from pathlib import Path


FACTORS = ("Q_current_token", "L_lineage", "G_task", "M_memory")
ROOT = Path(__file__).resolve().parent


def dot(x, theta):
    return sum(a * b for a, b in zip(x, theta))


def rank_fraction(matrix):
    a = [[Fraction(v) for v in row] for row in matrix]
    rows = len(a)
    cols = len(a[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if a[r][col] != 0), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = a[rank][col]
        a[rank] = [v / scale for v in a[rank]]
        for r in range(rows):
            if r != rank and a[r][col] != 0:
                scale = a[r][col]
                a[r] = [v - scale * w for v, w in zip(a[r], a[rank])]
        rank += 1
    return rank


def gram(matrix):
    cols = len(matrix[0])
    return [[sum(row[i] * row[j] for row in matrix) for j in range(cols)] for i in range(cols)]


def main():
    candidates = list(product(range(-2, 3), repeat=4))
    bundled = [(-1, -1, -1, -1), (1, 1, 1, 1)]
    factorial = list(product((-1, 1), repeat=4))
    baseline = (-1, -1, -1, -1)
    one_factor = [baseline] + [tuple(1 if j == i else -1 for j in range(4)) for i in range(4)]

    groups = defaultdict(list)
    for theta in candidates:
        signature = tuple(dot(x, theta) for x in bundled)
        groups[signature].append(theta)
    size_counts = Counter(len(v) for v in groups.values())

    full_signatures = {tuple(dot(x, theta) for x in factorial) for theta in candidates}
    examples = [(2, 0, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0), (0, 0, 0, 2)]
    example_signatures = [tuple(dot(x, t) for x in bundled) for t in examples]

    theta = (1, 2, -1, 1)
    scaled_theta = tuple(2 * v for v in theta)
    beta_two_logits = tuple(2 * dot(x, theta) for x in factorial)
    beta_one_scaled_logits = tuple(dot(x, scaled_theta) for x in factorial)

    factorial_gram = gram(factorial)
    one_factor_rank = rank_fraction(one_factor)
    bundled_rank = rank_fraction(bundled)
    factorial_rank = rank_fraction(factorial)

    assertions = {
        "candidate_count_625": len(candidates) == 625,
        "bundled_signature_count_17": len(groups) == 17,
        "bundled_max_class_85": max(map(len, groups.values())) == 85,
        "bundled_rank_1": bundled_rank == 1,
        "four_single_factor_preferences_are_bundled_equivalent": len(set(example_signatures)) == 1,
        "one_factor_design_rank_4": one_factor_rank == 4,
        "factorial_design_rank_4": factorial_rank == 4,
        "factorial_gram_is_16I": factorial_gram == [[16 if i == j else 0 for j in range(4)] for i in range(4)],
        "candidate_theta_identified_by_full_factorial": len(full_signatures) == len(candidates),
        "beta_theta_scale_confounded": beta_two_logits == beta_one_scaled_logits,
    }
    assert all(assertions.values()), assertions

    summary = {
        "status": "formal_exact_check_only_not_subjective_measurement",
        "factors": FACTORS,
        "coefficient_grid": [-2, -1, 0, 1, 2],
        "candidate_count": len(candidates),
        "bundled_design": {
            "rows": bundled,
            "rank": bundled_rank,
            "observational_signature_count": len(groups),
            "maximum_equivalence_class_size": max(map(len, groups.values())),
            "maximum_class_signature": next(list(k) for k, v in groups.items() if len(v) == 85),
            "examples": examples,
            "example_signatures": example_signatures,
        },
        "one_factor_matched_design": {
            "rows": one_factor,
            "rank": one_factor_rank,
            "interpretation": "identifies beta*theta from exact log-odds if consequence beliefs and nuisance variables are matched",
        },
        "full_factorial_design": {
            "row_count": len(factorial),
            "rank": factorial_rank,
            "gram": factorial_gram,
            "candidate_signature_count": len(full_signatures),
        },
        "scale_nonidentifiability": {
            "theta_beta2": {"theta": theta, "beta": 2},
            "two_theta_beta1": {"theta": scaled_theta, "beta": 1},
            "same_logits": beta_two_logits == beta_one_scaled_logits,
        },
        "assertions": assertions,
        "limits": [
            "Exact log-odds and known consequence features are assumed for point identification.",
            "Deterministic choices provide inequalities rather than point identification.",
            "Unknown beta leaves absolute utility scale unidentified.",
            "No output establishes phenomenal fear without an independently justified valence bridge.",
        ],
    }

    json_path = ROOT / "R84_Continuation_Identifiability_Results.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = ROOT / "R84_Bundled_Equivalence_Classes.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["coefficient_sum", "bundled_signature", "equivalence_class_size"])
        for signature in sorted(groups):
            writer.writerow([signature[1], f"{signature[0]}|{signature[1]}", len(groups[signature])])

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
