#!/usr/bin/env python3
"""Exact verification of the Q2 optimal-seed tensor obstruction.

The all-dimensional proof is in Q2_TENSOR_OBSTRUCTION.md.  This verifier uses
only integer ranks and scores and exhausts every sequence of the four optimal
Q2 seeds through m=5 (dimension 10).
"""
from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path
import time

OPTIMAL_CODES = (2, 3, 4, 5)
# code -> (low-coordinate input reflection e, output pair complement c)
PARAMETERS = {5: (0, 0), 3: (1, 0), 2: (0, 1), 4: (1, 1)}


def q2_rank(code: int) -> list[int]:
    signs = [1 if (code >> u) & 1 else -1 for u in range(3)]
    def visit(u: int, lo: int, hi: int) -> list[int]:
        if hi-lo == 1:
            return [lo]
        mid=(lo+hi)//2
        left=visit(2*u+1,lo,mid); right=visit(2*u+2,mid,hi)
        return left+right if signs[u] == 1 else right+left
    order=visit(0,0,4); rank=[0]*4
    for i,x in enumerate(order): rank[x]=i
    return rank


def phi(a: int, b: int) -> int:
    return 2*a + (1 ^ a ^ b)


def tensor_rank(x: int, codes: tuple[int, ...]) -> int:
    value=0
    for t,code in enumerate(codes):
        e,c=PARAMETERS[code]
        a=(x>>(2*t+1))&1; b=(x>>(2*t))&1
        digit=phi(a,b^e)
        if c: digit=3-digit
        value += digit << (2*t)
    return value


def witness_weights(codes: tuple[int, ...]) -> list[int]:
    m=len(codes); significance=[]; reflected=[]
    # Most significant sweep coordinate to least significant.
    for t,code in enumerate(codes):
        e,c=PARAMETERS[code]
        significance.append(2*t); reflected.append(e)
    for t in reversed(range(m)):
        e,c=PARAMETERS[codes[t]]
        significance.append(2*t+1); reflected.append(c)
    w=[0]*(2*m)
    for pos,(j,flip) in enumerate(zip(significance,reflected)):
        w[j]=(-1 if flip else 1) << (2*m-1-pos)
    return w


def score_order(n: int, w: list[int]) -> list[int]:
    scores=[sum(w[j]*((x>>j)&1) for j in range(n)) for x in range(1<<n)]
    assert len(set(scores)) == 1<<n
    return sorted(range(1<<n),key=scores.__getitem__)


def witness_order(codes: tuple[int, ...]) -> list[int]:
    m=len(codes); significance=[]; reflected=[]
    for t,code in enumerate(codes):
        e,c=PARAMETERS[code]; significance.append(2*t); reflected.append(e)
    for t in reversed(range(m)):
        e,c=PARAMETERS[codes[t]]; significance.append(2*t+1); reflected.append(c)
    order=[]
    for q in range(1<<(2*m)):
        x=0
        for pos,(j,flip) in enumerate(zip(reversed(significance),reversed(reflected))):
            x |= (((q>>pos)&1)^flip)<<j
        order.append(x)
    return order


def runs(values: list[int]) -> int:
    signs=[b>a for a,b in zip(values,values[1:])]
    return 1+sum(a!=b for a,b in zip(signs,signs[1:]))


def check_small_optimum() -> dict:
    orders=set()
    for w0 in range(-12,13):
        for w1 in range(-12,13):
            if w0 and w1 and abs(w0)!=abs(w1):
                orders.add(tuple(score_order(2,[w0,w1])))
    assert len(orders)==8
    rows=[]
    for code in range(8):
        rank=q2_rank(code)
        rlc=min(runs([rank[x] for x in order]) for order in orders)
        rows.append({'code':code,'rank':rank,'RLC':rlc})
    assert tuple(row['code'] for row in rows if row['RLC']==2)==OPTIMAL_CODES
    for code,(e,c) in PARAMETERS.items():
        expected=[]
        for x in range(4):
            a=(x>>1)&1; b=x&1; value=phi(a,b^e)
            expected.append(3-value if c else value)
        assert expected==q2_rank(code)
    return {'generic_additive_orders':len(orders),'all_tree_orders':rows,
            'optimal_codes':list(OPTIMAL_CODES)}


def check_tensor_powers() -> dict:
    rows=[]; digest=hashlib.sha256()
    for m in range(1,6):
        target=(1<<(m+1))-1; tested=0
        min_runs=1<<(2*m); max_runs=0
        for codes in itertools.product(OPTIMAL_CODES,repeat=m):
            w=witness_weights(codes); order=witness_order(codes)
            if tested==0:
                assert order==score_order(2*m,w)
            rank=[tensor_rank(x,codes) for x in range(1<<(2*m))]
            assert sorted(rank)==list(range(1<<(2*m)))
            actual=runs([rank[x] for x in order])
            assert actual==target
            digest.update(bytes(codes)+actual.to_bytes(4,'big'))
            min_runs=min(min_runs,actual); max_runs=max(max_runs,actual); tested+=1
        rows.append({'m':m,'dimension':2*m,'vertices':1<<(2*m),
                     'seed_sequences':tested,'expected_and_actual_runs':target,
                     'density':f'{target}/{1<<(2*m)}'})
        print('m',m,'passed',tested,flush=True)
    return {'rows':rows,'cases':sum(r['seed_sequences'] for r in rows),
            'digest_sha256':digest.hexdigest()}


def main() -> None:
    started=time.monotonic()
    result={'q2':check_small_optimum(),'tensor':check_tensor_powers(),
            'violations':0}
    result['elapsed_seconds']=round(time.monotonic()-started,3)
    Path(__file__).with_name('q2_tensor_verification.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
