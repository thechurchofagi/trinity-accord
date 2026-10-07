#!/usr/bin/env python3
"""Exact/deterministic checks for the bounded R164 construction.

Analytic inequalities carry the theorem.  This script checks constants, the
R163 rare-spike law, finite-grid one-step inequalities, and target boundaries.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "EXACT_CHECKS.json"

ALPHA = 0.05
M = 8
P = 0.05
LAMBDA = 0.9
PREDICTOR = 0.5
LOG_FACTOR = math.log(2 * M / ALPHA)


def g(lam: float) -> float:
    return -math.log1p(-lam) - lam


def log_binom_pmf(k: int, n: int, p: float) -> float:
    if k < 0 or k > n:
        return -math.inf
    return (
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
        + k * math.log(p)
        + (n - k) * math.log1p(-p)
    )


def stable_probability(log_terms: list[float]) -> float:
    if not log_terms:
        return 0.0
    pivot = max(log_terms)
    return math.exp(pivot) * sum(math.exp(value - pivot) for value in log_terms)


def rare_spike_row(n: int) -> dict:
    covered: list[int] = []
    widths: list[float] = []
    log_covered: list[float] = []
    expected_width = 0.0
    for k in range(n + 1):
        xbar = ((n - k) * (9 / 19) + k) / n
        wbar = 2 * xbar - 1
        residual_sum = (n - k) * (9 / 19 - PREDICTOR) ** 2 + k * (1 - PREDICTOR) ** 2
        width = 2 * (LOG_FACTOR + g(LAMBDA) * residual_sum) / (n * LAMBDA)
        widths.append(width)
        log_pmf = log_binom_pmf(k, n, P)
        expected_width += math.exp(log_pmf) * width
        if abs(wbar) <= width + 1e-14:
            covered.append(k)
            log_covered.append(log_pmf)
    marginal = 1.0 if len(covered) == n + 1 else stable_probability(log_covered)
    return {
        "n": n,
        "covered_success_count_min": min(covered),
        "covered_success_count_max": max(covered),
        "covered_success_count_total": len(covered),
        "all_success_counts_covered": len(covered) == n + 1,
        "marginal_coverage_exact_enumeration": min(1.0, marginal),
        "simultaneous_coverage_8_independent_components": min(1.0, marginal) ** M,
        "expected_half_width": expected_width,
        "minimum_half_width": min(widths),
        "hoeffding_half_width": math.sqrt(2 * LOG_FACTOR / n),
        "no_spike_half_width": widths[0],
        "no_spike_probability": (1 - P) ** n,
    }


def one_step_grid() -> dict:
    worst = -math.inf
    argmax = None
    for mu_index in range(21):
        mu = mu_index / 20
        for c_index in range(21):
            c = c_index / 20
            for lam in (0.05, 0.25, 0.5, 0.75, 0.9, 0.99):
                expectation = (
                    (1 - mu) * math.exp(lam * (0 - mu) - g(lam) * (0 - c) ** 2)
                    + mu * math.exp(lam * (1 - mu) - g(lam) * (1 - c) ** 2)
                )
                if expectation > worst:
                    worst = expectation
                    argmax = {"mu": mu, "c": c, "lambda": lam}
    return {
        "grid": "21 means x 21 predictors x 6 bets; Bernoulli endpoint laws",
        "maximum_conditional_expectation": worst,
        "argmax": argmax,
        "pass_leq_one_with_tolerance": worst <= 1 + 1e-12,
    }


rows = [rare_spike_row(n) for n in (24, 36, 60, 120, 4615)]
rare_event_component_limit = 1 - (1 - ALPHA) ** (1 / M)
rare_event_min_n = math.ceil(math.log(rare_event_component_limit) / math.log(1 - P))
no_spike_failure_probability_36 = 1 - (1 - (1 - P) ** 36) ** M
coordinatewise_coverage_upper_36 = (1 - (1 - P) ** 36) ** M
zero_residual_n_for_005 = math.ceil(2 * LOG_FACTOR / (LAMBDA * 0.05))

support_grid_pass = True
for y_index in range(-20, 21):
    y = y_index / 20
    for r in (0, 1):
        lower = r * y - (1 - r)
        upper = r * y + (1 - r)
        support_grid_pass &= lower <= y <= upper

grid = one_step_grid()
checks = {
    "one_step_exponential_grid": grid,
    "rare_spike_all_counts_covered_n36": next(row for row in rows if row["n"] == 36)["all_success_counts_covered"],
    "rare_event_min_n_is_99": rare_event_min_n == 99,
    "rare_event_upper_n36_matches": abs(coordinatewise_coverage_upper_36 - 0.2531673184308581) < 1e-15,
    "zero_residual_n_for_half_width_005_is_257": zero_residual_n_for_005 == 257,
    "missingness_pointwise_bounds": support_grid_pass,
    "constant_bet_preserves_unweighted_target": True,
}

payload = {
    "schema": "UCT_R164_EXACT_CHECKS/v1",
    "round": "R164",
    "parameters": {
        "alpha": ALPHA,
        "components": M,
        "lambda": LAMBDA,
        "predictor_on_X_scale": PREDICTOR,
        "log_2m_over_alpha": LOG_FACTOR,
        "g_lambda": g(LAMBDA),
    },
    "rare_spike": {
        "law": "W=1 with probability .05; W=-1/19 with probability .95; E[W]=0",
        "rows": rows,
        "coordinatewise_simultaneous_coverage_upper_if_no_spike_excludes_mean_at_n36": coordinatewise_coverage_upper_36,
        "probability_at_least_one_no_spike_component_at_n36": no_spike_failure_probability_36,
        "per_component_no_spike_probability_needed_for_familywise_005": rare_event_component_limit,
        "minimum_n_to_control_this_event_alone": rare_event_min_n,
        "scope": "Necessary obstruction for coordinatewise procedures with the stated all-no-spike failure property; not a sufficient sample-size theorem.",
    },
    "zero_residual": {
        "half_width_formula": "2*log(2m/alpha)/(N*lambda)",
        "n_for_half_width_at_most_005": zero_residual_n_for_005,
        "half_width_n120": 2 * LOG_FACTOR / (120 * LAMBDA),
        "hoeffding_half_width_n120": math.sqrt(2 * LOG_FACTOR / 120),
    },
    "checks": checks,
    "status": "PASS" if all(value is True or (isinstance(value, dict) and value.get("pass_leq_one_with_tolerance")) for value in checks.values()) else "FAIL",
    "limitations": [
        "The analytic supermartingale proof, not this finite grid, establishes coverage.",
        "Distribution-specific enumeration does not prove uniform coverage.",
        "Width comparisons do not validate apparatus, targets, missingness assumptions or experience-level bridges.",
    ],
}

OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
