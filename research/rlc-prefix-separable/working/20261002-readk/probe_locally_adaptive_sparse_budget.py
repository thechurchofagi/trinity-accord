#!/usr/bin/env python3
"""Target low-budget actual scans before testing the cyclic quarter guess.

Exploration only. Not a uniform bound or proof of solver optimality.
"""
import argparse,hashlib,json,random,time
from pathlib import Path
from adaptive_query_research import *
from probe_locally_adaptive_query_density import propose_bits,validate_witness

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=202610032015);ap.add_argument('--trees',type=int,default=60);ap.add_argument('--scans',type=int,default=50);args=ap.parse_args()
    rng=random.Random(args.seed);st=time.monotonic();stream=hashlib.sha256();rows=[];counter=None;solves=0
    for n in (7,8,9,10):
        N=1<<n;pool=[];attempts=0
        for t in range(args.trees):
            q=random_queries(n,rng)
            for k in range(args.scans):
                w=[1<<j for j in range(n)];rng.shuffle(w);w=[a*rng.choice((-1,1)) for a in w]
                p=additive_order(w);g=graph(q,n,p,True);budget=g['D']+g['K']+g['q'];attempts+=1
                if len(pool)<20 or budget<pool[-1][0]:
                    pool.append((budget,t,k,q,w,p,g));pool.sort(key=lambda r:r[0]);pool=pool[:20]
        best=N;minbudget=pool[0][0];witness=None
        for budget,t,k,q,w,p,g in pool:
            bits,status=propose_bits(g);solves+=1
            if bits is None:continue
            R,C=direct_counts(rank_table(q,n,bits),p)
            phi=sum(abs(v) for (u,vv),v in g['J'].items() if (bits.get(u,0)^bits.get(vv,0))!=(v<0));assert C==g['D']+g['K']+phi
            stream.update(json.dumps((n,budget,w,bits,R,C,status),sort_keys=True).encode())
            if C<best:
                best=C;witness={'n':n,'queries':sorted(q.items()),'signed_weights':w,'orientation_bits':sorted(bits.items()),'R':R,'C':C,
                               'D':g['D'],'K':g['K'],'q':g['q'],'budget':budget,'solver_status_NOT_a_proof':status}
                print('candidate',n,'R',R,'C',C,'budget',budget,'quarter',N//4,flush=True)
            if C<N//4:
                counter=validate_witness(q,n,w,bits,R);counter.update({'D':g['D'],'K':g['K'],'q':g['q'],'budget':budget});break
        rows.append({'n':n,'actual_binary_scans':attempts,'smallest_sampled_budget':minbudget,'best_exact_feasible_witness':witness})
        out={'status':'EXPLORATORY_SPARSE_BUDGET_TARGETING','seed':args.seed,'trees':args.trees,'scans':args.scans,'rows':rows,'milp_calls':solves,
             'cyclic_quarter_counterexample':counter,'stream_sha256':stream.hexdigest(),'seconds':time.monotonic()-st,
             'scope':'Only sampled scans and exact feasible upper witnesses. No optimization lower bounds or all-dimensional claim.'}
        Path('locally_adaptive_sparse_budget_pressure.json').write_text(json.dumps(out,indent=2)+'\n')
        print('dimension_done',n,'bestC',best,'minimum_budget',minbudget,flush=True)
        if counter:break
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','cyclic_quarter_counterexample')}),flush=True)
if __name__=='__main__':main()
