#!/usr/bin/env python3
"""Independent read-only reanalysis of Zenodo 18877381.

This is new analysis code, not a port or execution of anamax.m. Raw archive
bytes remain unchanged. It uses the paper's two-parameter cumulative-Gaussian
model but reports the fitted normal SD as `sigma`, never silently calling it
the archived `JND`. Timing values have unconfirmed units and event semantics.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import minimize
from scipy.special import log_ndtr
from scipy.stats import f as f_distribution
from scipy.stats import norm, t as t_distribution

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / 'sources' / 'Zenodo18877381' / 'Data'
OUT = BASE / 'results'
CONDITIONS = ['Control', 'Active', 'Passive']
ATTENTION = ['Start', 'End']
EXCLUDED_IDS = ['HN77', 'JD14', 'JN98']  # Explicit Zenodo metadata exclusions.
CLOCK_FIELDS = ['start_numeric', 'end_numeric', 'stimulation_numeric',
                'stimulation_after_numeric', 'latency_numeric', 'duration_numeric']


def finite_json(value):
    if isinstance(value, dict):
        return {str(k): finite_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_json(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(value) else None
    return value


def dump(name, value):
    (OUT / name).write_text(json.dumps(finite_json(value), ensure_ascii=False,
                                     indent=2, allow_nan=False) + '\n')


def write_csv(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_clock_tail(tokens, fields):
    """Explicit reconstruction hypothesis, not a correction of source bytes.

    Each clock value is either the single token NaN or a pair integer,ddd.
    Every source non-NaN fractional part must contain exactly three digits.
    This accounts for source commas used both as separators and decimals.
    A passive record must end in its observed speed-code field.
    """
    clock_tokens = tokens[3:]
    speed = None
    if fields == 10:
        speed = clock_tokens[-1]
        clock_tokens = clock_tokens[:-1]
    values, index = [], 0
    for _ in CLOCK_FIELDS:
        assert index < len(clock_tokens), 'Clock field missing'
        token = clock_tokens[index]
        if token == 'NaN':
            values.append(float('nan'))
            index += 1
        else:
            assert re.fullmatch(r'-?\d+', token), f'Noninteger clock prefix {token}'
            assert index + 1 < len(clock_tokens)
            suffix = clock_tokens[index + 1]
            assert re.fullmatch(r'\d{3}', suffix), f'Non-3-digit decimal {suffix}'
            values.append(float(token + '.' + suffix))
            index += 2
    assert index == len(clock_tokens), 'Unparsed clock token'
    return dict(zip(CLOCK_FIELDS, values)) | {'speed_code': speed}


def load_trials():
    trials, files, malformed, empty_lines = [], [], [], []
    for path in sorted(SOURCE.glob('*/*/*.csv')):
        relative = path.relative_to(SOURCE)
        condition, attention = relative.parts[:2]
        subject = path.stem.split('_')[0]
        raw = path.read_bytes()
        reader = csv.reader(raw.decode('utf-8-sig').splitlines())
        header = next(reader)
        assert header[:3] == ['TrialNumber', 'InputValue', 'VibrationCommand']
        assert len(header) in [3, 9, 10]
        records, widths = [], Counter()
        for line, row in enumerate(reader, 2):
            widths[len(row)] += 1
            if not row:
                empty_lines.append({'file': str(relative), 'line': line})
                continue
            # These three prefix fields are unambiguous without timing repair.
            assert len(row) >= 3
            record = {'subject': subject, 'condition': condition,
                      'attention': attention, 'file': str(relative), 'line': line,
                      'trial': int(row[0]), 'response': int(row[1]),
                      'command': int(row[2]), 'declared_fields': len(header),
                      'raw_fields': len(row), 'included_subject': subject not in EXCLUDED_IDS}
            assert record['response'] in [0, 1]
            assert 0 <= record['command'] <= 9
            record['valid_declared_command'] = 1 <= record['command'] <= 9
            if len(header) > 3:
                try:
                    record |= parse_clock_tail(row, len(header))
                    record['clock_parse'] = 'conditional_decimal_comma_reconstruction'
                except (AssertionError, ValueError) as error:
                    malformed.append({'file': str(relative), 'line': line,
                                      'reason': str(error), 'tokens': row})
                    record['clock_parse'] = 'unreconstructed'
            else:
                assert len(row) == 3
                record['clock_parse'] = 'no_clock_fields'
            trials.append(record)
            records.append(record)
        ids = [r['trial'] for r in records]
        files.append({'file': str(relative), 'subject': subject,
                      'condition': condition, 'attention': attention,
                      'included_subject': subject not in EXCLUDED_IDS,
                      'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                      'declared_fields': len(header),
                      'raw_width_counts': json.dumps(dict(sorted(widths.items()))),
                      'nonempty_records': len(records),
                      'command_zero_records': sum(not r['valid_declared_command'] for r in records),
                      'duplicate_trial_ids': len(ids) - len(set(ids)),
                      'missing_trial_ids_1_to_90': json.dumps(sorted(set(range(1, 91)) - set(ids))),
                      'nan_duration_records': sum(math.isnan(r.get('duration_numeric', 0)) for r in records),
                      'source_header': ','.join(header)})
    return trials, files, malformed, empty_lines


def paired_summary(differences):
    d = np.asarray(differences, dtype=float)
    n = len(d)
    mean = d.mean()
    sd = d.std(ddof=1)
    se = sd / np.sqrt(n)
    t = mean / se if se else float('nan')
    halfwidth = t_distribution.ppf(.975, n - 1) * se
    return {'n': n, 'mean_difference': mean, 'sd_difference': sd,
            'ci95_lower': mean - halfwidth, 'ci95_upper': mean + halfwidth,
            't': t, 'df': n - 1,
            'p_two_sided': 2 * t_distribution.sf(abs(t), n - 1),
            'effect_dz': mean / sd if sd else float('nan')}


def holm(p_values):
    p = np.array(p_values)
    order = np.argsort(p)
    adjusted = np.maximum.accumulate((len(p) - np.arange(len(p))) * p[order])
    result = np.empty_like(p)
    result[order] = np.minimum(1, adjusted)
    return result.tolist()


def rm_factor_test(coefficients):
    """Univariate repeated-measures F on orthonormal contrast coordinates.

    Epsilon is estimated in the factor's contrast space. The GG adjustment
    changes degrees of freedom, not F. No claim of reproducing JASP options.
    """
    z = np.asarray(coefficients)
    if z.ndim == 1:
        z = z[:, None]
    n, rank = z.shape
    mean = z.mean(axis=0)
    ss_effect = n * (mean @ mean)
    ss_error = np.square(z - mean).sum()
    F = (ss_effect / rank) / (ss_error / ((n - 1) * rank))
    covariance = np.atleast_2d(np.cov(z, rowvar=False, ddof=1))
    epsilon = float(np.trace(covariance) ** 2 /
                    (rank * np.trace(covariance @ covariance)))
    return {'F': F, 'df_numerator': rank, 'df_denominator': (n - 1) * rank,
            'p_uncorrected': f_distribution.sf(F, rank, (n - 1) * rank),
            'GG_epsilon': epsilon,
            'p_GG': f_distribution.sf(F, rank * epsilon, (n - 1) * rank * epsilon)}


def summarize_tensor(array):
    """Subject x movement[Control,Active,Passive] x attention[Start,End]."""
    y = np.asarray(array)
    n = len(y)
    cells = []
    within = []
    for i, condition in enumerate(CONDITIONS):
        for j, attention in enumerate(ATTENTION):
            values = y[:, i, j]
            cells.append({'condition': condition, 'attention': attention,
                          'n': n, 'mean': values.mean(), 'sd': values.std(ddof=1)})
        within.append({'contrast': condition + ': Start - End',
                       **paired_summary(y[:, i, 0] - y[:, i, 1])})
    adjusted = holm([r['p_two_sided'] for r in within])
    for r, a in zip(within, adjusted):
        r['p_Holm_family_3_within_movement'] = a
    # Movement contrast basis and attention basis are orthonormal.
    H = np.array([[1, -1, 0], [1, 1, -2]], dtype=float)
    H[0] /= np.sqrt(2)
    H[1] /= np.sqrt(6)
    a = np.array([1, -1]) / np.sqrt(2)
    movement = (y.sum(axis=2) / np.sqrt(2)) @ H.T
    attention = y.sum(axis=1) @ a / np.sqrt(3)
    interaction = (y @ a) @ H.T
    interaction_pairs = []
    d = y[:, :, 0] - y[:, :, 1]
    for left, right in [(2, 1), (2, 0), (1, 0)]:
        interaction_pairs.append({
            'contrast': f'({CONDITIONS[left]} Start - End) - ({CONDITIONS[right]} Start - End)',
            **paired_summary(d[:, left] - d[:, right])})
    adjusted = holm([r['p_two_sided'] for r in interaction_pairs])
    for r, p in zip(interaction_pairs, adjusted):
        r['p_Holm_family_3_interaction_pairs'] = p
    marginal = []
    means = y.mean(axis=2)
    for left, right in [(1, 0), (2, 0), (1, 2)]:
        marginal.append({'contrast': f'{CONDITIONS[left]} - {CONDITIONS[right]} averaged over attention',
                         **paired_summary(means[:, left] - means[:, right])})
    adjusted = holm([r['p_two_sided'] for r in marginal])
    for r, p in zip(marginal, adjusted):
        r['p_Holm_family_3_marginal'] = p
    return {'cells': cells, 'within_movement': within,
            'interaction_pairs': interaction_pairs, 'marginal_contrasts': marginal,
            'ANOVA': {'movement': rm_factor_test(movement),
                      'attention': rm_factor_test(attention),
                      'movement_by_attention': rm_factor_test(interaction)}}


def fit_psychometric(rows):
    x = np.array([r['command'] for r in rows], dtype=float)
    y = np.array([r['response'] for r in rows], dtype=float)
    def nll(z):
        standardized = (x - z[0]) / np.exp(z[1])
        return -np.sum(y * log_ndtr(standardized) + (1 - y) * log_ndtr(-standardized))
    estimates = [minimize(nll, [mu, math.log(sd)], method='L-BFGS-B',
                          bounds=[(-10, 20), (-4, 5)],
                          options={'ftol': 1e-12, 'gtol': 1e-8, 'maxiter': 1000})
                 for mu, sd in [(4.5, 1.5), (5, 3), (3, 1)]]
    best = min(estimates, key=lambda result: result.fun)
    sigma = np.exp(best.x[1])
    return {'n': len(rows), 'pse': best.x[0], 'sigma': sigma,
            'jnd_75_minus_50': norm.ppf(.75) * sigma,
            'nll': best.fun, 'optimizer_success': bool(best.success),
            'all_start_objective_spread': max(r.fun for r in estimates) - min(r.fun for r in estimates),
            'at_bound': bool(abs(best.x[0] + 10) < 1e-5 or abs(best.x[0] - 20) < 1e-5
                             or abs(best.x[1] + 4) < 1e-5 or abs(best.x[1] - 5) < 1e-5)}


def available_timing_filter(rows):
    # Sensitivity analysis only: curvature, gaze, command trigger, and absolute
    # clock semantics are not available. Published code filters Active only.
    if rows[0]['condition'] != 'Active':
        return rows
    latency = np.array([r.get('latency_numeric', np.nan) for r in rows])
    duration = np.array([r.get('duration_numeric', np.nan) for r in rows])
    keep = np.isfinite(latency) & np.isfinite(duration)
    for values in [latency, duration]:
        mean, sd = np.nanmean(values), np.nanstd(values, ddof=1)
        keep &= (values >= mean - 2 * sd) & (values <= mean + 2 * sd)
    return [r for r, k in zip(rows, keep) if k]


def main():
    OUT.mkdir(exist_ok=True)
    trials, files, malformed, empty_lines = load_trials()
    assert not malformed, 'Unexpected source encoding requires manual inspection'
    assert all(r['duplicate_trial_ids'] == 0 for r in files)
    write_csv('SOURCE_FILE_AUDIT.csv', files)
    subjects = sorted({r['subject'] for r in trials if r['included_subject']})
    included = [r for r in trials if r['included_subject']]
    grouped = defaultdict(list)
    for row in included:
        if row['valid_declared_command']:
            grouped[(row['subject'], row['condition'], row['attention'])].append(row)
    assert len(subjects) == 18
    assert len(grouped) == 18 * 3 * 2
    timing = []
    for condition in CONDITIONS:
        for attention in ATTENTION:
            all_rows = [r for r in trials if r['condition'] == condition and r['attention'] == attention]
            for sample_name, records in [('all_archived_subjects', all_rows),
                                          ('18_included_subjects', [r for r in all_rows if r['included_subject']])]:
                parsed = [r for r in records if r['clock_parse'].startswith('conditional')]
                offsets = Counter(round(r['stimulation_numeric'] - r['start_numeric'], 3) for r in parsed)
                duration_identity = [abs(r['end_numeric'] - r['start_numeric'] - r['duration_numeric'])
                                     for r in parsed if math.isfinite(r['duration_numeric'])]
                valid_duration = [r['duration_numeric'] for r in parsed if math.isfinite(r['duration_numeric'])]
                timing.append({'condition': condition, 'attention': attention, 'sample': sample_name,
                               'nonempty_records': len(records), 'parsed_clock_records': len(parsed),
                               'stimulation_minus_start_counts': dict(offsets),
                               'stimulation_after_counts': dict(Counter(r['stimulation_after_numeric'] for r in parsed)),
                               'speed_codes': dict(Counter(r['speed_code'] for r in parsed if r['speed_code'] is not None)),
                               'duration_finite_n': len(valid_duration),
                               'duration_median_numeric': float(np.median(valid_duration)) if valid_duration else None,
                               'duration_max_end_start_error': max(duration_identity) if duration_identity else None,
                               'latency_equals_start_count': sum(r['latency_numeric'] == r['start_numeric'] for r in parsed)})
    dump('TIMING_FIELD_AUDIT.json', {'status': 'EVENT_SEMANTICS_AND_UNITS_UNVALIDATED',
         'numeric_reconstruction': 'One NaN or integer + three-decimal-digit pair per declared time field',
         'claim_limit': 'Clock labels and decimal reconstruction do not measure physical stimulus onset or neural intake.',
         'by_cell': timing, 'blank_lines': empty_lines, 'unreconstructed_rows': malformed})

    summary_rows = list(csv.DictReader((SOURCE / 'PSE_and_JND.csv').open(encoding='utf-8-sig')))
    archived = {r['VP']: r for r in summary_rows}
    assert sorted(archived) == subjects
    archive_stats = {}
    for endpoint in ['PSE', 'JND']:
        tensor = np.array([[[float(archived[s][f'{endpoint}_{c}_{a.lower()}']) for a in ATTENTION]
                            for c in CONDITIONS] for s in subjects])
        archive_stats[endpoint] = summarize_tensor(tensor)
    dump('ARCHIVED_PARAMETER_REANALYSIS.json', archive_stats)

    fits, refit_stats = [], {}
    for version in ['all_endpoint_records', 'active_available_timing_filter']:
        lookup = {}
        for key in sorted(grouped):
            subject, condition, attention = key
            rows = grouped[key]
            retained = rows if version == 'all_endpoint_records' else available_timing_filter(rows)
            result = fit_psychometric(retained)
            published_pse = float(archived[subject][f'PSE_{condition}_{attention.lower()}'])
            published_jnd = float(archived[subject][f'JND_{condition}_{attention.lower()}'])
            result |= {'subject': subject, 'condition': condition, 'attention': attention,
                       'analysis': version, 'source_n': len(rows), 'removed_n': len(rows) - len(retained),
                       'archived_pse': published_pse, 'archived_jnd': published_jnd,
                       'pse_minus_archived': result['pse'] - published_pse,
                       'sigma_minus_archived_jnd': result['sigma'] - published_jnd,
                       'archived_jnd_over_sigma': published_jnd / result['sigma']}
            fits.append(result)
            lookup[key] = result
        refit_stats[version] = {}
        for endpoint in ['pse', 'sigma', 'jnd_75_minus_50']:
            tensor = np.array([[[lookup[(s, c, a)][endpoint] for a in ATTENTION]
                                for c in CONDITIONS] for s in subjects])
            refit_stats[version][endpoint] = summarize_tensor(tensor)
    write_csv('INDEPENDENT_PSYCHOMETRIC_FITS.csv', [finite_json(r) for r in fits])
    dump('INDEPENDENT_REFIT_STATISTICS.json', refit_stats)

    unfiltered = [r for r in fits if r['analysis'] == 'all_endpoint_records']
    ratios = np.array([r['archived_jnd_over_sigma'] for r in unfiltered])
    dump('EXACT_RESULTS.json', {
        'analysis_id': 'APPARATUS20261010',
        'status': 'PUBLIC_HUMAN_DATA_REANALYSED; NO_NEW_HARDWARE_OR_HUMAN_EXPERIMENT',
        'source_doi': '10.5281/zenodo.18877381',
        'source_zip_sha256': hashlib.sha256((BASE / 'sources' / 'Zenodo18877381_Data.zip').read_bytes()).hexdigest(),
        'analysis_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'trial_csv_count': len(files), 'archived_subject_count': len({r['subject'] for r in trials}),
        'included_subject_count': len(subjects), 'included_subject_ids': subjects,
        'explicit_source_exclusions': EXCLUDED_IDS,
        'nonempty_trial_records_all': len(trials), 'nonempty_trial_records_included': len(included),
        'valid_command_records_included': sum(r['valid_declared_command'] for r in included),
        'out_of_declared_command_records_all': sum(not r['valid_declared_command'] for r in trials),
        'out_of_declared_command_records_included': sum(not r['valid_declared_command'] for r in included),
        'out_of_declared_command_locators': [{'file':r['file'],'line':r['line'],'command':r['command'],
                                             'included_subject':r['included_subject']} for r in trials if not r['valid_declared_command']],
        'blank_lines': len(empty_lines),
        'raw_field_count_mismatch_records': sum(r['declared_fields'] != r['raw_fields'] for r in trials),
        'conditionally_reconstructed_clock_records': sum(r['clock_parse'].startswith('conditional') for r in trials),
        'source_duration_nan_records': sum(math.isnan(r.get('duration_numeric', 0)) for r in trials),
        'psychometric_parameter_cells': len(grouped), 'independent_fit_runs': len(fits),
        'optimizer_successful_runs': sum(r['optimizer_success'] for r in fits),
        'fits_at_parameter_bound': sum(r['at_bound'] for r in fits),
        'max_multistart_objective_spread': max(r['all_start_objective_spread'] for r in fits),
        'available_filter_removed_records': sum(r['removed_n'] for r in fits if r['analysis'] == 'active_available_timing_filter'),
        'archived_jnd_over_independent_unfiltered_sigma': {
            'min': ratios.min(), 'median': np.median(ratios), 'max': ratios.max()},
        'max_abs_unfiltered_pse_difference_from_archive': max(abs(r['pse_minus_archived']) for r in unfiltered),
        'limits': [
            'The source anamax.m dependency and experiment-control C#/Arduino code were not in the cited fitting repository.',
            'InputValue=1 is interpreted as comparison stronger, consistent with increasing command-response functions and the documented coding convention.',
            'The first three source fields support psychometric refitting without any time-column reconstruction.',
            'A recorded command zero is outside the declared 1–9 stimulus set and is excluded from independent endpoint fits; all such source rows remain in the audit.',
            'No source gaze, continuous trajectory, physical actuator onset, EMG, efference-copy or neural-consumer intake stream was provided.',
            'The source time columns have unquoted decimal commas and unvalidated units/trigger semantics.',
            'The sensitivity filter uses available Active latency/duration only, not absent path curvature or gaze.',
            'Fitted sigma, Phi^-1(.75)*sigma and archived JND are retained as separate named quantities.',
            'No equality/equivalence, anatomical OR gate, M/P consumer intervention or familiar feeling is established by these tests.'
        ]})
    print(json.dumps(finite_json({'subjects': len(subjects), 'records_all': len(trials),
          'records_included': len(included), 'fits': len(fits),
          'archive_JND_passive_start_minus_end': archive_stats['JND']['within_movement'][2],
          'refit_sigma_passive_start_minus_end': refit_stats['all_endpoint_records']['sigma']['within_movement'][2],
          'JND_ratio_range': [ratios.min(), np.median(ratios), ratios.max()]}), indent=2))


if __name__ == '__main__':
    main()
