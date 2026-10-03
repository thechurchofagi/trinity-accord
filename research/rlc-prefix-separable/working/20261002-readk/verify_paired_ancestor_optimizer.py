#!/usr/bin/env python3
"""New exact optimizer audits and fresh structured-scan quarter pressure."""
from pathlib import Path
from itertools import combinations
import hashlib,json,random,time
import numpy as np
from paired_sibling_ancestor_optimizer import optimize,plain_optimize,layout
from verify_paired_sibling_ranks import rank,linear_graph,fast_runs
from verify_gray_reflection_graph import gray,counts,order_and_scores

ROOT=Path(__file__).parent
SEED=202610030951

def check_order(p,n,plain=False,exhaust=False):
    g=linear_graph(p,n);result=optimize(g,n)
    if plain:assert plain_optimize(g,n)[0]==result['E_max']
    if exhaust:
        variables=(1<<(n-1))-1
        ix=np.arange(1<<variables,dtype=np.int64);ee=np.zeros(len(ix),dtype=np.int64)
        for a,b,v in g['edges']:ee+=v*(1-2*(((ix>>a)^(ix>>b))&1))
        assert int(ee.max())==result['E_max']
        # Independent rank comparisons at every optimizer, not just energy.
        for mask in np.flatnonzero(ee==ee.max())[:16]:
            r=tuple(rank(x,n,int(mask)) for x in p)
            assert fast_runs(r,tuple(range(len(p))))==1+(len(p)-2+g['D']-result['E_max'])//2
    r=tuple(rank(x,n,result['mask']) for x in p);R,C,_=counts(r)
    assert R==1+g['D']+g['K']+(g['W']-result['E_max'])//2
    return {**g,**result,'R_min_exact':R,'C_at_witness':C,
            'phi_exact':(g['W']-result['E_max'])//2,
            'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}

def main():
    start=time.monotonic();rng=random.Random(SEED);digest=hashlib.sha256();audits=[]
    for n in range(1,6):
        budget=12 if n<5 else 6
        for case in range(budget):
            p=list(range(1<<n));rng.shuffle(p);p=tuple(p)
            row={'n':n,'case':case,'order':p,'certificate':check_order(p,n,plain=True,exhaust=True)}
            audits.append(row);digest.update(json.dumps(row,sort_keys=True).encode())
    # Nonadditive exact negative control: ancestral structure alone cannot give a quarter bound.
    negatives=[]
    for n in range(3,9):
        p=tuple(sorted(range(1<<n),key=gray));row=check_order(p,n,plain=n<=6)
        assert row['R_min_exact']==1
        negatives.append({'n':n,'nonadditive_gray_rank_order':p,'certificate':row})
    rows=[];best={};total=0;violations=[]
    def test(w,tag):
        nonlocal total
        n=len(w);res=order_and_scores(w)
        if res is None:return
        p=res[0];row=check_order(p,n,plain=n<=7)
        item={'n':n,'tag':tag,'weights':w,'certificate':row};rows.append(item);total+=1
        digest.update(json.dumps(item,sort_keys=True).encode())
        if n not in best or row['R_min_exact']<best[n]['certificate']['R_min_exact']:
            best[n]=item
            print(json.dumps({'n':n,'tag':tag,'exact_R':row['R_min_exact'],'quarter_plus_one':(1<<n)//4+1,
                              'D_K_phi':[row['D'],row['K'],row['phi_exact']],
                              'weights':w,'elapsed':round(time.monotonic()-start,3)}),flush=True)
        if row['R_min_exact']<(1<<n)//4+1:violations.append(item)
    cores=[(4,6,3,0,8),(4,6,3,0,8,16,28),(4,6,3,0,8,24,36),
           (76,74,73,70,78,94,0,138),(108,106,105,102,110,126,32,170,0)]
    for b in cores:
        for n in range(len(b),min(13,len(b)+4)):
            A=sum(b)+1;secondary=b+tuple(A*(1<<j) for j in range(n-len(b)))
            B=sum(secondary)+1;test(tuple(B+x for x in secondary),'cardinality_numeric_tail')
    # All three-coordinate fast faces, not just the natural top face from prior work.
    for n in range(4,10):
        for fast in combinations(range(n),3):
            slow=tuple(j for j in range(n) if j not in fast)
            w=tuple(1<<fast.index(j) if j in fast else 8*(1<<slow.index(j)) for j in range(n))
            test(w,'every_three_coordinate_fast_face')
    for n in range(5,13):
        for case in range(12):
            bound=10**6
            w=tuple(rng.sample(range(1,bound),n));test(w,'fresh_random_pressure_not_coverage')
    out={'state':'EXACT_ANCESTOR_OPTIMIZER_VERIFIED_AND_STRUCTURED_PRESSURE_COMPLETE',
         'seed':SEED,'small_independent_audits':audits,'nonadditive_negative_controls':negatives,
         'genuine_scan_rows':rows,'best_by_dimension':best,'genuine_scans_checked':total,
         'quarter_counterexamples':violations,'optimizer_violations':0,
         'verification_digest':digest.hexdigest(),'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'Every listed scan optimum over the paired rank family is exact. Weight chambers are not classified. Empty counterexample lists do not prove the quarter inequality. Algorithm correctness and ancestor lemma are proved in PAIRED_ANCESTOR_OPTIMIZATION.md.'}
    (ROOT/'paired_ancestor_optimizer_verification.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k] for k in ('state','genuine_scans_checked','optimizer_violations','verification_digest','elapsed_seconds')}),flush=True)
    print(json.dumps({'quarter_counterexamples':len(violations),'best_by_dimension':{n:r['certificate']['R_min_exact'] for n,r in best.items()}}),flush=True)

if __name__=='__main__':main()
