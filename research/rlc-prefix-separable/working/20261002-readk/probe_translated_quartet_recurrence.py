#!/usr/bin/env python3
"""Exact orientation pressure for a proposed translated-quartet recurrence.

The face-block permutation is unrestricted here; this is a deliberate
relaxation, NOT a prefix-separable cube-rank theorem. Retain counterexamples
to a local-to-global shortcut with full integer scores and rank sequence.
"""
from pathlib import Path
import hashlib,json,random,time
import numpy as np

def solve(offsets,a,b,block_rank):
    F=len(offsets);N=4*F
    rows=sorted((s+c,f,x) for f,s in enumerate(offsets) for x,c in enumerate((0,a,b,a+b)))
    if len({s for s,f,x in rows})!=N:return None
    states=np.arange(1<<(2*F),dtype=np.int64)
    previous=None;turns=np.zeros(len(states),dtype=np.int64)
    for (_,f,x),(_,g,y) in zip(rows,rows[1:]):
        if f!=g:sg=1 if block_rank[g]>block_rank[f] else -1
        else:
            h=(x^y).bit_length()-1;index=2*f+h
            gx=x^(x>>1);gy=y^(y>>1)
            sg=(1 if gy>gx else -1)*(1-2*((states>>index)&1))
        if previous is not None:turns+=(previous!=sg)
        previous=sg
    j=int(np.argmin(turns));mask=int(states[j]);R=int(turns[j])+1
    values=[]
    for _,f,x in rows:
        local=(x^(x>>1))^((mask>>(2*f))&3)
        values.append(4*block_rank[f]+local)
    signs=[1 if y>x else -1 for x,y in zip(values,values[1:])]
    assert R==1+sum(x!=y for x,y in zip(signs,signs[1:]))
    upper=[block_rank[f] for f in sorted(range(F),key=offsets.__getitem__)]
    ss=[1 if y>x else -1 for x,y in zip(upper,upper[1:])]
    U=1+sum(x!=y for x,y in zip(ss,ss[1:]))
    target=min(F+1,4*U-3)
    return {'F':F,'offsets':offsets,'a':a,'b':b,'block_rank':block_rank,'optimal_local_mask':mask,
            'ordered_integer_scores':[s for s,f,x in rows],'ordered_face_vertex_pairs':[(f,x) for s,f,x in rows],
            'actual_rank_sequence':values,'upper_runs':U,'minimum_runs':R,'proposed_recurrence_bound':target,
            'recurrence_failure':R<target,'independent_orientation_states':len(states)}

def main():
    start=time.monotonic();rng=random.Random(202610031235);rows=[];fails=[]
    # Basic local-density shortcut already fails on arbitrarily many translated faces.
    # offsets 0..F-1, a=F+1,b=3(F+1), identity block order: four complete
    # increasing tracks with three downward joins, hence only seven runs.
    elementary=solve(list(range(8)),9,27,list(range(8)))
    assert elementary['minimum_runs']<=7<8+1
    for i in range(256):
        F=4 if i<128 else 8
        offsets=sorted(rng.sample(range(0,10000),F));a=rng.randrange(1,10000);b=rng.randrange(a+1,20001)
        block=list(range(F));rng.shuffle(block)
        z=solve(offsets,a,b,block)
        if z is None:continue
        rows.append(z)
        if z['recurrence_failure']:fails.append(z)
    out={'status':'EXACT_RELAXED_TRANSLATED_QUARTET_PRESSURE','seed':202610031235,
         'scope':'Arbitrary face-block permutations and independent two-bit orientations; not the full paired-sibling admissibility constraints.',
         'elementary_face_density_counterexample':elementary,'completed_generic_cases':len(rows),
         'proposed_min_F_plus_1_4_upper_minus_3_failures':fails,'rows':rows,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('translated_quartet_recurrence_pressure.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('elementary_face_density_counterexample','rows','proposed_min_F_plus_1_4_upper_minus_3_failures')}
                     |{'recurrence_failures':len(fails),'first_failure':fails[0] if fails else None}),flush=True)

if __name__=='__main__':main()
