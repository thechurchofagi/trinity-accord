#!/usr/bin/env python3
"""Deterministic targeted pressure of coherent cardinality INTERIOR energy.

Exact integer scores and exact spin optima; sampled secondary chambers.
No general lower or upper bound follows from absence of a better sample.
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import math
import os
import random
import time
from verify_face_local_obstruction import subset_scores
from verify_gray_reflection_graph import gray, energy, inverse_gray, counts
from probe_arbitrary_coherent_secondary import exact_gray_spin_optimizer

SEED=202610030845
BUDGETS={6:6000,7:6000,8:4000,9:2000,10:1000}
ROOT=Path(__file__).parent

def normalize(b):
    lo=min(b);v=tuple(x-lo for x in b)
    d=math.gcd(*v)
    return tuple(x//d for x in v) if d else v

def analyze(b):
    n=len(b);N=1<<n;b=normalize(b);s=subset_scores(b)
    fixed_ties=False
    if len(set((x.bit_count(),s[x]) for x in range(N)))!=N:
        b=normalize(tuple(N*v+(1<<j) for j,v in enumerate(b)))
        s=subset_scores(b);fixed_ties=True
    assert len(set((x.bit_count(),s[x]) for x in range(N)))==N
    p=tuple(sorted(range(N),key=lambda x:(x.bit_count(),s[x])))
    j=defaultdict(int);D=0
    for a,v,c in zip(p,p[1:],p[2:]):
        if a.bit_count()!=v.bit_count() or v.bit_count()!=c.bit_count():continue
        h=(a^v).bit_length()-1;k=(v^c).bit_length()-1
        e=1 if gray(v)>gray(a) else -1;f=1 if gray(c)>gray(v) else -1
        if h==k:D+=1
        else:j[tuple(sorted((h,k)))]+=e*f
    edges=tuple((h,k,v) for (h,k),v in sorted(j.items()) if v)
    assert all(k<n-1 for h,k,v in edges)
    W=sum(abs(v) for h,k,v in edges)
    E,mask=exact_gray_spin_optimizer({'edges':edges,'W':W},n)
    assert energy(edges,mask)==E
    return {'n':n,'secondary':b,'D_int':D,'W_int':W,'E_int':E,
            'interior_edges':edges,'net':E-D,'optimizing_gray_mask':mask,
            'input_reflection':inverse_gray(mask),
            'tail_limit_fraction':[(1<<n)+D-E,1<<(n+1)],
            'core_order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest(),
            'tie_refined':fixed_ties}

def main():
    start=time.monotonic();rng=random.Random(SEED);records=[];previous=None
    for n,budget in BUDGETS.items():
        elites=[];seen=set();examined=refined=duplicates=0;best=None;improvements=[]
        core=(4,6,3,0,8)+tuple(32*(1<<j) for j in range(n-5))
        seeds=[core]
        if previous:
            old=tuple(previous['secondary'])
            seeds.extend(old+(new,) for new in (sum(old)+1,max(old)//2,max(old)+1))
        for trial in range(budget):
            if trial<len(seeds):candidate=seeds[trial];mode='inherited'
            elif trial%7==0:
                bound=rng.choice((16,64,256,4096));candidate=tuple(rng.randrange(bound) for j in range(n));mode='random_restart'
            else:
                parent=tuple(rng.choice(elites[:8])['secondary'])
                v=list(parent);mode=rng.choice(('move','swap','replace','compress'))
                if mode=='swap':
                    a,c=rng.sample(range(n),2);v[a],v[c]=v[c],v[a]
                elif mode=='compress':
                    factor=rng.randrange(2,9);v=[x//factor for x in v]
                else:
                    j=rng.randrange(n);span=max(v)+1
                    if mode=='replace':v[j]=rng.randrange(span)
                    else:
                        scale=rng.choice((1,max(1,span//100),max(1,span//20),max(1,span//4),span))
                        v[j]+=rng.randrange(-3,4)*scale
                candidate=tuple(v)
            row=analyze(candidate);examined+=1;refined+=int(row['tie_refined'])
            h=row['core_order_sha256']
            if h in seen:duplicates+=1;continue
            seen.add(h);elites.append(row);elites.sort(key=lambda r:r['net'],reverse=True);elites=elites[:16]
            if best is None or row['net']>best['net']:
                best=row;improvements.append({'trial':trial,'mode':mode,**row})
                print(json.dumps({'n':n,'trial':trial,'net':row['net'],'D':row['D_int'],'E':row['E_int'],'limit':row['tail_limit_fraction'],'secondary':row['secondary']}),flush=True)
                checkpoint={'state':'RUNNING','pid':os.getpid(),'seed':SEED,'n':n,'trial':trial,
                            'budgets':BUDGETS,'completed_dimensions':records,'best':best,
                            'restart':'Do not duplicate a healthy PID. If stopped, replay deterministic seed through this trial; preserve checkpoint.'}
                (ROOT/'larger_cardinality_core_checkpoint.json').write_text(json.dumps(checkpoint,separators=(',',':'))+'\n')
        record={'n':n,'budget':budget,'examined':examined,'tie_refinements':refined,
                'duplicate_orders':duplicates,'distinct_sampled_orders':len(seen),
                'best':best,'improvements':improvements}
        records.append(record);previous=best
        print(json.dumps({'n':n,'complete':True,'distinct_sampled_orders':len(seen),'best_net':best['net'],'elapsed':round(time.monotonic()-start,3)}),flush=True)
    out={'state':'TARGETED_PRESSURE_COMPLETE_NOT_CHAMBER_CLASSIFICATION','seed':SEED,
         'budgets':BUDGETS,'records':records,'violations':0,
         'elapsed_seconds':round(time.monotonic()-start,3),
         'verification_digest':hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest(),
         'limitations':'All displayed interior graphs and sign energies are exact. Secondary chambers are sampled. Only the independently proved general core extension justifies an all-dimensional family for a chosen vector.'}
    (ROOT/'larger_cardinality_core_pressure.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    (ROOT/'larger_cardinality_core_checkpoint.json').write_text(json.dumps({'state':'COMPLETE','seed':SEED,'result':'larger_cardinality_core_pressure.json'},separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='records'}),flush=True)

if __name__=='__main__':main()
