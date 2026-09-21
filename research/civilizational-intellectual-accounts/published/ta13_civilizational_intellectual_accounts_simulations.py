#!/usr/bin/env python3
from __future__ import annotations
import json
import numpy as np
from scipy.optimize import linprog

SEED = 20260921
OUT = '/mnt/data/ta13_civilizational_intellectual_accounts_results.json'

DOMAINS = ['science','software','engineering','medicine','professional','public_decision']
W_LO = np.array([0.12,0.10,0.12,0.12,0.15,0.08], dtype=float)
W_HI = np.array([0.25,0.22,0.24,0.22,0.28,0.20], dtype=float)


def aggregate_bounds(lo, hi):
    lo = np.asarray(lo, dtype=float)
    hi = np.asarray(hi, dtype=float)
    bounds = list(zip(W_LO, W_HI))
    Aeq = np.ones((1, len(DOMAINS)))
    beq = np.array([1.0])
    mn = linprog(lo, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')
    mx = linprog(-hi, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')
    if not (mn.success and mx.success):
        raise RuntimeError('linear program failed')
    return {
        'lower': float(mn.fun),
        'upper': float(-mx.fun),
        'lower_attaining_weights': {d: float(v) for d,v in zip(DOMAINS,mn.x)},
        'upper_attaining_weights': {d: float(v) for d,v in zip(DOMAINS,mx.x)},
    }


def experiment_1_nonidentification():
    lo = np.array([0.28,0.58,0.35,0.18,0.30,0.12])
    hi = np.array([0.45,0.78,0.55,0.32,0.50,0.28])
    b = aggregate_bounds(lo,hi)
    midpoint = (lo+hi)/2
    equal = float(midpoint.mean())
    activity_weights = np.array([0.20,0.16,0.18,0.15,0.21,0.10])
    activity = float((activity_weights*midpoint).sum())
    return {
        'name': 'aggregation_nonidentification',
        'purpose': 'Show that plausible domain-attribution intervals and admissible domain weights do not point-identify a unique civilizational AI intellectual share.',
        'domains': DOMAINS,
        'domain_ai_share_intervals': {d:[float(l),float(h)] for d,l,h in zip(DOMAINS,lo,hi)},
        'admissible_weight_bounds': {d:[float(l),float(h)] for d,l,h in zip(DOMAINS,W_LO,W_HI)},
        'identified_set': [b['lower'],b['upper']],
        'equal_weight_midpoint_point_estimate': equal,
        'activity_weight_midpoint_point_estimate': activity,
        'lower_attaining_weights': b['lower_attaining_weights'],
        'upper_attaining_weights': b['upper_attaining_weights'],
        'interpretation': 'The same domain evidence supports materially different scalar summaries under admissible aggregation rules. A point estimate therefore reflects additional assumptions, not data alone.'
    }


def experiment_2_vintage_revision():
    rng = np.random.default_rng(SEED)
    n = 50000
    actors = rng.choice(np.array(['H','A','X']), size=n, p=[0.38,0.47,0.15])
    means = {'H':1.0,'A':0.9,'X':1.2}
    provisional = np.array([rng.lognormal(mean=np.log(means[a]), sigma=0.35) for a in actors])
    validation_mu = {'H':0.95,'A':0.68,'X':1.02}
    validation = np.array([max(0.0, rng.normal(validation_mu[a],0.18)) for a in actors])
    revised = provisional*validation
    def shares(weights):
        vals={a:float(weights[actors==a].sum()) for a in ['H','A','X']}
        t=sum(vals.values())
        return {a:vals[a]/t for a in vals}
    volume=shares(np.ones(n))
    prov=shares(provisional)
    val=shares(revised)
    return {
        'name':'vintage_revision_and_quality_adjustment',
        'purpose':'Illustrate why raw output counts and provisional quality weights can yield a different human/AI composition than later validated quality weights. Coefficients are stipulated and are not empirical claims about real AI quality.',
        'n': n,
        'seed': SEED,
        'volume_shares': volume,
        'provisional_quality_adjusted_shares': prov,
        'later_validated_shares': val,
        'ai_share_change_volume_to_validated': val['A']-volume['A'],
        'interpretation':'A production account that never revises quality can confuse generation volume with durable intellectual contribution.'
    }


def experiment_3_robust_crossover():
    data={
        2026:(np.array([.18,.45,.25,.10,.20,.08]),np.array([.32,.65,.42,.22,.38,.18])),
        2028:(np.array([.30,.60,.40,.20,.34,.15]),np.array([.48,.78,.58,.36,.52,.30])),
        2030:(np.array([.42,.70,.52,.30,.46,.22]),np.array([.58,.86,.68,.46,.64,.38])),
        2032:(np.array([.58,.80,.66,.46,.61,.38]),np.array([.72,.92,.80,.60,.76,.55])),
    }
    rows=[]
    for year,(lo,hi) in data.items():
        b=aggregate_bounds(lo,hi)
        midpoint=float(((lo+hi)/2).mean())
        status = 'robust_AI_majority' if b['lower']>0.5 else ('robust_human_majority' if b['upper']<0.5 else 'majority_not_identified')
        rows.append({'year':year,'identified_set':[b['lower'],b['upper']], 'equal_weight_midpoint':midpoint,'status':status})
    return {
        'name':'robust_crossover_timing',
        'purpose':'Show that a central point estimate can cross 0.5 earlier than a robust majority claim justified across all admissible assumptions.',
        'periods':rows,
        'interpretation':'In this stipulated example the equal-weight midpoint first exceeds 0.5 in 2030, but the lower bound of the identified set exceeds 0.5 only in 2032.'
    }


def main():
    out={
        'schema':'ta-tr-2026-13.design-validation.v1',
        'paper':'Civilizational Intellectual Production Satellite Accounts',
        'date':'2026-09-21',
        'epistemic_boundary':'All numbers are stipulated synthetic examples. They validate accounting logic and illustrate identification problems. They are not estimates of the actual human/AI composition of world intellectual production.',
        'experiments':[experiment_1_nonidentification(),experiment_2_vintage_revision(),experiment_3_robust_crossover()]
    }
    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
