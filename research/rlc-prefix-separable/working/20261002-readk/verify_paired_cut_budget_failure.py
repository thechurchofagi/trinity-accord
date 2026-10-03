#!/usr/bin/env python3
"""Exact all-dimension formula audits; analytic proof is in companion note."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,time
from verify_gray_reflection_graph import order_and_scores,positive_chambers
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs
from paired_sibling_ancestor_optimizer import optimize,layout
from paired_antipodal_half_graph import split,integer_cut

BASE=(1,14,4,8,16)
BASE_CYCLES=((14,1,12,2),(14,6,13,5),(14,0,15,7))

def offsets(n):return [(1<<(n-1))-(1<<(n-h-1)) for h in range(n-1)]

def audit(n):
    N=1<<n;L=1<<(n-5);w=list(BASE)
    while len(w)<n:w.append(sum(w)+1)
    p,scores=order_and_scores(w);base_p=order_and_scores(BASE)[0]
    assert p==tuple((row<<5)|x for row in range(L) for x in base_p)
    g=linear_graph(p,n);s=split(g,n);c=integer_cut(s['edges'],s['root'],s['top'])
    assert (g['D'],g['K'],g['W'],c['value'])==(0,6*L,20*L-2,1)
    old=offsets(5)+[15];new=offsets(n)
    def embed(u,row):
        if u==15:return 15 if n==5 else new[4]+(row>>1)
        h=next(h for h in range(4) if old[h]<=u<old[h+1])
        return new[h]+(row<<(3-h))+(u-old[h])
    J={(a,b):v for a,b,v in g['edges']};loads=defaultdict(int);cycles=[]
    for row in range(L):
        for cyc in BASE_CYCLES:
            z=[embed(u,row) for u in cyc];assert len(set(z))==4
            product=1
            for a,b in zip(z,z[1:]+z[:1]):
                key=tuple(sorted((a,b)));product*=1 if J[key]>0 else -1;loads[key]+=1
            assert product==-1;cycles.append(z)
    assert len(cycles)==3*L and all(v<=abs(J[key]) for key,v in loads.items())
    digest=hashlib.sha256(json.dumps((cycles,sorted(loads.items())),separators=(',',':')).encode()).hexdigest()
    result={'n':n,'weights':w,'copies':L,'D':g['D'],'K':g['K'],'W':g['W'],'half_cut':1,
            'cut_only_budget':6*L+1,'quarter_budget':N//4,
            'cut_only_R_bound':6*L+2,'internal_cycle_packing':3*L,
            'all_rank_internal_cycle_R_bound':9*L+1,'packing_digest':digest,
            'cut_shore_count':len(c['source_shore']),
            'cut_shore_sha256':hashlib.sha256(json.dumps(c['source_shore']).encode()).hexdigest(),
            'flow':c['signed_flows']}
    assert result['cut_only_budget']<result['quarter_budget']
    if n<=8:result.update(cycles=cycles,cycle_loads=[(a,b,v) for (a,b),v in sorted(loads.items())],graph_edges=g['edges'],full_cut=c)
    if n<=12:
        z=optimize(g,n);phi=(g['W']-z['E_max'])//2;R=1+g['D']+g['K']+phi
        assert phi>=3*L
        assert R==fast_runs([rank(x,n,z['mask']) for x in range(N)],p)
        result.update(exact_optimum=z,exact_phi=phi,exact_R=R)
        if n==5:
            assert phi==3 and R==10
            mask=3128
            assert sum(v*(-1 if ((mask>>a)^(mask>>b))&1 else 1) for a,b,v in g['edges'])==g['W']-2*len(cycles)
            result['independent_exact_attaining_mask']=mask
    return result

def main():
    start=time.monotonic();rows=[];dig=hashlib.sha256();small=[]
    for n in range(2,5):
        count=0;minimum=None;small_digest=hashlib.sha256()
        for positive in positive_chambers(n):
            for reflection in range(1<<n):
                w=[-v if (reflection>>j)&1 else v for j,v in enumerate(positive)]
                g=linear_graph(order_and_scores(w)[0],n);s=split(g,n)
                cut=integer_cut(s['edges'],s['root'],s['top'])['value'];budget=g['D']+g['K']+cut
                assert budget>=(1<<n)//4
                small_digest.update(json.dumps((w,g['D'],g['K'],cut)).encode());count+=1
                if minimum is None or budget<minimum:minimum=budget
        small.append({'n':n,'all_signed_chambers':count,'minimum_cut_only_budget':minimum,'digest':small_digest.hexdigest()})
    for n in range(5,19):
        z=audit(n);rows.append(z);dig.update(json.dumps(z,sort_keys=True).encode())
        print(json.dumps({k:z[k] for k in ('n','D','K','W','half_cut','cut_only_budget','quarter_budget','internal_cycle_packing','all_rank_internal_cycle_R_bound')}),flush=True)
    out={'status':'VERIFIED_ALL_DIMENSION_CUT_ONLY_BUDGET_EXCLUSION_AND_INTERNAL_BLOCK_BOUND',
         'all_dimension_formula':'For n>=5 and base weights (1,14,4,8,16), append each new coefficient as 1+sum(previous). Let L=2^(n-5). Then D=0,K=6L,W=20L-2,lambda=1, so D+K+lambda=6L+1<N/4. Three disjoint core cycles per block give phi>=3L and every paired rank has R>=9L+1.',
         'scope':'Not a counterexample to the primary M_n or universal paired quarter conjectures. Excludes root-to-top cut packing as the sole extra quantitative term. The internal block theorem holds for arbitrary slow-row orders preserving these core blocks.',
         'dimension_minimality_complete_chambers':small,
         'rows':rows,'violations':0,'seconds':time.monotonic()-start,'audit_sha256':dig.hexdigest()}
    Path(__file__).with_name('paired_cut_budget_failure_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
