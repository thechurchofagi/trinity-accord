#!/usr/bin/env python3
"""Exact all-dimensional cardinality half-density counterexample audit."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import time
from verify_face_local_obstruction import subset_scores
from verify_gray_reflection_graph import graph, gray, counts, optimize, energy
from probe_arbitrary_coherent_secondary import exact_gray_spin_optimizer
from verify_arbitrary_secondary_energy import split_graph

CORE=(4,6,3,0,8)

def primary_order(b):
    scores=subset_scores(b);N=1<<len(b)
    for k in range(len(b)+1):
        vals=[scores[x] for x in range(N) if x.bit_count()==k]
        assert len(set(vals))==len(vals)
    return tuple(sorted(range(N),key=lambda x:(x.bit_count(),scores[x])))

def main():
    start=time.monotonic();digest=hashlib.sha256();rows=[];scans=0
    cp=primary_order(CORE);cD,cJ=split_graph(cp,5)
    core_edges=((1,2,-2),(1,3,-2),(2,3,2))
    assert cD[0]==2 and cJ[0]==core_edges
    core_layers=[tuple(x for x in cp if x.bit_count()==k) for k in range(6)]
    for n in range(5,19):
        m=n-5;L=1<<m;N=1<<n
        b=CORE+tuple(32*(1<<j) for j in range(m));B=sum(b)+1
        assert B==32*L-10
        w=tuple(B+v for v in b);p=primary_order(b)
        actual_scores=subset_scores(w)
        assert len(set(actual_scores))==N
        assert p==tuple(sorted(range(N),key=actual_scores.__getitem__))
        g=graph(p,n);D,J=split_graph(p,n)
        expected=tuple((h,k,L*v) for h,k,v in core_edges)
        assert g['edges']==expected and g['D']==2*L+4 and g['W']==6*L
        assert D==[2*L,4] and J==[expected,()]
        E,mask=exact_gray_spin_optimizer(g,n)
        assert E==6*L and energy(expected,gray(3))==E
        reflections=range(N) if n<=10 else (0,3,7,N-1)
        minR=minC=N
        for z in reflections:
            signed=tuple(-v if z>>j&1 else v for j,v in enumerate(w))
            signed_scores=subset_scores(signed)
            actual=tuple(sorted(range(N),key=signed_scores.__getitem__))
            assert actual==tuple(x^z for x in p)
            R,C,_=counts(tuple(map(gray,actual)))
            assert R==C and C==(N+g['D']-energy(expected,gray(z)))//2
            minR=min(minR,R);minC=min(minC,C);scans+=1
            digest.update(json.dumps((n,z,R,C)).encode())
        assert minR==minC==14*L+2
        signed_attainer=tuple(-v if j<2 else v for j,v in enumerate(w))
        row={'n':n,'primary_buckets':n+1,'secondary':b,'B':B,
             'attaining_signed_weights':signed_attainer,'D':g['D'],
             'edges':expected,'E_star':E,'net_energy':E-g['D'],
             'minimum_R_C':[minR,minC],'independently_sorted_signs':len(reflections)}
        rows.append(row);digest.update(json.dumps(row,sort_keys=True).encode())

    # General core reduction is stressed without relying on the special
    # family's exact boundary cancellation.
    general=[]
    for base in ((2,4,8,1),CORE,(0,3,5,6,7),(0,3,8,19,41,84)):
        k=len(base);basep=primary_order(base)
        dd,jj=split_graph(basep,k);di=dd[0];ji=jj[0]
        assert all(v<k-1 for u,v,c in ji)
        ei,_=optimize({'edges':ji,'W':sum(abs(c) for u,v,c in ji)},k)
        A=sum(base)+1
        for m in range(9):
            n=k+m;L=1<<m;b=base+tuple(A*(1<<j) for j in range(m))
            p=primary_order(b);g=graph(p,n);dd,jj=split_graph(p,n)
            assert dd[0]==L*di
            assert jj[0]==tuple((u,v,L*c) for u,v,c in ji)
            en,_=exact_gray_spin_optimizer(g,n)
            assert 0<=g['D']-L*di<=2*(n+1)
            assert abs(en-L*ei)<=2*(n+1)
            cm=((1<<n)+g['D']-en)//2
            assert abs(2*cm-L*((1<<k)+di-ei))<=4*(n+1)
            row={'base':base,'n':n,'m':m,'D_int':di,'E_int':ei,
                 'D_n':g['D'],'E_n':en,'minimum_C':cm,
                 'limiting_density_numerator':(1<<k)+di-ei,
                 'limiting_density_denominator':1<<(k+1)}
            general.append(row);digest.update(json.dumps(row,sort_keys=True).encode())
    out={'state':'VERIFIED_ALL_DIMENSIONAL_CARDINALITY_HALF_DENSITY_COUNTEREXAMPLE',
         'core_secondary':CORE,'core_layers':core_layers,'core_interior_D_J':[2,core_edges],
         'exact_family':rows,'general_core_extension_checks':general,
         'independently_sorted_signed_scans':scans,'violations':0,
         'verification_digest':digest.hexdigest(),
         'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'Refutes half density for arbitrary coherent secondary cardinality scans, not positive constant density for this class or M_n; unrestricted Gray upper 5/16 is already smaller.'}
    Path(__file__).with_name('cardinality_half_density_verification.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('exact_family','general_core_extension_checks','core_layers')}),flush=True)

if __name__=='__main__':main()
