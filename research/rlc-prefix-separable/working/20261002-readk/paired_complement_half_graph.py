#!/usr/bin/env python3
"""Exact complement decomposition and integer terminal-cut certificates.

Ordinary cut only lower-bounds the two-copy frustration when the half
is unbalanced. No all-scan quarter theorem is inferred here.
"""
from collections import defaultdict,deque
from functools import lru_cache
from paired_sibling_ancestor_optimizer import layout


def decompose(graph,n):
    assert n>=2
    r,nodes,info=layout(n);a=nodes[(0,0)]
    def tau(u):
        if u==r:return r
        d,p=info[u]
        return nodes[(d,(1<<d)-1-p)]
    J={tuple(sorted((u,v))):c for u,v,c in graph['edges']}
    assert J.get(tuple(sorted((r,a))),0)==0
    for (u,v),c in J.items():
        uu,vv=tau(u),tau(v)
        eps=-1 if (u==r)!=(v==r) else 1
        assert J[tuple(sorted((uu,vv)))]==eps*c
        if u not in (r,a) and v not in (r,a):
            du,pu=info[u];dv,pv=info[v]
            assert (pu>>(du-1))==(pv>>(dv-1))
    keep={r,a}|{u for u,(d,p) in info.items() if d and p<(1<<(d-1))}
    H=tuple((u,v,c) for u,v,c in graph['edges'] if u in keep and v in keep)
    assert 2*sum(abs(c) for u,v,c in H)==graph['W']
    return H,r,a,tau


def conditional(H,n,a_spin):
    """Independent integer recursion in one half, fixing r=+1 and a=+/-1."""
    assert a_spin in (1,-1)
    r,nodes,info=layout(n);a=nodes[(0,0)]
    J={tuple(sorted((u,v))):c for u,v,c in H}
    active=set()
    for u,v,c in H:
        for z in (u,v):
            if z in (r,a):continue
            d,p=info[z]
            for dd in range(1,d+1):active.add(nodes[(dd,p>>(d-dd))])
    def coupling(u,v):return J.get(tuple(sorted((u,v))),0)
    @lru_cache(None)
    def solve(d,p,ancestors):
        u=nodes[(d,p)];best=None
        if u not in active:return 0,0
        for s in (1,-1):
            e=s*coupling(u,r);mask=int(s<0)<<u
            for dd,ss in enumerate(ancestors):
                e+=s*ss*coupling(u,nodes[(dd,p>>(d-dd))])
            if d<n-2:
                for pp in (2*p,2*p+1):
                    ee,mm=solve(d+1,pp,ancestors+(s,));e+=ee;mask|=mm
            if best is None or e>best[0]:best=(e,mask)
        return best
    if n==2:return (0,int(a_spin<0)<<a)
    e,m=solve(1,0,(a_spin,))
    return e,m|(int(a_spin<0)<<a)


def balance(H):
    adj=defaultdict(list)
    for u,v,c in H:
        s=1 if c>0 else -1
        adj[u].append((v,s));adj[v].append((u,s))
    spin={};parent={}
    for start in adj:
        if start in spin:continue
        spin[start]=1;parent[start]=None;queue=deque([start])
        while queue:
            u=queue.popleft()
            for v,s in adj[u]:
                if v not in spin:spin[v]=spin[u]*s;parent[v]=u;queue.append(v)
                elif spin[v]!=spin[u]*s:
                    up=[];z=u
                    while z is not None:up.append(z);z=parent[z]
                    vp=[];z=v
                    while z not in up:vp.append(z);z=parent[z]
                    return False,tuple(up[:up.index(z)+1]+vp[::-1])
    return True,spin


def terminal_cut(H,r,a):
    """Integer max flow with residual partition; parallel weights sum."""
    vertices=sorted({r,a}|{z for u,v,c in H for z in (u,v)})
    rem=defaultdict(int);adj=defaultdict(set)
    for u,v,c in H:
        rem[u,v]+=abs(c);rem[v,u]+=abs(c);adj[u].add(v);adj[v].add(u)
    flow=0
    while True:
        parent={r:None};queue=deque([r])
        while queue and a not in parent:
            u=queue.popleft()
            for v in sorted(adj[u]):
                if v not in parent and rem[u,v]>0:parent[v]=u;queue.append(v)
        if a not in parent:break
        v=a;capacity=None
        while v!=r:
            u=parent[v];capacity=rem[u,v] if capacity is None else min(capacity,rem[u,v]);v=u
        v=a
        while v!=r:
            u=parent[v];rem[u,v]-=capacity;rem[v,u]+=capacity;v=u
        flow+=capacity
    reachable=set(parent)
    observed=sum(abs(c) for u,v,c in H if (u in reachable)!=(v in reachable))
    assert observed==flow and r in reachable and a not in reachable
    return flow,tuple(sorted(reachable))
