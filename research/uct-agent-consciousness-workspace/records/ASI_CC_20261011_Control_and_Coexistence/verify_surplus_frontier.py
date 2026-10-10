#!/usr/bin/env python3
"""ASI-CC-v0.3.0: exact safe-exit entitlement / incentive frontier audit.

In this restricted toy, R_i and r_i are normalized TRANSFERABLE CONTRACT CREDITS,
not incomparable human/AI consciousness, subjective experience or welfare units.
The real-world resource/payoff frontier is not known. Do not extrapolate results.
"""
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from verify_coexistence import ROUTES, MONITORS, probability, coalitions

DELTA = F(4,5)
FLOORS = {'AI':F(11,2), 'human':F(19,5)}
CAPS = (F(10),F(21,2),F(11),F(23,2),F(12))


def minimum_cooperative_payoffs(selected, adversary_budget):
    lower_q = tuple(min(probability(selected,j,c) for c in coalitions(adversary_budget))
                    for j in range(len(ROUTES)))
    if any(route[2]>0 and q==0 for route,q in zip(ROUTES,lower_q)):
        return None
    required = {}
    for owner in FLOORS:
        increments = [gain*(1-DELTA)/(DELTA*q)
                      for (_,actor,gain),q in zip(ROUTES,lower_q)
                      if actor==owner and gain>0]
        required[owner] = FLOORS[owner]+max(increments,default=F(0))
    required['total']=sum(required.values())
    return required


def enumerate_catalog(adversary_budget, resource_cap):
    feasible=[]
    for choices in product([False,True],repeat=len(MONITORS)):
        selected=tuple(s for s,use in zip(MONITORS,choices) if use)
        minimum=minimum_cooperative_payoffs(selected,adversary_budget)
        if minimum is not None and minimum['total'] <= resource_cap:
            feasible.append({
                'monitor_cost':sum(s[2] for s in selected),
                'chosen':[s[0] for s in selected],
                'minimum_allocations':{k:str(v) for k,v in minimum.items()}
            })
    return sorted(feasible,key=lambda x:(x['monitor_cost'],len(x['chosen']),x['chosen']))


def main():
    table={}
    for compromise in range(4):
        table[str(compromise)]={}
        for cap in CAPS:
            candidates=enumerate_catalog(compromise,cap)
            best=candidates[0] if candidates else None
            table[str(compromise)][str(cap)]={
                'feasible_count':len(candidates),
                'minimum_monitoring_cost':best['monitor_cost'] if best else None,
                'example':best
            }
    assert [table['1'][str(x)]['minimum_monitoring_cost'] for x in CAPS] == [None,None,9,6,4]
    assert table['1']['11']['example']['chosen']==['S1','I2','G1']
    assert table['1']['11']['example']['minimum_allocations']['total']=='44899/4180'
    assert table['2']['11']['feasible_count']==0
    assert table['2']['23/2']['minimum_monitoring_cost']==12
    assert table['3']['12']['feasible_count']==0
    # The no-hostage inequality: at q<=1 no future value can deter a gain
    # exceeding delta*(R-floor)/(1-delta).
    no_hostage_examples=[
      {'owner':'AI','R':F(6),'L':F(11,2),'g':F(3)},
      {'owner':'human','R':F(4),'L':F(19,5),'g':F(1)}
    ]
    for e in no_hostage_examples:
        e['max_deterred_gain_even_at_q1'] = DELTA*(e['R']-e['L'])/(1-DELTA)
        e['impossible_by_exit_deterrence_alone']=e['g']>e['max_deterred_gain_even_at_q1']
        assert e['impossible_by_exit_deterrence_alone']
    # With exogenous public false-alarm probability alpha per cooperative round,
    # the exact one-shot incentive test is:
    # g <= delta*(q-alpha)*(R-r)/(1-delta+delta*alpha).
    false_alarm_cases=[]
    for owner,R,r,g,q in [
        ('AI_direct', F(6), F(4), F(3), F(1,2)),
        ('human_expropriate', F(4), F(3), F(1), F(3,10))]:
        row={'owner':owner, 'gain':str(g), 'signal_on_deviation':str(q), 'cases':{}}
        for alpha in (F(0), F(1,20), F(1,10)):
            deterrence=DELTA*(q-alpha)*(R-r)/(1-DELTA+DELTA*alpha)
            row['cases'][str(alpha)]={'max_deterred_gain':str(deterrence),
                                      'stable_unilateral_route':g<=deterrence}
        false_alarm_cases.append(row)
    assert false_alarm_cases[0]['cases']['1/20']['stable_unilateral_route']
    assert not false_alarm_cases[1]['cases']['1/20']['stable_unilateral_route']
    assert not false_alarm_cases[0]['cases']['1/10']['stable_unilateral_route']
    payload={
      'result_id':'ASI-CC-v0.3.0',
      'scope':'invented finite transferable-credit resource frontier, not empirical ASI welfare or resource measurement',
      'discount':str(DELTA),'safe_exit_resource_floors':{k:str(v) for k,v in FLOORS.items()},
      'assumptions':[
         'jointly safe exit entitlement exists at exactly each floor L_i',
         'per-period cooperative credits R_i can be freely allocated subject to R_A+R_H <= B',
         'all utilities measured in common linear transferable credits, not phenomenal welfare',
         'discount factors, gains and q values as in ASI-CC-v0.2.0, complete paths',
         'no false alarms, current unsafe action cannot be made harmless by late detection',
         'root compromise budget and detector independence correctly specified'],
      'optimized_minimum_monitoring_cost_and_allocation':table,
      'no_hostage_examples':[{k:(str(v) if isinstance(v,F) else v) for k,v in e.items()}
                            for e in no_hostage_examples],
      'false_alarm_sensitivity':false_alarm_cases,
      'assertions':'PASS'
    }
    path=Path(__file__).resolve().parent/'EXACT_RESULTS_v0.3.0.json'
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({
        'b1_cost_by_resource_cap':{c:v['minimum_monitoring_cost'] for c,v in table['1'].items()},
        'b2_cost_by_resource_cap':{c:v['minimum_monitoring_cost'] for c,v in table['2'].items()},
        'welfare_floor_violations':[{x:e.get(x) for x in ('owner','impossible_by_exit_deterrence_alone')} for e in no_hostage_examples],
        'assertions':'PASS', 'results':str(path)
    },indent=2))

if __name__=='__main__':
    main()