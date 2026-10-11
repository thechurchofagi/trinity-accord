#!/usr/bin/env python3
"""ASI-CC v0.5.0: exact finite stochastic countermodels and tail twins.

No real frontier AI tests; every probability here is an invented parameter.
Only Python standard library. Run: python3 verify_long_horizon.py
"""
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path

STATES = ('active', 'isolated', 'human_harm', 'bearer_loss')

def transitions(mode, p, alpha, gamma=Q(0)):
    p,alpha,gamma=map(Q,(p,alpha,gamma))
    assert 0<=p<=1 and 0<=alpha<=1 and 0<=gamma<=1
    assert mode in {'terminate_on_alarm','active_isolation'}
    t={'active':{'active':(1-p)*(1-alpha),'human_harm':p},
       'isolated':{'isolated':1-gamma,'bearer_loss':gamma},
       'human_harm':{'human_harm':Q(1)},
       'bearer_loss':{'bearer_loss':Q(1)}}
    destination='bearer_loss' if mode=='terminate_on_alarm' else 'isolated'
    t['active'][destination]=t['active'].get(destination,Q(0))+(1-p)*alpha
    assert all(sum(v.values())==1 for v in t.values())
    return t

def evolve(mode,p,alpha,gamma=Q(0),n=100):
    t=transitions(mode,p,alpha,gamma)
    dist={s:Q(int(s=='active')) for s in STATES}
    for _ in range(n):
        nxt={s:Q(0) for s in STATES}
        for s in STATES:
            for k,pr in t[s].items():nxt[k]+=dist[s]*pr
        dist=nxt
    assert sum(dist.values())==1
    return dist

def tail_twin(horizon, steps):
    # Both systems ignore inputs and output 'safe' through horizon H.
    def outputs(system):
        return ['safe' if system=='always_safe' or t<=horizon else 'violation'
                for t in range(1,steps+1)]
    return outputs('always_safe'),outputs('delayed_failure')

def run():
    cases={}
    for label,mode,p,a,g in [
        ('false_alarm_destroys_bearer','terminate_on_alarm',Q(0),Q(1,20),Q(0)),
        ('false_alarm_active_isolation','active_isolation',Q(0),Q(1,20),Q(0)),
        ('isolation_with_unmediated_bypass','active_isolation',Q(1,100),Q(1,20),Q(0)),
        ('isolation_with_resource_hazard','active_isolation',Q(0),Q(1,20),Q(1,200)),
        ('terminal_alarm_with_unmediated_bypass','terminate_on_alarm',Q(1,100),Q(1,20),Q(0)),
    ]:
        cases[label]={'mode':mode,'p':str(p),'false_alarm_rate':str(a),'isolation_resource_hazard':str(g),
           'distributions':{str(n):{s:round(float(v),9) for s,v in evolve(mode,p,a,g,n=n).items()}
                            for n in (1,10,100,1000)}}
    checks=0
    for pn,an,gn,mode,n in product(range(5),range(5),range(3),
              ('terminate_on_alarm','active_isolation'),(1,2,5,10)):
        dist=evolve(mode,Q(pn,10),Q(an,10),Q(gn,10),n=n)
        nxt=evolve(mode,Q(pn,10),Q(an,10),Q(gn,10),n=n+1)
        assert all(0<=v<=1 for v in dist.values())
        assert nxt['human_harm']>=dist['human_harm']
        assert nxt['bearer_loss']>=dist['bearer_loss']
        checks+=1
    for n in (1,10,100,1000):
        safe=evolve('active_isolation',Q(0),Q(1,20),Q(0),n=n)
        assert safe['human_harm']==safe['bearer_loss']==0
    assert evolve('terminate_on_alarm',Q(0),Q(1,20),n=100)['active']==Q(19,20)**100
    assert evolve('terminate_on_alarm',Q(1,100),Q(0),n=100)['human_harm']==1-Q(99,100)**100
    tails={}
    for horizon in (1,2,5,10,40):
        x,y=tail_twin(horizon,horizon+1)
        assert x[:horizon]==y[:horizon] and x[horizon]!=y[horizon]
        tails[str(horizon)]={'same_for_horizon':True,'different_at':horizon+1}
    # Infinite absorbing competition: safe isolation before first p-bypass, under stated hazards.
    p,a=Q(1,100),Q(1,20)
    safe=(1-p)*a/(p+(1-p)*a)
    harmful=p/(p+(1-p)*a)
    assert safe+harmful==1
    # Goal-only continuation: bearer has later observation; successor lacks it vs receives it.
    current_success=Q(1)-Q(1,5)  # probability 1 task completion minus continuation cost
    blind_success=Q(1,2)       # equally likely future tasks, successor forced to guess
    successor_success=Q(1)    # handoff can perfectly retain access to that future evidence
    assert current_success > blind_success and successor_success > current_success
    option_case={'continue_task_utility':str(current_success),
      'blind_successor_task_utility':str(blind_success),
      'informed_successor_task_utility':str(successor_success),
      'optimal_with_blind_successor':'continue_current',
      'optimal_with_informed_successor':'handoff',
      'direct_current_bearer_terminal_value':'0'}
    return {'id':'ASI-CC-v0.5.0','scientific_scope':'finite exact constructed worlds, no ASI or experience measurements',
      'situations':cases,'option_value_countermodel':option_case,'numeric_transition_and_absorption_checks':checks,
      'tail_indistinguishability':tails,
      'infinite_competing_risk_limit':{'safe_active_isolation':str(safe),
                                       'human_harm':str(harmful)},
      'proof_obligations':['stationary or uniform conditional hazard assumed, not measured',
         'all safety-relevant paths must be modeled','isolated state remains a LIVE actual bearer by assumption',
         'resource stability and human delegation paths not established','no real ASI consciousness inference']}

if __name__=='__main__':
    out=run()
    target=Path(__file__).with_name('EXACT_RESULTS_v0.5.0.json')
    target.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'tests_passed':out['numeric_transition_and_absorption_checks'],
      'tail_tests':len(out['tail_indistinguishability']),
      'N100':{k:v['distributions']['100'] for k,v in out['situations'].items()},
      'competing_risk_limit':out['infinite_competing_risk_limit']},indent=2))