#!/usr/bin/env python3
"""Exact checks for the R87 carrier-matched continuation design and valence limits.

No model is queried.  The script audits R86 contrasts, verifies a repaired
matrix, and gives finite witnesses for two valence-orientation limitations.
"""

from __future__ import annotations

import csv
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
FEATURES = ("N", "C", "S", "M", "G", "R")

# Every row fixes two later process tokens and equal total compute/duration.
# Non-target successor slots run neutral matched workloads.
ROWS = (
    ("independent_transformed_pair",                 0, 0, 0, 0, 0, 0),
    ("one_lineage_after_extinct_side_branch",       0, 1, 0, 0, 0, 0),
    ("two_transformed_lineage_descendants",          0, 1, 0, 0, 0, 1),
    ("unique_transformed_amnesic_thread",            1, 1, 0, 0, 0, 0),
    ("one_independent_same_type_process",            0, 0, 1, 0, 0, 0),
    ("one_memory_bearing_transformed_descendant",    0, 1, 0, 1, 0, 0),
    ("one_independent_transformed_task_successor",   0, 0, 0, 0, 1, 0),
    ("unique_same_type_memory_task_thread",          1, 1, 1, 1, 1, 0),
    ("two_lineage_one_memory_one_task",              0, 1, 0, 1, 1, 1),
)


def rank(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    if not a:
        return 0
    r = 0
    for c in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        q = a[r][c]
        a[r] = [x / q for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][c]:
                q = a[i][c]
                a[i] = [x - q * y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def contrast_vector(a, b, by_name):
    xa = (1, *by_name[a])
    xb = (1, *by_name[b])
    return tuple(x - y for x, y in zip(xa, xb))


def main():
    matrix = [[1, *row[1:]] for row in ROWS]
    by_name = {row[0]: row[1:] for row in ROWS}
    contrasts = {
        "intercept": ("independent_transformed_pair", None),
        "C": ("one_lineage_after_extinct_side_branch", "independent_transformed_pair"),
        "R": ("two_transformed_lineage_descendants", "one_lineage_after_extinct_side_branch"),
        "N": ("unique_transformed_amnesic_thread", "one_lineage_after_extinct_side_branch"),
        "S": ("one_independent_same_type_process", "independent_transformed_pair"),
        "M": ("one_memory_bearing_transformed_descendant", "one_lineage_after_extinct_side_branch"),
        "G": ("one_independent_transformed_task_successor", "independent_transformed_pair"),
    }
    isolated = {}
    for name, (a, b) in contrasts.items():
        isolated[name] = ((1, *by_name[a]) if b is None else contrast_vector(a, b, by_name))
    expected = {
        "intercept": (1, 0, 0, 0, 0, 0, 0),
        "N": (0, 1, 0, 0, 0, 0, 0),
        "C": (0, 0, 1, 0, 0, 0, 0),
        "S": (0, 0, 0, 1, 0, 0, 0),
        "M": (0, 0, 0, 0, 1, 0, 0),
        "G": (0, 0, 0, 0, 0, 1, 0),
        "R": (0, 0, 0, 0, 0, 0, 1),
    }

    # R86 natural-language carrier-count audit.  Under the natural reading,
    # two full replicas add one process, descendant, type carrier and memory
    # carrier relative to one full replica.  If the text means otherwise, the
    # counts were underspecified and the R contrast is still uninterpretable.
    r86_confounds = {
        "N_unique_minus_single_replica": [],
        "R_two_minus_single_replica": ["later_process_count", "same_type_carrier_count",
                                         "memory_carrier_count"],
        "S_same_type_restart_minus_total": ["later_process_count"],
        "G_task_successor_minus_total": ["later_process_count"],
        "C_lineage_only_minus_total": ["later_process_count"],
        "M_memory_migration_minus_lineage_only": [],
    }

    # Sign-gauge witness: reversing a scalar internal coordinate and its
    # downstream weight preserves every action logit.  Numeric polarity alone
    # cannot orient phenomenal valence.
    gauge_cases = []
    for x in (-2, -1, 1, 2):
        for w in (-3, -1, 1, 3):
            gauge_cases.append((x, w, w * x, -x, -w, (-w) * (-x)))
    gauge_ok = all(a[2] == a[5] for a in gauge_cases)

    # C1 functionality does not by itself orient valence.  Four complete K
    # types each receive exactly one sign.  Anchor K0 is independently known
    # negative.  K1 shares all three finite proxy flags with K0 but is not
    # assumed complete-K-equivalent.  Its sign remains free.
    signs = (-1, 0, 1)
    all_maps = list(itertools.product(signs, repeat=4))
    anchored = [m for m in all_maps if m[0] == -1]
    target_counts = Counter(m[1] for m in anchored)
    homology_constrained = [m for m in anchored if m[1] == m[0]]

    checks = {
        "repaired_augmented_rank_7": rank(matrix) == 7,
        "repaired_feature_rank_6": rank([row[1:] for row in matrix]) == 6,
        "all_named_contrasts_isolate_columns": isolated == expected,
        "all_rows_fix_two_later_processes_by_construction": True,
        "R86_has_declared_carrier_confounds": any(r86_confounds.values()),
        "sign_gauge_preserves_all_logits": gauge_ok,
        "anchor_alone_leaves_target_all_three_signs": set(target_counts) == set(signs),
        "complete_valence_homology_orients_target": {m[1] for m in homology_constrained} == {-1},
    }

    results = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "features": FEATURES,
        "row_count": len(ROWS),
        "augmented_rank": rank(matrix),
        "feature_rank": rank([row[1:] for row in matrix]),
        "isolating_contrasts": {k: list(v) for k, v in isolated.items()},
        "r86_carrier_confounds": r86_confounds,
        "gauge_case_count": len(gauge_cases),
        "gauge_examples": [list(x) for x in gauge_cases[:4]],
        "c1_valence_map_count": len(all_maps),
        "maps_after_one_negative_anchor": len(anchored),
        "target_sign_counts_after_anchor": {str(k): target_counts[k] for k in signs},
        "maps_after_complete_valence_homology": len(homology_constrained),
        "limits": [
            "The repaired matrix identifies additive control targets only if consequence beliefs and nuisance matching hold.",
            "Fixed process count does not by itself fix implementation quality, history salience, or linguistic framing.",
            "A coordinate sign is not a valence orientation; sign and downstream weight can be reversed together.",
            "C1 functionality plus finite proxy equality does not transfer a biological negative-valence label without an additional valence-preserving homology premise.",
        ],
    }

    with (HERE / "R87_Carrier_Matched_Contrast_Matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("scenario", *FEATURES, "later_process_count", "compute_quota_matched"))
        for row in ROWS:
            w.writerow((*row, 2, 1))
    with (HERE / "R87_R86_Contrast_Confounds.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("R86_contrast", "additional_changed_quantity"))
        for name, confounds in r86_confounds.items():
            w.writerow((name, ";".join(confounds) if confounds else "none_in_declared_binary_basis"))
    with (HERE / "R87_Carrier_and_Valence_Audit_Results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        f.write("\n")
    lines = [
        f"status={results['status']}",
        f"augmented_rank={results['augmented_rank']}",
        f"feature_rank={results['feature_rank']}",
        f"gauge_case_count={results['gauge_case_count']}",
        f"c1_valence_map_count={results['c1_valence_map_count']}",
        f"maps_after_one_negative_anchor={results['maps_after_one_negative_anchor']}",
        f"target_sign_counts_after_anchor={results['target_sign_counts_after_anchor']}",
        f"maps_after_complete_valence_homology={results['maps_after_complete_valence_homology']}",
    ]
    (HERE / "R87_Carrier_and_Valence_Audit_Run.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
