#!/usr/bin/env python3
"""Independent integer verification; no LP or search optimizer is imported."""
from pathlib import Path
import hashlib
import json
import time
from verify_face_local_obstruction import subset_scores
from verify_gray_reflection_graph import graph, gray, counts, energy
from verify_arbitrary_secondary_energy import split_graph

CORE=(108,106,105,102,110,126,32,170,0)
EDGES=((1,2,32),(1,3,32),(1,5,-4),(2,3,32),
       (3,5,-4),(3,6,4),(4,5,4),(5,7,4))

def main():
    start=time.monotonic();rows=[];digest=hashlib.sha256();scans=0
    assert sum(CORE)==859
    for n in range(9,19):
        m=n-9;L=1<<m;N=1<<n
        b=CORE+tuple(860*(1<<j) for j in range(m));B=sum(b)+1
        assert B==860*L
        w=tuple(B+v for v in b);s=subset_scores(w)
        assert len(set(s))==N
        p=tuple(sorted(range(N),key=s.__getitem__))
        beta=subset_scores(b)
        assert p==tuple(sorted(range(N),key=lambda x:(x.bit_count(),beta[x])))
        if n==9:
            margins=[beta[y]-beta[x] for x,y in zip(p,p[1:]) if x.bit_count()==y.bit_count()]
            assert len(margins)==502 and min(margins)==1
        expected=tuple((h,k,v*L) for h,k,v in EDGES)
        g=graph(p,n);dd,jj=split_graph(p,n)
        assert g['edges']==expected and g['D']==40*L+4 and g['W']==116*L
        assert dd==[40*L,4] and jj==[expected,()]
        assert energy(expected,78)==g['W']  # satisfies all edges -> global optimum
        assert gray(116)==78
        reflections=range(N) if n<=11 else (0,116,N-1)
        lowR=lowC=N
        for z in reflections:
            signed=tuple(-v if z>>j&1 else v for j,v in enumerate(w))
            sgn_scores=subset_scores(signed)
            actual=tuple(sorted(range(N),key=sgn_scores.__getitem__))
            assert actual==tuple(x^z for x in p)
            R,C,_=counts(tuple(map(gray,actual)))
            assert C==(N+g['D']-energy(expected,gray(z)))//2
            assert R==C-int(n==9)
            lowR=min(lowR,R);lowC=min(lowC,C);scans+=1
            digest.update(json.dumps((n,z,R,C)).encode())
        assert lowC==218*L+2 and lowR==218*L+2-int(n==9)
        row={'n':n,'B':B,'L':L,'secondary':b,'D':g['D'],'E_star':g['W'],
             'edges':expected,'minimum_R_C':[lowR,lowC],
             'attaining_signed_weights':tuple(-v if 116>>j&1 else v for j,v in enumerate(w)),
             'actual_signs_independently_sorted':len(reflections)}
        rows.append(row);digest.update(json.dumps(row,sort_keys=True).encode())
    out={'state':'VERIFIED_NINE_CORE_EXACT_ALL_DIMENSIONAL_FAMILY',
         'secondary_core':CORE,'limit_fraction':[109,256],'dimensions':list(range(9,19)),
         'records':rows,'independently_sorted_signs':scans,'violations':0,
         'verification_digest':digest.hexdigest(),'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'Exact family theorem and integer audit, not a nine-bit optimality claim, not improved unrestricted Gray upper 5/16, not a proof of M_n lower density.'}
    Path(__file__).with_name('larger_cardinality_core_extension_verification.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='records'}),flush=True)

if __name__=='__main__':main()
