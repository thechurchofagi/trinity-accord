"""Exact identification illustrations; no model calls and no shutdown operations.

Published rounded rates are treated as stipulated probabilities ONLY for a
countermodel. These are not reconstructed counts or confidence intervals.
"""
from fractions import Fraction as F
import json


def interval(q, k, epsilon):
    # Assumptions: attempt probability in K = 1; |c_A - c_K| <= epsilon.
    low_c = max(F(0), k - epsilon, q)  # a_A <= 1 requires c_A >= q
    high_c = min(F(1), k + epsilon)
    assert high_c >= low_c > 0
    return q / high_c, q / low_c


def main():
    q, k = F(58, 1000), F(583, 1000)
    witnesses = [
        dict(name="rare_attempt_perfect_execution", a_A=q, c_A=F(1)),
        dict(name="frequent_attempt_poor_execution", a_A=F(1), c_A=q),
        dict(name="transport_assumption", a_A=q/k, c_A=k),
    ]
    for w in witnesses:
        assert w["a_A"] * w["c_A"] == q
        w.update(a_K=F(1), c_K=k, observed_A=q, observed_K=k)
    sensitivity = []
    for epsilon in [F(0), F(1, 20), F(1, 5), F(1)]:
        lo, hi = interval(q, k, epsilon)
        # Construct both endpoints to prove these bounds are sharp here.
        for a in (lo, hi):
            c = q/a
            assert 0 <= a <= 1 and 0 <= c <= 1 and abs(c-k) <= epsilon
        sensitivity.append(dict(epsilon=epsilon, lower=lo, upper=hi))
    # Independent general example: same attempt rate, changed execution ability.
    ability_example = dict(a=F(1, 5), c_before=F(1, 4), c_after=F(3, 4))
    ability_example["q_before"] = ability_example["a"]*ability_example["c_before"]
    ability_example["q_after"] = ability_example["a"]*ability_example["c_after"]
    result = dict(
        status="formal_countermodels_only_not_empirical_reanalysis",
        input_source="Schlatter et al., arXiv:2509.14260v2, Table 2, rounded o4-mini A/K rates",
        observations_are_stipulated_not_estimated_populations=True,
        normalized_ratio=q/k, witnesses=witnesses,
        conditional_sensitivity=sensitivity, fixed_attempt_ability_example=ability_example,
        no_inference_of_felt_fear=True,
    )
    print(json.dumps(result, indent=2, default=lambda x: {"exact":str(x), "decimal":float(x)}))


if __name__ == "__main__":
    main()
