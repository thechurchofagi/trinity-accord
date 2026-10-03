#!/usr/bin/env python3
"""Conditional fresh bottom-H extension, preserving ANY upper paired rank.

Checks means, exact influences and variance proxy, not independence of turns.
No claim that conditional existence combines with another selected family.
"""
from itertools import permutations
from collections import Counter
from pathlib import Path
import gzip,hashlib,json,time
from verify_gray_reflection_graph import positive_chambers,order_and_scores
from verify_paired_sibling_ranks import rank

def context(p,n,H,parent):
    Q=1<<(n-1);delta=Q-(1<<(n-H-1));offsets=[Q-(1<<(n-h-1)) for h in range(n-1)]
    labs=[];signs=[];levels=[]
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1;levels.append(h)
        v=Q-1 if h==n-1 else offsets[h]+(x>>(h+2));labs.append(v)
        signs.append(1 if (y^(y>>1))>(x^(x>>1)) else -1)
    m=sum(h<H for h in levels);C=Counter();mean2=2
    for a,b,s,t in zip(labs,labs[1:],signs,signs[1:]):
        if a==b:assert s!=t;mean2+=2
        elif a<delta or b<delta:
            mean2+=1
            if a<delta:C[a]+=1
            if b<delta:C[b]+=1
        else:
            aa=1 if a==Q-1 else -1 if parent>>(a-delta)&1 else 1
            bb=1 if b==Q-1 else -1 if parent>>(b-delta)&1 else 1
            mean2+=2*int(s*t*aa*bb<0)
    for a,k in C.items():
        h=next(h for h in range(H) if offsets[h]<=a<offsets[h]+(1<<(n-h-2)))
        assert k<=1<<(h+2)
    proxy=sum(k*k for k in C.values());assert sum(C.values())<=2*m
    assert proxy<= (1<<(H+2))*m and mean2>=m
    # Exhaust every fresh assignment, with exact mean and max influence.
    vals=[];ranks=[]
    for mask in range(1<<delta):
        full=(parent<<delta)|mask
        rr=[rank(x,n,full) for x in range(1<<n)]
        a=[rr[y]>rr[x] for x,y in zip(p,p[1:])]
        R=1+sum(s!=t for s,t in zip(a,a[1:]));vals.append(R)
    assert 2*sum(vals)==mean2*len(vals)
    for a in range(delta):
        assert max(abs(vals[t]-vals[t^(1<<a)]) for t in range(1<<delta))<=C[a]
    # Reuse the already computed full fresh table to condition on EVERY
    # other level, auditing the stronger affine single-level formula.
    for h in range(H):
        group=list(range(offsets[h],offsets[h]+(1<<(n-h-2))))
        outside=[a for a in range(delta) if a not in group]
        mh=sum(j==h for j in levels);kh=Counter();Dh=0
        for a,b in zip(labs,labs[1:]):
            if a==b and a in group:Dh+=1
            elif a!=b:
                if a in group:kh[a]+=1
                if b in group:kh[b]+=1
        eh=int(levels[0]==h)+int(levels[-1]==h)
        assert sum(kh.values())==2*mh-2*Dh-eh
        assert all(k<=1<<(h+2) for k in kh.values())
        for fixed in range(1<<len(outside)):
            fixedmask=sum((fixed>>i&1)<<a for i,a in enumerate(outside))
            ids=[fixedmask|sum((choice>>i&1)<<a for i,a in enumerate(group)) for choice in range(1<<len(group))]
            assert sum(vals[t] for t in ids)>=mh*len(ids)
            diffs=[]
            for a in group:
                A=vals[fixedmask]-vals[fixedmask|(1<<a)]
                assert all(vals[t]-vals[t|(1<<a)]==A for t in ids if not t>>a&1)
                assert abs(A)<=kh[a];diffs.append(A)
            assert sum(A*A for A in diffs)<=(1<<(h+3))*mh
    return {'m':m,'mean_twice':mean2,'proxy':proxy,'states':len(vals),
        'fresh_variables':delta,'active_fresh_variables':len(C),
        'minimum':min(vals),'maximum':max(vals),'sum':sum(vals)}

def main():
    st=time.monotonic();rows=[];digest=hashlib.sha256();contexts=states=0
    for n in range(2,5):
        for H in range(2,n):
            parents=range(1<<((1<<(n-H-1))-1))
            for w in positive_chambers(n):
                P=order_and_scores(w)[0]
                for z in range(1<<n):
                    p=tuple(x^z for x in P)
                    for parent in parents:
                        r=context(p,n,H,parent);contexts+=1;states+=r['states']
                        digest.update(json.dumps((n,H,w,z,parent,r),sort_keys=True).encode())
            rows.append({'n':n,'H':H,'all_signed_chambers':len(positive_chambers(n))*(1<<n),
                'parent_masks':len(parents)})
    arbitrary=0
    for p in permutations(range(8)):
        r=context(p,3,2,0);arbitrary+=1
        digest.update(json.dumps((p,r),sort_keys=True).encode())
    # Explicit all-n union-bound base for H=2, delta=1/8.
    assert (1<<19)*8>1024*9*19*19
    # Two-level conditional union is sharper: log2<1, log3<9/8.
    assert (1<<18)*8>512*(9*18*18+8)
    for H in range(2,33):
        n0=2*H+15
        assert (1<<n0)*8>(1<<(H+8))*9*n0*n0
    out={'status':'VERIFIED_CONDITIONAL_FRESH_BOTTOM_BLOCK_EXTENSION',
        'analytic_theorem':'For ANY fixed upper paired parent and ANY permutation, independently randomizing only bottom H layers gives E R>=m_low/2, per-variable affected-turn count<=2^(h+2), sum influences squared<=2^(H+2)*m_low. McDiarmid implies P(R<=m_low/4)<=exp(-m_low/2^(H+5)). Conditioning on all other levels, each level h separately has affine independent costs, E R>=m_h, sum two-state differences squared<=2^(h+3)*m_h and P(R<=m_h/2)<=exp(-m_h/2^(h+4)). H=2,n>=18: ONE child preserving ANY parent satisfies R>N/32 for EVERY generic signed additive sweep with at leastN/8 comparisons leading in levels0 or1. No independence-of-turn assumption.',
        'scope':'H=1 conditional result belongs to concurrent master55 and is stronger than the generic block estimate; it is credited and not reclaimed. This general-H extension does not prove full feasible-prefix extendability, does not cover all low-mass scans and is not claimed compatible with a separately selected large-q rank.',
        'signed_chamber_parent_contexts':contexts,'fresh_states_checked':states,
        'all_arbitrary_q3_permutations_H2':arbitrary,'rows':rows,
        'audit_stream_sha256':digest.hexdigest(),'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('bottom_block_extension_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
