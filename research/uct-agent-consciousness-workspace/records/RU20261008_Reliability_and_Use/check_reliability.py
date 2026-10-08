#!/usr/bin/env python3
"""Exact finite thought-experiment checks; standard library, no consciousness variable.
Run: python check_reliability.py --out MODEL_RESULTS.json
The source X is four uniform bits; A is independent/uniform over 15 nonzero parities.
Only one source-dependent bit is transmitted before A is known. Known circuit design
and independent tie-breaking randomization are allowed; no later source access.
"""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import product
from pathlib import Path


def parity(x: int) -> int:
    return x.bit_count() & 1


def quadratic(x: int) -> int:
    return ((x & 1) * ((x >> 1) & 1)) ^ (((x >> 2) & 1) * ((x >> 3) & 1))


def walsh(values: list[int]) -> list[int]:
    w = [1 - 2*v for v in values]
    step = 1
    while step < len(w):
        for start in range(0, len(w), 2*step):
            for j in range(start, start+step):
                a, b = w[j], w[j+step]
                w[j], w[j+step] = a+b, a-b
        step *= 2
    return w


def cells_for(encoder, decoder):
    cells = defaultdict(lambda: [0, 0])
    records = []
    for a in range(1, 16):
        for x in range(16):
            b = encoder(x)
            y = decoder(a, b)
            correct = int(y == parity(a & x))
            cells[(a, b)][correct] += 1
            records.append((x, a, b, y, correct))
    return cells, records


def law_for(cells):
    law = Counter()
    for count in cells.values():
        law[F(count[1], sum(count))] += F(sum(count), 240)
    return law


def accuracy(law):
    return sum(q*w for q, w in law.items())


def frontier(law, coverage: F) -> F:
    """Exact expected accuracy at fixed positive coverage; independent tie randomization."""
    if not 0 < coverage <= 1:
        raise ValueError('coverage must be in (0,1]')
    remaining, good = coverage, F(0)
    for q, mass in sorted(law.items(), reverse=True):
        accepted = min(remaining, mass)
        good += accepted*q
        remaining -= accepted
        if remaining == 0:
            return good/coverage
    raise AssertionError('posterior law did not normalize')


def utility(law, loss: F) -> F:
    return sum(w * max(F(0), (1+loss)*q-loss) for q, w in law.items())


def serial(obj):
    if isinstance(obj, F): return str(obj)
    if isinstance(obj, dict): return {str(k): serial(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)): return [serial(v) for v in obj]
    return obj


def run():
    Lcells, Lrows = cells_for(lambda x: x & 1,
                             lambda a,b: b if a == 1 else 0)
    Qcells, Qrows = cells_for(quadratic, lambda a,b: b ^ quadratic(a))
    L, Q = law_for(Lcells), law_for(Qcells)
    assert L == {F(1): F(1,15), F(1,2): F(14,15)}
    assert Q == {F(3,5): F(5,8), F(2,3): F(3,8)}
    assert accuracy(L) == F(8,15) and accuracy(Q) == F(5,8)
    assert all(sum(c) in (6,10) for c in Qcells.values())
    # All conditional cells, not merely query-averaged accuracy, are checked.
    for (_, b), counts in Qcells.items():
        assert F(counts[1],sum(counts)) == (F(3,5) if b == 0 else F(2,3))
    assert frontier(L, F(1,10)) == F(5,6)
    assert frontier(Q, F(1,10)) == F(2,3)
    for i in range(1, 241):
        c = F(i,240)
        expected_L = F(1) if c <= F(1,15) else F(1,2)+F(1,30)/c
        expected_Q = F(2,3) if c <= F(3,8) else F(3,5)+F(1,40)/c
        assert frontier(L,c) == expected_L
        assert frontier(Q,c) == expected_Q
        sign = (frontier(L,c)>frontier(Q,c))-(frontier(L,c)<frontier(Q,c))
        assert sign == ((c<F(1,5))-(c>F(1,5)))
    for i in range(0, 361):
        ell = F(i,120)
        expected_L = F(1,15) + F(14,15)*max(F(0),(1-ell)/2)
        expected_Q = F(5,8)*max(F(0),(3-2*ell)/5)+F(3,8)*max(F(0),(2-ell)/3)
        assert utility(L,ell) == expected_L and utility(Q,ell) == expected_Q
        sign=(utility(Q,ell)>utility(L,ell))-(utility(Q,ell)<utility(L,ell))
        assert sign == ((ell<F(67,45))-(ell>F(67,45)))
    assert utility(Q,F(67,45)) == utility(L,F(67,45)) == F(1,15)
    assert utility(Q,F(2)) == 0 and utility(L,F(2)) == F(1,15)

    # Every deterministic one-bit encoder: characterize all mean-optimal encoders.
    best = -1
    opt_codes, opt_laws = [], set()
    # Utility maxima below are enumeration-only unless separately proved.
    losses = [F(0), F(1), F(3,2), F(2)]
    allcode_utility_max = {ell: -1 for ell in losses}
    allcode_utility_counts = {ell: 0 for ell in losses}
    for code in range(65536):
        values = [(code >> x) & 1 for x in range(16)]
        W = walsh(values)
        l1 = sum(abs(v) for v in W[1:])
        assert sum(v*v for v in W) == 256
        assert all((v-W[0])%4 == 0 for v in W)
        if l1 > best: best, opt_codes, opt_laws = l1, [], set()
        if l1 == 60:
            assert all(abs(v) == 4 for v in W)
            n0, n1 = 16-sum(values), sum(values)
            assert sorted((n0,n1)) == [6,10]
            law = Counter()
            for v in W[1:]:
                for n in (n0,n1):
                    q = F(2*n+abs(v),4*n)
                    law[q] += F(n,240)
            assert law == Q
            opt_codes.append(code)
            opt_laws.add(tuple(sorted(law.items())))
        n0,n1=16-sum(values),sum(values)
        for ell in losses:
            numerator=0
            for v in W[1:]:
                for n in (n0,n1):
                    if n:
                        good=(2*n+abs(v))//4
                        assert (2*n+abs(v))%4 == 0
                        numerator+=max(0,good*ell.denominator-(n-good)*ell.numerator)
            score=F(numerator,240*ell.denominator)
            if score > allcode_utility_max[ell]:
                allcode_utility_max[ell]=score; allcode_utility_counts[ell]=1
            elif score == allcode_utility_max[ell]:
                allcode_utility_counts[ell]+=1
    assert best == 60 and len(opt_codes) == 896 and len(opt_laws)==1

    # Target binding: wrong monitor wire has same answer stream and q histogram.
    binding={}
    for mode in ('aligned','misbound','correct_but_unused','constant_report'):
        total_reward=F(0); report_hist=Counter(); confidence_counts=defaultdict(lambda:[0,0])
        answers=[]
        for x,a,b,y,c in Lrows:
            true_q=F(1) if a==1 else F(1,2)
            wired_q=(F(1) if a==2 else F(1,2)) if mode=='misbound' else true_q
            report_q=F(8,15) if mode=='constant_report' else wired_q
            act= True if mode=='correct_but_unused' else (wired_q>F(2,3))
            total_reward += (F(1) if c else F(-2)) * int(act) / 240
            report_hist[report_q]+=F(1,240)
            confidence_counts[wired_q][c]+=1
            answers.append(y)
        binding[mode]={'utility_L2':total_reward,'report_histogram':dict(report_hist),
                       'true_accuracy_by_wired_confidence':{q:F(v[1],sum(v)) for q,v in confidence_counts.items()}}
        assert answers == [r[3] for r in Lrows]
    assert binding['aligned']['utility_L2']==F(1,15)
    assert binding['misbound']['utility_L2']==F(-1,30)
    assert binding['correct_but_unused']['utility_L2']==F(-2,5)
    assert binding['constant_report']['utility_L2']==F(1,15)
    assert binding['misbound']['report_histogram']==binding['aligned']['report_histogram']
    assert binding['misbound']['true_accuracy_by_wired_confidence'][F(1)]==F(1,2)

    # Complemented actual answer: a difficulty-only estimate is not self-answer reliability.
    for cells, rows in ((Lcells,Lrows),(Qcells,Qrows)):
        complemented=defaultdict(lambda:[0,0])
        for x,a,b,y,c in rows:
            complemented[a,b][int((y^1)==parity(a&x))]+=1
        for key,c in cells.items():
            q=F(c[1],sum(c)); cp=complemented[key]
            assert F(cp[1],sum(cp))==1-q

    # A monitor must bind to the actual proposed answer, not an old candidate.
    stale_value = sum((F(1) if 1-c else F(-2))*int(a==1)/240
                      for x,a,b,y,c in Lrows)
    rebound_value = F(0)  # New correct posteriors are 0 or 1/2; both reject.
    assert stale_value == F(-2,15) and rebound_value == 0

    return serial({
      'record':'RU20261008','status':'ACTUALLY_EXECUTED_EXACT_CHECKS',
      'scope':'One-bit source synopsis; uniform four-bit source and 15 parity queries. No human or AI experience measurements.',
      'joint_source_query_cases_per_model':240,
      'conditional_cells':{'linear':len(Lcells),'quadratic':len(Qcells)},
      'posterior_laws':{'linear':dict(L),'quadratic':dict(Q)},
      'forced_accuracy':{'linear':accuracy(L),'quadratic':accuracy(Q)},
      'coverage_10_percent_accuracy':{'linear':frontier(L,F(1,10)),'quadratic':frontier(Q,F(1,10))},
      'coverage_crossover':F(1,5),'coverage_grid_checks':240,
      'loss_crossover':F(67,45),'loss_grid_checks':361,
      'mean_optimum_all_encoders':F(5,8),'maximizing_encoders':len(opt_codes),
      'all_mean_optimal_encoders_have_same_posterior_law':True,
      'mean_optimal_best_positive_coverage_accuracy':'2/3',
      'allcode_utility_maxima_ENUMERATION_ONLY':{ell:{'value':v,'encoders':allcode_utility_counts[ell]} for ell,v in allcode_utility_max.items()},
      'binding_experiment':binding,
      'changed_candidate_monitoring':{'stale_reference_utility_L2':stale_value, 'correctly_rebound_utility_L2':rebound_value},
      'nonclaims':['No general intelligence ordering','No calibrated confidence is identified with a feeling','No basal gate','No full graph semantic audit','No historical novelty established']
    })

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='MODEL_RESULTS.json')
    args=ap.parse_args(); result=run()
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
