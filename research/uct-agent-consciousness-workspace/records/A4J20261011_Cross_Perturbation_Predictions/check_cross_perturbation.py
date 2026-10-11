#!/usr/bin/env python3
"""Exact finite check for A4J's two-intervention signed prediction contract.

This script assigns no phenomenal state.  It enumerates qualitative total-effect
signs under two scoped pure candidates after independently declared first-stage
directions.  Cross-effects are deliberately unrestricted.
"""

from itertools import product
import json

SIGNS = (-1, 0, 1)


def classify(observed, relation_predictions, fit_predictions):
    in_relation = observed in relation_predictions
    in_fit = observed in fit_predictions
    if in_relation and in_fit:
        return "both"
    if in_relation:
        return "relation_only"
    if in_fit:
        return "fit_only"
    return "neither"


def run(strict=True):
    # Coordinates are total effects under (Z_R, Z_F).
    # Z_R is independently established to lower R; Z_F to lower F.
    main = {-1} if strict else {-1, 0}
    relation_predictions = set(product(main, SIGNS))
    fit_predictions = set(product(SIGNS, main))
    rows = []
    counts = {k: 0 for k in ("both", "relation_only", "fit_only", "neither")}
    for observed in product(SIGNS, repeat=2):
        label = classify(observed, relation_predictions, fit_predictions)
        counts[label] += 1
        rows.append(
            {
                "observed_total_effect_signature": list(observed),
                "compatible_with_B_relation": observed in relation_predictions,
                "compatible_with_B_fit": observed in fit_predictions,
                "classification": label,
            }
        )
    return {
        "strict_signed_sensitivity": strict,
        "relation_prediction_set": [list(x) for x in sorted(relation_predictions)],
        "fit_prediction_set": [list(x) for x in sorted(fit_predictions)],
        "classification_counts": counts,
        "rows": rows,
    }


def unrestricted_nonidentification():
    all_signatures = set(product(SIGNS, repeat=2))
    return {
        "relation_prediction_set": [list(x) for x in sorted(all_signatures)],
        "fit_prediction_set": [list(x) for x in sorted(all_signatures)],
        "sets_equal": True,
        "intersection_size": len(all_signatures),
        "phenomenal_assignments": 0,
    }


def latent_worlds():
    # (dR_ZR, dF_ZR, dR_ZF, dF_ZF); target directions are fixed at -1.
    worlds = [(-1, d_f_zr, d_r_zf, -1) for d_f_zr, d_r_zf in product(SIGNS, repeat=2)]
    signatures = [
        {
            "world": list(w),
            "B_relation_signature": [w[0], w[2]],
            "B_fit_signature": [w[1], w[3]],
        }
        for w in worlds
    ]
    assert len(worlds) == 9
    assert len({tuple(x["B_relation_signature"]) for x in signatures}) == 3
    assert len({tuple(x["B_fit_signature"]) for x in signatures}) == 3
    return signatures


def main():
    result = {
        "schema": "a4j-cross-perturbation/1",
        "scope": (
            "Two randomized total-effect signs under scoped pure monotone candidates; "
            "no H_cont truth, human feasibility, actual-route installation, or general causal discovery."
        ),
        "strict": run(strict=True),
        "weak": run(strict=False),
        "unrestricted_without_signed_first_stages": unrestricted_nonidentification(),
        "cross_effect_worlds_with_strict_main_directions": latent_worlds(),
    }
    assert result["strict"]["classification_counts"] == {
        "both": 1,
        "relation_only": 2,
        "fit_only": 2,
        "neither": 4,
    }
    assert result["weak"]["classification_counts"] == {
        "both": 4,
        "relation_only": 2,
        "fit_only": 2,
        "neither": 1,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
