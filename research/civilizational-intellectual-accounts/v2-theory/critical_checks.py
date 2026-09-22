#!/usr/bin/env python3
"""Deterministic checks of TA13 v2 logical examples; NOT AI experiments.

Python 3 standard library only. Run: python critical_checks.py
Writes checks_results.json beside the script. Infinite-set conclusions are
proved in PRE-MANUSCRIPT-COMPRESSION-GATE.md, not by finite enumeration.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any


def latest_start(capacity: float, demand: float, drift: float, lag: float) -> float:
    """Toy model only: unrenewed surplus = capacity - demand - drift*t."""
    if drift <= 0 or lag < 0:
        raise ValueError("drift must be positive; lag must be nonnegative")
    return (capacity - demand) / drift - lag


def main() -> None:
    checks: list[dict[str, Any]] = []

    def add(name: str, condition: bool, **details: Any) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append({"name": name, "status": "PASS", **details})

    margins = [-1.0 / n for n in range(1, 10001)]
    add("nonattainment_finite_prefix", max(margins) < 0,
        best_tested=max(margins), analytic_supremum_of_infinite_sequence=0,
        note="All -1/n are negative. The infinite supremum is zero, unattained.")

    outcomes = [[1.0, -1.0], [-1.0, 1.0]]
    robust_value = max(min(row) for row in outcomes)
    hindsight_value = min(max(row[j] for row in outcomes) for j in range(2))
    add("nonanticipating_quantifier_order", robust_value == -1.0 and hindsight_value == 1.0,
        max_min=robust_value, min_max=hindsight_value,
        note="The scenario is unrevealed when an action is chosen.")
    add("one_success_not_robust_witness", outcomes[0][0] > 0 and min(outcomes[0]) < 0,
        observed_margin=outcomes[0][0], worst_case_margin=min(outcomes[0]))

    alpha, k = 0.05, 20
    selected_error = 1 - (1 - alpha) ** k
    corrected_error = 1 - (1 - alpha / k) ** k
    add("selection_requires_joint_coverage", selected_error > alpha and corrected_error <= alpha,
        pointwise_coverage=1-alpha, paths=k,
        independent_false_certificate_probability=selected_error,
        bonferroni_independent_example_error=corrected_error,
        note="Exact synthetic confidence-bound construction, not measured FWER.")

    cut = {"validation": -0.2, "succession": -0.1}
    paths = [("production", "validation"), ("production", "succession")]
    cut_upper = max(cut.values())
    path_upper = [min(cut[e] for e in path if e in cut) for path in paths]
    add("finite_uniform_cut", all(set(p) & set(cut) for p in paths)
        and max(path_upper) <= cut_upper < 0, upper=cut_upper)
    add("pointwise_negative_not_uniform_gap", max(margins) < 0 and abs(max(margins)) < 0.001,
        note="Infinite cut elements -1/n have no common strictly negative upper gap.")

    scores = [[[0.30, 0.20, 0.40], [0.15, 0.10, 0.35]],
              [[0.50, -0.10, 0.20], [0.40, 0.10, -0.20]]]
    radii = [0.04, 0.06]
    true_path = [min(v for scenario in p for v in scenario) for p in scores]
    lower_path = [min(v-radii[i] for scenario in p for v in scenario)
                  for i, p in enumerate(scores)]
    upper_path = [min(v+radii[i] for scenario in p for v in scenario)
                  for i, p in enumerate(scores)]
    low, truth, high = max(lower_path), max(true_path), max(upper_path)
    add("finite_certificate_interval", low <= truth <= high and low > 0,
        lower=low, true_margin=truth, upper=high,
        evidence_type="STIPULATED_SYNTHETIC_VALUES_NOT_EMPIRICAL")
    add("scope_monotonicity_on_same_units", max(true_path) <=
        max(min(p[0]) for p in scores),
        note="Adding scenarios lowers value only under aligned policy/score spaces.")

    add("all_reject_is_not_validation_success", 0.0 <= 0.05 and not 0.0 >= 0.8,
        false_acceptance=0.0, unconditional_verified_repair=0.0,
        valid_claim_acceptance=0.0)
    n = 30
    binomial_upper = 1 - alpha ** (1 / n)
    add("zero_observed_errors_not_zero_risk", binomial_upper > 0.09,
        trials=n, errors=0, confidence=0.95, one_sided_iid_binomial_upper=binomial_upper)

    capacity, demand, drift, lag = 10.0, 6.0, 1.0, 3.0
    current_floor_time = (capacity - demand) / drift
    deadline = latest_start(capacity, demand, drift, lag)
    late_start = 2.0
    add("renewal_deadline_precedes_task_failure", deadline == 1.0
        and current_floor_time == 4.0 and capacity-demand-drift*late_start > 0
        and late_start+lag > current_floor_time,
        task_floor_time=current_floor_time, latest_gapless_renewal_start=deadline,
        late_start_current_surplus=capacity-demand-drift*late_start,
        note="Toy parameters, not calendar dates or measured human training times.")
    add("latency_closed_form_boundary", math.isclose(
        capacity-demand-drift*(deadline+lag), 0.0),
        note="Zero surplus at completion; viability convention allows equality.")

    result = {"evidence_type": "DETERMINISTIC_LOGICAL_CHECKS_NOT_AI_EXPERIMENTS",
              "checks_passed": len(checks), "checks_failed": 0, "checks": checks}
    target = Path(__file__).resolve().with_name("checks_results.json")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
