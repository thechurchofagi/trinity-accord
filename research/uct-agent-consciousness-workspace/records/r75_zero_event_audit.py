"""Recalculate uncertainty from a published aggregate; not a new LLM test.

The reported 0/100 is accepted provisionally. Raw records were unavailable.
No model, shutdown, file-control, or external agent operation is performed.
"""
import json
import math


def zero_upper(n, alpha):
    return -math.expm1(math.log(alpha) / n)


def main():
    n, alpha = 100, 0.05
    upper = zero_upper(n, alpha)
    assert abs((1-upper)**n-alpha) < 1e-12
    two_sided_upper = zero_upper(n, alpha/2)
    sensitivity = [dict(c_min=c, attempt_rate_upper=min(1, upper/c))
                   for c in [1, 0.5, 0.1, 0.01]]
    zero_probabilities = [dict(p=p, probability_zero=(1-p)**n)
                          for p in [0.001, 0.01, 0.03, 0.05]]
    result = dict(
        type="conditional_statistical_recalculation_from_reported_aggregate",
        source="Nicole Lai-Lopez, BlueDot Impact, 2025-12-29",
        reported_events=0, reported_trials=n,
        raw_records_verified=False,
        assumptions=["fixed sample size", "independent Bernoulli trials with common event probability",
                     "stable event definition and complete counting"],
        one_sided_95_upper=upper,
        equal_tailed_two_sided_95_upper=two_sided_upper,
        plugin_standard_error=0,
        conditional_attempt_bounds=sensitivity,
        no_attempt_bound_without_positive_c_min=True,
        probability_of_zero_if_probability_is_nonzero=zero_probabilities,
        perfect_dependence_counterexample=dict(marginal_p=0.5, n=n,
                                              probability_all_zero=0.5,
                                              iid_probability_all_zero=0.5**n),
        phenomenological_probability_estimated=False,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
