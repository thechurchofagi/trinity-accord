#!/usr/bin/env python3
"""One predeclared conditional Monte Carlo check of the centered source family.

This is a count-level model check, not a new experiment or a parameter fit.
The source table is read only. The 19,999 simulations use its observed pair
totals and the exact conditional hypergeometric null.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import numpy as np
import pandas as pd
import scipy
from scipy.special import xlogy
from scipy.stats import binomtest, hypergeom

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
INPUT = BASE / 'empirical' / 'inputs' / 'Experiment_3.xlsx'
PLAN = json.loads((HERE / 'SYMMETRY_ANALYSIS_PLAN.json').read_text())
TASKS = ['ownership', 'simultaneity']
CONDITIONS = ['8Hz', 'sham', '13Hz']
SOAS = [-400, -200, -100, 0, 100, 200, 400]
N = 10

def load_source_counts(input_path=INPUT):
    """Read the original workbook without running the conditional simulation.

    First worksheet B4:AQ33: participant, task, condition, signed SOA.
    The task order is ownership then simultaneity; conditions are 8 Hz,
    sham, 13 Hz; the seven SOAs follow SOAS. Each cell has ten judgments.
    """
    sheet = pd.read_excel(input_path, sheet_name=0, header=None)
    flat = sheet.iloc[3:33, 1:43].to_numpy(float)
    assert flat.shape == (30, 42)
    assert np.all(np.isfinite(flat))
    assert np.all(flat == np.round(flat)) and np.all((flat >= 0) & (flat <= N))
    cube = flat.astype(int).reshape(30, 2, 3, 7)
    rows = [
        dict(participant=i + 1, task=TASKS[t], stimulation=CONDITIONS[f],
             asynchrony_ms=SOAS[s], n_trials=N, yes=int(cube[i, t, f, s]))
        for i, t, f, s in np.ndindex(cube.shape)
    ]
    return pd.DataFrame(rows), cube

def gain(positive, totals):
    """Twice the binomial LL gain, allowing 0 and 10 successes exactly."""
    negative = totals - positive
    unrestricted = (xlogy(positive, positive / N) +
                    xlogy(N - positive, (N - positive) / N) +
                    xlogy(negative, negative / N) +
                    xlogy(N - negative, (N - negative) / N))
    pooled = xlogy(totals, totals / (2 * N)) + xlogy(2 * N - totals, (2 * N - totals) / (2 * N))
    return 2 * (unrestricted - pooled)

def main():
    df, workbook_cube = load_source_counts()
    assert len(df) == 1260
    assert sorted(df.participant.unique()) == list(range(1, 31))
    assert set(df.task) == set(TASKS)
    assert set(df.stimulation) == set(CONDITIONS)
    assert set(df.asynchrony_ms) == set(SOAS)
    assert np.all(df.n_trials == N)
    assert np.all(df.yes == np.round(df.yes)) and df.yes.between(0, N).all()
    keys = ['participant', 'task', 'stimulation', 'asynchrony_ms']
    assert not df.duplicated(keys).any()
    indexed = df.set_index(keys).yes
    cube = np.array([[[[indexed.loc[(i, t, f, s)] for s in SOAS]
                       for f in CONDITIONS] for t in TASKS] for i in range(1, 31)])
    assert np.array_equal(cube, workbook_cube)
    rows = []
    for i in range(1, 31):
        for t in TASKS:
            for f in CONDITIONS:
                for magnitude in [100, 200, 400]:
                    pos = int(indexed.loc[(i, t, f, magnitude)])
                    neg = int(indexed.loc[(i, t, f, -magnitude)])
                    rows.append(dict(participant=i, task=t, stimulation=f,
                                     abs_soa_ms=magnitude, yes_positive=pos,
                                     yes_negative=neg, total_yes=pos + neg))
    pairs = pd.DataFrame(rows)
    totals = pairs.total_yes.to_numpy()
    positives = pairs.yes_positive.to_numpy()
    pairs['deviance_contribution'] = gain(positives, totals)
    pairs['positive_minus_negative_rate'] = (pairs.yes_positive - pairs.yes_negative) / N
    observed = float(pairs.deviance_contribution.sum())

    # Independently verify one-pair conditional laws on every feasible K.
    # This also checks the combinatorial support used by the simulator.
    conditional_means = []
    conditional_vars = []
    for k in range(21):
        support = np.arange(max(0, k - 10), min(10, k) + 1)
        mass = hypergeom.pmf(support, 20, k, 10)
        assert abs(mass.sum() - 1) < 1e-12
        assert abs(np.dot(support, mass) - k / 2) < 1e-12
        values = gain(support, k)
        assert np.min(values) >= -1e-12
        assert np.allclose(gain(support, k), gain(k - support, k))
        conditional_means.append(float(mass @ values))
        conditional_vars.append(float(mass @ values**2 - (mass @ values)**2))
    exact_mean = float(np.array(conditional_means)[totals].sum())
    exact_sd = float(np.sqrt(np.array(conditional_vars)[totals].sum()))

    rng = np.random.default_rng(PLAN['seed'])
    B = PLAN['replicates']
    simulated = np.empty(B)
    chunk = 500
    for start in range(0, B, chunk):
        stop = min(start + chunk, B)
        positive = rng.hypergeometric(totals, 20 - totals, N, size=(stop - start, len(pairs)))
        simulated[start:stop] = gain(positive, totals).sum(axis=1)
    exceedances = int((simulated >= observed - 1e-10).sum())
    ci = binomtest(exceedances, B).proportion_ci(method='exact', confidence_level=.95)
    task_rows = []
    condition_rows = []
    for task, frame in pairs.groupby('task', sort=False):
        task_rows.append(dict(task=task, n_pairs=len(frame),
                              deviance_contribution=float(frame.deviance_contribution.sum()),
                              mean_signed_rate_difference=float(frame.positive_minus_negative_rate.mean())))
    for (task, condition), frame in pairs.groupby(['task', 'stimulation'], sort=False):
        condition_rows.append(dict(task=task, stimulation=condition, n_pairs=len(frame),
                                   deviance_contribution=float(frame.deviance_contribution.sum()),
                                   mean_signed_rate_difference=float(frame.positive_minus_negative_rate.mean())))
    res = {
        'completed_utc': datetime.now(timezone.utc).isoformat(),
        'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        'plan_sha256': hashlib.sha256((HERE / 'SYMMETRY_ANALYSIS_PLAN.json').read_bytes()).hexdigest(),
        'python_version': platform.python_version(),
        'numpy_version': np.__version__, 'scipy_version': scipy.__version__,
        'count_mapping_matches_original_workbook_exactly': True,
        'input_mapping': 'First worksheet B4:AQ33; 30 participants x 2 tasks x 3 conditions x 7 signed SOAs.',
        'n_participants': 30, 'n_pairs': len(pairs),
        'n_count_cells_tested': 2 * len(pairs), 'nominal_judgments_tested': 2 * len(pairs) * N,
        'all_pairs_equal_probability_restrictions': len(pairs),
        'pairs_with_nonconstant_conditional_null': int(((totals > 0) & (totals < 20)).sum()),
        'observed_deviance': observed,
        'conditional_null_exact_mean': exact_mean,
        'conditional_null_exact_sd': exact_sd,
        'conditional_simulated_mean': float(simulated.mean()),
        'conditional_simulated_sd': float(simulated.std(ddof=1)),
        'B': B, 'seed': PLAN['seed'], 'exceedances': exceedances,
        'plus_one_p': (exceedances + 1) / (B + 1),
        'conditional_tail_MC_ci95': [float(ci.low), float(ci.high)],
        'conditional_quantiles': dict(zip(['min', '2.5%', '50%', '95%', '97.5%', 'max'],
                                          np.quantile(simulated, [0, .025, .5, .95, .975, 1]).tolist())),
        'task_summaries_descriptive_only': task_rows,
        'task_by_stimulation_summaries_descriptive_only': condition_rows,
        'inference': 'One global conditional independent-binomial symmetry-family test. Subsidiary summaries are descriptive; no subsidiary p values.',
        'limitations': PLAN['scope'],
    }
    pairs.to_csv(HERE / 'symmetry_pair_diagnostics.csv', index=False)
    pd.DataFrame(task_rows).to_csv(HERE / 'symmetry_task_summaries.csv', index=False)
    pd.DataFrame(condition_rows).to_csv(HERE / 'symmetry_task_condition_summaries.csv', index=False)
    np.savez(HERE / 'symmetry_conditional_simulations.npz', statistic=simulated,
             observed=observed, totals=totals)
    (HERE / 'SYMMETRY_TEST_RESULTS.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps(res, indent=2))

if __name__ == '__main__':
    main()
