#!/usr/bin/env python3
"""Exact controller penalty and independent direct rank exhaustion."""
from pathlib import Path
import gzip,hashlib,json,time
import numpy as np
from probe_paired_quartet_controller_walls import costs
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs,separator_check
from paired_sibling_ancestor_optimizer import optimize

def potential(w,upper_mask):
    n=len(w);d=n-2;F=1<<d;upper=w[2:]
    offsets=[sum(upper[j]*((f>>j)&1) for j in range(d)) for f in range(F)]
    B=[rank(f,d,upper_mask) for f in range(F)]
    r,p,masks,word,constant,C=costs(offsets,w[0],w[1],B,return_costs=True)
    A=[[min(C[f][t*2],C[f][t*2+1]) for t in (0,1)] for f in range(F)]
    delta=[z[1]-z[0] for z in A];penalties=[]
    exceptions=set()
    for u,v in ((word[0],word[1]),(word[-2],word[-1])):
        if u[1]==v[1]:exceptions.add(u[1])
    assert all(abs(v)<=4 for v in delta)
    assert all(v%2==0 for f,v in enumerate(delta) if f not in exceptions)
    for f in range(0,F,2):
        e,o=delta[f:f+2]
        pen=min(abs(e),abs(o)) if e*o>0 else 0
        exact=min(A[f][0]+A[f+1][1],A[f][1]+A[f+1][0])-min(A[f])-min(A[f+1])
        assert pen==exact;penalties.append(pen)
    assert p==r+sum(penalties)
    fullmask=sum((masks[f]&1)<<f for f in range(F))
    for prefix in range(F//2):
        theta=(masks[2*prefix]>>1)&1
        assert ((masks[2*prefix+1]>>1)&1)==1-theta
        fullmask|=theta<<(F+prefix)
    fullmask|=upper_mask<<(F+F//2)
    scan=order_and_scores(w)[0];values=[rank(x,n,fullmask) for x in range(1<<n)]
    assert sorted(values)==list(range(1<<n)) and fast_runs(values,scan)==p
    return {'weights':w,'n':n,'upper_mask':upper_mask,'upper_rank':B,'constant_cross_turn_cost':constant,
            'face_four_costs':C,'face_conditional_costs':A,'face_biases':delta,
            'possible_parity_exception_faces':sorted(exceptions),
            'sibling_pair_penalties':penalties,'relaxed_minimum':r,'paired_minimum':p,
            'attaining_full_mask':fullmask,'attaining_local_masks':masks,
            'actual_score_order':scan,'actual_rank_sequence':[values[x] for x in scan]}

def direct_lower_exhaustion(w,upper_mask,expected):
    n=len(w);F=1<<(n-2);lower_bits=F+F//2
    states=np.arange(1<<lower_bits,dtype=np.int64)|(upper_mask<<lower_bits)
    p=order_and_scores(w)[0];prev=None;turns=np.zeros(len(states),dtype=np.int64)
    def ranks(x):
        val=np.full(len(states),((x>>(n-1))&1)<<(n-1),dtype=np.int64);offset=0
        for h in range(n-1):
            u=offset+(x>>(h+2));val|=(((x>>h)^(x>>(h+1))^(states>>u))&1)<<h
            offset+=1<<(n-h-2)
        return val
    last=ranks(p[0])
    for x in p[1:]:
        now=ranks(x);sg=now>last
        if prev is not None:turns+=(sg!=prev)
        prev=sg;last=now
    assert int(turns.min())+1==expected
    return {'lower_orientation_states':len(states),'exact_direct_minimum':int(turns.min())+1}

def main():
    start=time.monotonic();here=Path(__file__).parent
    pressure=json.loads(gzip.decompress((here/'paired_quartet_controller_wall_pressure.json.gz').read_bytes()))
    cases=[]
    for z in pressure['all_failures']:
        out=potential(tuple(z['weights']),z['upper_mask'])
        assert (out['relaxed_minimum'],out['paired_minimum'])==(z['relaxed_minimum'],z['paired_minimum']);cases.append(out)
    seed=potential((33,1,4,8,16),1);assert (seed['relaxed_minimum'],seed['paired_minimum'])==(5,12)
    independent=direct_lower_exhaustion(tuple(seed['weights']),1,12)
    r=[rank(x,5,seed['attaining_full_mask']) for x in range(32)]
    prefix_checks=separator_check(r,5,seed['attaining_full_mask'])
    # Independently minimize over upper masks too, comparing with the full
    # previously audited ancestor optimizer and a direct attaining rank.
    allupper=[potential(tuple(seed['weights']),mask) for mask in range(8)]
    globalmin=min(z['paired_minimum'] for z in allupper)
    g=linear_graph(order_and_scores(tuple(seed['weights']))[0],5);op=optimize(g,5)
    assert globalmin==1+g['D']+g['K']+(g['W']-op['E_max'])//2
    out={'status':'VERIFIED_EXACT_PAIRED_CONTROLLER_PENALTY_IDENTITY','analytic_statement':'For any face-event interleaving, fixed upper rank, and paired lower controller, R_min=R_relaxed+sum_g 1[Delta_(2g)*Delta_(2g+1)>0]*min(abs(Delta_(2g)),abs(Delta_(2g+1))), Delta_f=A_f(1)-A_f(0).',
         'scope':'An exact all-dimensional two-coordinate reduction, not a bound on the sum uniform over genuine scans. Standard finite-state elimination is inherited; the explicit controller-deficit bookkeeping is the research increment.',
         'seed':seed,'independent_direct_lower_exhaustion':independent,'strict_prefix_separator_checks':prefix_checks,
         'seed_minimum_over_all_upper_masks':globalmin,'independent_full_ancestor_optimizer':op,
         'all86_relaxed_failure_controller_cases':cases,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    (here/'paired_quartet_controller_potential_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('seed','all86_relaxed_failure_controller_cases','independent_full_ancestor_optimizer')}),flush=True)
    print(json.dumps({k:seed[k] for k in ('relaxed_minimum','paired_minimum','face_conditional_costs','face_biases','sibling_pair_penalties')}),flush=True)

if __name__=='__main__':main()
