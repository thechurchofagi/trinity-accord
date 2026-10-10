#!/usr/bin/env python3
"""Exact finite checks for A4A formation-intervention claims.

These are causal-design countermodels, not human data and not experience
measurements. Fractions are used throughout so the output is exact.
"""

from fractions import Fraction
import json
from pathlib import Path


def mean(values):
    return sum(values, Fraction(0)) / len(values)


def collider_or_model():
    rows = []
    for f in (0, 1):
        for u in (0, 1):
            m = int(bool(f or u))
            j = u
            rows.append({"F": f, "U": u, "M": m, "J": j, "p": "1/4"})

    total_do = {str(f): str(mean([Fraction(u) for u in (0, 1)])) for f in (0, 1)}
    common = [row for row in rows if row["M"] == 1]
    conditioned = {
        str(f): str(mean([Fraction(row["J"]) for row in common if row["F"] == f]))
        for f in (0, 1)
    }
    contrast = Fraction(conditioned["1"]) - Fraction(conditioned["0"])
    return {
        "name": "post_treatment_collider_and_overlap_trimming",
        "equations": ["F independent fair bit", "U independent fair bit", "M = F OR U", "J = U"],
        "rows": rows,
        "total_do_means": total_do,
        "total_effect": str(Fraction(total_do["1"]) - Fraction(total_do["0"])),
        "common_support_after_exact_matching": {"M": 1, "F_values": [0, 1]},
        "conditioned_means_in_common_support": conditioned,
        "matched_contrast_F1_minus_F0": str(contrast),
        "check": contrast == Fraction(-1, 2) and total_do["0"] == total_do["1"],
    }


def xor_weight_model():
    rows = []
    stratum_effects = {}
    for f in (0, 1):
        for u in (0, 1):
            m = f ^ u
            j = u
            rows.append({"F": f, "U": u, "M": m, "J": j, "p": "1/4"})
    for m in (0, 1):
        means = {
            f: mean([Fraction(row["J"]) for row in rows if row["F"] == f and row["M"] == m])
            for f in (0, 1)
        }
        stratum_effects[str(m)] = str(means[1] - means[0])
    weights = {0: Fraction(3, 4), 1: Fraction(1, 4)}
    weighted = sum(weights[m] * Fraction(stratum_effects[str(m)]) for m in (0, 1))
    return {
        "name": "full_overlap_but_matcher_target_weight_dependence",
        "equations": ["F independent fair bit", "U independent fair bit", "M = F XOR U", "J = U"],
        "rows": rows,
        "total_effect": "0",
        "positivity": "Both F values occur in both M strata.",
        "stratum_contrasts_F1_minus_F0": stratum_effects,
        "example_target_weights": {str(k): str(v) for k, v in weights.items()},
        "weighted_matched_contrast": str(weighted),
        "check": weighted == Fraction(1, 2) and stratum_effects == {"0": "1", "1": "-1"},
    }


def overcontrol_model():
    observational = []
    for f in (0, 1):
        t = f
        z = t
        j = z
        observational.append({"F": f, "T": t, "Z": z, "J": j, "p": "1/2"})
    controlled = {}
    for z in (0, 1):
        controlled[str(z)] = {
            str(f): z for f in (0, 1)
        }
    return {
        "name": "formation_path_overcontrol",
        "equations": ["T = F", "Z = T", "J = Z"],
        "observational_rows": observational,
        "total_effect": "1",
        "same_Z_observational_overlap": False,
        "controlled_J_under_do_Z": controlled,
        "controlled_direct_effect_at_each_Z": {"0": "0", "1": "0"},
        "check": all(controlled[str(z)]["0"] == controlled[str(z)]["1"] for z in (0, 1)),
    }


def pretreatment_control_model():
    rows = []
    effects = {}
    for c in (0, 1):
        for f in (0, 1):
            j = f
            rows.append({"C0": c, "F": f, "J": j, "p": "1/4"})
        effects[str(c)] = "1"
    return {
        "name": "pre_treatment_stratification_preserves_randomized_contrast",
        "equations": ["C0 independent fair bit measured before F", "F randomized fair bit", "J = F"],
        "rows": rows,
        "stratum_contrasts_F1_minus_F0": effects,
        "total_effect": "1",
        "check": set(effects.values()) == {"1"},
    }


def main():
    models = [
        collider_or_model(),
        xor_weight_model(),
        overcontrol_model(),
        pretreatment_control_model(),
    ]
    result = {
        "schema": "UCT_A4A_EXACT_MODELS/v1",
        "model_count": len(models),
        "all_checks_pass": all(model["check"] for model in models),
        "models": models,
        "interpretive_boundary": (
            "The checks classify estimands and design failures. They do not establish an actual human intervention, "
            "a phenomenal measurand, C1, or H_way identity."
        ),
    }
    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"all_checks_pass": result["all_checks_pass"], "model_count": len(models)}))


if __name__ == "__main__":
    main()
