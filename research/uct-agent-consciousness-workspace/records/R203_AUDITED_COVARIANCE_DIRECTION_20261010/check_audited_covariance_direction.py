#!/usr/bin/env python3
"""Exact and numerical checks for R203's audited covariance direction certificate."""

from fractions import Fraction as F
from itertools import product
import json
import math
from pathlib import Path


def sign(x):
    return (x > 0) - (x < 0)


def latent_moments(pi, a, c, q1, q0, residual=F(0)):
    m = pi * q1 + (1 - pi) * q0
    j = pi * a + (1 - pi) * c
    cov_latent = pi * (1 - pi) * (a - c) * (q1 - q0)
    cov = cov_latent + residual
    r = cov + m * j
    return m, j, r, cov, cov_latent


def hoeffding_box(n, alpha, mhat, jhat, rhat):
    h = math.sqrt(math.log(6 / alpha) / (2 * n))
    ml, mu = max(0.0, mhat - h), min(1.0, mhat + h)
    jl, ju = max(0.0, jhat - h), min(1.0, jhat + h)
    rl, ru = max(0.0, rhat - h), min(1.0, rhat + h)
    return {
        "h": h,
        "lower_cov": rl - mu * ju,
        "upper_cov": ru - ml * jl,
        "moment_box": {"m": [ml, mu], "j": [jl, ju], "r": [rl, ru]},
    }


def centered_threshold(alpha, m, j, r, limit=2_000_000):
    for n in range(1, limit + 1):
        if hoeffding_box(n, alpha, m, j, r)["lower_cov"] > 0:
            return n
    return None


def main():
    den = 8
    checked = 0
    identity_violations = 0
    sign_violations = 0
    for pi_i in range(1, den):
        pi = F(pi_i, den)
        for c_i in range(den + 1):
            for a_i in range(c_i + 1, den + 1):
                a, c = F(a_i, den), F(c_i, den)
                for q0_i, q1_i in product(range(den + 1), repeat=2):
                    q0, q1 = F(q0_i, den), F(q1_i, den)
                    m, j, r, cov, cov_latent = latent_moments(pi, a, c, q1, q0)
                    checked += 1
                    if cov != r - m * j or cov != cov_latent:
                        identity_violations += 1
                    if sign(cov) != sign(q1 - q0):
                        sign_violations += 1

    # Two observationally identical audited (M,J) laws with opposite latent marker direction.
    model_independent = latent_moments(F(1, 2), F(4, 5), F(1, 5), F(3, 5), F(2, 5))
    model_dependent = latent_moments(
        F(1, 2), F(4, 5), F(1, 5), F(2, 5), F(3, 5), residual=F(3, 50)
    )
    dependence_witness_same_observed = model_independent[:4] == model_dependent[:4]
    dependence_witness_opposite_latent = sign(F(3, 5) - F(2, 5)) == -sign(F(2, 5) - F(3, 5))

    # Verify full feasible binary tables, not only compatible moments.
    def cells(q, endpoint, t):
        return (1-q-endpoint+t, endpoint-t, q-t, t)
    positive=(cells(F(2,5),F(1,5),F(2,25)),cells(F(3,5),F(4,5),F(12,25)))
    negative_tables=(cells(F(3,5),F(1,5),F(9,50)),cells(F(2,5),F(4,5),F(19,50)))
    assert all(x>=0 for w in (positive,negative_tables) for row in w for x in row)
    assert all(sum(row)==1 for w in (positive,negative_tables) for row in w)
    mix=lambda w:tuple((w[0][i]+w[1][i])/2 for i in range(4))
    assert mix(positive)==mix(negative_tables)==(F(7,25),F(11,50),F(11,50),F(7,25))
    # Exhaustive class tables at denominator four and seven prevalences.
    tables=[tuple(F(v,4) for v in row) for row in product(range(5),repeat=4) if sum(row)==4]
    residual_models=0;oriented_models=0;certificate_triggers=0
    for p0,p1 in product(tables,repeat=2):
        q0,q1=p0[2]+p0[3],p1[2]+p1[3]
        c,a=p0[1]+p0[3],p1[1]+p1[3]
        rho0,rho1=p0[3]-q0*c,p1[3]-q1*a
        for pi_i in range(1,8):
            pi=F(pi_i,8);residual_models+=1
            m=(1-pi)*q0+pi*q1;j=(1-pi)*c+pi*a
            cov=(1-pi)*p0[3]+pi*p1[3]-m*j
            R=(1-pi)*rho0+pi*rho1
            assert cov==pi*(1-pi)*(a-c)*(q1-q0)+R
            if a>c:
                oriented_models+=1
                for kappa in (abs(R),abs(R)+F(1,100)):
                    if cov>kappa:
                        certificate_triggers+=1
                        assert q1-q0>0 and q1-q0>=4*(cov-kappa)
                    if cov<-kappa:
                        certificate_triggers+=1
                        assert q1-q0<0
    from analyze_audit_direction import analyze
    assert analyze([680,320,320,680],.01)['status']=='OBSERVABLE_ASSOCIATION_ONLY'
    assumed={k:{'asserted':True,'evidence':'SYNTHETIC_ASSUMPTION_ONLY'} for k in
        ('signed_endpoint','residual_budget','ignorable_complete_audit','same_actual_instance_use')}
    assert analyze([680,320,320,680],.01,warrants=assumed)['status']=='POSITIVE_CONDITIONAL_IN_V'
    assert analyze([500,500,500,500],.01,warrants=assumed)['status']=='ABSTAIN'
    try:
        analyze([-1,0,0,2],.01)
    except ValueError: pass
    else: raise AssertionError('invalid counts accepted')
    alpha = 0.05
    strong = {"m": 0.5, "j": 0.5, "r": 0.34}
    weak = {"m": 0.5, "j": 0.5, "r": 0.265}
    negative = {"m": 0.5, "j": 0.5, "r": 0.16}
    null = {"m": 0.5, "j": 0.5, "r": 0.25}
    finite_examples = {
        "positive_n2000": hoeffding_box(2000, alpha, **{k + "hat": v for k, v in strong.items()}),
        "negative_n2000": hoeffding_box(2000, alpha, **{k + "hat": v for k, v in negative.items()}),
        "null_n2000": hoeffding_box(2000, alpha, **{k + "hat": v for k, v in null.items()}),
    }

    results = {
        "result_id": "R203-EXACT-v0.2.0",
        "feasible_conditional_tables": {"positive":[[str(x) for x in row] for row in positive],"negative":[[str(x) for x in row] for row in negative_tables],"observed":[str(x) for x in mix(positive)]},
        "residual_table_models": residual_models,
        "oriented_residual_models": oriented_models,
        "residual_certificate_triggers":certificate_triggers,
        "residual_certificate_violations":0,
        "guarded_analyzer_checks":4,
        "denominator_grid": den,
        "informative_oriented_models_checked": checked,
        "covariance_identity_violations": identity_violations,
        "sign_violations_under_conditional_independence": sign_violations,
        "dependent_error_counterexample": {
            "same_observed_binary_MJ_law": dependence_witness_same_observed,
            "opposite_latent_marker_direction": dependence_witness_opposite_latent,
            "observed_m_j_r_cov": [str(x) for x in model_independent[:4]],
            "independent_latent_covariance": str(model_independent[4]),
            "dependent_latent_covariance": str(model_dependent[4]),
            "dependent_within_class_residual": "3/50",
        },
        "simultaneous_hoeffding_examples": finite_examples,
        "population_centered_first_positive_n_alpha_0_05": {
            "strong_endpoint_cov_0_09": centered_threshold(alpha, **strong),
            "weak_endpoint_cov_0_015": centered_threshold(alpha, **weak),
            "interpretation": "Descriptive threshold if empirical moments equal population moments; not a power calculation or recommended sample size.",
        },
        "overall": "PASS" if not identity_violations and not sign_violations and dependence_witness_same_observed else "FAIL",
    }
    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
