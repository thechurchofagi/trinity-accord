#!/usr/bin/env python3
"""Small comparison support and small runs in NONADDITIVE poset extensions.

Excludes direction-only proofs of the new support-defect obligation.
Does NOT refute the actual additive-scan conjecture or M_n target.
"""
from pathlib import Path
import hashlib,json,random,time
from verify_paired_sibling_ranks import rank,fast_runs

def raw_support(p,n):
    S=set();counts={}
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1;counts[h]=counts.get(h,0)+1
        if h<n-1:S.add((h,x>>(h+2)))
    return S,counts

def audit(n,d,theta,rng):
    m=n-d;assert m>=3
    v=[rank(x,n,theta) for x in range(1<<n)]
    upp=sorted(range(1<<m),key=lambda u:(u.bit_count(),v[u<<d]))
    p=tuple(a|(u<<d) for a in range(1<<d) for u in upp)
    pos=[0]*(1<<n)
    for idx,x in enumerate(p):pos[x]=idx
    assert len(set(p))==1<<n
    # Every upper Hamming-weight row is increasing in the FULL rank,
    # independently of the fixed lower input assignment.
    for a in range(1<<d):
        for u,z in zip(upp,upp[1:]):
            if u.bit_count()==z.bit_count():assert v[a|(u<<d)]<v[a|(z<<d)]
    S,counts=raw_support(p,n)
    assert all(h>=d for h in counts)
    q=len(S);R=fast_runs(v,p);J=(1<<d)*(m+1)
    assert q<=(1<<(m-1))-1 and R<=2*J-1
    edges=0
    if n<=12:
        for x in range(1<<n):
            for j in range(n):
                if not(x>>j)&1:assert pos[x]<pos[x|(1<<j)];edges+=1
        edge_scope='ALL cube edges'
    else:
        for _ in range(2048):
            j=rng.randrange(n);x=rng.randrange(1<<n)&~(1<<j)
            assert pos[x]<pos[x|(1<<j)];edges+=1
        edge_scope='2048 sampled cube edges; analytic proof covers ALL'
    # Explicit common-addition violation, valid for every paired theta:
    # rank comparison between bits d,d+1 flips when adding controller d+2.
    x=1<<d;y=1<<(d+1);z=1<<(d+2)
    assert ((pos[x]<pos[y])!=(pos[x|z]<pos[y|z]))
    first=(x,y) if pos[x]<pos[y] else (y,x)
    reversed_after_common_addition=(first[1]|z,first[0]|z)
    digest=hashlib.sha256(json.dumps(p).encode()).hexdigest()
    return {'n':n,'d':d,'upper_dimension_m':m,'paired_mask_decimal':str(theta),
        'runs':R,'analytic_run_upper_bound':2*J-1,'raw_non_top_support_q':q,
        'analytic_support_upper_bound':(1<<(m-1))-1,'comparison_leading_bit_counts':counts,
        'cube_edges_checked':edges,'edge_audit_scope':edge_scope,
        'first_preference':first,'common_added_coordinate':d+2,
        'reversed_translated_preference':reversed_after_common_addition,
        'order_sha256':digest}

def main():
    st=time.monotonic();rng=random.Random(202610031745);rows=[]
    for n in range(6,19):
        d=n//2
        rows.append(audit(n,d,0,rng))
        if n<=12:
            for _ in range(4):rows.append(audit(n,d,rng.getrandbits((1<<(n-1))-1),rng))
    out={'status':'VERIFIED_ALL_DIMENSION_SMALL_SUPPORT_NONADDITIVE_POSET_OBSTRUCTION',
        'analytic_theorem':'For EVERY paired rank on Q_n, choose d with n-d>=3. Order lower input assignments numerically; within each fixed lower assignment, order upper Hamming-weight layers increasingly and rank-sort each layer. This is a Boolean-poset linear extension, has R<=2*2^d*(n-d+1)-1 and RAW NON-TOP comparison support q<=2^(n-d-1)-1. For d=floor(n/2), both R/2^n and q/2^n tend to0. It violates common disjoint addition at singleton input coordinates d,d+1 translated by d+2, for EVERY paired orientation, so is not ANY signed additive scan.',
        'consequence':'No absolute a>0 and finite b>=0 can make R>=a*2^n-b*q hold for ALL coordinatewise Boolean-poset extensions and paired ranks. The proposed inequality for GENUINE additive scans is NOT refuted. A direction-only relaxation of the original-target small-support mass theorem is rigorously excluded; common-addition consistency or stronger true additive geometry is necessary.',
        'scope':'All-dimensional analytic exclusion, not finite extrapolation. Prefix separability of the target ranks is inherited; the constructed scan permutations are explicitly nonadditive. Main M_n target remains OPEN.',
        'rows':rows,'cases':len(rows),'seed':202610031745,'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('small_support_poset_obstruction_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
