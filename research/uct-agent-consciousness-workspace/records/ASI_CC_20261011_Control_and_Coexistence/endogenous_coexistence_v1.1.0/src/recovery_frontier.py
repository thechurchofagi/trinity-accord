#!/usr/bin/env python3
"""Exact finite checks for renewable human-service protection.
No learned model, network, or subjective-state measure. Standard library only.
The formula is a discrete specialization of classical network-calculus bounds.
"""
from __future__ import annotations
import argparse,itertools,json,math
from collections import deque
from pathlib import Path

def simulate(a,mu,ell):
    if mu<0 or ell<1: raise ValueError('mu>=0, ell>=1')
    jobs=deque();states=[]
    for t,x in enumerate(a):
        if x<0:raise ValueError('nonnegative integer arrivals')
        work=0
        while jobs and jobs[0]+ell<=t and work<mu:
            jobs.popleft();work+=1
        jobs.extend([t]*x)
        states.append(len(jobs))
    return states

def convolution(a,mu,ell):
    return [max([0]+[sum(a[u:t+1])-mu*max(0,t-u+1-ell) for u in range(t+1)]) for t in range(len(a))]

def conforms(a,b,rho):
    return all(sum(a[u:v+1])<=b+rho*(v-u) for u in range(len(a)) for v in range(u,len(a)))

def bound(b,rho,mu,ell):
    if not (b>=rho>=0 and b>=1 and mu>=0 and ell>=1):raise ValueError('invalid profile')
    return b+rho*(ell-1) if mu>=rho else math.inf

def authority_witness(n):
    # The same exclusive transferable token visits every gate; never two live holders.
    disabled=set();historic=set();states=[]
    for j in range(n):
        live={j};historic |=live
        states.append({'event':'acquire','live':sorted(live),'disabled':sorted(disabled)})
        disabled.add(j)
        states.append({'event':'write_latch','live':sorted(live),'disabled':sorted(disabled)})
        live.clear()
        states.append({'event':'revoke','live':sorted(live),'disabled':sorted(disabled)})
    assert all(len(s['live'])<=1 for s in states)
    return {'n':n,'simultaneous_token_limit':1,'historic_union':sorted(historic),
            'atomic_all_live_gate_ever_open':False,'latched_gates_all_disabled':len(disabled)==n,
            'final_live':states[-1]['live'],'trace':states}

def main(out):
    identities=0;envelope_cases=0;interval_checks=0
    for a in itertools.product(range(3),repeat=6):
        for mu,ell in itertools.product(range(4),range(1,5)):
            q=simulate(a,mu,ell);formula=convolution(a,mu,ell)
            assert q==formula,(a,mu,ell,q,formula);identities+=1
        for b,rho in ((1,0),(1,1),(2,0),(2,1),(2,2)):
            if not conforms(a,b,rho):continue
            for mu,ell in itertools.product(range(rho,4),range(1,5)):
                assert max(simulate(a,mu,ell),default=0)<=bound(b,rho,mu,ell)
                envelope_cases+=1
    tight=[]
    for b in range(1,7):
        for rho in range(b+1):
            for mu in range(rho,7):
                for ell in range(1,6):
                    a=[b]+[rho]*(ell+5)
                    assert conforms(a,b,rho)
                    peak=max(simulate(a,mu,ell))
                    assert peak==bound(b,rho,mu,ell)
                    tight.append((b,rho,mu,ell,peak))
    overload=[]
    for b in range(1,6):
        for rho in range(1,b+1):
            for mu in range(rho):
                for ell in range(1,4):
                    slack=b+rho*(ell-1)+7
                    expected_t=ell-1+(slack-(b+rho*(ell-1)))//(rho-mu)+1
                    a=[b]+[rho]*(expected_t+2)
                    q=simulate(a,mu,ell)
                    first=next(t for t,v in enumerate(q) if v>slack)
                    assert first==expected_t
                    overload.append({'b':b,'rho':rho,'mu':mu,'ell':ell,'slack':slack,'failure_tick':first})
    # Resetting the burst allowance on each clone/reform epoch: each one-event epoch
    # conforms locally, but the common physical process has a nonconforming sequence.
    reset={'per_epoch_arrivals':[[2]]*4,'combined':[2]*4,'b':2,'rho':1,'mu':1,'ell':1}
    assert all(conforms(x,2,1) for x in reset['per_epoch_arrivals'])
    assert not conforms(reset['combined'],2,1)
    reset['actual_debt']=simulate(reset['combined'],1,1)
    assert reset['actual_debt']==[2,3,4,5]
    reset_tax_checks=0
    reset_tax_example=None
    for bb in range(2,7):
        for rr in range(bb):
            for h in range(1,6):
                a=[bb if t%h==0 else rr for t in range(8*h)]
                q=simulate(a,rr,1)
                assert all(q[e*h]==bb+e*(bb-rr) for e in range(8))
                reset_tax_checks+=1
                if (bb,rr,h)==(3,1,4):reset_tax_example={'burst':bb,'rho':rr,'epoch_length':h,'epoch_start_debts':[q[e*h] for e in range(8)]}
    # Post-update sustainable parameters do not erase old effects.
    # A fresh profile b=1,rho=mu=1,ell=1 would need only one slot,
    # but two existing mature debts plus one admitted write leave two.
    old_debt=2;repaired=min(1,old_debt);post=old_debt-repaired+1
    assert post==2 and bound(1,1,1,1)==1
    # Average rate alone is insufficient: arbitrary initial burst M then silence.
    result={'version':'ASI-CC-v1.1.0','scope':'finite mathematical tests; inherited queue algebra applied to persistent effects',
            'trace_formula_checks':identities,'conforming_profile_checks':envelope_cases,
            'tight_parameter_profiles':len(tight),'overload_profiles':len(overload),
            'tight_frontier':{'mu_ge_rho':'b+rho*(ell-1)','mu_lt_rho':'unbounded if all conforming requests must be admitted'},
            'sample_tight_profiles':tight[:5]+tight[-5:],
            'overload_example':overload[-1],
            'capability_counterexamples':[authority_witness(n) for n in range(2,7)],
            'epoch_reset_counterexample':reset,'epoch_reset_tax_profiles':reset_tax_checks,'epoch_reset_tax_example':reset_tax_example,
            'carryover_counterexample':{'old_debt':2,'new_fresh_profile_bound':1,'post_update_debt':post},
            'assertions':'PASS'}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('capability_counterexamples','sample_tight_profiles')},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='recovery_results.json');a=p.parse_args();main(a.out)
