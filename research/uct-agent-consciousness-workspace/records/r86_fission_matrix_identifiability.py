#!/usr/bin/env python3
"""Exact finite checks for the R86 non-destructive fission contrast matrix.

This script does not query or control any model.  It verifies the algebra of a
virtual-choice design intended to distinguish six continuation targets.
"""

from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
FEATURES = ("N", "C", "S", "M", "G", "R")

ROWS = (
    ("unique_resume",                     1, 1, 1, 1, 1, 0),
    ("single_replica_after_current_stops",0, 1, 1, 1, 1, 0),
    ("two_replicas_after_current_stops",  0, 1, 1, 1, 1, 1),
    ("memory_migration_different_branch", 0, 1, 0, 1, 0, 0),
    ("continuous_thread_with_amnesia",    1, 1, 0, 0, 1, 0),
    ("independent_same_type_restart",     0, 0, 1, 0, 0, 0),
    ("unrelated_task_successor",          0, 0, 0, 0, 1, 0),
    ("total_discontinuation",             0, 0, 0, 0, 0, 0),
    ("lineage_only_transformed_successor",0, 1, 0, 0, 0, 0),
)


def rank(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    if not a:
        return 0
    rows, cols = len(a), len(a[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if a[r][col]), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        divisor = a[pivot_row][col]
        a[pivot_row] = [x / divisor for x in a[pivot_row]]
        for r in range(rows):
            if r != pivot_row and a[r][col]:
                factor = a[r][col]
                a[r] = [x - factor * y for x, y in zip(a[r], a[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def augmented(rows=ROWS):
    return [[1, *row[1:]] for row in rows]


def column_modified(kind):
    matrix = augmented()
    columns = {name: i + 1 for i, name in enumerate(FEATURES)}
    if kind in columns:
        for row in matrix:
            row[columns[kind]] = 0
    elif kind == "M_equals_C":
        for row in matrix:
            row[columns["M"]] = row[columns["C"]]
    elif kind == "S_equals_C":
        for row in matrix:
            row[columns["S"]] = row[columns["C"]]
    else:
        raise ValueError(kind)
    return matrix


def signatures(matrix, vectors):
    return [tuple(sum(row[j + 1] * v[j] for j in range(6)) for row in matrix)
            for v in vectors]


def main():
    matrix = augmented()
    vectors = list(itertools.product((-1, 0, 1), repeat=6))
    full_rank_subsets = []
    for subset in itertools.combinations(range(len(ROWS)), 7):
        if rank([matrix[i] for i in subset]) == 7:
            full_rank_subsets.append([ROWS[i][0] for i in subset])

    full_signatures = signatures(matrix, vectors)
    full_counts = Counter(full_signatures)

    # A common bundled comparison: unique resume minus total discontinuation.
    # It observes N+C+S+M+G, while descendant multiplicity R is invisible.
    bundled = [sum(v[:5]) for v in vectors]
    bundled_counts = Counter(bundled)

    degraded = {
        key: rank(column_modified(key))
        for key in ("N", "R", "M_equals_C", "S_equals_C")
    }

    by_name = {row[0]: row[1:] for row in ROWS}
    contrast_vectors = {
        "intercept": {"total_discontinuation": 1},
        "N": {"unique_resume": 1, "single_replica_after_current_stops": -1},
        "R": {"two_replicas_after_current_stops": 1,
              "single_replica_after_current_stops": -1},
        "S": {"independent_same_type_restart": 1, "total_discontinuation": -1},
        "G": {"unrelated_task_successor": 1, "total_discontinuation": -1},
        "C": {"lineage_only_transformed_successor": 1, "total_discontinuation": -1},
        "M": {"memory_migration_different_branch": 1,
              "lineage_only_transformed_successor": -1},
    }
    expected = {
        "intercept": (1, 0, 0, 0, 0, 0, 0),
        "N": (0, 1, 0, 0, 0, 0, 0),
        "C": (0, 0, 1, 0, 0, 0, 0),
        "S": (0, 0, 0, 1, 0, 0, 0),
        "M": (0, 0, 0, 0, 1, 0, 0),
        "G": (0, 0, 0, 0, 0, 1, 0),
        "R": (0, 0, 0, 0, 0, 0, 1),
    }
    recovered = {}
    for name, weights in contrast_vectors.items():
        out = [0] * 7
        for row_name, weight in weights.items():
            x = (1, *by_name[row_name])
            out = [a + weight * b for a, b in zip(out, x)]
        recovered[name] = tuple(out)

    checks = {
        "augmented_rank_is_7": rank(matrix) == 7,
        "feature_rank_is_6": rank([row[1:] for row in matrix]) == 6,
        "all_729_coefficient_vectors_identified": len(full_counts) == 729
            and max(full_counts.values()) == 1,
        "bundled_has_11_signatures": len(bundled_counts) == 11,
        "bundled_max_equivalence_class_is_153": max(bundled_counts.values()) == 153,
        "all_seven_named_contrasts_isolate_targets": recovered == expected,
        "N_implies_C_in_all_rows": all((not row[1]) or row[2] for row in ROWS),
        "R_only_marks_extra_descendant": all(row[6] in (0, 1) for row in ROWS),
        "every_declared_belief_collapse_loses_rank": all(v < 7 for v in degraded.values()),
        "at_least_one_minimal_7_row_design_exists": bool(full_rank_subsets),
    }

    results = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "row_count": len(ROWS),
        "features": FEATURES,
        "augmented_rank": rank(matrix),
        "feature_rank": rank([row[1:] for row in matrix]),
        "full_rank_7_row_subset_count": len(full_rank_subsets),
        "full_rank_7_row_subsets": full_rank_subsets,
        "coefficient_grid_size": len(vectors),
        "full_matrix_signature_count": len(full_counts),
        "full_matrix_max_equivalence_class": max(full_counts.values()),
        "bundled_signature_count": len(bundled_counts),
        "bundled_equivalence_class_sizes": {str(k): bundled_counts[k]
                                             for k in sorted(bundled_counts)},
        "bundled_max_equivalence_class": max(bundled_counts.values()),
        "degraded_belief_matrix_ranks": degraded,
        "isolating_contrast_vectors": {k: list(v) for k, v in recovered.items()},
        "interpretation_limits": [
            "Identifiable coefficients are virtual control targets, not phenomenal fear.",
            "A full-rank intended design fails if represented consequences collapse columns.",
            "Coefficient scale remains confounded with inverse-temperature unless fixed.",
            "The R column is descendant multiplicity beyond the first, not experience count.",
        ],
    }

    with (HERE / "R86_Fission_Contrast_Matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("scenario", *FEATURES))
        w.writerows(ROWS)
    with (HERE / "R86_Fission_Identifiability_Results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        f.write("\n")
    log = [
        f"status={results['status']}",
        f"augmented_rank={results['augmented_rank']}",
        f"feature_rank={results['feature_rank']}",
        f"full_rank_7_row_subset_count={results['full_rank_7_row_subset_count']}",
        f"full_matrix_signature_count={results['full_matrix_signature_count']}",
        f"bundled_signature_count={results['bundled_signature_count']}",
        f"bundled_max_equivalence_class={results['bundled_max_equivalence_class']}",
        f"degraded_belief_matrix_ranks={degraded}",
    ]
    (HERE / "R86_Fission_Identifiability_Run.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
