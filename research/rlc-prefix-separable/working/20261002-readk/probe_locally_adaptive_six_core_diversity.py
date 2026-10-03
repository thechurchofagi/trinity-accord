#!/usr/bin/env python3
"""Broader genuine Q6 cyclic-quarter search; exact feasible witness only.

Checkpointed after each finite geometry orbit. Does not prove a lower bound.
"""
import argparse,gzip,hashlib,json,random,time
from pathlib import Path
from adaptive_query_research import *
from probe_locally_adaptive_query_extensions import extend
from probe_locally_adaptive_query_density import propose_bits,validate_witness

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=202610031956);ap.add_argument('--draws',type=int,default=8);args=ap.parse_args()
    st=time.monotonic();rng=random.Random(args.seed);stream=hashlib.sha256();attempts=solves=0;best=64;counter=None;minima=[]
    seeds=[tuple(r['coherence_certificate']['integer_weights']) for r in json.loads(gzip.decompress(Path('paired_boolean_term_orders_certificate.json.gz').read_bytes()))['n5_orders_and_certificates'] if r['coherence_certificate']['coherent']]
    orbits=json.loads(Path('locally_adaptive_query_orbits_q5.json').read_text())['orbits'];assert len(seeds)==516 and len(orbits)==16
    for oi,orb in enumerate(orbits):
        q=dict(enumerate(orb['representative_queries'],1));local=64
        for seed in seeds:
            for _ in range(args.draws):
                old=list(seed);rng.shuffle(old);old=[2*a*rng.choice((-1,1)) for a in old]
                mask=rng.randrange(256);qq=extend(q,5,{u:(mask>>j)&1 for j,u in enumerate(range(8,16))})
                a=2*rng.randrange(1,sum(abs(v) for v in old)+1)+1;ww=old+[a];p=additive_order(ww);assert p is not None
                attempts+=1;g=graph(qq,6,p,True)
                if g['D']+g['K']>=min(best,16):continue
                bits,status=propose_bits(g);solves+=1
                if bits is None:continue
                R,C=direct_counts(rank_table(qq,6,bits),p)
                phi=sum(abs(v) for (u,vv),v in g['J'].items() if (bits.get(u,0)^bits.get(vv,0))!=(v<0))
                assert C==g['D']+g['K']+phi
                stream.update(json.dumps((oi,ww,mask,bits,R,C,status),sort_keys=True).encode())
                local=min(local,C)
                if C<best:
                    best=C;witness=validate_witness(qq,6,ww,bits,R)
                    print('bestC',C,'R',R,'orbit',oi,'case',attempts,'solves',solves,flush=True)
                if C<16:counter=validate_witness(qq,6,ww,bits,R);break
            if counter:break
        minima.append({'orbit':oi,'sampled_feasible_C':None if local==64 else local})
        out={'status':'EXPLORATORY_DIVERSE_ACTUAL_Q6_EXTENSION','seed':args.seed,'draws_per_seed':args.draws,'attempts':attempts,'milp_calls':solves,
             'orbit_candidate_minima':minima,'best_verified_witness':witness if best<64 else None,'cyclic_quarter_counterexample':counter,
             'stream_sha256':stream.hexdigest(),'seconds':time.monotonic()-st,'scope':'INCOMPLETE sweep/geometry pressure. Only feasible integer witnesses; no numerical lower certificate or all-n conclusion.'}
        Path('locally_adaptive_six_core_diversity_pressure.json').write_text(json.dumps(out,indent=2)+'\n')
        print('orbit_done',oi,'attempts',attempts,'solves',solves,'bestC',best,flush=True)
        if counter:break
    print(json.dumps({k:v for k,v in out.items() if k not in ('orbit_candidate_minima','best_verified_witness','cyclic_quarter_counterexample')}),flush=True)
if __name__=='__main__':main()
