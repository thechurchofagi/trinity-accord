#!/usr/bin/env python3
"""Deterministic implementation checks for the proved confidence construction.

These finite checks do not prove a continuous parameter claim. PROOF.md does
that analytically. No original empirical fits or simulations are rerun here.
"""
from dataclasses import replace
from datetime import datetime, timezone
from itertools import combinations_with_replacement
from pathlib import Path
import hashlib
import json
import platform

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from scipy.special import ndtr
from scipy.stats import binom, binomtest

import confidence_sets as cs

HERE = Path(__file__).resolve().parent


def direct_rectangle(h1, h2, rho):
    if abs(rho) == 1:
        return 2*ndtr(min(h1, h2))-1
    sd = np.sqrt(1-rho*rho)
    def integrand(z):
        return (np.exp(-z*z/2)/np.sqrt(2*np.pi) *
                (ndtr((h2-rho*z)/sd)-ndtr((-h2-rho*z)/sd)))
    # Split near the conditional-window edges for near-singular correlations.
    points = [x for x in (-h2/rho, h2/rho) if -h1 < x < h1] if rho else []
    return quad(integrand, -h1, h1, epsabs=1e-13, epsrel=1e-12,
                limit=200, points=points)[0]


def direct_candidate_probability_range(a, calibration):
    radius = calibration.kappa*np.sqrt((calibration.v_o-a)*(calibration.v_s-a))
    denominator = np.sqrt(calibration.v_o*calibration.v_s)
    rlo = max(0.0, a-radius)/denominator
    rhi = (a+radius)/denominator
    return (cs.p11_from_abs_rho(float(np.clip(rlo, 0, 1)), calibration),
            cs.p11_from_abs_rho(float(np.clip(rhi, 0, 1)), calibration))


def main():
    receipt = {"created_utc": datetime.now(timezone.utc).isoformat(),
               "runtime": {"python": platform.python_version(),
                           "numpy": np.__version__, "scipy": scipy.__version__},
               "scope": "Deterministic numerical checks, not a machine-certified proof or a continuous-calibration grid envelope."}

    # A genuinely different probability evaluation: conditional-normal integral
    # versus the main routine's Owen-T identity for the ordinary-size rectangles.
    errors = []
    for h1 in [.001, .04, .05, .1, .8, 1.5, 4.]:
        for h2 in [.003, .07, .6, 1.3, 3., 8.]:
            for rho in [-.9999, -.95, -.3, 0., .001, .6, .95, .9999]:
                errors.append(abs(cs.centered_rectangle_probability(h1, h2, rho) -
                                  direct_rectangle(h1, h2, rho)))
    assert max(errors) < 2e-11
    receipt["gaussian_rectangle"] = {"cases": len(errors),
                                     "max_absolute_difference": max(errors),
                                     "comparison": "Direct deterministic conditional-normal quadrature."}

    cp_errors = []
    cp_coverages = []
    for alpha in [.01, .05, .2]:
        for n in [1, 8, 64]:
            intervals = np.array([cs.clopper_pearson(k, n, alpha) for k in range(n+1)])
            for k, interval in enumerate(intervals):
                check = np.array(binomtest(k, n).proportion_ci(confidence_level=1-alpha))
                cp_errors.append(float(np.max(np.abs(interval-check))))
            for p in np.linspace(0, 1, 31):
                inside = (intervals[:, 0] <= p) & (p <= intervals[:, 1])
                covered = float(binom.pmf(np.arange(n+1), n, p) @ inside)
                assert covered >= 1-alpha-2e-13
                cp_coverages.append((alpha, covered))
    assert max(cp_errors) < 2e-11
    assert cs.clopper_pearson(0, 0) == (0.0, 1.0)
    receipt["clopper_pearson"] = {"scipy_root_inversion_comparisons": len(cp_errors),
                                  "max_endpoint_difference": max(cp_errors),
                                  "finite_binomial_coverage_checks": len(cp_coverages),
                                  "minimum_coverage_minus_nominal": min(c-(1-a) for a, c in cp_coverages)}

    variance_pairs = [(1., 1.), (1., 4.), (4., 1.), (.04, 5.),
                      (9., 10.), (100., 200.), (.5, .6)]
    kappas = [0., .02, .2, .8, 1-1e-8, 1.]
    range_errors, projection_checks, ambiguous = [], 0, 0
    inverse_errors = []
    for v1, v2 in variance_pairs:
        for kap in kappas:
            cal = cs.PairCalibration(v1, v2, .8*np.sqrt(v1), 1.3*np.sqrt(v2), .05, .12, kap)
            m, den = min(v1, v2), np.sqrt(v1*v2)
            def upper_covariance(a):
                return (a+kap*np.sqrt(max(0, (v1-a)*(v2-a))))/den
            numerical = minimize_scalar(lambda x: -upper_covariance(x),
                                         bounds=(0., m), method="bounded",
                                         options={"xatol": 1e-13*m})
            maximum = max(upper_covariance(0.), upper_covariance(m), -numerical.fun)
            analytic = cs.attainable_abs_rho_max(cal)
            range_errors.append(abs(analytic-maximum))
            assert analytic >= maximum-2e-12
            assert abs(analytic-maximum) < 2e-8
            pmin, pmax = cs.attainable_probability_range(cal)
            assert cs.confidence_set(0, 0, cal).a_interval == (0., m)
            ppoints = [pmin+(pmax-pmin)*f for f in [0., .1, .5, .9, 1.]]
            pintervals = list(combinations_with_replacement(ppoints, 2))
            pintervals += [(0., 1.), (0., pmin/2), ((pmax+1)/2, 1.)]
            candidates = np.linspace(0, m, 101)
            direct = [direct_candidate_probability_range(float(a), cal) for a in candidates]
            for plo, phi in pintervals:
                projected = cs.project_probability_interval(plo, phi, cal)
                for a, (amin, amax) in zip(candidates, direct):
                    # Boundary values are checked with declared numerical
                    # tolerances, without treating them as probability errors.
                    expected = plo <= amax+1e-12 and phi >= amin-1e-12
                    actual = projected.contains(float(a), atol=2e-9*m)
                    if expected != actual:
                        margin = min(abs(plo-amax), abs(phi-amin))
                        if margin < 1e-10:
                            ambiguous += 1
                            continue
                        raise AssertionError((v1, v2, kap, plo, phi, a,
                                              projected.to_dict(), (amin, amax)))
                    projection_checks += 1
            # Keep off the r=0 weak inverse when reporting its numerical error.
            for fraction in [.1, .4, .8]:
                r = analytic*fraction
                p = cs.p11_from_abs_rho(r, cal)
                result = cs.population_identified_set(p, cal)
                inverse_errors.append(max(abs(x-r) for x in result.rho_interval))
    receipt["unequal_variance_projection"] = {
        "calibrations": len(variance_pairs)*len(kappas),
        "global_max_comparison": "Analytic formula versus bounded scalar maximization plus both domain endpoints.",
        "max_global_rho_difference": max(range_errors),
        "direct_candidate_membership_checks": projection_checks,
        "numerically_ambiguous_boundary_checks_not_counted": ambiguous,
        "max_off_boundary_rho_inverse_error": max(inverse_errors),
        "note": "Finite implementation checks; continuity and sharpness are proved analytically in PROOF.md."}

    # The degenerate cases have one attainable probability, and therefore the
    # entire a-domain or the empty set. They must not return a boundary estimate.
    base = cs.PairCalibration(1., 4., .8, 2.6, .05, .12, .2)
    degenerates = [replace(base, k_o=0.), replace(base, k_s=0.),
                   replace(base, k_o=0., k_s=0.), replace(base, lapse_o=1.),
                   replace(base, lapse_s=1.), replace(base, lapse_o=1., lapse_s=1.),
                   replace(base, k_o=0., lapse_o=0.)]
    for cal in degenerates:
        pmin, pmax = cs.attainable_probability_range(cal)
        assert pmin == pmax
        assert cs.project_probability_interval(pmin, pmax, cal).a_interval == (0., 1.)
        assert cs.project_probability_interval(0., 1., cal).a_interval == (0., 1.)
        incompatible = ((pmax+1)/2, 1.) if pmax < 1 else (0., .5)
        assert cs.project_probability_interval(*incompatible, cal).empty
    receipt["degenerate_readouts"] = {"cases": len(degenerates), "all_passed": True,
                                      "n_zero_contract_checked_for": len(variance_pairs)*len(kappas)}

    base = cs.PairCalibration(1., 1., .8, 1.3, .05, .05, .2)
    large = cs.PairCalibration(25., 25., 4., 6.5, .05, .05, .2)
    finite = cs.finite_calibration_union(2200, 4096, [base, large], alpha=.025, gamma=.025)
    assert len(finite.intervals) == 2
    assert finite.coverage_lower_bound == .95
    assert not finite.contains((finite.intervals[0][1]+finite.intervals[1][0])/2)
    assert cs.finite_calibration_union(1, 8, [], alpha=.025, gamma=.025).empty
    kappa_union = cs.kappa_calibration_interval(500, 1024, base, .02, .2, alpha=.025, gamma=.025)
    endpoint = cs.confidence_set(500, 1024, replace(base, kappa=.2), alpha=.025)
    assert kappa_union.intervals == (endpoint.a_interval,)
    for kap in np.linspace(.02, .2, 23):
        partial = cs.confidence_set(500, 1024, replace(base, kappa=float(kap)), alpha=.025)
        assert kappa_union.contains(partial.a_interval[0], atol=1e-12)
        assert kappa_union.contains(partial.a_interval[1], atol=1e-12)
    receipt["calibration_unions"] = {"finite_union_preserves_two_disjoint_intervals": finite.intervals,
                                     "continuous_kappa_result": kappa_union.intervals,
                                     "nominal_joint_lower_bound": finite.coverage_lower_bound,
                                     "continuous_multivariate_grid_envelope_claimed": False}

    # Physical signed-covariance twins are identical centrally; the nuisance
    # projection admits negative correlations without treating c as sensory a.
    cal = cs.PairCalibration(1., 1., .8, 1.3, .05, .05, .2)
    pneg = cs.paired_yes_probability(.1, -.18, cal)
    ppos = cs.paired_yes_probability(.1, -.02, cal)
    assert abs(pneg-ppos) < 1e-14
    assert cs.population_identified_set(pneg, cal).contains(.1, atol=1e-12)
    receipt["signed_covariance"] = {"negative_total_covariance": -.08,
                                    "positive_total_covariance": .08,
                                    "joint_probability_difference": abs(pneg-ppos),
                                    "true_a_retained_in_population_union": True}

    receipt["sha256"] = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                         for name in ["confidence_sets.py", "check_confidence_sets.py", "PROOF.md"]}
    receipt["status"] = "PASS"
    output = HERE/"CONFIDENCE_SET_CHECKS.json"
    output.write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
