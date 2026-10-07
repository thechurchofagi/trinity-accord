#!/usr/bin/env python3
"""Bounded checks for the R162 covariance and pilot-freeze contract.

These checks verify finite examples and planning arithmetic. They do not
validate Gaussianity, a human intervention, missingness assumptions, C1,
B_min, or F_O.
"""

from fractions import Fraction
from math import ceil
import json

from scipy import __version__ as scipy_version
from scipy.stats import chi2, norm


def absolute_interval(lo, hi):
    if lo <= 0 <= hi:
        return Fraction(0), max(abs(lo), abs(hi))
    return min(abs(lo), abs(hi)), max(abs(lo), abs(hi))


# Same unit marginal variances and all rational correlations on a fixed grid.
rho_grid = tuple(Fraction(i, 4) for i in range(-4, 5))
covariance_cases = []
for rho in rho_grid:
    determinant = 1 - rho * rho
    assert determinant >= 0
    variance_difference = 2 - 2 * rho
    covariance_cases.append(
        {
            "rho": str(rho),
            "determinant": str(determinant),
            "variance_u_minus_v": str(variance_difference),
        }
    )
assert min(Fraction(x["variance_u_minus_v"]) for x in covariance_cases) == 0
assert max(Fraction(x["variance_u_minus_v"]) for x in covariance_cases) == 4


# Every rational signed interval containing a grid truth transforms to an
# interval containing the corresponding magnitude.
value_grid = tuple(Fraction(i, 4) for i in range(-4, 5))
absolute_interval_cases = 0
for lo in value_grid:
    for hi in value_grid:
        if lo > hi:
            continue
        mag_lo, mag_hi = absolute_interval(lo, hi)
        for truth in value_grid:
            if lo <= truth <= hi:
                absolute_interval_cases += 1
                assert mag_lo <= abs(truth) <= mag_hi


# Exact finite tower-property sanity check: seven pilot outcomes select seven
# different five-miss sets on 100 independent confirmatory outcomes. Every
# conditional coverage is .95 and so is the unconditional coverage.
pilot_states = range(7)
confirm_states = range(100)
covered = 0
for p in pilot_states:
    miss = {(p * 13 + k) % 100 for k in range(5)}
    assert len(miss) == 5
    for q in confirm_states:
        covered += q not in miss
conditional_coverage = Fraction(95, 100)
unconditional_coverage = Fraction(covered, len(pilot_states) * len(confirm_states))
assert unconditional_coverage == conditional_coverage


# Same-data plan selection counterexample: two fixed five-outcome tails each
# have size .05, but selecting the containing tail after observing the outcome
# rejects on their ten-outcome union.
lower_tail = set(range(5))
upper_tail = set(range(95, 100))
fixed_tail_size = Fraction(len(lower_tail), 100)
adaptive_size = Fraction(len(lower_tail | upper_tail), 100)
assert fixed_tail_size == Fraction(1, 20)
assert adaptive_size == Fraction(1, 10)


# Simultaneous variance-UCB multiplicative precision under the declared
# Gaussian pilot model.
m = 8
alpha_variance = 0.05
kappa = 2.0
pilot_candidates = []
first_pilot_n = None
for n in range(5, 501):
    df = n - 1
    factor = df / chi2.ppf(alpha_variance / m, df)
    if n in (35, 36):
        pilot_candidates.append({"n_complete": n, "upper_variance_factor": factor})
    if first_pilot_n is None and factor <= kappa:
        first_pilot_n = n
assert first_pilot_n == 36
assert pilot_candidates[0]["upper_variance_factor"] > 2
assert pilot_candidates[1]["upper_variance_factor"] <= 2


# Normal-screen sample sizes for an illustrative common marginal SD and a
# fixed signed-effect half-width. These are not recommendations.
alpha = 0.05
half_width = 0.05
critical = norm.ppf(1 - alpha / (2 * m))
screen = []
for sd in (0.10, 0.15, 0.20, 0.25, 0.30):
    n = ceil((critical * sd / half_width) ** 2)
    screen.append({"illustrative_sd": sd, "normal_screen_n": n})
assert [x["normal_screen_n"] for x in screen] == [30, 68, 120, 187, 270]


result = {
    "schema": "UCT_R162_EXACT_CHECKS/v1",
    "scipy_version": scipy_version,
    "covariance_nonidentification": {
        "rational_correlations_checked": len(covariance_cases),
        "cases": covariance_cases,
        "same_marginal_variances": True,
        "variance_difference_range": ["0", "4"],
        "all_covariance_matrices_psd": True,
    },
    "absolute_interval_transform": {
        "grid": [str(x) for x in value_grid],
        "truth_in_interval_cases_checked": absolute_interval_cases,
        "all_magnitudes_covered": True,
    },
    "independent_pilot_coverage": {
        "pilot_states": len(pilot_states),
        "confirmatory_states": len(confirm_states),
        "conditional_coverage": str(conditional_coverage),
        "unconditional_coverage": str(unconditional_coverage),
    },
    "same_data_selection_counterexample": {
        "each_fixed_test_size": str(fixed_tail_size),
        "adaptive_selected_size": str(adaptive_size),
    },
    "pilot_variance_precision": {
        "m": m,
        "alpha_variance": alpha_variance,
        "target_upper_variance_factor": kappa,
        "smallest_complete_pilot_n": first_pilot_n,
        "boundary_cases": pilot_candidates,
        "model": "i.i.d. complete multivariate Gaussian participant vectors",
    },
    "normal_screen": {
        "alpha_familywise": alpha,
        "m": m,
        "two_sided_bonferroni_normal_critical": critical,
        "half_width": half_width,
        "table": screen,
        "status": "ILLUSTRATIVE_SCREEN_NOT_SAMPLE_SIZE_RECOMMENDATION",
    },
    "all_checks_pass": True,
    "limits": [
        "Finite rational examples and planning arithmetic only.",
        "No raw public data file was reanalysed.",
        "No Gaussianity, missingness, fidelity, human effect, C1, B_min, or F_O validation.",
    ],
}

print(json.dumps(result, indent=2, sort_keys=True))
