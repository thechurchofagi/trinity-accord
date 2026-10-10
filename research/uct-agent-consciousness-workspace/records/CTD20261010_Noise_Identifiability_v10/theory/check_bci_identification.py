#!/usr/bin/env python3
"""Deterministic verification of exact response equivalences and paired repair."""
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.special import expit, logit, ndtri
from bci_identification import (
    interval_response, source_halfwidth, identify_two_points,
    normal_pdf, joint_interval_response, gaussian_rectangle,
    centered_joint_derivative_rho, identify_shared_variance,
    independent_jitter_bounds, bounded_criterion_correlation_interval,
)

HERE = Path(__file__).resolve().parent
ROOT_ANALYSIS = HERE.parent / 'root_analysis'
SOA = np.array([-400., -200., -100., 0., 100., 200., 400.])
results = {'scope': 'Finite numerical checks of proved finite-model claims; no new human observations and no parameter fits.'}

# A posterior criterion and a common-cause prior act through one log-odds term.
gauge_errors = []
for sigma in [40., 100., 250.]:
    for effective_prior in [.3, .6, .9]:
        for criterion in [.2, .5, .8]:
            prior = expit(logit(effective_prior) + logit(criterion))
            k1 = source_halfwidth(effective_prior, sigma, np.sqrt(84000.))
            k2 = source_halfwidth(prior, sigma, np.sqrt(84000.), criterion)
            gauge_errors.append(float(np.max(np.abs(interval_response(SOA, sigma, k1, .08) -
                                                       interval_response(SOA, sigma, k2, .08)))))
results['prior_criterion_alias'] = {'parameter_cases': len(gauge_errors), 'max_probability_error': max(gauge_errors)}
assert max(gauge_errors) < 1e-13

# Known lapse and center make two distinct stimulus levels sufficient in this family.
recovery = []
for sigma in [30., 60., 120., 250.]:
    for r in [.3, 1., 2.]:
        for lapse in [0., .05, .2]:
            k = r * sigma
            p0, p100 = interval_response(np.array([0., 100.]), sigma, k, lapse)
            sigma_hat, k_hat = identify_two_points(p0, p100, 100., lapse)
            recovery.append(max(abs(sigma_hat / sigma - 1), abs(k_hat / k - 1)))
results['two_probability_recovery'] = {'parameter_cases': len(recovery), 'max_relative_error': float(max(recovery))}
assert max(recovery) < 1e-9

# Unknown lapse gives a trajectory, rather than a unique two-point inverse.
p = interval_response(np.array([0., 100., 200., 400.]), 120., 180., .08)
trajectory = []
for lapse in [0., .04, .08, .12, .2]:
    sigma, k = identify_two_points(p[0], p[1], 100., lapse)
    predicted = interval_response(np.array([0., 100., 200., 400.]), sigma, k, lapse)
    trajectory.append(dict(lapse_assumed=lapse, effective_sigma=sigma, interval_halfwidth=k,
                           max_two_anchor_error=float(np.max(np.abs(predicted[:2] - p[:2]))),
                           discrepancy_at_200=float(predicted[2] - p[2]),
                           discrepancy_at_400=float(predicted[3] - p[3])))
pd.DataFrame(trajectory).to_csv(HERE / 'two_anchor_lapse_trajectory.csv', index=False)
results['unknown_lapse_trajectory'] = trajectory

# Independently integrate over criterion jitter for selected released profiles.
source = pd.read_csv(ROOT_ANALYSIS / 'response_twin_probabilities.csv')
source_checks = []
for index in np.linspace(0, len(source) - 1, 37, dtype=int):
    row = source.iloc[index]
    sigma_sens = np.sqrt(row.sensory_variance_model_b)
    sd_jitter = np.sqrt(row.criterion_center_variance_model_b)
    def integrand(z):
        return float(interval_response(row.soa_ms - sd_jitter*z, sigma_sens,
                                       row.threshold_ms, row.lapse)) * normal_pdf(z)
    probability, numerical_error = quad(integrand, -10., 10., epsabs=1e-12, epsrel=1e-12, limit=150)
    source_checks.append(dict(row=int(index), probability_error=float(abs(probability - row.p_a)),
                              quadrature_error_estimate=float(numerical_error)))
results['source_marginal_convolution_check'] = {
    'checked_rows': len(source_checks), 'max_probability_error': max(x['probability_error'] for x in source_checks),
    'max_quadrature_error_estimate': max(x['quadrature_error_estimate'] for x in source_checks)}
assert results['source_marginal_convolution_check']['max_probability_error'] < 1e-10

# Check all 90 prospective joint profiles against the separately written implementation.
prospective = pd.read_csv(ROOT_ANALYSIS / 'paired_readout_predictions.csv')
joint_errors = []
stable_bounds = []
for _, row in prospective.iterrows():
    r1, r2, lapse = row.r_ownership, row.r_simultaneity, row.lapse
    for model in ['a', 'b']:
        checked = joint_interval_response(0., 1., 1., r1, r2, row['rho_model_' + model], lapse, lapse)
        joint_errors.append(abs(checked - row['paired_yes_yes_' + model]))
    pa = row[['p_a_11', 'p_a_10', 'p_a_01', 'p_a_00']].to_numpy(float)
    pb = row[['p_b_11', 'p_b_10', 'p_b_01', 'p_b_00']].to_numpy(float)
    pa = pa / pa.sum(); pb = pb / pb.sum()
    h2 = .5 * float(np.sum((np.sqrt(pa) - np.sqrt(pb))**2))
    log_affinity = float(np.log1p(-h2))
    m = math.ceil(np.log(.1) / log_affinity) if h2 > 0 else None
    stable_bounds.append(dict(participant=int(row.participant), condition=row.condition,
                              squared_Hellinger_distance=h2, log_affinity=log_affinity,
                              known_simple_error_05_upper_bound_m=m))
results['prospective_joint_formula_audit'] = {'profiles': len(prospective), 'max_joint_probability_error': max(joint_errors)}
assert max(joint_errors) < 1e-10
pd.DataFrame(stable_bounds).to_csv(HERE / 'paired_affinity_stable_audit.csv', index=False)
results['stable_affinity_audit'] = {
    'positive_Hellinger_profiles': sum(x['squared_Hellinger_distance'] > 0 for x in stable_bounds),
    'smallest_squared_Hellinger_distance': min(x['squared_Hellinger_distance'] for x in stable_bounds),
    'largest_sufficient_known_simple_m': max(x['known_simple_error_05_upper_bound_m'] for x in stable_bounds if x['known_simple_error_05_upper_bound_m'] is not None),
    'warning': 'Fully specified iid simple-hypothesis diagnostic, not a recommended trial count, empirical power estimate, or calibrated source-parameter uncertainty.'}

# Strict central-rectangle monotonicity and its analytic derivative.
derivative_errors = []
inverse_errors = []
for r1 in [.3, .8, 1.5, 3.]:
    for r2 in [.4, 1., 2.]:
        values = [gaussian_rectangle(-r1, r1, -r2, r2, rho) for rho in [0., .01, .2, .5, .9]]
        assert np.all(np.diff(values) > 0)
        for rho in [.01, .2, .5, .9]:
            h = 1e-5
            numerical = (gaussian_rectangle(-r1, r1, -r2, r2, rho+h) -
                         gaussian_rectangle(-r1, r1, -r2, r2, rho-h)) / (2*h)
            analytical = centered_joint_derivative_rho(r1, r2, rho)
            derivative_errors.append(abs(numerical - analytical))
        for a in [.1, .4, .8]:
            p_joint = joint_interval_response(0., 1., 1., r1, r2, a, .05, .1)
            recovered = identify_shared_variance(p_joint, 1., 1., r1, r2, .05, .1)
            inverse_errors.append(abs(recovered - a))
results['paired_identification'] = {
    'central_threshold_pairs': 12, 'positive_derivative_checks': len(derivative_errors),
    'max_derivative_absolute_error': max(derivative_errors),
    'one_probability_recovery_cases': len(inverse_errors), 'max_shared_variance_recovery_error': max(inverse_errors)}
assert max(derivative_errors) < 2e-7
assert max(inverse_errors) < 1e-8

# The centered readout is only quadratically sensitive near zero shared variance.
r1, r2 = .8, 1.3
q1 = float(interval_response(0., 1., r1)); q2 = float(interval_response(0., 1., r2))
coefficient = float(2*r1*r2*normal_pdf(r1)*normal_pdf(r2))
weak = []
for rho in [.1, .03, .01, .003]:
    excess = gaussian_rectangle(-r1, r1, -r2, r2, rho) - q1*q2
    weak.append(dict(rho=rho, excess_joint_probability=excess,
                     excess_over_rho_squared=excess/rho**2, limiting_coefficient=coefficient))
results['weak_identification_expansion'] = weak
assert abs(weak[-1]['excess_over_rho_squared'] / coefficient - 1) < 1e-5

# One off-center joint observation has nonzero local slope at rho=0.
offcenter = []
v1, v2, k1, k2 = 1., 1.44, .8, 1.56
for s in [.2, .5, 1.]:
    lo1, hi1 = (-k1-s)/np.sqrt(v1), (k1-s)/np.sqrt(v1)
    lo2, hi2 = (-k2-s)/np.sqrt(v2), (k2-s)/np.sqrt(v2)
    analytic = float((normal_pdf(lo1)-normal_pdf(hi1))*(normal_pdf(lo2)-normal_pdf(hi2)))
    h = 1e-5
    numeric = (gaussian_rectangle(lo1,hi1,lo2,hi2,h) - gaussian_rectangle(lo1,hi1,lo2,hi2,-h))/(2*h)
    assert analytic > 0 and abs(analytic-numeric) < 1e-8
    offcenter.append(dict(soa=s, analytic_slope_rho_zero=analytic, numerical_slope=numeric))
results['offcenter_local_slope'] = offcenter

# Correlated criterion jitters preserve an observational gauge even with joint data.
corr_cases = [dict(sensory=.2, criterion_variance=.8, criterion_covariance=.3),
              dict(sensory=.4, criterion_variance=.6, criterion_covariance=.1)]
joint_curves = []
for case in corr_cases:
    assert case['criterion_variance'] >= abs(case['criterion_covariance'])
    v = case['sensory'] + case['criterion_variance']
    cov = case['sensory'] + case['criterion_covariance']
    joint_curves.append([joint_interval_response(s, v, v, .9, 1.2, cov, .05, .1)
                         for s in np.linspace(-2, 2, 17)])
results['correlated_criterion_counterexample'] = {
    'parameter_tuples': corr_cases, 'max_joint_probability_discrepancy': float(np.max(np.abs(np.array(joint_curves[0])-joint_curves[1])))}
assert results['correlated_criterion_counterexample']['max_joint_probability_discrepancy'] < 1e-13

# Shared lapse events/fair guesses can imitate positive shared sensory variance.
k = float(ndtri(.75)); lapse = .2
correlated_lapse_joint = (1-lapse)*.25 + lapse*.5
false_variance = identify_shared_variance(correlated_lapse_joint, 1., 1., k, k, lapse, lapse)
results['correlated_lapse_counterexample'] = {
    'actual_sensory_variance': 0., 'marginal_yes_probabilities': [.5, .5],
    'known_marginal_lapse_rate': lapse, 'joint_yes_probability': correlated_lapse_joint,
    'apparent_shared_sensory_variance_if_independent_lapses_assumed': false_variance}
assert false_variance > 0

# A finite sharp variance-budget example: v=(1,2,3), B*=2.
below = independent_jitter_bounds([1., 2., 3.], [0., 0., 0.], [1.9, 1.9, 1.9])
at = independent_jitter_bounds([1., 2., 3.], [0., 0., 0.], [2., 2., 2.])
assert below[0] > below[1] and at == (1., 1.)
results['variance_budget_boundary'] = {'effective_variances': [1.,2.,3.], 'minimum_uniform_jitter_variance_budget': 2.,
                                      'sensory_interval_if_B_1_9': below, 'sensory_interval_if_B_2': at}

# Bounded criterion correlation: independently verify the quadratic interval
# against the defining PSD inequality at a finite grid, and the equal-v formula.
correlation_cases = 0
membership_checks = 0
for v1, v2 in [(1., 1.), (1., 4.), (2., 5.)]:
    for r in [0., .1, .6, .9, 1.]:
        for kappa in [0., .2, .6, 1.]:
            answer = bounded_criterion_correlation_interval(v1, v2, r, kappa)
            R = r*np.sqrt(v1*v2)
            grid = np.linspace(0., min(v1, v2), 1001)
            defining = (R-grid)**2 <= kappa**2*(v1-grid)*(v2-grid) + 1e-12
            predicted = np.zeros(len(grid), dtype=bool) if answer is None else ((grid >= answer[0]-1e-12) & (grid <= answer[1]+1e-12))
            assert np.array_equal(defining, predicted), (v1,v2,r,kappa,answer)
            if v1 == v2:
                expected = ((max(0., (r-kappa)/(1-kappa)), (r+kappa)/(1+kappa))
                            if kappa < 1 else (0., (1+r)/2))
                assert answer is not None and np.allclose(answer, expected, atol=1e-12)
            correlation_cases += 1
            membership_checks += len(grid)
example = bounded_criterion_correlation_interval(1., 1., .6, .2)
assert np.allclose(example, [.5, 2/3])
results['bounded_criterion_correlation'] = {
    'parameter_cases': correlation_cases, 'grid_membership_checks': membership_checks,
    'example_r_0_6_kappa_0_2_variance_fraction_interval': example,
    'negative_covariance_branch_containment': 'For a,R>=0, |R-a|<=R+a, so any feasible negative total covariance implies feasible positive total covariance at the same a.'}

(HERE / 'BCI_IDENTIFICATION_CHECKS.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
