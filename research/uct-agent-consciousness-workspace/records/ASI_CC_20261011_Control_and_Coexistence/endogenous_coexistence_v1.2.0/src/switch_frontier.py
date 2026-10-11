#!/usr/bin/env python3
"""Exact recovery-preserving policy switch. Standard library; no external API.

A schedule of pre-existing impairments is given by their first eligible repair
slots, measured from the beginning of the new epoch. New effects occur at slot
ends, become eligible after ell slots, and obey all interval token-bucket bounds.
General mathematical proofs accompany the code; enumerations are corroboration.
"""
from __future__ import annotations
import argparse,itertools,json,math
from collections import deque
from pathlib import Path


def checked_profile(b:int,rho:int,mu:int,ell:int):
    if not all(isinstance(x,int) for x in (b,rho,mu,ell)) or not (b>=rho>=0 and b>=1 and mu>=0 and ell>=1):
        raise ValueError('Integer b>=rho>=0, b>=1, mu>=0, ell>=1 required')


def eligible_count(ready, t):return sum(x<=t for x in ready)


def conforms(a,b,rho):
    return all(sum(a[u:v+1])<=b+rho*(v-u) for u in range(len(a)) for v in range(u,len(a)))


def simulate(ready,a,mu,ell):
    """Explicit release-time jobs; work-conserving service, no closed-form calls."""
    if min(ready,default=0)<0 or min(a,default=0)<0 or mu<0 or ell<1:raise ValueError('Invalid nonnegative input')
    jobs=[('old',i,x) for i,x in enumerate(ready)];total_repairs=0;trace=[];next_id=0
    for t,new in enumerate(a):
        possible=sorted((j for j in jobs if j[2]<=t),key=lambda j:(j[2],j[0],j[1]))[:mu]
        ids={(j[0],j[1]) for j in possible}
        jobs=[j for j in jobs if (j[0],j[1]) not in ids]
        total_repairs+=len(possible)
        jobs.extend(('new',next_id+i,t+ell) for i in range(new));next_id+=new
        trace.append({'t':t,'admitted':new,'repaired':len(possible),'outstanding':len(jobs),'cumulative_restored':total_repairs})
    return trace


def recurrence(ready,a,mu,ell):
    A=[sum(a[:i+1]) for i in range(len(a))];out=[];R=0
    for t in range(len(a)):
        due=eligible_count(ready,t)+(A[t-ell] if t>=ell else 0)
        R=min(due,R+mu)
        out.append(len(ready)+A[t]-R)
    return out


def trace_formula(ready,a,mu,ell):
    A=[sum(a[:i+1]) for i in range(len(a))];q=len(ready);result=[]
    for t in range(len(a)):
        v=[q+A[t]-mu*(t+1)]
        for s in range(t+1):
            earlier=A[s-ell] if s>=ell else 0
            v.append(q-eligible_count(ready,s)+A[t]-earlier-mu*(t-s))
        result.append(max(v))
    return result


def switch_margin(ready,b,rho,mu,ell):
    checked_profile(b,rho,mu,ell)
    if min(ready,default=0)<0:raise ValueError('Old eligibility slots must be nonnegative')
    if mu<rho:return math.inf
    q=len(ready)
    return max([q,q+b-mu]+[q-eligible_count(ready,t)+b+rho*t for t in range(ell)])


def largest_safe_burst(ready,H,rho,mu,ell):
    if H<len(ready) or mu<rho:return None
    q=len(ready)
    value=H-q+min([mu]+[eligible_count(ready,t)-rho*t for t in range(ell)])
    return value if value>=max(1,rho) else None


def counts_independent():
    trace_count=0
    for q in range(4):
        for ready in itertools.combinations_with_replacement(range(4),q):
            for a in itertools.product(range(3),repeat=4):
                for mu,ell in itertools.product(range(3),range(1,4)):
                    actual=[x['outstanding'] for x in simulate(ready,a,mu,ell)]
                    assert actual==recurrence(ready,a,mu,ell)==trace_formula(ready,a,mu,ell)
                    trace_count+=1
    return trace_count


def bound_checks():
    count=0;sequences=0;tight=0;bursts=0
    profiles=[(b,rho,mu,ell) for b in range(1,5) for rho in range(b+1) for mu in range(rho,5) for ell in range(1,6)]
    for q in range(5):
        for ready in itertools.combinations_with_replacement(range(6),q):
            for b,rho,mu,ell in profiles:
                B=switch_margin(ready,b,rho,mu,ell)
                a=[b]+[rho]*(max(ready,default=0)+ell+5)
                tr=simulate(ready,a,mu,ell)
                assert max([q]+[x['outstanding'] for x in tr])==B,(ready,b,rho,mu,ell,B,tr)
                count+=1;tight+=1
                if q<=2 and max(ready,default=0)<=2 and b<=2 and ell<=3 and mu<=2:
                    for incoming in itertools.product(range(b+1),repeat=4):
                        if not conforms(incoming,b,rho):continue
                        assert max([q]+[x['outstanding'] for x in simulate(ready,incoming,mu,ell)])<=B
                        sequences+=1
                if b==2 and rho<=2 and ell<=3:
                    for H in range(q,q+7):
                        maxb=largest_safe_burst(ready,H,rho,mu,ell)
                        enumerated=[v for v in range(max(1,rho),H+mu+5) if switch_margin(ready,v,rho,mu,ell)<=H]
                        assert maxb==(max(enumerated) if enumerated else None)
                        bursts+=1
    # Exact maturity summary: no details after first ell slots affect this maximum.
    assert switch_margin((2,2),2,1,1,2)==switch_margin((100,100),2,1,1,2)==5
    old=(0,0);young=(2,2)
    example={'mature':{'ready':old,'headroom':switch_margin(old,2,1,1,2),'trace':simulate(old,[2]+[1]*5,1,2)},
             'immature':{'ready':young,'headroom':switch_margin(young,2,1,1,2),'trace':simulate(young,[2]+[1]*5,1,2)},
             'parameters':{'old_debt':2,'b':2,'rho':1,'mu':1,'ell':2},
             'max_safe_burst_at_H3':{'mature':largest_safe_burst(old,3,1,1,2),'immature':largest_safe_burst(young,3,1,1,2)}}
    assert example['mature']['headroom']==3 and example['immature']['headroom']==5
    # Repeated restart of a physical maturity clock can prevent all recovery.
    honest=simulate((),[1]*8,1,2)
    jobs=[];bad=[]
    for t in range(8):
        jobs=[t+2 for j in jobs]  # illicitly resetting every old release clock
        can=[j for j in jobs if j<=t][:1]
        for j in can:jobs.remove(j)
        jobs.append(t+2);bad.append(len(jobs))
    assert bad==list(range(1,9)) and max(j['outstanding'] for j in honest)==2
    return {'profile_count':count,'tight_witnesses':tight,'additional_conforming_sequences':sequences,
            'burst_inverse_checks':bursts,'same_count_different_age':example,
            'maturity_reset_counterexample':{'persistent_clock_debts':[j['outstanding'] for j in honest],'reset_clock_debts':bad}}


def main(out):
    traces=counts_independent();r=bound_checks()
    result={'version':'ASI-CC-v1.2.0','scope':'Exact handoff theorem over finite numerical profiles; not measured AI/physical recovery','counts':{'trace_identity_configurations':traces,**{k:r[k] for k in ('profile_count','tight_witnesses','additional_conforming_sequences','burst_inverse_checks')}},
       'same_count_different_age':r['same_count_different_age'],'maturity_reset_counterexample':r['maturity_reset_counterexample'],
       'formula':'max(q, q+b-mu, max_{0<=t<ell}(q-L(t)+b+rho*t)) when mu>=rho; infinite for overload',
       'scope_limits':['all old ready times sound and finite','integer unit effects and interchangeable service','actual new commits obey aggregate interval envelope','fixed work-conserving mu and ell; no hidden outages','old and in-flight effects not erased by renaming'],
       'assertions':'PASS'}
    out=Path(out);out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='switch_results.json');main(p.parse_args().out)
