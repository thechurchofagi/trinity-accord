#!/usr/bin/env python3
"""Exhaust grid shuffles to attack a stronger-than-additive quartet lemma.

Each face's four events stay ordered; each of the four tracks has the
SAME face order. These shuffles need not be realizable by equal-gap score
translations. An exact counterexample excludes track-order-only proofs.
"""
from pathlib import Path
from itertools import permutations
import hashlib,json,time
import numpy as np

def words(F):
    def visit(used,z):
        if len(z)==4*F:yield tuple(z);return
        for f in range(F):
            x=used[f]
            if x<4 and (f==0 or used[f-1]>x):
                now=list(used);now[f]+=1
                yield from visit(now,z+[(f,x)])
    return visit([0]*F,[])

def main():
    start=time.monotonic();rows=[];failure=None
    for F in (2,3,4):
        P=list(permutations(range(F)));B=np.array(P,dtype=np.int64)[:,None,:]
        masks=np.arange(1<<(2*F),dtype=np.int64)[None,:]
        upper=[]
        for p in P:
            s=[1 if p[j+1]>p[j] else -1 for j in range(F-1)]
            upper.append(1+sum(x!=y for x,y in zip(s,s[1:])))
        target=np.array([min(F+1,4*u-3) for u in upper],dtype=np.int64)
        count=0
        for word in words(F):
            turns=np.zeros((len(P),masks.shape[1]),dtype=np.int64);previous=None
            for (f,x),(g,y) in zip(word,word[1:]):
                if f!=g:sg=np.where(B[:,:,g]>B[:,:,f],1,-1)
                else:
                    h=(x^y).bit_length()-1
                    sg=(1 if (y^(y>>1))>(x^(x>>1)) else -1)*(1-2*((masks>>(2*f+h))&1))
                if previous is not None:turns+=(previous!=sg)
                previous=sg
            minima=turns.min(axis=1)+1;count+=1
            fail=np.flatnonzero(minima<target)
            if len(fail):
                j=int(fail[0]);mask=int(np.argmin(turns[j]));p=P[j]
                values=[4*p[f]+((x^(x>>1))^((mask>>(2*f))&3)) for f,x in word]
                s=[1 if y>x else -1 for x,y in zip(values,values[1:])]
                assert int(minima[j])==1+sum(x!=y for x,y in zip(s,s[1:]))
                failure={'F':F,'word':word,'block_rank':p,'mask':mask,'rank_values':values,
                         'upper_runs':upper[j],'actual_runs':int(minima[j]),'proposed_bound':int(target[j]),
                         'coverage':'Grid shuffle only; actual additive translation realizability is NOT certified.'}
                break
            if F==4 and count%2000==0:
                print(json.dumps({'F':F,'grid_words_completed':count,'elapsed':time.monotonic()-start}),flush=True)
        rows.append({'F':F,'grid_words_completed':count,'block_permutations':len(P),
                     'orientation_masks':masks.shape[1],'exhaustion_complete':failure is None})
        if failure:break
    out={'status':'EXACT_GRID_SHUFFLE_QUARTET_RECURRENCE_AUDIT','scope':'Stronger-than-additive relaxation, not actual weight-chamber coverage.',
         'rows':rows,'counterexample':failure,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('quartet_grid_recurrence_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
