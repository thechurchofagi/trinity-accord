#!/usr/bin/env python3
"""Exact verifier for the written coherent bucket cancellation theorem."""
import itertools,json,random,hashlib,time
from collections import defaultdict
from pathlib import Path
from verify_gray_reflection_graph import gray,counts,graph,optimize,order_and_scores

def check(a, full=False):
    n=len(a);N=1<<n
    s=[0]
    for v in a:s += [t+v for t in s]
    p=tuple(sorted(range(N),key=lambda x:(s[x],x)))
    w=tuple(N*v+(1<<j) for j,v in enumerate(a))
    assert order_and_scores(w)[0]==p
    q=len(set(s));g=graph(p,n)
    interior=defaultdict(int);boundary=defaultdict(int)
    triples=0
    for i in range(N):
        x,y,z=(p[(i+j)%N] for j in range(3))
        h,k=g['labels'][i],g['labels'][(i+1)%N]
        if h==k:continue
        key=tuple(sorted((h,k)))
        value=g['signs'][i]*g['signs'][(i+1)%N]
        if s[x]==s[y]==s[z]:
            interior[key]+=value;triples+=1
            m=max(h,k)
            if m<n-1:
                xx,yy,zz=(v^(1<<(m+1)) for v in (x,y,z))
            else:
                xx,yy,zz=(v^(N-1) for v in (z,y,x))
            positions={v:j for j,v in enumerate(p)} if full else None
            if full:
                at=positions[xx]
                assert p[at:at+3]==(xx,yy,zz)
                assert s[xx]==s[yy]==s[zz]
                hh=(xx^yy).bit_length()-1;kk=(yy^zz).bit_length()-1
                assert tuple(sorted((hh,kk)))==key
                prod=(1 if gray(yy)>gray(xx) else -1)*(1 if gray(zz)>gray(yy) else -1)
                assert prod==-value
        else:boundary[key]+=value
    assert all(v==0 for v in interior.values())
    assert tuple((h,k,v) for (h,k),v in sorted(boundary.items()) if v)==g['edges']
    assert g['W']<=2*q
    E,phi=optimize(g,n)
    minimum=(N+g['D']-E)//2
    assert minimum>=N//2-q
    if full:
        actual=min(counts(tuple(gray(x^z) for x in p))[1] for z in range(N))
        assert actual==minimum
    return {'n':n,'q':q,'W':g['W'],'interior_mixed_triples':triples,
            'minimum_C_over_signs':minimum}

def main():
    start=time.monotonic();records=[]
    for n in range(2,5):
        for a in itertools.product(range(1,5),repeat=n):
            records.append(check(a,True))
    rng=random.Random(202610030810)
    for n in range(5,13):
        for draw in range(30):
            a=tuple(rng.randrange(1,2*n+1) for j in range(n))
            records.append(check(a,False))
    result={'status':'PASS','vectors':len(records),
            'vertex_entries':sum(1<<r['n'] for r in records),
            'interior_mixed_triples':sum(r['interior_mixed_triples'] for r in records),
            'violations':0,'dimensions':[2,12],
            'deterministic_sha256':hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest(),
            'seconds':round(time.monotonic()-start,3),
            'scope':'Finite checks of the pairing and formula; all-dimensional coverage is the written proof.'}
    Path(__file__).with_name('coherent_bucket_cancellation_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
