#!/usr/bin/env python3
"""Exact seed and specified lifts of the coherent cardinality flux obstruction."""
import json,hashlib
from collections import defaultdict
from pathlib import Path
from verify_prefix_transport_defect import scores
from verify_gray_reflection_graph import graph,optimize,order_and_scores,gray,counts
SEED=(16,59,15,4,49,11,7)

def interior(p,s,g):
    K=defaultdict(int)
    for i in range(len(p)-2):
        if s[p[i]]==s[p[i+1]]==s[p[i+2]]:
            h,k=g['labels'][i],g['labels'][i+1]
            if h!=k:K[tuple(sorted((h,k)))]+=g['signs'][i]*g['signs'][i+1]
    return {key:v for key,v in K.items() if v}

def main():
    seed_s=scores((1,)*7);seed_u=scores(SEED)
    assert len(set(zip(seed_s,seed_u)))==128
    p=tuple(sorted(range(128),key=lambda x:(seed_s[x],seed_u[x])))
    g=graph(p,7);K=interior(p,seed_s,g)
    assert K=={(2,4):-4,(2,5):12,(4,5):-6}
    assert g['D']==30 and g['W']==22>16
    assert g['edges']==((2,4,-4),(2,5,12),(4,5,-6))
    seed_w=tuple(162+v for v in SEED)
    seed_signed=[]
    for z in range(128):
        pp=order_and_scores(tuple(-v if z>>j&1 else v for j,v in enumerate(seed_w)))[0]
        R,C,_=counts(tuple(map(gray,pp)))
        seed_signed.append((R,C))
    assert min(R for R,C in seed_signed)==min(C for R,C in seed_signed)==68
    rows=[]
    for n in range(7,16):
        copies=1<<(n-7)
        b=SEED+tuple(162*(1<<j) for j in range(n-7))
        L=162*copies
        assert sum(b)==L-1
        w=tuple(L+v for v in b)
        result=order_and_scores(w);assert result is not None
        p=result[0];s=scores((1,)*n)
        u=scores(b)
        assert p==tuple(sorted(range(1<<n),key=lambda x:(s[x],u[x])))
        gg=graph(p,n);KK=interior(p,s,gg)
        assert KK=={key:v*copies for key,v in K.items()}
        diagonal=sum(s[p[i]]==s[p[i+1]]==s[p[i+2]] and gg['labels'][i]==gg['labels'][i+1] for i in range(len(p)-2))
        assert diagonal==28*copies and gg['D']>=28*copies
        assert gg['W']<=22*copies+2*(n+1)
        J=dict(((h,k),v) for h,k,v in gg['edges'])
        assert abs(J.get((2,5),0)-12*copies)<=2*(n+1)
        assert gg['W']>=12*copies-2*(n+1)
        if n>=9:assert gg['W']>2*(n+1)
        E,phi=optimize(gg,n)
        assert ((1<<n)+gg['D']-E)//2 >= (1<<(n-1))+3*copies-(n+1)
        rows.append({'n':n,'q':n+1,'D':gg['D'],'W':gg['W'],'E':E,
                     'interior_J25':KK[(2,5)],'total_J25':J.get((2,5),0),
                     'minimum_C':((1<<n)+gg['D']-E)//2})
    receipt={'status':'PASS','seed_secondary':SEED,'seed_actual_weights':[162+v for v in SEED],
             'seed_interior_edges':[[h,k,v] for (h,k),v in sorted(K.items())],
             'seed_interior_D':28,'seed_signs_sorted':128,'seed_min_R_and_C':68,
             'seed_joint_score_sha256':hashlib.sha256(json.dumps(list(zip(seed_s,seed_u))).encode()).hexdigest(),
             'rows':rows,'violations':0,
             'scope':'Proves failure of W=O(q) for arbitrary coherent secondary orders, not failure of positive run density.'}
    receipt['deterministic_sha256']=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('cardinality_prefix_flux_verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
