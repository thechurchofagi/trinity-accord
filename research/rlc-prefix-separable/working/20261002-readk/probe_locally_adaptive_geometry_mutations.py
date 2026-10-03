#!/usr/bin/env python3
"""Exact-orientation, exploratory-geometry counterexample search.

The graph minimization reuses known integer ancestor DP. Geometry/weights are
sampled and mutated, so absence of a counterexample proves no uniform bound.
"""
import argparse,gzip,hashlib,json,math,random,time
from pathlib import Path
from adaptive_query_research import *
from adaptive_query_exact_optimizer import exact_minimum
from probe_locally_adaptive_query_density import validate_witness

def mutation(q,n,rng):
    out=dict(q);u=rng.randrange(1,1<<(n-1));d=u.bit_length()-1;anc=u;free=set(range(n));path=[]
    while anc>1:path.append(anc//2);anc//=2
    for a in reversed(path):free.remove(q[a])
    if len(free)<2:return None
    a,b=rng.sample(sorted(free),2)
    for v in out:
        dv=v.bit_length()-1
        if dv>=d and v>>(dv-d)==u:
            out[v]=b if out[v]==a else a if out[v]==b else out[v]
    if u>1 and len(free)+1>=3 and out[u]==out[u^1]:return None
    validate(out,n);return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=202610032030);ap.add_argument('--restarts',type=int,default=40);ap.add_argument('--steps',type=int,default=80);args=ap.parse_args()
    rng=random.Random(args.seed);st=time.monotonic();stream=hashlib.sha256();rows=[];counter=None;cases=0
    seeds=[tuple(r['coherence_certificate']['integer_weights']) for r in json.loads(gzip.decompress(Path('paired_boolean_term_orders_certificate.json.gz').read_bytes()))['n5_orders_and_certificates'] if r['coherence_certificate']['coherent']]
    for n in (6,8):
        N=1<<n;best=N;witness=None;minima=[]
        for restart in range(args.restarts if n==6 else max(4,args.restarts//4)):
            if n==6:
                w=[2*a for a in rng.choice(seeds)];rng.shuffle(w);w=[a*rng.choice((-1,1)) for a in w];w.append(2*rng.randrange(1,sum(abs(a) for a in w)+1)+1)
            else:
                w=[N*rng.randrange(-50,51)+(1<<j) for j in range(n)]
            p=additive_order(w);assert p is not None;q=random_queries(n,rng)
            # Frequently align the root with the largest weight to target low forced turns.
            if restart%2==0:
                target=max(range(n),key=lambda j:abs(w[j]));old=q[1]
                q={u:target if j==old else old if j==target else j for u,j in q.items()}
            value=exact_minimum(q,n,p);cases+=1
            for step in range(args.steps):
                qq=mutation(q,n,rng)
                if qq is None:continue
                proposal=exact_minimum(qq,n,p);cases+=1
                temp=.5+1.0*(1-step/args.steps)
                if proposal['C']<=value['C'] or rng.random()<math.exp((value['C']-proposal['C'])/temp):q=qq;value=proposal
                if value['C']<best:
                    best=value['C'];witness={'n':n,'queries':sorted(q.items()),'signed_weights':w,'orientation_bits':sorted(value['bits'].items()),
                        'R':value['R'],'C':value['C'],'table_sha256':value['table_sha256'],'conditional_states':value['conditional_states'],
                        'D':value['D'],'K':value['K'],'q':value['q']}
                    print('new_minimum',n,'C',best,'R',value['R'],'restart',restart,'step',step,'cases',cases,flush=True)
                if value['C']<N//4:
                    counter=validate_witness(q,n,w,value['bits'],value['R']);counter.update({'exact_C_minimum':value['C'],'table_sha256':value['table_sha256']});break
            minima.append({'restart':restart,'weights':w,'final_exact_C_minimum':value['C']})
            stream.update(json.dumps((n,restart,w,sorted(q.items()),value),sort_keys=True).encode())
            out={'status':'EXPLORATORY_GEOMETRY_WITH_EXACT_ORIENTATION_MINIMA','seed':args.seed,'restarts':args.restarts,'steps':args.steps,'exact_contexts':cases,
                 'previous_dimensions':rows,'current_dimension':n,'current_minima':minima,'best_verified_candidate':witness,
                 'cyclic_quarter_counterexample':counter,'stream_sha256':stream.hexdigest(),'seconds':time.monotonic()-st,
                 'scope':'Each orientation minimum is exact; query geometries/weights sampled. NOT an all-weight lower or all-n theorem.'}
            Path('locally_adaptive_geometry_mutation_pressure.json').write_text(json.dumps(out,indent=2)+'\n')
            print('restart_done',n,restart,'bestC',best,'cases',cases,flush=True)
            if counter:break
        rows.append({'n':n,'best_candidate':witness,'restart_final_minima':minima})
        if counter:break
    print(json.dumps({k:v for k,v in out.items() if k in ('status','seed','exact_contexts','seconds','scope')}),flush=True)
if __name__=='__main__':main()
