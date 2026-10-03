#!/usr/bin/env python3
"""Exact pressure on all-dimensional conjectures, never coverage by sampling."""
from itertools import permutations
from pathlib import Path
import hashlib,json,random,time
from verify_paired_sibling_ranks import rank,linear_graph,fast_runs
from paired_sibling_ancestor_optimizer import optimize,plain_optimize

def evaluate(b,n):
    N=1<<n;B=1+sum(abs(z) for z in b);w=[B+z for z in b]
    s=[sum(w[j] for j in range(n) if (x>>j)&1) for x in range(N)]
    if len(set(s))<N:return None
    p=sorted(range(N),key=s.__getitem__)
    assert p==sorted(range(N),key=lambda x:(x.bit_count(),sum(b[j] for j in range(n) if (x>>j)&1)))
    g=linear_graph(p,n);z=optimize(g,n);phi=(g['W']-z['E_max'])//2
    assert phi>=0 and (g['W']-z['E_max'])%2==0
    R=fast_runs([rank(x,n,z['mask']) for x in range(N)],p)
    assert R==1+g['D']+g['K']+phi
    if n<=7:assert plain_optimize(g,n)[0]==z['E_max']
    return {'n':n,'secondary':b,'weights':w,'D':g['D'],'K':g['K'],'W':g['W'],
            'phi':phi,'R_min':R,'attaining_mask':z['mask'],
            'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest(),
            'dp_table_sha256':z['table_sha256']}

def main():
    rng=random.Random(202610031037);start=time.monotonic();digest=hashlib.sha256()
    summaries=[];witnesses=[];counterexamples=[];rejected=0;total=0
    def sweep(n,candidates,scope):
        nonlocal rejected,total
        best_R=None;best_DK=None;count=0
        for b in candidates:
            r=evaluate(b,n)
            if r is None:rejected+=1;continue
            count+=1;total+=1;digest.update(json.dumps(r,sort_keys=True).encode())
            if best_R is None or r['R_min']<best_R['R_min']:best_R=r
            if best_DK is None or r['D']+r['K']<best_DK['D']+best_DK['K']:best_DK=r
            if r['R_min']<(1<<n)//4+2 or r['D']+r['K']<(1<<n)//4+1:counterexamples.append(r)
        summaries.append({'n':n,'scope':scope,'evaluated':count,'minimum_R_witness':best_R,'minimum_D_plus_K_witness':best_DK})
        if best_R:witnesses.append(best_R)
        print(json.dumps(summaries[-1]),flush=True)
    for n in range(3,8):
        def values():
            for sigma in permutations(range(n)):
                b=[0]*n
                for i,j in enumerate(sigma):b[j]=1<<i
                yield b
        sweep(n,values(),'every coordinate permutation of a superincreasing secondary scan')
    for n,budget in ((5,128),(6,256),(7,256),(8,256),(9,128),(10,128)):
        sweep(n,(rng.sample(range(-100000,100001),n) for _ in range(budget)),
              'fresh signed integer secondary samples; no chamber coverage')
    output={'seed':202610031037,'total_evaluated':total,'nongeneric_rejections':rejected,
            'summaries':summaries,'counterexamples_to_R_N_over_4_plus_2_or_DK_N_over_4_plus_1':counterexamples,
            'evaluated_digest':digest.hexdigest(),'seconds':time.monotonic()-start,
            'scope':'Exact fixed-scan minima. Exhaustive only for listed superincreasing permutations in n<=7. No all-dimensional conclusion from absence of counterexamples.'}
    Path(__file__).with_name('paired_cardinality_secondary_pressure.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k not in ('summaries','counterexamples_to_R_N_over_4_plus_2_or_DK_N_over_4_plus_1')}),flush=True)

if __name__=='__main__':main()
