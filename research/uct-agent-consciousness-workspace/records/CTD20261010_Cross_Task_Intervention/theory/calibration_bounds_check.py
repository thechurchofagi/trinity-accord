#!/usr/bin/env python3
"""Exhaustive finite checks for the calibration-gap intervention note.

This is a mathematical finite-model enumeration, not biological data.
The candidate response functions are generated independently of the formulas.
Outputs are written next to this file so the root task can package them.
"""

from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path
import csv
import json
import math


ROOT = Path(__file__).resolve().parent
DOMAIN = tuple(range(7))
GRID_MAX = 10


def enumerate_monotone_functions():
    # Every nondecreasing function on 0,...,6 with h(0)=0,h(6)=10.
    return [(0, *middle, GRID_MAX)
            for middle in combinations_with_replacement(range(GRID_MAX + 1), 5)]


def admissible(function, anchors):
    return all(low <= function[position] <= high
               for position, low, high in anchors)


def bounds_formula(x, y, anchors):
    if x == y:
        return (0, 0)
    if x > y:
        low, high = bounds_formula(y, x, anchors)
        return (-high, -low)
    lower_x = max(low for position, low, high in anchors if position <= x)
    lower_y = max(low for position, low, high in anchors if position <= y)
    upper_x = min(high for position, low, high in anchors if position >= x)
    upper_y = min(high for position, low, high in anchors if position >= y)
    return (max(0, lower_y - upper_x), upper_y - lower_x)


def check_scenario(name, extra_anchors, universe):
    anchors = [(0, 0, 0), (6, 10, 10), *extra_anchors]
    functions = [function for function in universe if admissible(function, anchors)]
    assert functions, name
    pairs_checked = 0
    for x in DOMAIN:
        for y in DOMAIN:
            effects = [function[y] - function[x] for function in functions]
            enumeration_bounds = (min(effects), max(effects))
            closed_form_bounds = bounds_formula(x, y, anchors)
            assert enumeration_bounds == closed_form_bounds, (
                name, x, y, enumeration_bounds, closed_form_bounds)
            # Check interval fullness in this integer-grid example as well.
            assert set(effects) == set(range(enumeration_bounds[0], enumeration_bounds[1]+1))
            pairs_checked += 1
    effects = [function[5] - function[1] for function in functions]
    low, high = min(effects), max(effects)
    lower_witness = next(function for function in functions if function[5]-function[1] == low)
    upper_witness = next(function for function in functions if function[5]-function[1] == high)
    return {
        "name": name,
        "anchors": anchors,
        "admissible_functions": len(functions),
        "ordered_pairs_checked": pairs_checked,
        "target_pair": [1, 5],
        "target_effect_bounds_grid": [low, high],
        "target_effect_bounds_normalized": [low/10, high/10],
        "lower_witness_grid": lower_witness,
        "upper_witness_grid": upper_witness,
        "effect_histogram_grid": dict(sorted(Counter(effects).items())),
    }


def assert_compression_no_go():
    rows = []
    for exponent in (1, 2, 4, 6, 9):
        epsilon = 10.0**(-exponent)
        # Keep an exterior calibration pair and an interior midpoint fixed.
        # A genuinely strictly increasing piecewise-linear map exists through
        # these values; the target contrast shrinks while calibration is exact.
        values = (0, .5-epsilon, .5-epsilon/2, .5, .5+epsilon/2, .5+epsilon, 1)
        assert all(a < b for a, b in zip(values[:-1], values[1:]))
        assert values[0] == 0 and values[3] == .5 and values[6] == 1
        effect = values[5] - values[1]
        assert math.isclose(effect, 2*epsilon, rel_tol=1e-6, abs_tol=1e-16)
        rows.append({"epsilon": epsilon, "strictly_increasing_values": values,
                     "target_effect": effect})
    return rows


def assert_sharp_contamination_threshold():
    gap = .4
    cases = []
    for epsilon in (0, .1, .15, .199, .2, .25):
        positive = (gap-epsilon, 1+epsilon)
        null = (-epsilon, epsilon)
        overlap = max(positive[0], null[0]) <= min(positive[1], null[1]) + 1e-12
        predicted_overlap = gap <= 2*epsilon + 1e-12
        assert overlap == predicted_overlap
        cases.append({"contrast_bias_budget": epsilon,
                      "positive_interval": positive,
                      "null_interval": null,
                      "sets_overlap": overlap,
                      "signed_gap": gap-2*epsilon})
    # Explicit identical observed difference at the exact boundary.
    # All four Bernoulli mean endpoints are in [0,1].
    rescue_model = {"latent_readout_off": .3, "latent_readout_on": .7,
                    "bias_off": 0, "bias_on": -.2}
    null_model = {"latent_readout_off": .3, "latent_readout_on": .3,
                  "bias_off": 0, "bias_on": .2}
    rescue_observed = [rescue_model["latent_readout_off"] + rescue_model["bias_off"],
                       rescue_model["latent_readout_on"] + rescue_model["bias_on"]]
    null_observed = [null_model["latent_readout_off"] + null_model["bias_off"],
                     null_model["latent_readout_on"] + null_model["bias_on"]]
    assert all(math.isclose(a,b) for a,b in zip(rescue_observed,null_observed))
    assert all(0 <= value <= 1 for value in rescue_observed + null_observed)
    return {"cases": cases, "boundary_twin": {
        "rescue_model": rescue_model, "null_model": null_model,
        "identical_observed_means": rescue_observed,
        "paired_contrast": rescue_observed[1]-rescue_observed[0]}}


def strict_monotone_distributions_sample_no_go():
    # No uniform finite-sample guarantee if the class permits arbitrarily small
    # nonzero response gaps.  Bernoulli product laws approach the null law.
    n_per_arm = 100
    records = []
    for delta in (.1, .01, .001, .0001):
        p, q = .5 + delta, .5
        kl_one = p*math.log(p/q) + (1-p)*math.log((1-p)/(1-q))
        kl_product = n_per_arm*kl_one
        tv_upper = min(1.0, math.sqrt(kl_product/2))
        max_error_lower = max(0.0, (1-tv_upper)/2)
        records.append({"delta": delta, "n_per_arm": n_per_arm,
                        "KL_to_null": kl_product,
                        "Pinsker_TV_upper": tv_upper,
                        "minimax_max_error_lower": max_error_lower})
    return records


def main():
    universe = enumerate_monotone_functions()
    scenarios = [
        ("exterior_calibration_only", []),
        ("one_exact_interior_anchor", [(3, 5, 5)]),
        ("two_exact_interior_anchors", [(2, 3, 3), (4, 7, 7)]),
        ("two_uncertain_interior_anchors", [(2, 2, 4), (4, 6, 8)]),
        ("overlapping_interior_anchor_bands", [(2, 2, 6), (4, 4, 8)]),
    ]
    summaries = [check_scenario(name, anchors, universe) for name, anchors in scenarios]
    result = {
        "kind": "exact finite-model enumeration; no new biological observations",
        "domain": DOMAIN, "output_grid": list(range(GRID_MAX+1)),
        "all_monotone_functions_with_endpoints": len(universe),
        "scenario_count": len(summaries),
        "ordered_pair_checks": sum(summary["ordered_pairs_checked"] for summary in summaries),
        "scenarios": summaries,
        "strict_compression_witnesses": assert_compression_no_go(),
        "contamination_threshold": assert_sharp_contamination_threshold(),
        "finite_sample_no_go": strict_monotone_distributions_sample_no_go(),
        "all_checks_passed": True,
    }
    (ROOT / "calibration_bounds_results.json").write_text(json.dumps(result, indent=2)+"\n")
    with (ROOT / "calibration_bounds_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["scenario", "admissible_functions", "lower_gap", "upper_gap"])
        writer.writeheader()
        for summary in summaries:
            low, high = summary["target_effect_bounds_normalized"]
            writer.writerow({"scenario": summary["name"], "admissible_functions": summary["admissible_functions"],
                             "lower_gap": low, "upper_gap": high})
    print(json.dumps({"all_checks_passed": True, "universe_size": len(universe),
                      "ordered_pairs_checked": result["ordered_pair_checks"],
                      "scenarios": [{"name": summary["name"],
                                     "count": summary["admissible_functions"],
                                     "effect_bounds": summary["target_effect_bounds_normalized"]}
                                    for summary in summaries]}, indent=2))


if __name__ == "__main__":
    main()
