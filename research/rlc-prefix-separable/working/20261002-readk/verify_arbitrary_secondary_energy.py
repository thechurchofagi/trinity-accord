#!/usr/bin/env python3
"""Exact audit of the all-dimensional cardinality coupling obstruction."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import time
from verify_gray_reflection_graph import gray, graph, counts, energy
from verify_face_local_obstruction import subset_scores

def split_graph(p,n):
    jj=[defaultdict(int),defaultdict(int)];dd=[0,0];N=1<<n
    for i in range(N):
        a,b,c=p[i],p[(i+1)%N],p[(i+2)%N]
        h=(a^b).bit_length()-1;k=(b^c).bit_length()-1
        e=1 if gray(b)>gray(a) else -1
        f=1 if gray(c)>gray(b) else -1
        boundary=int(not(a.bit_count()==b.bit_count()==c.bit_count()))
        if h==k:
            assert e==-f
            dd[boundary]+=1
        else:jj[boundary][tuple(sorted((h,k)))]+=e*f
    return dd,[tuple((h,k,v) for (h,k),v in sorted(t.items()) if v) for t in jj]

def main():
    start=time.monotonic();digest=hashlib.sha256();rows=[];signed_scans=0
    core=(2,4,8,1)
    core_scores=subset_scores(core)
    layers=[tuple(sorted((x for x in range(16) if x.bit_count()==k),key=core_scores.__getitem__)) for k in range(5)]
    assert layers==[(0,),(8,1,2,4),(9,10,3,12,5,6),(11,13,14,7),(15,)]
    for n in range(4,19):
        N=1<<n;B=N;b=core+tuple(1<<j for j in range(4,n))
        weights=tuple(B+v for v in b);scores=subset_scores(weights)
        assert len(set(scores))==N
        p=tuple(sorted(range(N),key=scores.__getitem__))
        secondary=subset_scores(b)
        assert p==tuple(sorted(range(N),key=lambda x:(x.bit_count(),secondary[x])))
        L=1<<(n-4);edges=((1,2,2*L),);g=graph(p,n)
        assert g['D']==2*L+4 and g['W']==2*L and g['edges']==edges
        dd,jj=split_graph(p,n)
        assert dd==[2*L,4] and jj==[edges,()]
        groups=0;at=0
        while at<N:
            t=p[at]>>4;k=p[at].bit_count();end=at+1
            while end<N and p[end]>>4==t and p[end].bit_count()==k:end+=1
            assert tuple(x&15 for x in p[at:end])==layers[k-t.bit_count()]
            groups+=1;at=end
        assert groups==5*L
        reflections=range(N) if n<=9 else (0,1,3,N-1)
        lowC=N;lowR=N
        for z in reflections:
            signed=tuple(-v if z>>j&1 else v for j,v in enumerate(weights))
            actual_scores=subset_scores(signed)
            actual=tuple(sorted(range(N),key=actual_scores.__getitem__))
            assert actual==tuple(x^z for x in p)
            R,C,_=counts(tuple(map(gray,actual)))
            assert C==(N+g['D']-energy(edges,gray(z)))//2
            assert R==C-int(n==4)
            lowC=min(lowC,C);lowR=min(lowR,R);signed_scans+=1
            digest.update(json.dumps((n,z,R,C)).encode())
        assert lowC==N//2+2 and lowR==N//2+2-int(n==4)
        row={'n':n,'primary_buckets':n+1,'secondary':b,'weights':weights,
             'D':g['D'],'interior_D':dd[0],'boundary_D':dd[1],
             'edges':edges,'E_star':2*L,'minimum_C':N//2+2,
             'minimum_R':N//2+2-int(n==4),'signed_scans':len(reflections),
             'core_groups':groups,'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}
        rows.append(row);digest.update(json.dumps(row,sort_keys=True).encode())
    out={'state':'VERIFIED_ALL_DIMENSIONAL_ENERGY_OBSTRUCTION_PROOF_WITH_FINITE_STRESS',
         'theorem':'For n>=4, cardinality primary has q=n+1 but E*=2^(n-3), D=E*+4 and min C=2^(n-1)+2.',
         'dimensions':list(range(4,19)),'core_layers':layers,'records':rows,
         'signed_scans_independently_sorted':signed_scans,'violations':0,
         'verification_digest':digest.hexdigest(),
         'elapsed_seconds':round(time.monotonic()-start,3),
         'limitation':'The theorem excludes polynomial-energy cancellation extensions; it neither disproves half-density for this class nor solves M_n.'}
    Path(__file__).with_name('arbitrary_secondary_energy_verification.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
