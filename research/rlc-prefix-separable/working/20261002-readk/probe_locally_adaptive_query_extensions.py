#!/usr/bin/env python3
"""Actual one-coordinate extension pressure, with repaired local query constraints.

Exploratory search only. Exact scores/ranks audit every feasible counterexample.
"""
import json,time,hashlib
from pathlib import Path
from itertools import product
from adaptive_query_research import *
from probe_locally_adaptive_query_density import propose_bits,validate_witness

def extend(q,n,repairs):
    out={};N=1<<n
    def visit(u,rem):
        j=q[u];out[u]=j;rest=tuple(h for h in rem if h!=j)
        if len(rem)==2:
            old=rest[0];swap=repairs[u]
            for b in (0,1):
                v=2*u+b;k=n if b==swap else old;other=old if k==n else n
                out[v]=k;out[2*v]=other;out[2*v+1]=other
        else:
            visit(2*u,rest);visit(2*u+1,rest)
    visit(1,tuple(range(n)));validate(out,n+1);return out

def main():
    st=time.monotonic();x=json.loads(Path('locally_adaptive_query_pressure.json').read_text())['quarter_counterexample']
    q=dict(x['queries']);n=5;w=x['signed_weights'];scores=sorted(sum(w[h] for h in range(n) if a>>h&1) for a in range(1<<n))
    walls=sorted({abs(a-b) for a in scores for b in scores});params=[walls[i]+walls[i+1] for i in range(len(walls)-1)]+[2*walls[-1]+1]
    # Scale old weights by two; every odd sum midpoint represents a genuine interval.
    old=[2*a for a in w];params=[a for a in params if a%2]
    nodes=list(range(1<<(n-2),1<<(n-1)));attempts=solves=0;best=64;counter=None;stream=hashlib.sha256()
    for mask in range(1<<len(nodes)):
        qq=extend(q,n,{u:(mask>>j)&1 for j,u in enumerate(nodes)})
        for a in params:
            ww=old+[a];p=additive_order(ww)
            if p is None:continue
            attempts+=1;g=graph(qq,n+1,p,True)
            if g['D']+g['K']>=min(best,16):continue
            bits,status=propose_bits(g);solves+=1
            if bits is None:continue
            R,C=direct_counts(rank_table(qq,n+1,bits),p)
            phi=sum(abs(v) for (u,vv),v in g['J'].items() if (bits.get(u,0)^bits.get(vv,0))!=(v<0))
            assert C==g['D']+g['K']+phi
            stream.update(json.dumps((mask,a,R,C,bits,status),sort_keys=True).encode())
            if C<best:
                best=C;witness=validate_witness(qq,n+1,ww,bits,R)
                print('bestC',best,'R',R,'repair',mask,'newweight',a,'attempts',attempts,'solves',solves,flush=True)
            if C<16:counter=witness;break
        out={'status':'EXPLORATORY_REPAIRED_LOCAL_QUERY_EXTENSION','n':6,'actual_attempts':attempts,'milp_calls':solves,
             'core_queries':sorted(q.items()),'core_weights':w,'new_weight_parameters':params,'best_verified_witness':witness if best<64 else None,
             'quarter_cyclic_counterexample':counter,'stream_sha256':stream.hexdigest(),'seconds':time.monotonic()-st,
             'scope':'Incomplete family/weights; feasible witnesses checked exactly. No numerical lower bounds, no all-n claim.'}
        Path('locally_adaptive_query_extension_pressure.json').write_text(json.dumps(out,indent=2)+'\n')
        if counter:break
    print(json.dumps({k:v for k,v in out.items() if k not in ('best_verified_witness','quarter_cyclic_counterexample','core_queries','new_weight_parameters')}),flush=True)
if __name__=='__main__':main()
