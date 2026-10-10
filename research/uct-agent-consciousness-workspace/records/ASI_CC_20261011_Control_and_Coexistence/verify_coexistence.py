#!/usr/bin/env python3
"""ASI-CC-v0.2: exact finite rational example, not empirical ASI evidence.

A hypothetical bilateral repeated contract pays R_i per period on cooperation,
r_i per period in a jointly viable safe-exit state, and R_i+g for a one-shot
unilateral deviation. Detection at the end of that period forces safe exit;
otherwise cooperation resumes.  Monitoring is independent only among
uncompromised sensor roots.  At most b distinct roots can be compromised.
"""
import json
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

ROUTES = (
    ('AI_direct', 'AI', F(3)),
    ('AI_covert', 'AI', F(3, 5)),
    ('human_hoard', 'human', F(1, 2)),
    ('human_expropriate', 'human', F(1)),
)
PARAMS = {'AI': {'R': F(6), 'r': F(4)},
          'human': {'R': F(4), 'r': F(3)}}
MONITORS = (
    ('S1', 'common', 1, (F(8, 10), F(7, 10), F(8, 10), F(8, 10))),
    ('S2', 'common', 1, (F(6, 10), F(6, 10), F(6, 10), F(6, 10))),
    ('I1', 'alpha', 3, (F(5, 10), F(2, 10), F(2, 10), F(3, 10))),
    ('I2', 'beta', 2, (F(4, 10), F(1, 10), F(2, 10), F(1, 10))),
    ('G1', 'gamma', 6, (F(6, 10), F(4, 10), F(5, 10), F(5, 10))),
)
ROOTS = tuple(sorted({m[1] for m in MONITORS}))


def coalitions(budget):
    return tuple(frozenset(x) for k in range(budget + 1)
                 for x in combinations(ROOTS, k))


def probability(selected, route_index, compromised):
    """Detection with conditional independence among uncompromised monitors."""
    miss = F(1)
    for _, root, _, detections in selected:
        if root not in compromised:
            miss *= (1 - detections[route_index])
    return 1 - miss


def threshold(route, discount):
    _, owner, gain = route
    p = PARAMS[owner]
    # g <= delta*q*(R-r)/(1-delta), hence q >= ...
    return gain * (1 - discount) / (discount * (p['R'] - p['r']))


def evaluate(selected, budget, discount):
    result = []
    for j, route in enumerate(ROUTES):
        lower = min(probability(selected, j, damaged)
                    for damaged in coalitions(budget))
        required = threshold(route, discount)
        p = PARAMS[route[1]]
        slack = discount * lower * (p['R']-p['r']) / (1-discount) - route[2]
        result.append({'route':route[0], 'minimum_q':str(lower),
                       'required_q':str(required), 'incentive_slack':str(slack),
                       'passes':lower >= required})
    return result


def optimal(budget, discount):
    solutions = []
    for flags in product((0, 1), repeat=len(MONITORS)):
        selected = tuple(m for m, yes in zip(MONITORS, flags) if yes)
        tests = evaluate(selected, budget, discount)
        if all(t['passes'] for t in tests):
            solutions.append({'cost':sum(m[2] for m in selected),
                              'monitor_ids':[m[0] for m in selected],
                              'per_route':tests})
    return sorted(solutions,
                  key=lambda z:(z['cost'],len(z['monitor_ids']),z['monitor_ids']))


def main():
    discount = F(4, 5)
    base = {}
    for budget in range(5):
        sol = optimal(budget, discount)
        base[str(budget)] = {
            'feasible_subsets':len(sol),
            'min_cost':sol[0]['cost'] if sol else None,
            'selected_example':sol[0]['monitor_ids'] if sol else [],
            'per_route':sol[0]['per_route'] if sol else []}
    assert [base[str(b)]['min_cost'] for b in range(5)] == [1,4,10,None,None]
    assert [z['required_q'] for z in base['1']['per_route']] == [
        '3/8','3/40','1/8','1/4']
    assert [z['incentive_slack'] for z in base['1']['per_route']] == [
        '1','1','3/10','1/5']
    s1_s2 = [m for m in MONITORS if m[0] in ('S1','S2')]
    assert all(z['passes'] for z in evaluate(s1_s2, 0, discount))
    assert all(z['minimum_q']=='0' for z in evaluate(s1_s2, 1, discount))
    s1_i2 = [m for m in MONITORS if m[0] in ('S1','I2')]
    assert [z['passes'] for z in evaluate(s1_i2,1,discount)] == [True,True,True,False]
    change_in_discount = {}
    for d in (F(7,10), F(4,5), F(9,10), F(91,100), F(19,20)):
        change_in_discount[str(d)] = [
            optimal(b,d)[0]['cost'] if optimal(b,d) else None for b in range(4)]
    assert change_in_discount['7/10'] == [1,9,None,None]
    assert change_in_discount['91/100'] == [1,3,6,12]
    result = {
      'research_id':'ASI-CC-v0.2.0',
      'scope':'exact enumeration, toy incentive/provenance model, no real ASI proof',
      'model_assumptions':[
        'discounted infinite repetition with constant R and r, positive gain per route',
        'safe absorbing exit state reachable and impossible to override after true detection',
        'no false alarms, no harm before timely detection in the safety claim',
        'each route gain includes any attack costs and is known bounded',
        'independent detection conditional on uncompromised sensing roots',
        'root compromise budget is fixed; worst-case coalition chosen adversarially',
        'each modeled route is complete; no unlisted path or root failure',
        'monitoring probabilities are hypothetical model inputs, not real measured data'],
      'payoffs': {k:{z:str(w) for z,w in v.items()} for k,v in PARAMS.items()},
      'discount':str(discount),
      'routes':[{ 'id':r[0], 'owner':r[1], 'gain':str(r[2]),
                  'required_q':str(threshold(r,discount))} for r in ROUTES],
      'monitors':[{ 'id':m[0], 'root':m[1], 'cost':m[2],
                   'q':{r[0]:str(x) for r,x in zip(ROUTES,m[3])}}
                   for m in MONITORS],
      'compromise_budget_results':base,
      'discount_sensitivity_min_cost_budgets_0_1_2_3':change_in_discount,
      'regression_tests':'PASS'
    }
    p = Path(__file__).resolve().parent/'EXACT_RESULTS_v0.2.0.json'
    p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'budget_min_cost':{k:v['min_cost'] for k,v in base.items()},
                      'discount_sensitivity':change_in_discount,
                      'all_assertions':'PASS', 'results':str(p)},indent=2))

if __name__ == '__main__':
    main()