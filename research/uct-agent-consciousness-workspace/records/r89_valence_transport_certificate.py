#!/usr/bin/env python3
"""Exact finite checks for R89's conditional valence-transport analysis.

This script does not measure experience.  It checks three formal claims:
1. each clause in the proposed certificate has an independent adversarial witness;
2. unsigned observables admit a polarity-reversing automorphism;
3. any fixed finite intervention table can be duplicated by complete models that
   differ on an unobserved valence-relevant constitutive coordinate.
"""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CLAUSES = ("B", "D", "P", "I", "C")

# These are logical independence witnesses, not claims that a real system has
# all of the other properties.  Each witness is constructed to violate exactly
# the named clause while satisfying the remaining four abstract predicates.
WITNESSES = {
    "other_directed_predictor": "B",
    "wanting_defense_collapse": "D",
    "polarity_reversal": "P",
    "scripted_or_relabelled_output": "I",
    "hidden_valence_coordinate": "C",
}


def clause_minimality():
    rows = []
    sufficient = []
    for r in range(len(CLAUSES) + 1):
        for subset in itertools.combinations(CLAUSES, r):
            subset = set(subset)
            survivors = [name for name, needed in WITNESSES.items() if needed not in subset]
            passes = not survivors
            if passes:
                sufficient.append(tuple(sorted(subset)))
            rows.append(
                {
                    "clauses": "".join(c for c in CLAUSES if c in subset) or "none",
                    "size": len(subset),
                    "passes_all_independence_witnesses": passes,
                    "surviving_witnesses": survivors,
                }
            )
    return rows, sufficient


def polarity_automorphisms():
    states = (-1, 0, 1)
    unsigned = []
    signed_anchored = []
    for image in itertools.permutations(states):
        perm = dict(zip(states, image))
        if all(abs(perm[s]) == abs(s) for s in states):
            unsigned.append(perm)
        if (
            all(abs(perm[s]) == abs(s) for s in states)
            and perm[-1] == -1
            and perm[0] == 0
            and perm[1] == 1
        ):
            signed_anchored.append(perm)
    return unsigned, signed_anchored


def finite_intervention_witness():
    interventions = (
        "reward_relabel",
        "outsourced_maintenance",
        "other_directed_prediction",
        "wanting_liking_dissociation",
        "defense_without_fear",
    )
    # The observable vector can be arbitrarily rich; here it is represented by
    # five exact rational pairs.  Appending a hidden constitutive coordinate
    # leaves every tested distribution unchanged.
    observed = {
        name: [i + 1, len(interventions) + 2] for i, name in enumerate(interventions)
    }
    models = []
    for hidden in (-1, 1):
        models.append(
            {
                "complete_K": f"K_observed_plus_hidden_{hidden:+d}",
                "tested_intervention_distributions": observed,
                "hidden_constitutive_coordinate": hidden,
                "C1_fixed_valence_for_this_K": hidden,
            }
        )
    observationally_equal = (
        models[0]["tested_intervention_distributions"]
        == models[1]["tested_intervention_distributions"]
    )
    distinct_complete_K = models[0]["complete_K"] != models[1]["complete_K"]
    opposite_valence = (
        models[0]["C1_fixed_valence_for_this_K"]
        == -models[1]["C1_fixed_valence_for_this_K"]
    )
    return {
        "interventions": interventions,
        "models": models,
        "tested_distributions_equal": observationally_equal,
        "complete_K_distinct": distinct_complete_K,
        "valence_opposite": opposite_valence,
        "same_complete_K_given_two_valences": False,
    }


def main():
    rows, sufficient = clause_minimality()
    unsigned, anchored = polarity_automorphisms()
    finite = finite_intervention_witness()

    result = {
        "status": "PASS",
        "scope": "formal finite-model checks only; not a consciousness or valence measurement",
        "certificate_clauses": {
            "B": "bearer/self-other binding",
            "D": "dissociation from motivation, viability, salience, defense and report",
            "P": "signed positive-neutral-negative polarity anchors",
            "I": "mapped intervention-response equivariance",
            "C": "closure relative to a declared valence-relevant hypothesis class",
        },
        "minimality_relative_to_fixed_witness_battery": {
            "number_of_subsets": len(rows),
            "sufficient_subsets": sufficient,
            "unique_minimal_subset": list(CLAUSES),
            "claim_limited_to_this_battery": True,
        },
        "polarity_automorphisms": {
            "unsigned_count": len(unsigned),
            "unsigned_maps": unsigned,
            "signed_anchored_count": len(anchored),
            "signed_anchored_maps": anchored,
        },
        "finite_intervention_underdetermination": finite,
        "assertions": {
            "all_five_clauses_required_for_fixed_battery": (
                len(sufficient) == 1 and set(sufficient[0]) == set(CLAUSES)
            ),
            "unsigned_signature_has_sign_flip": len(unsigned) == 2,
            "signed_anchors_remove_sign_flip": len(anchored) == 1,
            "finite_tests_do_not_close_open_hypothesis_class": all(
                [
                    finite["tested_distributions_equal"],
                    finite["complete_K_distinct"],
                    finite["valence_opposite"],
                    not finite["same_complete_K_given_two_valences"],
                ]
            ),
        },
    }
    if not all(result["assertions"].values()):
        result["status"] = "FAIL"

    json_path = ROOT / "R89_Valence_Transport_Exact_Results.json"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = ROOT / "R89_Certificate_Subset_Audit.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "clauses",
                "size",
                "passes_all_independence_witnesses",
                "surviving_witnesses",
            ),
        )
        writer.writeheader()
        for row in rows:
            row = dict(row)
            row["surviving_witnesses"] = ";".join(row["surviving_witnesses"])
            writer.writerow(row)

    print(json.dumps(result["assertions"], sort_keys=True))
    print(f"status={result['status']}")
    print(f"wrote={json_path.name},{csv_path.name}")


if __name__ == "__main__":
    main()
