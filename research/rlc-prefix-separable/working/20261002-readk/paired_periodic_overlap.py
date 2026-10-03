#!/usr/bin/env python3
"""Explicit genuine sweeps with constant raw/cut budgets and exact cycle packing."""
from collections import defaultdict


def weights(n):
    assert n>=5
    return (1,10,28,16)+tuple(56*(1<<j) for j in range(n-5))+(8,)


def explicit_order(n,tail_order=None):
    ell=n-5;T=1<<ell
    rows=tuple(range(T)) if tail_order is None else tuple(tail_order)
    assert sorted(rows)==list(range(T))
    Q=(0,8,1,4,9,12,5,2,13,10,3,6,11,14,7,15)
    p=[(q&7)+(t<<3)+((q>>3)<<(ell+3)) for t in rows for q in Q]
    for t in range(T-1):
        i=16*t+15;p[i],p[i+1]=p[i+1],p[i]
    return tuple(v for y in p for v in(2*y,2*y+1))


def leaf(n,t,b,c,z):
    T=1<<(n-5)
    return c+2*b+4*t+4*T*z


def backbone(n,t,z):
    T=1<<(n-5)
    return 14 if T==1 else 14*T+(t>>1)+(T//2)*z


def variable(n,x,y):
    h=(x^y).bit_length()-1;q=1<<(n-1)
    return q-1 if h==n-1 else q-(1<<(n-h-1))+(x>>(h+2))


def normal_graph(n,tail_order=None):
    T=1<<(n-5);ell=n-5;r=16*T-1;J={}
    rows=tuple(range(T)) if tail_order is None else tuple(tail_order)
    assert sorted(rows)==list(range(T))
    def put(u,v,c):
        key=tuple(sorted((u,v)));assert key not in J
        assert c;J[key]=c
    for t in range(T):
        for z in (0,1):
            sz=1-2*z;ct=sz if T==1 else 1-2*(t&1);v=backbone(n,t,z)
            for b,c,m in((0,0,-1),(1,0,2),(0,1,-2),(1,1,1)):
                u=leaf(n,t,b,c,z);root=2*sz
                if (t,b,c,z)==(rows[0],0,0,1):root+=1
                if (t,b,c,z)==(rows[-1],1,1,0):root-=1
                put(u,r,root);put(u,v,ct*m)
    for t,tt in zip(rows,rows[1:]):
        for z in (0,1):
            x=2*(7+8*t+(z<<(ell+3)))+1;y=2*(8*tt+(z<<(ell+3)))
            h=(x^y).bit_length()-1;v=variable(n,x,y)
            alpha=(1-2*((x>>(h+1))&1))*(((y>>h)&1)-((x>>h)&1))
            assert abs(alpha)==1
            put(leaf(n,t,1,1,z),v,-alpha)
            put(leaf(n,tt,0,0,z),v,alpha)
    edges=tuple((u,v,c) for (u,v),c in sorted(J.items()))
    return {'D':0,'K':2,'W':32*T-6,'edges':edges,'variables':16*T}


def cycles(n,tail_order=None):
    T=1<<(n-5);ell=n-5;r=16*T-1
    rows=tuple(range(T)) if tail_order is None else tuple(tail_order)
    for t in range(T):
        for z in(0,1):
            v=backbone(n,t,z)
            yield (r,leaf(n,t,0,0,z),v,leaf(n,t,1,1,z)),1,'backbone'
            yield (r,leaf(n,t,1,0,z),v,leaf(n,t,0,1,z)),2,'backbone'
    for t,tt in zip(rows,rows[1:]):
        for z in(0,1):
            x=2*(7+8*t+(z<<(ell+3)))+1;y=2*(8*tt+(z<<(ell+3)))
            yield (r,leaf(n,t,1,1,z),variable(n,x,y),leaf(n,tt,0,0,z)),1,'boundary'


def attaining_mask(graph,n):
    L=1<<(n-2);field=[0]*L
    for u,v,c in graph['edges']:
        assert u<L<=v;field[u]+=c
    # All higher-variable spins are +1; choose each lowest spin independently.
    mask=sum(1<<u for u,f in enumerate(field) if f<0)
    return mask,sum(abs(f) for f in field),field


def packing_certificate(graph,n,keep_cycles=False,tail_order=None):
    J={(u,v):c for u,v,c in graph['edges']};loads=defaultdict(int)
    value=0;parts=defaultdict(int);saved=[]
    for cy,amount,kind in cycles(n,tail_order):
        sign=1
        assert len(set(cy))==4
        for u,v in zip(cy,cy[1:]+cy[:1]):
            key=tuple(sorted((u,v)));sign*=1 if J[key]>0 else -1;loads[key]+=amount
        assert sign==-1;value+=amount;parts[kind]+=amount
        if keep_cycles:saved.append({'cycle':cy,'amount':amount,'kind':kind})
    assert all(v<=abs(J[k]) for k,v in loads.items())
    assert value==(1<<n)//4-2
    unused=[(u,v,abs(c)-loads[u,v]) for u,v,c in graph['edges'] if abs(c)>loads[u,v]]
    assert sum(c for u,v,c in unused)==2
    return {'value':value,'parts':dict(parts),'unused_capacities':unused,'cycles':saved}
