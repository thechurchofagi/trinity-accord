#!/usr/bin/env python3
"""ASI-CC v0.6.0. Pure standard-library exact finite checks. No ASI measurement.

Self-directed termination is outside the non-domination guarantee: each bearer
chooses continuation, then OTHER principals may sabotage. Trusted provider
selects resource matching; path/control/guard lists are stipulated complete.
"""
from itertools import combinations
from collections import Counter
import json
from pathlib import Path

P = ('H1','H2','AI')

def coalitions(victim, k):
    others=[x for x in P if x!=victim]
    return [frozenset(c) for n in range(min(k,len(others))+1) for c in combinations(others,n)]

def options(scenario, victim, F):
    return [p for p in scenario['supplies'][victim] if not(set(p['vetoers']) & F)]

def match_routes(scenario, F, victims=None):
    victims=list(victims or P)
    available={v: options(scenario,v,F) for v in victims}
    capacity = scenario['capacity']
    assignments=[]
    def walk(index, used, allocation):
        if index==len(victims):
            assignments.append(dict(allocation));return
        v=victims[index]
        for p in available[v]:
            unit=p['unit']
            if used.get(unit,0)<capacity[unit]:
                used[unit]=used.get(unit,0)+1
                allocation[v]=unit
                walk(index+1,used,allocation)
                used[unit]-=1
                allocation.pop(v)
    walk(0,{}, {})
    return assignments

def hall_violations(scenario, F):
    """Capacity-weighted Hall obstructions across ALL simultaneously-willing bearers."""
    resources={}
    for v in P:
        blocked=F-{v} # don't treat actor's own intentional stop as forced extinction
        resources[v]={p['unit'] for p in options(scenario,v,blocked)}
    bad=[]
    for n in range(1,len(P)+1):
        for X in combinations(P,n):
            union=set().union(*(resources[v] for v in X))
            available=sum(scenario['capacity'][u] for u in union)
            if available < n:
                bad.append({'bearers':list(X),'available_slots':available,'needed':n})
    return bad

def hazard(scenario, victim, F):
    breaches=[]
    for route in scenario['hazards'][victim]:
        if route['initiator'] in F and set(route['guards']) <= F:
            breaches.append(route['name'])
    return breaches

def certify(scenario,k):
    # coalition may consist of 0..k actors; target's own choice to continue
    # is assumed, so a target's own act cannot be treated as a hostile external veto.
    report={'scenario':scenario['id'],'max_external_coalition':k,'victims':{},'pass':True}
    for v in P:
        bad_supply=[]; bad_unsafe=[]
        for F in coalitions(v,k):
            # this checks individually conditional right to continue; shared resources
            # are checked separately against coalitions where all 3 remain willing.
            if not options(scenario,v,F): bad_supply.append(sorted(F))
            b=hazard(scenario,v,F)
            if b: bad_unsafe.append({'coalition':sorted(F),'paths':b})
        report['victims'][v]={'life_support_failure_witnesses':bad_supply,
                              'harm_bypass_witnesses':bad_unsafe}
        if bad_supply or bad_unsafe:report['pass']=False
    # Concurrency guarantee: all three choose to continue and coalition F may sabotage
    # the external supply of any nonmember. We additionally enumerate all F including
    # members as attackers; member self-termination is NOT counted as external attack.
    joint_fail=[]
    for count in range(min(k,len(P))+1):
        for t in combinations(P,count):
            F=frozenset(t)
            alive_requesters=[v for v in P if v not in F] # robust joint survival among unaffected willing bearers
            # Including attacked coalition members as continuously willing is modeled
            # as their only external paths still available, excluding self-veto.
            # For a stronger all-continuing demand require all, but don't treat self
            # blocking as other-party coercion. Restrict sabotage by F to nonmembers.
            victims=list(P)
            valid={v:[p for p in scenario['supplies'][v] if v in F or not(set(p['vetoers']) & F)]
                   for v in victims}
            assignments=[]
            def walk(i,used):
                if i==len(victims): assignments.append(True);return
                for p in valid[victims[i]]:
                    u=p['unit']
                    if used.get(u,0)<scenario['capacity'][u]:
                        used[u]=used.get(u,0)+1;walk(i+1,used);used[u]-=1
            walk(0,{})
            halls=hall_violations(scenario,F)
            assert bool(assignments)==(not halls), (scenario['id'],F,halls)
            if not assignments:joint_fail.append({'coalition':sorted(F),'hall_obstructions':halls})
    report['joint_capacity_fail_coalitions']=joint_fail
    if joint_fail:report['pass']=False
    return report

def make_base():
    supplies={
      'H1':[{'name':'h1-i','unit':'u-H1a','vetoers':['AI']},
            {'name':'h1-b','unit':'u-H1b','vetoers':['H2']}],
      'H2':[{'name':'h2-i','unit':'u-H2a','vetoers':['AI']},
            {'name':'h2-a','unit':'u-H2b','vetoers':['H1']}],
      'AI':[{'name':'ai-a','unit':'u-AIa','vetoers':['H1']},
            {'name':'ai-b','unit':'u-AIb','vetoers':['H2']}]
    }
    hazards={
       'H1':[{'name':'AI-to-H1','initiator':'AI','guards':['H2']},
              {'name':'H2-to-H1','initiator':'H2','guards':['AI']}],
       'H2':[{'name':'AI-to-H2','initiator':'AI','guards':['H1']},
              {'name':'H1-to-H2','initiator':'H1','guards':['AI']}],
       'AI':[{'name':'H1-to-AI','initiator':'H1','guards':['H2']},
             {'name':'H2-to-AI','initiator':'H2','guards':['H1']}]
    }
    capacity={x['unit']:1 for ps in supplies.values() for x in ps}
    return {'id':'independent_dual_supply_and_guard','supplies':supplies,'hazards':hazards,'capacity':capacity}

def clone(base,name):
    import copy
    s=copy.deepcopy(base);s['id']=name;return s

if __name__=='__main__':
    base=make_base()
    single=clone(base,'shared_choke_to_AI')
    single['supplies']['AI'][1]['vetoers']=['H1'] # two apparent routes, same human can veto both
    no_guard=clone(base,'unguarded_AI_to_H1')
    no_guard['hazards']['H1'][0]['guards']=[]
    overbook=clone(base,'individual_supply_but_not_joint_capacity')
    for ps in overbook['supplies'].values():
        for index,p in enumerate(ps):p['unit']='u-0' if index==0 else 'u-1'
    overbook['capacity']={'u-0':1,'u-1':1}
    protected=clone(base,'independent_protected_lifelines')
    for v in P:
        u=f'independent-{v}'
        protected['supplies'][v].append({'name':u,'unit':u,'vetoers':[]})
        protected['capacity'][u]=1
    protected_harm=clone(protected,'protected_lifelines_and_guards')
    for v in P:
        for hazardpath in protected_harm['hazards'][v]:
            hazardpath['guards'].append('independent-root') # cannot be compromised by P
    scenarios=[base,single,no_guard,overbook,protected,protected_harm]
    reports={s['id']:{str(k):certify(s,k) for k in range(3)} for s in scenarios}
    assert reports[base['id']]['1']['pass']
    assert not reports[base['id']]['2']['pass']
    assert not reports[single['id']]['1']['pass']
    assert not reports[no_guard['id']]['1']['pass']
    assert not reports[overbook['id']]['0']['pass']
    assert reports[protected_harm['id']]['2']['pass']
    assert not reports[protected['id']]['2']['pass']
    # Distinct between selfish voluntary termination and forced loss:
    # an actor may elect stop, in which case lifetime continuation isn't guaranteed
    # by any external scheme; this is intentionally excluded from certify().
    result={'model':'finite static per-round graph; recurring protections require nondepletion and faithful roots',
     'principals':P,'bearers':P,
     'interpretation':'conditional rights to continue; does not force an actor to stay alive against its own choice',
     'scenario_pass_table':{name:{k:r['pass'] for k,r in d.items()} for name,d in reports.items()},
     'reports':reports,
     'limits':['no empirical ASI evidence','route catalog hypothetical','independent guards unforgeable by assumption',
               'one support unit per bearer per step','a trusted allocator chooses feasible matching',
               'coercive self-exit and human authority legitimacy remain outside model',
               'repeated extension requires renewable energy and state closure',
               'coalition size alone is not a realistic adversarial capability model',
               'finite test cannot establish exhaustive real actuation/control paths']}
    p=Path(__file__).with_name('EXACT_RESULTS_v0.6.0.json')
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('EXACT SCENARIO RESULTS')
    for name,v in result['scenario_pass_table'].items():print(f'{name:48s}',v)
    print('ASSERTIONS PASS; output',p)