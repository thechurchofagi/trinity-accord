#!/usr/bin/env python3
"""Read-only post-repair audit; does not optimize or rerun the bootstrap."""
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent
EMP = ROOT.parent / 'empirical'
spec = importlib.util.spec_from_file_location('audit_target', EMP / 'fit_count_clock.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fits = np.load(EMP / 'results/count_model_fits.npz')
source = np.load(EMP / 'alignment_diagnostic.npz')
summary = json.loads((EMP / 'results/count_model_summary.json').read_text())
counts = fits['counts']
res = {
    'audit_status': 'Post-repair verification; prior clipping defect closed',
    'role': 'Independent read-only audit; no optimization or full bootstrap rerun',
    'prior_audit': 'history/count_audit_before_stable_log_fix',
    'source_sha256': hashlib.sha256((EMP / 'fit_count_clock.py').read_bytes()).hexdigest(),
    'count_shape': list(counts.shape),
    'original_count_noninteger_max': float(np.max(np.abs(source['counts'] - np.round(source['counts'])))),
    'saved_counts_match_original': bool(np.array_equal(counts, source['counts'])),
}
res['embedding_max_probability_error'] = float(max(
    np.max(np.abs(mod.decode(th, True)[0] - mod.decode(mod.null_to_alt(th), False)[0]))
    for th in fits['nulltheta']))
res['null_embedding_within_alt_bounds'] = all(
    all(low - 1e-12 <= value <= high + 1e-12
        for value, (low, high) in zip(mod.null_to_alt(th), mod.bounds(False)))
    for th in fits['nulltheta'])

def check_gradient(th, y, shared, step):
    loss, analytic = mod.lossgrad(th, y, shared)
    numerical = []
    for index in range(len(th)):
        lo = th.copy(); hi = th.copy()
        lo[index] -= step; hi[index] += step
        numerical.append((mod.lossgrad(hi, y, shared)[0] - mod.lossgrad(lo, y, shared)[0]) / (2 * step))
    numerical = np.array(numerical)
    error = np.abs(analytic - numerical)
    return {
        'loss': float(loss),
        'finite_loss_and_gradient': bool(np.isfinite(loss) and np.all(np.isfinite(analytic))),
        'max_abs_error': float(error.max()),
        'max_scaled_error': float(np.max(error / (1 + np.abs(numerical)))),
        'max_abs_width_error': float(error[12:].max()),
        'max_scaled_width_error': float(np.max(error[12:] / (1 + np.abs(numerical[12:])))),
        'smallest_predicted_probability': float(mod.decode(th, shared)[0].min()),
        'underflowed_zero_probabilities': int((mod.decode(th, shared)[0] == 0).sum()),
        'finite_difference_step': step,
    }

res['fits'] = {}
res['gradient_checks'] = []
res['extreme_checks'] = []
for shared, key in [(True, 'nulltheta'), (False, 'alttheta')]:
    ths = fits[key]
    bound = np.array(mod.bounds(shared))
    pb = np.array([mod.decode(th, shared)[0] for th in ths])
    near_lower = np.abs(ths - bound[:, 0]) < 1e-6
    near_upper = np.abs(ths - bound[:, 1]) < 1e-6
    projected_max = []
    for th, y in zip(ths, counts):
        _, grad = mod.lossgrad(th, y, shared)
        grad = grad.copy()
        grad[((th - bound[:, 0] < 1e-6) & (grad > 0)) |
             ((bound[:, 1] - th < 1e-6) & (grad < 0))] = 0
        projected_max.append(float(np.max(np.abs(grad))))
    res['fits'][key] = {
        'probability_min': float(pb.min()),
        'probability_max': float(pb.max()),
        'cells_below_former_probability_floor_not_clipped': int((pb <= 1e-12).sum()),
        'params_near_lower_by_index': near_lower.sum(axis=0).tolist(),
        'params_near_upper_by_index': near_upper.sum(axis=0).tolist(),
        'participants_any_bound': int(np.any(near_lower | near_upper, axis=1).sum()),
        'participants_amplitude_upper_bound': int(np.any(near_upper[:, :6], axis=1).sum()),
        'participants_center_or_width_bound': int(np.any((near_lower | near_upper)[:, 6:], axis=1).sum()),
        'projected_gradient_max_over_people': max(projected_max),
        'projected_gradient_median': float(np.median(projected_max)),
    }
    for person in (0, 3, 4, 14, 23, 29):
        th = ths[person].copy()
        th = np.maximum(bound[:, 0] + 1e-4, np.minimum(bound[:, 1] - 1e-4, th))
        th += .002 * np.sin(np.arange(len(th)) + 1)
        th = np.maximum(bound[:, 0] + 1e-4, np.minimum(bound[:, 1] - 1e-4, th))
        test = check_gradient(th, counts[person], shared, 1e-6)
        test.update(model=key, person_index=person)
        res['gradient_checks'].append(test)
    # Admissible narrow curves force genuine numerical underflow of exp(logp).
    # The log likelihood must still retain their finite tail evidence and slope.
    th = ths[0].copy()
    th[:6] = 1
    th[6:12] = np.array([.013, -.027, .041, -.019, .033, -.047])
    if shared:
        th[12:14] = -2.999
        th[14:16] = -2.999
    else:
        th[12:18] = -5.999
    for y, label in [(np.ones((2, 3, 7), dtype=int), 'narrow_curve_positive_tail_counts'),
                     (np.zeros((2, 3, 7), dtype=int), 'narrow_curve_zero_counts')]:
        test = check_gradient(th, y, shared, 1e-5)
        test.update(model=key, scenario=label)
        res['extreme_checks'].append(test)

# Repeat the initial audit's narrow-width construction. A central derivative is legitimate
# for the smooth objective at the bound, although one perturbed point is outside
# the optimizer box. The preceding checks are wholly inside the parameter box.
th = fits['alttheta'][0].copy()
th[12:] = -6
y = np.ones((2, 3, 7), dtype=int)
loss, g = mod.lossgrad(th, y, False)
idx = 12; step = 1e-5
lo = th.copy(); hi = th.copy()
lo[idx] -= step; hi[idx] += step
ng = (mod.lossgrad(hi, y, False)[0] - mod.lossgrad(lo, y, False)[0]) / (2 * step)
res['former_counterexample_after_repair'] = {
    'parameter_index': idx,
    'loss_finite': bool(np.isfinite(loss)),
    'analytic_gradient': float(g[idx]),
    'numerical_gradient': float(ng),
    'scaled_error': float(abs(g[idx] - ng) / (1 + abs(ng))),
    'cells_below_former_floor': int((mod.decode(th, False)[0] <= 1e-12).sum()),
    'underflowed_zero_probabilities': int((mod.decode(th, False)[0] == 0).sum()),
}

nullvals = np.array([mod.lossgrad(th, y, True)[0] for th, y in zip(fits['nulltheta'], counts)])
altvals = np.array([mod.lossgrad(th, y, False)[0] for th, y in zip(fits['alttheta'], counts)])
obs = float(2 * np.sum(nullvals - altvals))
res['recomputed_LRT'] = obs
res['LRT_summary_abs_error'] = abs(obs - summary['test_statistic'])
res['minimum_person_LRT'] = float(np.min(2 * (nullvals - altvals)))
res['all_original_fit_pairs_reported_converged'] = all(
    x['null_converged'] and x['alt_converged'] for x in summary['original_fit_status'])
res['original_fitted_probabilities_match_saved'] = {
    key: float(np.max(np.abs(np.array([mod.decode(th, shared)[0] for th in fits[theta]]) - fits[key])))
    for key, theta, shared in [('pnull', 'nulltheta', True), ('palt', 'alttheta', False)]
}
boot = np.load(EMP / 'results/count_model_bootstrap.npz')
bad = boot['converged'] != len(counts)
values = boot['lrt']
exceed = int((values >= obs).sum())
ci = stats.binomtest(exceed, len(values)).proportion_ci(confidence_level=.95, method='exact')
res['bootstrap'] = {
    'B': len(values),
    'all_statistics_finite': bool(np.all(np.isfinite(values))),
    'flagged_replicates': int(bad.sum()),
    'converged_subject_fit_pairs': int(boot['converged'].sum()),
    'total_subject_fit_pairs': len(counts) * len(values),
    'tail_exceedances': exceed,
    'plus_one_p': (1 + exceed) / (1 + len(values)),
    'binomial_tail_MC_ci95': [float(ci.low), float(ci.high)],
    'numerical_retries_reported_by_fit_run': summary['parametric_bootstrap']['numerical_retry_count'],
    'note': 'Recorded fit statuses and final statistics checked; no bootstrap refits performed by this audit.',
}

assert res['saved_counts_match_original']
assert res['embedding_max_probability_error'] == 0
assert res['null_embedding_within_alt_bounds']
assert res['all_original_fit_pairs_reported_converged']
assert res['LRT_summary_abs_error'] < 1e-8
assert res['minimum_person_LRT'] >= -1e-7
assert max(x['max_abs_error'] for x in res['gradient_checks']) < 2e-6
assert all(x['finite_loss_and_gradient'] for x in res['extreme_checks'])
assert max(x['max_scaled_width_error'] for x in res['extreme_checks']) < 1e-5
assert res['former_counterexample_after_repair']['scaled_error'] < 1e-7
assert res['bootstrap']['flagged_replicates'] == 0
assert res['bootstrap']['tail_exceedances'] == summary['parametric_bootstrap']['exceedances']
assert res['bootstrap']['plus_one_p'] == summary['parametric_bootstrap']['p_plus_one']
(ROOT / 'COUNT_MODEL_AUDIT.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps({k: v for k, v in res.items() if k not in ['gradient_checks', 'extreme_checks']}, indent=2))
print('Routine gradient max abs error:', max(x['max_abs_error'] for x in res['gradient_checks']))
print('Extreme cases:', json.dumps(res['extreme_checks'], indent=2))
