#!/usr/bin/env python3
"""Independent R122 B1 raw-count, history, metric and fold checks.

Reconstructs predictors from raw MAT values without importing b1_kernel or the
shared loader. Re-fits only the first fold of the first session for four models
to resolve whether saved OOF probabilities use the stated training/purge rule.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.stats import t as student_t
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def metrics(y, p):
    return {"log_loss": float(np.mean(-(y*np.log(p)+(1-y)*np.log1p(-p)))),
            "brier": float(np.mean((y-p)**2)),
            "accuracy": float(np.mean(y == (p >= .5)))}


def check_session(s, data, results, refit=False):
    tr = loadmat(data/s["source_file"], simplify_cells=True, variable_names=["Trials"])["Trials"]
    p = pd.read_csv(results/f"{s['session_id']}_oof_predictions.csv")
    normalized = pd.read_csv(results/s["session_id"]/'all_source_trials.csv')
    basic = (tr["trial_type"] == 'a') & (tr["violated"] == 0) & np.isin(tr["pokedR"], [0, 1])
    assert np.array_equal(p.source_row1.to_numpy(), np.flatnonzero(basic)+1)
    assert len(p) == s['n_eligible_trials']
    count_checks = 0
    nuisance = []
    for z, row in enumerate(p.itertuples()):
        i = int(row.source_row1)-1
        assert row.choice == int(tr['pokedR'][i])
        a = np.asarray(tr['leftBups'][i], dtype=float).reshape(-1)
        b = np.asarray(tr['rightBups'][i], dtype=float).reshape(-1)
        a, b = a[1:]-a[0], b[1:]-b[0]
        edges = np.linspace(0, float(tr['stim_dur_s_actual'][i]), 11)
        manual = []
        for k in range(10):
            in_a = (a >= edges[k]) & (a < edges[k+1] if k < 9 else a <= edges[k+1])
            in_b = (b >= edges[k]) & (b < edges[k+1] if k < 9 else b <= edges[k+1])
            manual.append(int(in_b.sum()-in_a.sum()))
        assert np.array_equal(manual, p.iloc[z][[f'e{k}' for k in range(1, 11)]].to_numpy(dtype=float))
        assert sum(manual) == int(tr['click_diff'][i])
        valid_history = i > 0 and basic[i-1] and tr['is_hit'][i-1] in [0, 1]
        signed = 2*int(tr['pokedR'][i-1])-1 if valid_history else 0
        reward = signed*float(tr['is_hit'][i-1]) if valid_history else 0
        error = signed*(1-float(tr['is_hit'][i-1])) if valid_history else 0
        missing = 0 if valid_history else 1
        saved = normalized.iloc[i]
        assert saved.previous_rewarded_choice == reward
        assert saved.previous_error_choice == error
        assert saved.previous_history_missing == missing
        nuisance.append([float(tr['stim_dur_s_actual'][i]), reward, error, missing])
        count_checks += 10
    y = p.choice.to_numpy(dtype=int)
    max_metric_error = 0.0
    for model in ['full10', 'lastbin', 'total', 'nuisance']:
        pr = p[f'p_right_{model}'].to_numpy()
        assert np.all(np.isfinite(pr)) and np.all((pr > 0) & (pr < 1))
        m = metrics(y, pr)
        for key, v in m.items():
            err = abs(v-s['models'][model][key])
            assert err < 1e-12
            max_metric_error = max(max_metric_error, err)
    for k, left, right in [
        ('loss_gain_full10_over_lastbin', 'lastbin', 'full10'),
        ('loss_gain_total_over_lastbin', 'lastbin', 'total'),
        ('loss_gain_full10_over_total', 'total', 'full10')]:
        expected = metrics(y, p[f'p_right_{left}'])['log_loss']-metrics(y, p[f'p_right_{right}'])['log_loss']
        assert abs(expected-s['paired_loss_gain'][k]) < 1e-12
    folds = []
    for fold in s['folds']:
        test = np.flatnonzero(p.fold.to_numpy() == fold['fold'])
        assert np.array_equal(test, np.arange(test.min(), test.max()+1))
        train = np.ones(len(p), dtype=bool)
        train[test] = False
        for idx in [test.min()-1, test.max()+1]:
            if 0 <= idx < len(train):
                train[idx] = False
        assert int(train.sum()) == fold['n_train']
        assert len(test) == fold['n_test']
        # No training predictor may use a held-out label as previous source row.
        train_source = set(p.loc[train, 'source_row1'].astype(int))
        test_source = set(p.iloc[test].source_row1.astype(int))
        assert not any(row1-1 in test_source for row1 in train_source)
        folds.append((train, test))
    refit_error = None
    if refit:
        e = p[[f'e{k}' for k in range(1,11)]].to_numpy(dtype=float)
        nu = np.asarray(nuisance)
        train, test = folds[0]
        errors = {}
        for model, evidence in [('full10', e), ('lastbin', e[:, -1:]),
                                ('total', e.sum(axis=1, keepdims=True)),
                                ('nuisance', np.empty((len(e), 0)))]:
            x = np.column_stack([evidence, nu])
            scale = StandardScaler().fit(x[train])
            m = LogisticRegression(C=1.0, l1_ratio=0.0, solver='lbfgs', tol=1e-8, max_iter=2000)
            m.fit(scale.transform(x[train]), y[train])
            pr = m.predict_proba(scale.transform(x[test]))[:, 1]
            err = float(np.max(np.abs(pr-p.iloc[test][f'p_right_{model}'].to_numpy())))
            assert err < 1e-9
            errors[model] = err
        refit_error = errors
    return {'session': s['source_file'], 'n_source_trials': len(normalized),
            'n_eligible_trials': len(p), 'n_temporal_counts_checked': count_checks,
            'raw_previous_source_history_checks': len(p), 'folds_purge_validated': len(folds),
            'max_metric_error': max_metric_error, 'first_fold_independent_refit_max_probability_errors': refit_error}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--results', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    summary = json.loads((args.results/'B1_results.json').read_text())
    session_checks = [check_session(s, args.data, args.results, refit=(i == 0))
                      for i, s in enumerate(summary['sessions'])]
    metrics_names = ['log_loss', 'brier', 'accuracy']
    errors = []
    for model in ['full10', 'lastbin', 'total', 'nuisance']:
        for metric in metrics_names:
            ratmeans = [np.mean([s['models'][model][metric] for s in summary['sessions'] if s['rat'] == r])
                        for r in sorted({s['rat'] for s in summary['sessions']})]
            r = summary['aggregate']['models'][model][metric]
            mean = float(np.mean(ratmeans))
            width = student_t.ppf(.975, len(ratmeans)-1)*np.std(ratmeans, ddof=1)/np.sqrt(len(ratmeans))
            assert abs(r['mean']-mean) < 1e-12
            assert np.allclose(r['descriptive_t95'], [mean-width, mean+width], atol=1e-12, rtol=0)
            errors.append(abs(r['mean']-mean))
    here = Path(__file__).resolve().parent
    result = {'status': 'passed', 'scope': 'B1 raw counts/history, blocked purge, OOF metrics and equal-rat aggregation',
              'code_sha256': {n: sha(here/n) for n in ['b1_kernel.py', 'rat_cells.py', 'independent_b1_checks.py']},
              'n_eligible_trials': sum(r['n_eligible_trials'] for r in session_checks),
              'n_temporal_counts_checked': sum(r['n_temporal_counts_checked'] for r in session_checks),
              'aggregate_mean_max_error': max(errors), 'session_checks': session_checks,
              'inference_limit': 'Verifies specified observational analysis. Does not establish neural causal use, exclusive accumulator strategy, T2 closure or experience.'}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'session_checks'}, indent=2))


if __name__ == '__main__':
    main()
