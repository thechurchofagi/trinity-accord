#!/usr/bin/env python3
"""Actual paired translated faces lose a linear sum-of-local-turn budget.

No optimization solver is used. The formula and sign analysis prove all n;
complete integer orders/ranks independently audit n4..18.
"""
from pathlib import Path
from fractions import Fraction
import hashlib,json,time
from verify_gray_reflection_graph import order_and_scores,positive_chambers
from verify_paired_sibling_ranks import rank,fast_runs,separator_check

CORE=(4,6,8,9);SEED_MASK=6

def find_seed():
    cases=0
    for d in (2,3):
        for w in positive_chambers(d):
            order,scores=order_and_scores(w)
            cuts=sorted({Fraction(0)}|{Fraction(abs(a-b)) for a in scores for b in scores if a!=b})
            cuts.append(cuts[-1]+2)
            for lo,hi in zip(cuts,cuts[1:]):
                delta=(lo+hi)/2;ww=tuple(2*z for z in w)+(int(2*delta),)
                p,_=order_and_scores(ww);N=1<<d
                for theta in range(1<<((1<<d)-1)):
                    r=[rank(x,d+1,theta) for x in range(2*N)]
                    ra=fast_runs(r,order);rb=fast_runs(r,tuple(x+N for x in order));R=fast_runs(r,p);cases+=1
                    if R<ra+rb-1:
                        return {'checked_cases_before_first_failure':cases,'weights':ww,'mask':theta,
                                'R':R,'face_runs':[ra,rb],'score_word':p,'rank_word':[r[x] for x in p],
                                'coverage':'Exact intervals for fixed Q2/Q3 metric representatives and all masks until first failure; not complete Q4 metric space.'}
    raise AssertionError('seed not found')

def main():
    start=time.monotonic();seed=find_seed();assert tuple(seed['weights'])==CORE and seed['mask']==SEED_MASK
    corep,corescores=order_and_scores(CORE);base=[rank(u,4,SEED_MASK) for u in range(16)]
    signs=[1 if base[b]>base[a] else -1 for a,b in zip(corep,corep[1:])]
    assert fast_runs(base,corep)==8 and signs[0]==1 and signs[-1]==-1
    parts=[tuple(u for u in corep if u>>3==side) for side in (0,1)]
    assert parts[0][0]==0 and parts[0][-1]==7 and parts[1][0]==8 and parts[1][-1]==15
    assert all(fast_runs(base,p)==5 for p in parts)
    assert all(base[a]<base[b] for a in parts[0] for b in parts[1])
    rows=[]
    for n in range(4,19):
        m=n-4;T=1<<m;L=28;weights=tuple(L*(1<<j) for j in range(m))+CORE
        p,scores=order_and_scores(weights)
        score_by_vertex=dict(zip(p,scores))
        assert len(set(scores))==1<<n
        assert p==tuple((u<<m)|t for t in range(T) for u in corep)
        values=[]
        for x in range(1<<n):
            u=x>>m;t=x&(T-1)
            low=(t^(t>>1))^((T//2)*(u&1)) if m else 0
            values.append(T*base[u]+low)
        theta=SEED_MASK<<((1<<(n-1))-8)
        assert all(rank(x,n,theta)==values[x] for x in range(1<<n))
        assert len(set(values))==1<<n
        faces=[tuple(x for x in p if x>>(m+3)==side) for side in (0,1)]
        # Two faces are exact translates by weight9, including ALL interior events.
        assert faces[1]==tuple(x+(1<<(m+3)) for x in faces[0])
        assert all(score_by_vertex[b]-score_by_vertex[a]==9 for a,b in zip(faces[0],faces[1]))
        ra,rb=[fast_runs(values,f) for f in faces];R=fast_runs(values,p)
        assert (ra,rb,R)==(6*T-1,6*T-1,8*T)
        assert ra+rb-1-R==4*T-3==(1<<n)//4-3
        assert max(values[x] for x in faces[0])<min(values[x] for x in faces[1])
        out={'n':n,'T':T,'weights':weights,'face_coordinate':m+3,'translation':9,
             'full_R':R,'face_runs':[ra,rb],'proposed_lossless_budget':ra+rb-1,
             'strict_deficit':4*T-3,'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest(),
             'rank_sha256':hashlib.sha256(json.dumps(values).encode()).hexdigest()}
        if n<=6:out['strict_prefix_separator_checks']=separator_check(values,n,theta)
        rows.append(out)
    out={'status':'VERIFIED_ACTUAL_ALL_DIMENSION_INTERIOR_FACE_MERGE_LOSS',
         'analytic_statement':'For every n>=4, T=2^(n-4), actual positive generic additive scans and paired prefix-separable ranks have two identical translated (n-1)-faces with R_A=R_B=6T-1, but R_full=8T. The lost proposed budget (R_A+R_B-1)-R_full=4T-3=2^n/4-3.',
         'scope':'Excludes universal lossless interior-overlap compensation, even for actual paired restrictions and genuine common translations. Does NOT refute any constant-density target: actual fullR=2^(n-1). Does NOT assert least dimension or optimized local minima.',
         'seed_search':seed,'core_rank':base,'core_face_orders':parts,
         'proof':'Low coordinates have weights28*2^j, exceeding core span27, so the scan is Tcomplete core rows. The shifted paired mask6 has exact rank T*r4(u)+g_m(t) XOR ((T/2)*(u&1)). Core comparisons dominate low bits. Full core rows have7turns, endpoint signs+,- and descending rank-block row joins, each adding1turn: R=7T+1+(T-1)=8T. First face rows have4turns and endpoint signs+,+, but row joins are descending, adding2turns. Second face rows have4turns and endpoint signs-,-, but joins are ascending, also adding2turns. Therefore each faceR=4T+1+2(T-1)=6T-1. Both faces have identical score order, constant translation9 and disjoint contiguous rank intervals.',
         'actual_dimension_audits':rows,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('paired_interior_overlap_loss_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('actual_dimension_audits','proof','core_rank','core_face_orders','seed_search')}),flush=True)

if __name__=='__main__':main()
