#!/usr/bin/env python3
from itertools import permutations
N=5
edges={frozenset((i,(i+1)%N)) for i in range(N)}
def aut(p): return {frozenset((p[a],p[b])) for a,b in map(tuple,edges)}==edges
autos=[p for p in permutations(range(N)) if aut(p)]
c=list(edges)
def act(p,s): return frozenset(p[i] for i in s)
assert len(autos)==10
assert {act(p,c[0]) for p in autos}==set(c)
assert not [x for x in c if all(act(p,x)==x for p in autos)]
print("Aut(C5) size:",len(autos)); print("PASS")
