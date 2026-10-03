#!/usr/bin/env python3
"""Conditional entropy with arbitrary frozen labels and a fixed root.

Exhaustive Q2/Q3 arbitrary vertex permutations, every frozen subset and
assignment, every active fresh state and every small-run threshold.
This audits the conditioned refinement of the existing entropy lemma.
"""
import hashlib,json,time
from itertools import permutations
from math import comb
from pathlib import Path
from fractions import Fraction
from verify_paired_sibling_ranks import rank

def audit(p,n):
    N=1<<n;Q=(1<<(n-1))-1;active=0;root=False
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1
        if h==n-1:root=True
        else:
            a=(1<<(n-1))-(1<<(n-h-1))+(x>>(h+2));active|=1<<a
    assert root
    words=[];trans=[];runs=[]
    for mask in range(1<<Q):
        rr=[rank(x,n,mask) for x in p];s=0
        for i,(x,y) in enumerate(zip(rr,rr[1:])):s|=int(y>x)<<i
        t=(s^(s>>1))&((1<<(N-2))-1)
        words.append(s);trans.append(t);runs.append(1+t.bit_count())
    groups=states=thresholds=0;maxq=0
    for frozen in range(1<<Q):
        fixed=[a for a in range(Q) if frozen>>a&1]
        fresh=[a for a in range(Q) if active>>a&1 and not frozen>>a&1]
        qf=len(fresh);maxq=max(maxq,qf)
        for assignment in range(1<<len(fixed)):
            base=sum((assignment>>j&1)<<a for j,a in enumerate(fixed))
            ids=[base|sum((choice>>j&1)<<a for j,a in enumerate(fresh)) for choice in range(1<<qf)]
            assert len({words[i] for i in ids})==len({trans[i] for i in ids})==1<<qf
            assert qf>=active.bit_count()-frozen.bit_count()
            total=0
            for K in range(1,N):
                total+=comb(N-2,K-1)
                assert sum(runs[i]<=K for i in ids)<=total
                thresholds+=1
            groups+=1;states+=len(ids)
    return groups,states,thresholds,maxq

def main():
    st=time.monotonic();stream=hashlib.sha256();rows=[]
    for n in [2,3]:
        contexts=groups=states=thresholds=0
        for p in permutations(range(1<<n)):
            r=audit(p,n);contexts+=1;groups+=r[0];states+=r[1];thresholds+=r[2]
            stream.update(json.dumps((n,p,r)).encode())
        rows.append({'n':n,'all_arbitrary_vertex_permutations':contexts,'frozen_contexts':groups,
            'fresh_states':states,'all_threshold_checks':thresholds})
    # Exact rational bases. H2(1/128)<17/256 uses log2>2/3 and
    # log(1+1/127)<1/127. Earlier proofs establish log3<9/8.
    assert Fraction(7,128)+Fraction(3,256)==Fraction(17,256)
    assert Fraction(9*13*13,8)+10-Fraction(5*(1<<13),128)<0
    assert 1+Fraction(9*15*15,8)-Fraction(1<<15,128)<0
    assert Fraction(9,8)+Fraction(9*18*18,8)-Fraction(1<<18,512)<0
    assert Fraction(7,384)>Fraction(1,128)>Fraction(1,512)
    # Rejected shortcut: without fixing a comparison phase, complement
    # every label AND the root. All signs flip; transition words coincide.
    p=(0,1,2,3);phase_free=[]
    for top in [0,1]:
        for mask in [0,1]:
            rr=[rank(x,2,mask,top) for x in p]
            a=sum(int(y>x)<<i for i,(x,y) in enumerate(zip(rr,rr[1:])))
            phase_free.append((mask,top,a,(a^(a>>1))&3))
    assert len({r[-1] for r in phase_free})==2<4
    out={'status':'VERIFIED_FROZEN_PREFIX_CONDITIONAL_ENTROPY',
        'analytic_lemma':'With fixed root, any frozen label set F and ANY complete vertex permutation have active fresh qf=|raw non-top support minus F|. Conditional probability P(R<=K)<=2^(-qf)*sum(j=0..K-1,binom(N-2,j)); qf>=q-|F|. Fixed signs and transition words remain injective in active fresh labels.',
        'corollaries':'ANYn>=18 retaining fixed upper-five mask2 admits ONE rank simultaneously handling ALLq>=N/8 scans atR>N/128, ALLm0+m1>=N/8 scans atR>N/32, and ALLseparated five-core rows atR>=3N/8-1. More generally ANYparent in dimensionn-4 admits ONE4-bottom-level child with the first two guarantees forn>=18. Largeq-only with fixed15 labels already holds forn>=13; largeq andm0 with fixed core holds forn>=15.',
        'scope':'Refinement of inherited entropy and conditional mass lemmas, not a new entropy method. Original all-scan target remains OPEN. For the four-step theorem do not infer the same two-level guarantee at every intermediate dimension.',
        'audits':rows,'root_free_noninjectivity_certificate':phase_free,
        'audit_stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('frozen_prefix_entropy_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
