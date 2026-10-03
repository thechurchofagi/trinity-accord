#!/usr/bin/env python3
"""Reusable query-tree geometry and exact signed comparison bookkeeping.

No all-dimensional constant-density theorem is asserted here.
"""
import random
from itertools import product

def query_trees(free, node=1, forced=None):
    if not free:
        yield {}; return
    for j in free if forced is None else (forced,):
        rest=tuple(k for k in free if k!=j)
        if not rest:
            yield {node:j}; continue
        pairs=((a,b) for a in rest for b in rest if a!=b) if len(rest)>=2 else ((rest[0],rest[0]),)
        for a,b in pairs:
            for left,right in product(query_trees(rest,2*node,a),query_trees(rest,2*node+1,b)):
                yield {node:j,**left,**right}

def random_queries(n,rng):
    q={}
    def visit(free,u,forced=None):
        if not free:return
        j=rng.choice(free) if forced is None else forced;q[u]=j
        rest=tuple(k for k in free if k!=j)
        if not rest:return
        a=rng.choice(rest);b=rng.choice(tuple(k for k in rest if k!=a)) if len(rest)>1 else a
        visit(rest,2*u,a);visit(rest,2*u+1,b)
    visit(tuple(range(n)),1);return q

def rank_table(q,n,bits=None):
    bits={} if bits is None else bits
    rr=[]
    for x in range(1<<n):
        u=1;r=0
        for _ in range(n):
            b=(x>>q[u])&1;r=2*r+(b^bits.get(u,0));u=2*u+b
        rr.append(r)
    assert sorted(rr)==list(range(1<<n));return rr

def validate(q,n):
    def visit(free,u):
        if not free:assert u not in q;return
        assert q[u] in free
        rem=tuple(k for k in free if k!=q[u])
        if len(rem)>=2:assert q[2*u]!=q[2*u+1]
        visit(rem,2*u);visit(rem,2*u+1)
    visit(tuple(range(n)),1);assert len(q)==(1<<n)-1

def direct_counts(rr,p):
    s=[1 if rr[b]>rr[a] else -1 for a,b in zip(p,p[1:])]
    R=1+sum(a!=b for a,b in zip(s,s[1:]));closing=1 if rr[p[0]]>rr[p[-1]] else -1
    C=R-1+(s[0]!=closing)+(s[-1]!=closing)
    return R,C

def additive_order(w):
    s=[sum(w[h] for h in range(len(w)) if x>>h&1) for x in range(1<<len(w))]
    if len(set(s))!=len(s):return None
    return sorted(range(len(s)),key=s.__getitem__)

def graph(q,n,p,cyclic=False):
    N=1<<n;rr=rank_table(q,n);a=[rr[x] for x in p]
    aa=a+[a[0]] if cyclic else a
    u=[(N+x)>>((x^y).bit_length()) for x,y in zip(aa,aa[1:])]
    s=[1 if y>x else -1 for x,y in zip(aa,aa[1:])]
    J={};D=0
    total=N if cyclic else N-2
    for i in range(total):
        j=(i+1)%len(u)
        if u[i]==u[j]:
            assert s[i]!=s[j];D+=1
        else:
            e=tuple(sorted((u[i],u[j])));J[e]=J.get(e,0)+s[i]*s[j]
    J={e:v for e,v in J.items() if v};W=sum(abs(v) for v in J.values());K=(total-D-W)//2
    assert 2*K==total-D-W and K>=0 and 1 in u
    labels=sorted(set(u)-{1});baseline=sum((s[i]>0)<<i for i in range(len(s)))
    columns={v:sum((u[i]==v)<<i for i in range(len(s))) for v in labels}
    return {'D':D,'K':K,'q':len(labels),'J':J,'u':u,'s':s,'labels':labels,'word':baseline,'columns':columns}

def exact_orientation_minimum(q,n,p):
    g=graph(q,n,p);N=1<<n;word=g['word'];mask=(1<<(N-2))-1;best=N;bestbits=None;prior=0;bestC=N;bestCbits=None
    baseline=rank_table(q,n);closing=int(baseline[p[0]]>baseline[p[-1]])
    for k in range(1<<g['q']):
        gray=k^(k>>1)
        if k:
            diff=gray^prior;v=g['labels'][diff.bit_length()-1];word^=g['columns'][v]
        R=1+((word^(word>>1))&mask).bit_count()
        if R<best:best=R;bestbits={v:(gray>>i)&1 for i,v in enumerate(g['labels'])}
        full=word|(closing<<(N-1));rotate=(full>>1)|((full&1)<<(N-1));C=(full^rotate).bit_count()
        if C<bestC:bestC=C;bestCbits={v:(gray>>i)&1 for i,v in enumerate(g['labels'])}
        prior=gray
    rr=rank_table(q,n,bestbits);R,C=direct_counts(rr,p);assert R==best
    phi=sum(abs(v) for (a,b),v in g['J'].items() if (bestbits.get(a,0)^bestbits.get(b,0))!=(v<0))
    assert R==1+g['D']+g['K']+phi
    g['min_C']=bestC;g['min_C_bits']=bestCbits
    assert direct_counts(rank_table(q,n,bestCbits),p)[1]==bestC
    return best,C,bestbits,g

def separator(q,n,bits,z):
    c=[0]*n;u=1
    for t in range(n):
        j=q[u];c[j]=(-1 if bits.get(u,0) else 1)*3**(n-1-t);u=2*u+((z>>j)&1)
    return c

def reflect_geometry(q,n,z):
    out={}
    def visit(u,v,free):
        if not free:return
        j=q[u];out[v]=j
        for b in (0,1):visit(2*u+(b^((z>>j)&1)),2*v+b,free-1)
    visit(1,1,n);return out
