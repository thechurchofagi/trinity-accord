#!/usr/bin/env python3
"""Exact integer ancestor-conditioned optimization of paired-sibling graphs.

This is standard bounded-tree-depth DP on the specific certified prefix
embedding, not a claim to invent a general optimization algorithm.
"""
import hashlib
import numpy as np

def layout(n):
    q=1<<(n-1);nodes={};by_index={}
    for depth in range(n-1):
        for prefix in range(1<<depth):
            u=q-(1<<(depth+1))+prefix
            nodes[(depth,prefix)]=u;by_index[u]=(depth,prefix)
    return q-1,nodes,by_index

def optimize(graph,n):
    top,nodes,by_index=layout(n)
    if n==1:return {'E_max':0,'mask':0,'conditional_states':0,'table_sha256':hashlib.sha256(b'').hexdigest()}
    J={};E_abs=sum(abs(v) for a,b,v in graph['edges'])
    assert E_abs<1<<62
    for a,b,v in graph['edges']:
        assert a!=b
        if a==top:a,b=b,a
        elif b!=top and by_index[a][0]<by_index[b][0]:a,b=b,a
        da,pa=by_index[a]
        if b==top:pass
        else:
            db,pb=by_index[b]
            assert db<da and pb==pa>>(da-db),('non-ancestor edge',a,b)
        J[(a,b)]=v
    values={};choices={};states=0;digest=hashlib.sha256()
    for depth in range(n-2,-1,-1):
        size=1<<depth;ix=np.arange(size,dtype=np.int64)
        for prefix in range(1<<depth):
            u=nodes[(depth,prefix)]
            field=np.full(size,J.get((u,top),0),dtype=np.int64)
            for d in range(depth):
                ancestor=nodes[(d,prefix>>(depth-d))]
                v=J.get((u,ancestor),0)
                if v:field += v*(1-2*((ix>>d)&1))
            plus=field.copy();minus=-field
            if depth<n-2:
                for pp in (2*prefix,2*prefix+1):
                    child=values[nodes[(depth+1,pp)]]
                    plus+=child[:size];minus+=child[size:]
            negative=minus>plus
            values[u]=np.maximum(plus,minus);choices[u]=negative
            states+=size
            digest.update(values[u].astype('<i8',copy=False).tobytes())
            digest.update(negative.tobytes())
    mask=0
    def recover(depth,prefix,state):
        nonlocal mask
        u=nodes[(depth,prefix)];negative=int(choices[u][state])
        mask|=negative<<u
        if depth<n-2:
            state|=negative<<depth
            recover(depth+1,2*prefix,state);recover(depth+1,2*prefix+1,state)
    recover(0,0,0)
    E=int(values[nodes[(0,0)]][0])
    observed=sum(v*(-1 if ((mask>>a)^(mask>>b))&1 else 1) for a,b,v in graph['edges'])
    assert E==observed
    assert states==((1<<(2*(n-1)))-1)//3
    return {'E_max':E,'mask':mask,'conditional_states':states,'table_sha256':digest.hexdigest()}

def plain_optimize(graph,n):
    """Independent standard-library recursion with explicit ancestor signs."""
    from functools import lru_cache
    top,nodes,info=layout(n);edges=tuple(graph['edges'])
    if n==1:return 0,0
    def coupling(a,b):return sum(v for x,y,v in edges if {x,y}=={a,b})
    @lru_cache(None)
    def solve(depth,prefix,ancestors):
        u=nodes[(depth,prefix)];result=None
        for spin in (1,-1):
            e=spin*coupling(u,top);mask=int(spin<0)<<u
            for d,s in enumerate(ancestors):
                e+=spin*s*coupling(u,nodes[(d,prefix>>(depth-d))])
            if depth<n-2:
                for pp in (2*prefix,2*prefix+1):
                    ee,mm=solve(depth+1,pp,ancestors+(spin,));e+=ee;mask|=mm
            if result is None or e>result[0]:result=(e,mask)
        return result
    return solve(0,0,())
