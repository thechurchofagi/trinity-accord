#!/usr/bin/env python3
"""Independent exhaustive arrival/commit oracle. Does not import the analyzer.
Enumerates actual pending commit times, every conforming new-commit stream and
per-job repair. Then compares its maxima with a separately written closed form.
The claimed all-time peak theorem justifies using T+1 slots in the tiny grid.
"""
import argparse,itertools,json,time
from pathlib import Path

def simulate(old,pending,chosen,new,mu,ell):
    # Bare lists and remove-by-index; intentionally no analyzer helpers.
    jobs=list(old);peak=len(jobs);trace=[]
    for tick in range(len(new)):
        for _ in range(mu):
            matured=[(ready,idx) for idx,ready in enumerate(jobs) if ready<=tick]
            if not matured:break
            _,idx=min(matured);jobs.pop(idx)
        for i,(left,right,delay) in enumerate(pending):
            if chosen[i]==tick:jobs.append(tick+delay)
        jobs.extend([tick+ell]*new[tick]);trace.append(len(jobs));peak=max(peak,len(jobs))
    return peak,trace

def allowable(H,b,r):
    values=[]
    for a in itertools.product(range(b+1),repeat=H):
        if all(sum(a[i:j])<=b+r*(j-i-1) for i in range(H) for j in range(i+1,H+1)):values.append(a)
    return values

def main(out):
    start=time.monotonic();profiles=0;trajectories=0
    kinds=[(u,v,L) for u in range(3) for v in range(u,3) for L in (1,2)]
    pend=[()]+[(x,) for x in kinds]+list(itertools.combinations_with_replacement(kinds,2))
    oldlist=[(),(0,),(2,),(0,2)]
    configs=[(1,0,0,1),(1,0,1,1),(1,1,1,1),(2,1,1,2),(2,1,2,2),(2,2,2,3)]
    streams={(b,r):allowable(3,b,r) for b,r,_,_ in configs}
    for old,P,ps in itertools.product(oldlist,pend,configs):
        b,r,mu,ell=ps;peak=len(old);best=None
        for choices in itertools.product(*(range(u,v+1) for u,v,L in P)):
            for a in streams[b,r]:
                value,trace=simulate(old,P,choices,a,mu,ell);trajectories+=1
                if value>peak:peak=value;best={'commit_times':choices,'new':a,'trace':trace}
        T=max([ell-1,0]+[u for u,v,L in P]);q=len(old);prediction=q
        for t in range(T+1):
            prediction=max(prediction,q+b+r*t+sum(u<=t for u,v,L in P)-mu*(t+1))
            for s in range(t+1):
                K=sum(u<=t and v+L>s for u,v,L in P)
                prediction=max(prediction,q-sum(v<=s for v in old)+b+r*(t-max(0,s-ell+1))+K-mu*(t-s))
        assert prediction==peak,(old,P,ps,prediction,peak,best)
        profiles+=1
    # Full min/max endpoint heuristics, using every admissible new stream.
    P=((0,3,1),(1,1,1));streams4=allowable(4,1,0)
    early=max(simulate((),P,(0,1),a,1,1)[0] for a in streams4)
    late=max(simulate((),P,(3,1),a,1,1)[0] for a in streams4)
    all_schedules=[(c,a,simulate((),P,c,a,1,1)) for c in itertools.product(range(4),(1,)) for a in streams4]
    worst=max(all_schedules,key=lambda x:x[2][0])
    assert early==late==2 and worst[2][0]==3
    # Coupled schedules forbid coincidence: a rectangular relaxation is safe,
    # but NOT exact for this stricter semantics.
    serial=max(simulate((),P,c,a,1,1)[0] for c,a,_ in all_schedules if c[0]!=c[1])
    assert serial==2
    # Asymptotic timing-information separation, independently simulated.
    factors=[]
    for p in range(1,21):
        P=tuple((i,i,1) for i in range(p));actual=0
        for burst in range(p+2):
            a=[0]*(p+3);a[burst]=1
            actual=max(actual,simulate((),P,tuple(range(p)),a,1,1)[0])
        assert actual==2
        broad=tuple((0,p-1,1) for i in range(p));a=[1]+[0]*(p+2)
        assert simulate((),broad,tuple([0]*p),a,1,1)[0]==p+1
        factors.append({'tickets':p,'exact_fixed_schedule_headroom':2,'timing_erased_headroom':p+1})
    result={'version':'ASI-CC-v1.3.0','method':'Full product of eligible commit times and every admissible3-slot fresh trace; independent per-job simulator, no analyzer import',
       'profiles':profiles,'complete_trajectories':trajectories,'maximum_earliest_commit':2,'maximum_new_delay':3,
       'all_maxima_match':True,'endpoint_heuristic_counterexample':{'all_earliest_max':early,'all_latest_max':late,'true_max':worst[2][0],'witness':worst},
       'coupled_schedule_negative_control':{'no_two_pending_at_same_slot_max':serial,'independent_interval_relaxation_max':3},
       'timing_information_family':factors,'elapsed_seconds':round(time.monotonic()-start,3),'assertions':'PASS'}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='timing_information_family'},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='oracle_results.json');main(p.parse_args().out)
