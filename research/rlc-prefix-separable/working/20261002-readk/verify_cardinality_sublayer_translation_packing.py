#!/usr/bin/env python3
"""Exact all-n packing in fragmented cardinality sublayers.

No local finite run minimum is needed: one common-translation obligation
per five-face works for every paired mask, with disjoint full-turn supports.
"""
from pathlib import Path
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import rank,fast_runs

def core_ok(b):
    scores=[sum(b[j]*((x>>j)&1) for j in range(5)) for x in range(32)]
    return all(len({scores[x] for x in range(32) if x.bit_count()==r})==sum(x.bit_count()==r for x in range(32)) for r in range(6))

def packing(b):
    n=len(b);N=1<<n;S=sum(abs(x) for x in b[:5]);B=2*sum(abs(x) for x in b)+1
    assert core_ok(b[:5]) and (b[4]>max(b[1:3]) or b[4]<min(b[1:3]))
    outerp,os=order_and_scores(b[5:]);assert len(os)==1 or min(t-s for s,t in zip(os,os[1:]))>S
    w=tuple(B+x for x in b);p,scores=order_and_scores(w)
    assert all(x.bit_count()<=y.bit_count() for x,y in zip(p,p[1:]))
    pos=[0]*N
    for i,x in enumerate(p):pos[x]=i
    points=tuple(sorted((3,5,17),key=lambda x:sum(b[j]*((x>>j)&1) for j in range(5))))
    assert sorted(((points[0]^points[1]).bit_length()-1,(points[1]^points[2]).bit_length()-1))==[2,4]
    supports=[];owners={};digest=hashlib.sha256()
    for f in range(1<<(n-5)):
        t=tuple((f<<5)|x for x in points);q=tuple(x^8 for x in t)
        ix=[pos[x] for x in t];iy=[pos[x] for x in q]
        assert ix[0]<ix[1]<ix[2] and iy[0]<iy[1]<iy[2]
        support=list(range(ix[0]+1,ix[2]))+list(range(iy[0]+1,iy[2]))
        assert len(support)==len(set(support))
        assert all(p[i]>>5==f for i in support)
        assert all(i not in owners for i in support)
        for i in support:owners[i]=f
        supports.append((t,q,support))
        digest.update(json.dumps((f,t,q,ix,iy,support)).encode())
    assert len(supports)==1<<(n-5)
    return w,p,supports,{'n':n,'secondary':b,'primary_B':B,'weights':w,
         'certified_ALL_paired_mask_lower_bound':1+(1<<(n-5)),
         'disjoint_witnesses':len(supports),'occupied_turn_positions':len(owners),
         'core_exchange_triple':points,'support_sha256':digest.hexdigest()}

def main():
    start=time.monotonic();rng=random.Random(202610031455);rows=[];checks=0
    for n in range(5,14):
        for trial in range(8):
            if trial==0:core=(1,2,4,8,16)
            else:
                while True:
                    core=tuple(rng.randrange(-100,101) for _ in range(5))
                    if core_ok(core) and (core[4]>max(core[1:3]) or core[4]<min(core[1:3])):break
            L=sum(abs(x) for x in core)+1
            tail=[L*(1<<j)*(1 if rng.getrandbits(1) else -1) for j in range(n-5)];rng.shuffle(tail)
            b=core+tuple(tail);w,p,ws,row=packing(b);R=[]
            for j in range(8):
                theta=rng.getrandbits((1<<(n-1))-1);v=[rank(x,n,theta) for x in range(1<<n)]
                word=[v[x] for x in p];sg=[1 if y>x else -1 for x,y in zip(word,word[1:])]
                for t,q,support in ws:
                    A=(v[t[1]]-v[t[0]])*(v[t[2]]-v[t[1]])
                    C=(v[q[1]]-v[q[0]])*(v[q[2]]-v[q[1]])
                    assert (A>0)!=(C>0)
                    assert any(sg[i-1]!=sg[i] for i in support)
                r=fast_runs(v,p);assert r>=row['certified_ALL_paired_mask_lower_bound'];R.append(r);checks+=1
            row['rank_audit_runs']=R;rows.append(row)
    out={'status':'VERIFIED_ALL_DIMENSION_CARDINALITY_SUBLAYER_TRANSLATION_PACKING',
         'analytic_statement':'For any n>=5, choose arbitrary lowest-five secondary b with every cardinality layer generic and b4 extreme among b1,b2,b4. All outer secondary subset-score gaps must exceed sum absolute core secondary coefficients. Let B>2sum|b| and actual positive generic weights w_j=B+b_j. Every paired rank has R>=1+2^(n-5). Each five-face supplies the ordered equal-cardinality exchange triple from(3,5,17), and its toggle8 translate; full-turn supports lie inside two disjoint cardinality sublayers of that face. They are disjoint across ALL faces.',
         'scope':'A genuine all-dimensional restricted scan CLASS, with arbitrary permitted core secondary and signed/permuted outer secondary. NOT an unrestricted RLC or M_n lower bound. No finite core minimum, ancestor optimizer or LP is used. Existing stronger numerical-cardinality quarter theorem is credited, not reclaimed.',
         'proof':'The two leading changed bits are2,4 because b4 is extreme. Common bit3 is zero, so toggle8 reverses exactly one paired comparison. Original points all have core cardinality2, translates core cardinality3. Cardinality primary separates layers; outer secondary gaps greater than the complete core range make different faces score-disjoint WITHIN each layer. Thus each interval support contains vertices of just its own face and its own layer. All unions for different face prefixes are disjoint. One forced turn perface gives the lower bound.',
         'actual_scan_cases':len(rows),'direct_rank_audits':checks,'seed':202610031455,
         'rows':rows,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('cardinality_sublayer_translation_packing_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','proof')}),flush=True)

if __name__=='__main__':main()
