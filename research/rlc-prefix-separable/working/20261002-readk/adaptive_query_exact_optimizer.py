#!/usr/bin/env python3
"""Apply the already audited standard ancestor DP to full query-tree graphs.

Not a new optimization framework. Exact integer tables and attained counts.
"""
from paired_sibling_ancestor_optimizer import optimize
from adaptive_query_research import graph,rank_table,direct_counts

def exact_minimum(q,n,p,cyclic=True):
    N=1<<n;g=graph(q,n,p,cyclic);labels={}
    for u in range(1,N):
        d=u.bit_length()-1;prefix=u-(1<<d);labels[u]=N-(1<<(d+1))+prefix
    mapped={'edges':[(labels[a],labels[b],J) for (a,b),J in g['J'].items()]}
    out=optimize(mapped,n+1);bits={u:(out['mask']>>lab)&1 for u,lab in labels.items()};assert bits[1]==0
    E=sum(J*(-1 if bits[a]^bits[b] else 1) for (a,b),J in g['J'].items());assert E==out['E_max']
    R,C=direct_counts(rank_table(q,n,bits),p)
    value=(N+g['D']-E)//2 if cyclic else 1+(N-2+g['D']-E)//2
    assert value==(C if cyclic else R)
    return {'minimum':value,'R':R,'C':C,'bits':bits,'D':g['D'],'K':g['K'],'q':g['q'],
            'E_max':E,'conditional_states':out['conditional_states'],'table_sha256':out['table_sha256']}
