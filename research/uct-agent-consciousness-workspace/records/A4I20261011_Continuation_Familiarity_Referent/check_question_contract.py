#!/usr/bin/env python3
"""Exact finite check for the A4I content-separation screen.

The intended-target bit is a stipulation inside a comprehension vignette.  It
is not an assignment of a participant's phenomenal state.
"""

import itertools
import json


rows = []
for intended, effort_high, remembers_practice in itertools.product((0, 1), repeat=3):
    policies = {
        "target_content": intended,
        "ease_substitution": 1 - effort_high,
        "practice_memory_substitution": remembers_practice,
        "target_or_memory": int(bool(intended or remembers_practice)),
    }
    rows.append(
        {
            "intended_content_in_vignette": intended,
            "effort_high": effort_high,
            "remembers_practice": remembers_practice,
            "policy_outputs": policies,
        }
    )

policy_names = tuple(rows[0]["policy_outputs"])
signatures = {
    name: "".join(str(row["policy_outputs"][name]) for row in rows)
    for name in policy_names
}
pairwise_distances = {}
for left, right in itertools.combinations(policy_names, 2):
    distance = sum(a != b for a, b in zip(signatures[left], signatures[right]))
    pairwise_distances[f"{left}__vs__{right}"] = distance

result = {
    "schema": "a4i-question-contract/1",
    "rows": rows,
    "policy_signatures": signatures,
    "pairwise_hamming_distances": pairwise_distances,
    "all_signatures_distinct": len(set(signatures.values())) == len(signatures),
    "target_vs_effort_distance": pairwise_distances[
        "target_content__vs__ease_substitution"
    ],
    "target_vs_memory_distance": pairwise_distances[
        "target_content__vs__practice_memory_substitution"
    ],
    "phenomenal_assignments": 0,
    "scope": (
        "Logical/comprehension-policy separation only; no human feasibility, "
        "truth calibration, or H_way measurement."
    ),
}

print(json.dumps(result, indent=2, sort_keys=True))

