"""Independent table-based verification and publication figures for CTD.

All plotted quantities come from the released fitted widths. No confidence
intervals are fabricated for individual fitted parameters or model distances.
"""
from pathlib import Path
import argparse
import itertools
import json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import linprog
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'empirical' / 'results')
    args = parser.parse_args()
    frame = pd.read_csv(args.data_dir / 'published_tbw_tidy.csv')
    table = frame.pivot(index='participant', columns=['task', 'stimulation'], values='TBW_ms')
    tasks = ['ownership', 'simultaneity']
    conds = ['8Hz', 'sham', '13Hz']
    widths = np.stack([table.loc[:, [(t, f) for f in conds]].to_numpy() for t in tasks], axis=1)
    lw = np.log(widths)
    assert widths.shape == (30, 2, 3)
    assert np.isfinite(lw).all()
    gap = lw[:, 0] - lw[:, 1]
    x = lw[:, 1, 0] - lw[:, 1, 2]
    y = lw[:, 0, 0] - lw[:, 0, 2]
    d = y - x
    ep = np.ptp(gap, axis=1) / 4
    em = np.array([min(.5 * max(0., *(z[t, p[j]] - z[t, p[k]]
                  for t in range(2) for j in range(3) for k in range(j + 1, 3)))
                  for p in itertools.permutations(range(3))) for z in lw])
    same_order = np.array([all(np.sign(z[0, f] - z[0, g]) == np.sign(z[1, f] - z[1, g])
                              for f in range(3) for g in range(f + 1, 3)) for z in lw])
    # Independent LP: fix a_S = 0, optimize a_O, three column effects and epsilon.
    lp_distances = []
    for z in lw:
        A, b = [], []
        for t in range(2):
            for f in range(3):
                design = np.zeros(5)
                design[0] = t == 0
                design[1 + f] = 1
                for sign in (1, -1):
                    row = sign * design
                    row[-1] = -1
                    A.append(row)
                    b.append(sign * z[t, f])
        fit = linprog([0, 0, 0, 0, 1], A_ub=A, b_ub=b,
                      bounds=[(None, None)] * 4 + [(0, None)], method='highs')
        assert fit.success
        lp_distances.append(fit.fun)
    assert np.allclose(ep, lp_distances, atol=1e-12)
    assert np.all(em <= ep + 1e-12)
    assert np.array_equal(em < 1e-12, same_order)
    m, se = float(d.mean()), float(stats.sem(d))
    ci = stats.t.interval(.95, 29, loc=m, scale=se)
    verify = {
        'method': 'Independent pivot by explicit participant/task/condition labels; separate linear program for every proportional distance.',
        'n_participants': 30, 'n_widths': 180,
        'mean_log_gain_difference': m,
        't': float(m/se), 'p_two_sided': float(2*stats.t.sf(abs(m/se), 29)),
        'ci95': [float(v) for v in ci],
        'max_abs_formula_vs_LP': float(np.max(np.abs(ep - lp_distances))),
        'ordinal_rank_agreement_count': int(same_order.sum()),
        'max_ordinal_upper_allowance_pct': float(100*np.expm1(em.max())),
        'median_proportional_upper_allowance_pct': float(np.median(100*np.expm1(ep))),
        'inference': 'Point-estimate distance calculations are descriptive, not participant-level hypothesis tests.'
    }
    (ROOT / 'review').mkdir(exist_ok=True)
    (ROOT / 'review' / 'ROOT_NUMERICAL_VERIFICATION.json').write_text(json.dumps(verify, indent=2)+'\n')
    diagnostics = pd.DataFrame({'participant': table.index, 'log_gain_S': x, 'log_gain_O': y,
                               'log_gain_difference': d, 'epsilon_proportional': ep,
                               'epsilon_ordinal_closure': em,
                               'upper_allowance_proportional_pct': 100*np.expm1(ep),
                               'upper_allowance_ordinal_pct': 100*np.expm1(em),
                               'same_strict_order_including_ties': same_order})
    (ROOT / 'results').mkdir(exist_ok=True)
    diagnostics.to_csv(ROOT / 'results' / 'verified_participant_diagnostics.csv', index=False)
    figs = ROOT / 'figures'
    figs.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                         'axes.spines.top':False, 'axes.spines.right':False,
                         'axes.titlesize':12, 'axes.labelsize':10,
                         'pdf.fonttype':42, 'ps.fonttype':42})
    fig, ax = plt.subplots(figsize=(6.4, 5.25), layout='constrained')
    ax.plot([0, 1], [0, 1], color='#8a9299', lw=1.2, ls='--', zorder=1)
    ax.scatter(x[same_order], y[same_order], s=39, c='#234c78', label='Same three-condition order', zorder=3)
    ax.scatter(x[~same_order], y[~same_order], s=48, c='#b85b35', marker='^', label='Opposing order in point estimates', zorder=3)
    for k in np.where(~same_order | (ep > .12))[0]:
        ax.annotate(str(table.index[k]), (x[k], y[k]), xytext=(5,5),
                    textcoords='offset points', fontsize=8)
    ax.set(xlim=(0,1), ylim=(0,1), aspect='equal',
           xlabel='Simultaneity: log(width at 8 Hz / width at 13 Hz)',
           ylabel='Ownership: log(width at 8 Hz / width at 13 Hz)',
           title='Cross-task gains in the released width estimates')
    ax.grid(alpha=.18)
    ax.legend(loc='upper left', frameon=False, fontsize=8.3)
    for ext in ['png', 'pdf']:
        fig.savefig(figs/f'figure1_log_gains.{ext}', dpi=220, bbox_inches='tight')
    plt.close(fig)
    order = np.argsort(ep)
    pp, mm = 100*np.expm1(ep[order]), 100*np.expm1(em[order])
    fig, ax = plt.subplots(figsize=(8.2, 4.6), layout='constrained')
    xx=np.arange(30)
    ax.vlines(xx, mm, pp, lw=1.2, color='#c8d2dc')
    ax.scatter(xx, pp, s=34, facecolors='white', edgecolors='#234c78', linewidth=1.5,
               label='Proportional bridge', zorder=3)
    ax.scatter(xx, mm, s=21, c='#168072', label='Common nondecreasing order', zorder=4)
    ax.set_xticks(xx, [str(v) for v in table.index[order]], fontsize=8)
    ax.set(xlim=(-.7,29.7), ylim=(-.65,15),
           xlabel='Participant ID, ordered by proportional adjustment budget',
           ylabel='Minimum uniform upper multiplicative allowance (%)',
           title='Exact model distances; individual uncertainty not available')
    ax.yaxis.grid(True, alpha=.2)
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    for ext in ['png', 'pdf']:
        fig.savefig(figs/f'figure2_model_distances.{ext}', dpi=220, bbox_inches='tight')
    plt.close(fig)
    print(json.dumps(verify, indent=2))

if __name__ == '__main__':
    main()
