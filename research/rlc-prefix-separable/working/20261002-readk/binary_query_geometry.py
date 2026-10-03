#!/usr/bin/env python3
"""Exact lex-scan geometry costs, with no unrestricted M_n claim.

Coordinates are numbered by increasing superincreasing weight. Geometry
children use RAW input bits, independently of the rank orientation labels.
"""
from functools import lru_cache
from math import isqrt, comb

def node_cost(n, free, j):
    fixed=((1<<n)-1)^free
    m=(fixed&-fixed).bit_length()-1 if fixed else n
    d=free.bit_count()
    return (1<<(d-1-j))-(1<<(d-m)) if j<m else 0

def controller_cost(q,n):
    total=0;active=0
    def visit(free,u):
        nonlocal total,active
        if not free:return
        j=q[u];assert free>>j&1
        fixed=((1<<n)-1)^free
        m=(fixed&-fixed).bit_length()-1 if fixed else n
        active+=int(j<m);total+=node_cost(n,free,j)
        rest=free^(1<<j)
        visit(rest,2*u);visit(rest,2*u+1)
    visit((1<<n)-1,1)
    return 2*(1+total),active-1

@lru_cache(None)
def pair_cost(m,h):
    """Sum of two best DISTINCT forced child-query costs.

There are m consecutive lowest free coordinates and h inactive higher ones.
For one remaining coordinate both children must query that same coordinate.
"""
    if m+h<=1:return 0
    vals=[(forced_cost(m,h,j),('low',j)) for j in range(m)]
    if h:
        v=pair_cost(m,h-1)
        vals.extend((v,('high',t)) for t in range(min(h,2)))
    vals.sort()
    return vals[0][0]+vals[1][0]

def forced_cost(m,h,j):
    assert 0<=j<m
    return (1<<h)*((1<<(m-1-j))-1)+pair_cost(j,h+m-1-j)

def minimum_binary_cyclic(n):
    vals=[forced_cost(n,0,j) for j in range(n)]
    return 2*(1+min(vals)),vals

def optimal_queries(n):
    """Explicit minimum geometry for this SINGLE numeric binary scan."""
    full=(1<<n)-1;q={}
    def value(free,j):
        fixed=full^free;m=(fixed&-fixed).bit_length()-1 if fixed else n
        h=free.bit_count()-m
        return forced_cost(m,h,j) if j<m else pair_cost(m,h-1)
    def build(free,j,u):
        q[u]=j;rest=free^(1<<j)
        if not rest:return
        vals=sorted((value(rest,k),k) for k in range(n) if rest>>k&1)
        a=vals[0][1];b=vals[1][1] if len(vals)>1 else a
        build(rest,a,2*u);build(rest,b,2*u+1)
    j=min(range(n),key=lambda j:(value(full,j),j))
    build(full,j,1);return q

def sparse_queries(n,k=None):
    """Deterministic locally-distinct family with vanishing density.

This is a counterexample to a UNIVERSAL local-condition guarantee,
not to the existential original M_n target.
"""
    if k is None:k=min(n-1,isqrt(n))
    assert 0<=k<n;q={}
    def build(free,j,u):
        q[u]=j;rem=tuple(x for x in free if x!=j)
        if not rem:return
        if len(rem)==1:a=b=rem[0]
        else:
            fixed=set(range(n))-set(rem);m=min(fixed) if fixed else n
            high=tuple(x for x in rem if x>=m)
            if high and m:a,b=high[0],m-1
            elif high:a,b=high[:2]
            else:a,b=rem[-1],rem[-2]
        build(rem,a,2*u);build(rem,b,2*u+1)
    build(tuple(range(n)),k,1);return q,k

def sparse_bounds(n,k):
    t=(1<<(k+1))*comb(n-1,k)
    return {'C_upper':(1<<(n-k))+t,'q_upper':t-1,
            'budget_upper':(1<<(n-k))+2*t-1}
