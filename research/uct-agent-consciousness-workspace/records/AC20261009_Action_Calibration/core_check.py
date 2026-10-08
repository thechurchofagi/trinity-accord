#!/usr/bin/env python3
"""Compact independent AC20261009 checks, not a phenomenal assay."""
from itertools import permutations, product
from collections import defaultdict, Counter
from fractions import Fraction as F
from math import factorial, comb, prod

def act(p,u):
    return sum(((u>>i)&1)<<j for i,j in enumerate(p))

def inspect(probes):
    n=4
    ps=list(permutations(range(n)))
    concrete=(2,0,3,1)
    ys=tuple(act(concrete,u) for u in probes)
    posterior=[p for p in ps if tuple(act(p,u) for u in probes)==ys]
    A=defaultdict(list);B=defaultdict(list)
    for i in range(n):
        A[tuple((u>>i)&1 for u in probes)].append(i)
        B[tuple((y>>i)&1 for y in ys)].append(i)
    assert A.keys()==B.keys()
    assert len(posterior)==prod(factorial(len(b)) for b in A.values())
    success=[]
    for g in range(16):
        brute=max(F(sum(act(p,u)==g for p in posterior),len(posterior)) for u in range(16))
        theory=prod(F(1,comb(len(b),sum((g>>j)&1 for j in b))) for b in B.values())
        assert brute==theory
        success.append(brute)
    return len(posterior),sum(success[1<<j] for j in range(4))/4,success[15]

cases=[inspect(p) for p in [(),(15,15),(12,12),(12,10)]]
assert cases==[(24,F(1,4),F(1)),(24,F(1,4),F(1)),(4,F(1,2),F(1)),(1,F(1),F(1))]

# Exhaustively compare response-table equivalence with task-stabilizer count.
n=3
ps=list(permutations(range(n)))
for mask in range(256):
    goals=[g for g in range(8) if (mask>>g)&1]
    behaviors=set()
    for p in ps:
        inv=tuple(p.index(j) for j in range(n))
        behaviors.add(tuple(act(inv,g) for g in goals))
    groups=Counter(tuple((g>>j)&1 for g in goals) for j in range(n))
    assert len(behaviors)==factorial(n)//prod(factorial(v) for v in groups.values())

for p,a,b in product(ps,repeat=3):
    transported=tuple(b[p[a.index(i)]] for i in range(n))
    for u in range(8):
        assert act(transported,act(a,u))==act(b,act(p,u))

prior={(0,1):F(9,10),(1,0):F(1,10)}
score=sum(w*F(sum(act(p,1<<j)==1<<j for j in range(2)),2) for p,w in prior.items())
assert score==F(9,10)>F(1,2)
assert all(act((1,2,3,0),1<<j)!=1<<j for j in range(4))
print('CORE PASS: four calibration regimes, 256 goal families, 1728 covariance equalities, failure controls')
print('Finite noiseless mathematical checks only; no subjective experience measured.')
