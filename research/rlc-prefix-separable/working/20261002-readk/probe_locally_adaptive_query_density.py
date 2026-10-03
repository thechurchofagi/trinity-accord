#!/usr/bin/env python3
"""Pressure testing only: search for an actual quarter-density counterexample.

MILP proposes orientations; every accepted candidate is independently checked
with exact integer scores, direct ranks, and all prefix separators.
No numerical solver lower bound is used as a mathematical certificate.
"""
import argparse,gzip,hashlib,json,random,time
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix
from adaptive_query_research import *

SEED=202610031947

def propose_bits(g):
    nodes=sorted({1,*g['labels']});ix={u:i for i,u in enumerate(nodes)};edges=list(g['J'].items());m=len(nodes);E=len(edges)
    c=np.zeros(m+E);A=lil_matrix((4*E,m+E));upper=[]
    for e,((u,v),J) in enumerate(edges):
        i,j=ix[u],ix[v];k=m+e;c[k]=J
        for t,co in enumerate(((1,-1,-1),(-1,1,-1),(-1,-1,1),(1,1,1))):
            A[4*e+t,i]=co[0];A[4*e+t,j]=co[1];A[4*e+t,k]=co[2]
        upper.extend((0,0,0,2))
    hi=np.ones(m+E);hi[ix[1]]=0
    res=milp(c,integrality=np.ones(m+E),bounds=Bounds(np.zeros(m+E),hi),
        constraints=LinearConstraint(A.tocsr(),-np.inf,np.array(upper)),options={'time_limit':0.25})
    if res.x is None:return None,int(res.status)
    return {u:int(res.x[ix[u]]>=.5) for u in nodes},int(res.status)

def validate_witness(q,n,w,bits,R):
    p=additive_order(w);assert p is not None;rr=rank_table(q,n,bits);assert direct_counts(rr,p)[0]==R
    inv=sorted(range(1<<n),key=rr.__getitem__)
    for k in range(1,1<<n):
        z=inv[k];c=separator(q,n,bits,z)
        for x in range(1<<n):
            S=sum(c[j]*(((x>>j)&1)-((z>>j)&1)) for j in range(n))
            assert (S<0)==(rr[x]<k)
    return {'n':n,'queries':sorted(q.items()),'signed_weights':w,'orientation_bits':sorted(bits.items()),
            'R':R,'C':direct_counts(rr,p)[1],'scan':p,'rank_word':[rr[x] for x in p]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--per-seed',type=int,default=6);ap.add_argument('--cyclic',action='store_true');ap.add_argument('--seed',type=int,default=SEED);args=ap.parse_args()
    st=time.monotonic();rng=random.Random(args.seed);stream=hashlib.sha256();best=32;counter=None;attempts=solves=ties=0;minima=[]
    source=Path('paired_boolean_term_orders_certificate.json.gz').read_bytes()
    assert hashlib.sha256(source).hexdigest()=='e00dba962c76e8ad0031c53f4ed2e9a643f8ae0312e3a7531c8415cacd63933c'
    rows=json.loads(gzip.decompress(source))['n5_orders_and_certificates']
    seeds=[tuple(r['coherence_certificate']['integer_weights']) for r in rows if r['coherence_certificate']['coherent']]
    assert len(seeds)==516
    orbits=json.loads(Path('locally_adaptive_query_orbits_q5.json').read_text())['orbits']
    for oi,orb in enumerate(orbits):
        q=dict(enumerate(orb['representative_queries'],1));n=5;local=32
        for seed in seeds:
            for _ in range(args.per_seed):
                w=list(seed);rng.shuffle(w);w=[a*rng.choice((-1,1)) for a in w]
                p=additive_order(w);assert p is not None;attempts+=1;g=graph(q,n,p,cyclic=args.cyclic)
                offset=0 if args.cyclic else 1
                if offset+g['D']+g['K']>=min(best,8):continue
                bits,status=propose_bits(g);solves+=1
                if bits is None:continue
                rr=rank_table(q,n,bits);R,C=direct_counts(rr,p)
                phi=sum(abs(v) for (a,b),v in g['J'].items() if (bits.get(a,0)^bits.get(b,0))!=(v<0))
                value=C if args.cyclic else R
                assert value==offset+g['D']+g['K']+phi
                stream.update(json.dumps((oi,w,bits,R,C,status),sort_keys=True).encode())
                if value<local:local=value
                if value<best:
                    best=value;witness=validate_witness(q,n,w,bits,R)
                    print('best',best,'orbit',oi,'attempts',attempts,'solves',solves,flush=True)
                if value<8:counter=validate_witness(q,n,w,bits,R);break
            if counter:break
        minima.append({'orbit':oi,'sampled_feasible_candidate_minimum_R':None if local==32 else local})
        partial={'status':'EXPLORATORY_ACTUAL_WEIGHT_PRESSURE','seed':args.seed,'per_seed':args.per_seed,'cyclic_objective':args.cyclic,
                 'complete_orbit_geometry_scope':16,'INCOMPLETE_signed_weight_scope':True,'attempts':attempts,'milp_calls':solves,
                 'best_verified_witness':witness if best<32 else None,'quarter_counterexample':counter,'orbit_candidate_minima':minima,
                 'stream_sha256':stream.hexdigest(),'seconds':time.monotonic()-st,
                 'scope':'Only exact feasible upper witnesses are claimed; no solver lower bounds or all-weight/all-n theorem.'}
        Path('locally_adaptive_query_cyclic_pressure.json' if args.cyclic else 'locally_adaptive_query_pressure.json').write_text(json.dumps(partial,indent=2)+'\n')
        print('orbit_done',oi,'attempts',attempts,'solves',solves,'best',best,flush=True)
        if counter:break
    print(json.dumps({k:v for k,v in partial.items() if k not in ('best_verified_witness','orbit_candidate_minima','quarter_counterexample')}),flush=True)
if __name__=='__main__':main()
