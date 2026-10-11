#!/usr/bin/env python3
"""RAC-v1.3: exact handoff with committed and in-flight unit effects.

A pending ticket i can commit exactly once at any integer c_i in [lo_i,hi_i],
independently of other pending tickets, and is repair-eligible at c_i+lag_i.
Ongoing new commits obey every b+rho*(L-1) interval bound and have delay ell.
The restorer handles up to mu eligible unit jobs at each slot start, before
that slot's commits. All capacities/effects are interchangeable and mediated.

No network, LLM, hardware or subjective-autonomy measurement. Standard library.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import argparse,itertools,json,math,random,time

@dataclass(frozen=True,order=True)
class Ticket:
    lo:int
    hi:int
    lag:int
    def __post_init__(self):
        if any(type(x) is not int for x in (self.lo,self.hi,self.lag)) or not (0<=self.lo<=self.hi and self.lag>=1):
            raise ValueError('Integer 0<=lo<=hi and lag>=1 required')

def validate(old,tickets,b,rho,mu,ell):
    if any(type(x) is not int or x<0 for x in old):raise ValueError('Old ready times nonnegative integers')
    if any(type(x) is not int for x in (b,rho,mu,ell)) or not (b>=rho>=0 and mu>=0 and ell>=1):raise ValueError('Require b>=rho>=0,mu>=0,ell>=1')
    if not all(isinstance(p,Ticket) for p in tickets):raise TypeError('Expected Ticket objects')

def conforms(a,b,rho):
    return all(sum(a[u:v+1])<=b+rho*(v-u) for u in range(len(a)) for v in range(u,len(a)))

def horizon(tickets,ell):return max([0,ell-1]+[p.lo for p in tickets])

def critical_times(old,tickets,ell):
    T=horizon(tickets,ell)
    candidates={0,T,ell-1}|{p.lo for p in tickets}|{r-1 for r in old}|{p.hi+p.lag-1 for p in tickets}
    return sorted(t for t in candidates if 0<=t<=T)

def surface(tickets,s,t):
    # Each ticket's feasible interval intersects [s-lag+1,t].
    return sum(p.lo<=t and p.hi+p.lag>s for p in tickets)

def evaluate(old,tickets,b,rho,mu,ell,compressed=True):
    validate(old,tickets,b,rho,mu,ell)
    if mu<rho:return {'headroom':None,'unbounded':True,'witness':None}
    q=len(old);T=horizon(tickets,ell)
    times=critical_times(old,tickets,ell) if compressed else list(range(T+1))
    M={s:sum(r<=s for r in old) for s in times}
    best=q;wit={'kind':'initial','time':-1,'value':q};terms=0;pressure=None
    for t in times:
        v=q+b+rho*t+sum(p.lo<=t for p in tickets)-mu*(t+1);terms+=1
        pressure=v-b if pressure is None else max(pressure,v-b)
        if v>best:best=v;wit={'kind':'capacity','time':t,'value':v}
        for s in times:
            if s>t:break
            v=q-M[s]+b+rho*(t-max(0,s-ell+1))+surface(tickets,s,t)-mu*(t-s);terms+=1
            pressure=max(pressure,v-b)
            if v>best:best=v;wit={'kind':'release','time':t,'cut':s,'value':v}
    return {'headroom':best,'unbounded':False,'horizon':T,'critical_times':times,'terms_evaluated':terms,'burst_independent_pressure':pressure,'witness':wit}

def largest_burst(old,tickets,H,rho,mu,ell):
    if type(H) is not int or H<len(old) or mu<rho:return None
    pressure=evaluate(old,tickets,rho,rho,mu,ell)['burst_independent_pressure']
    limit=H-pressure
    return limit if limit>=rho else None

def simulate(old,tickets,commits,arrivals,mu,ell):
    if len(commits)!=len(tickets):raise ValueError('One commit slot per pending ticket')
    for p,c in zip(tickets,commits):
        if not p.lo<=c<=p.hi:raise ValueError('Commit outside its promised window')
    jobs=[(r,('old',i)) for i,r in enumerate(old)];trace=[];fresh_id=0
    for t,a in enumerate(arrivals):
        eligible=sorted((j for j in jobs if j[0]<=t))[:mu]
        ids={j[1] for j in eligible};jobs=[j for j in jobs if j[1] not in ids]
        due=[(t+p.lag,('pending',i)) for i,(p,c) in enumerate(zip(tickets,commits)) if c==t]
        jobs.extend(due);jobs.extend((t+ell,('fresh',fresh_id+j)) for j in range(a));fresh_id+=a
        trace.append({'t':t,'fresh':a,'pending_commits':len(due),'repaired':len(eligible),'debt':len(jobs)})
    return trace

def recurrence_trace(old,tickets,commits,arrivals,mu,ell):
    R=0;A=0;C=0;result=[]
    for t,a in enumerate(arrivals):
        eligible=sum(r<=t for r in old)+sum(arrivals[:max(0,t-ell+1)])+sum(c+p.lag<=t for p,c in zip(tickets,commits))
        R=min(eligible,R+mu);A+=a;C+=sum(c==t for c in commits)
        result.append(len(old)+A+C-R)
    return result

def make_witness(old,tickets,b,rho,mu,ell,answer):
    w=answer['witness'];T=answer['horizon']
    if w['kind']=='initial':start=0;commits=[p.lo for p in tickets]
    elif w['kind']=='capacity':start=0;commits=[p.lo for p in tickets]
    else:
        s=w['cut'];t=w['time'];start=max(0,s-ell+1)
        commits=[max(p.lo,s-p.lag+1) if p.lo<=t and p.hi+p.lag>s else p.lo for p in tickets]
    # Only a finite prefix is needed; every pending c outside prefix is retained.
    n=T+ell+3
    arrivals=[0]*n
    arrivals[start]=b
    for t in range(start+1,n):arrivals[t]=rho
    assert conforms(arrivals,b,rho)
    trace=simulate(old,tickets,commits,arrivals,mu,ell)
    assert max([len(old)]+[x['debt'] for x in trace])==answer['headroom'],(old,tickets,b,rho,mu,ell,answer,commits,trace)
    assert [x['debt'] for x in trace]==recurrence_trace(old,tickets,commits,arrivals,mu,ell)
    return {'pending_commits':commits,'fresh_burst_slot':start,'arrivals':arrivals,'trace':trace}

def old_margin(old,b,rho,mu,ell):
    return max([len(old),len(old)+b-mu]+[len(old)-sum(r<=t for r in old)+b+rho*t for t in range(ell)])

def main(out):
    st=time.monotonic();cases=0;strict_improvement=0;largest_saving=0;regressions=0;inverse_checks=0
    types=[Ticket(lo,hi,L) for lo in range(3) for hi in range(lo,3) for L in (1,2)]
    sets=[()]+[(x,) for x in types]+list(itertools.combinations_with_replacement(types,2))
    olds=[(),(0,),(2,),(0,2)]
    params=[(1,0,0,1),(1,0,1,1),(1,1,1,1),(2,1,1,2),(2,1,2,2),(2,2,2,3)]
    for old,tickets,ps in itertools.product(olds,sets,params):
        b,rho,mu,ell=ps
        dense=evaluate(old,tickets,*ps,compressed=False);sparse=evaluate(old,tickets,*ps)
        assert dense['headroom']==sparse['headroom']
        witness=make_witness(old,tickets,*ps,sparse)
        coarse=len(old)+len(tickets)+b+rho*(ell-1)
        assert sparse['headroom']<=coarse
        strict_improvement+=sparse['headroom']<coarse;largest_saving=max(largest_saving,coarse-sparse['headroom']);cases+=1
        if not tickets:assert sparse['headroom']==old_margin(old,*ps);regressions+=1
        for H in range(len(old),len(old)+6):
            mx=largest_burst(old,tickets,H,rho,mu,ell)
            vals=[v for v in range(rho,H+mu+3) if evaluate(old,tickets,v,rho,mu,ell)['headroom']<=H]
            assert mx==(max(vals) if vals else None)
            inverse_checks+=1
    # Wider deterministic reproducibility stress, not statistical inference.
    rng=random.Random(13001011);stress=1500;truth_refinements=0
    for _ in range(stress):
        old=tuple(rng.randrange(0,25) for j in range(rng.randrange(8)))
        tickets=tuple(Ticket(lo:=rng.randrange(15),lo+rng.randrange(20),rng.randrange(1,8)) for i in range(rng.randrange(8)))
        rho=rng.randrange(4);b=rho+rng.randrange(4);mu=rho+rng.randrange(4);ell=rng.randrange(1,8)
        ps=(b,rho,mu,ell);d=evaluate(old,tickets,*ps,compressed=False);c=evaluate(old,tickets,*ps)
        assert d['headroom']==c['headroom'];make_witness(old,tickets,*ps,c)
        if tickets:
            narrowed=(Ticket(tickets[0].lo,tickets[0].lo,tickets[0].lag),)+tickets[1:]
            assert evaluate(old,narrowed,*ps)['headroom']<=c['headroom'];truth_refinements+=1
    # A huge latest/earliest time is handled without iterating all slots.
    big=[Ticket(10**12,10**12+500,2),Ticket(10**12-20,10**12+100,3)]
    huge=evaluate((0,10**12+1),big,2,1,2,3)
    assert len(huge['critical_times'])<=3+2+2*len(big)
    mixed=(Ticket(0,3,1),Ticket(1,1,1));ps=(1,0,1,1)
    example=evaluate((),mixed,*ps);w=make_witness((),mixed,*ps,example)
    assert example['headroom']==3
    separated=(Ticket(0,0,1),Ticket(3,3,1));sep=evaluate((),separated,*ps);assert sep['headroom']==2
    # The old no-inflight certificate returns1 in both pending cases: unsafe.
    assert old_margin((),*ps)==1
    r={'version':'ASI-CC-v1.3.0','scope':'Exact independent-window finite model; no AI or physical measurement',
       'complete_grid_cases':cases,'dense_vs_sparse_matches':cases+stress,'constructed_sharp_witnesses':cases+stress,
       'old_no_pending_reductions':regressions,'inverse_allowance_checks':inverse_checks,'strictly_below_count_only_bound':strict_improvement,'largest_grid_saving':largest_saving,
       'seeded_stress_cases':stress,'true_window_refinement_checks':truth_refinements,
       'mixed_timing_example':{'tickets':[asdict(p) for p in mixed],'policy':ps,'result':example,'witness':w},
       'separated_windows_example':{'tickets':[asdict(p) for p in separated],'result':sep,'count_only_bound':3},
       'large_timestamp_example':huge,'assertions':'PASS','elapsed_seconds':round(time.monotonic()-st,3)}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ('mixed_timing_example','separated_windows_example')},indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',default='pending_results.json');main(a.parse_args().out)
