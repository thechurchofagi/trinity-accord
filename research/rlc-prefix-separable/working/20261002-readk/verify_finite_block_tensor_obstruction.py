#!/usr/bin/env python3
"""Exact checks for the mixed finite-block tree-tensor obstruction.

The theorem is analytic. This program independently builds each factor rank by
recursive traversal, realizes the proposed sweep by strict integer scores, and
checks the exact run formula on exhaustive and seeded-random cases.
"""
from __future__ import annotations
import hashlib, itertools, json, random, time
from functools import lru_cache
from pathlib import Path

SEED=202610030113

@lru_cache(maxsize=None)
def tree_rank(d:int, code:int)->tuple[int,...]:
    def visit(u:int,lo:int,hi:int)->list[int]:
        if hi-lo==1:return [lo]
        mid=(lo+hi)//2
        left=visit(2*u+1,lo,mid);right=visit(2*u+2,mid,hi)
        return left+right if (code>>u)&1 else right+left
    order=visit(0,0,1<<d);rank=[0]*len(order)
    for i,x in enumerate(order):rank[x]=i
    return tuple(rank)

def tensor_rank(x:int,dims:tuple[int,...],codes:tuple[int,...])->int:
    value=0;coord=0;place=1
    for d,code in zip(dims,codes):
        mask=(1<<d)-1
        value += place*tree_rank(d,code)[(x>>coord)&mask]
        coord += d;place <<= d
    return value

def witness(dims:tuple[int,...],codes:tuple[int,...]):
    offsets=[];s=0
    for d in dims:offsets.append(s);s+=d
    significance=[];flips=[]
    # All non-root coordinates are outer variables; their order is irrelevant.
    for off,d in zip(offsets,dims):
        for j in range(d-1):significance.append(off+j);flips.append(0)
    # Root variables are the inner counter, most significant factor first.
    for off,d,code in reversed(list(zip(offsets,dims,codes))):
        significance.append(off+d-1)
        flips.append(0 if (code&1) else 1)
    n=sum(dims);weights=[0]*n
    for pos,(j,flip) in enumerate(zip(significance,flips)):
        weights[j]=(-1 if flip else 1) << (n-1-pos)
    scores=[sum(weights[j]*((x>>j)&1) for j in range(n)) for x in range(1<<n)]
    assert len(set(scores))==1<<n
    return sorted(range(1<<n),key=scores.__getitem__),weights

def runs(a:list[int])->int:
    s=[b>a for a,b in zip(a,a[1:])]
    return 1+sum(x!=y for x,y in zip(s,s[1:]))

def classify_q3():
    # After reflecting coordinates and sorting absolute weights, the only Q3
    # chamber decision is whether the largest magnitude exceeds the other two.
    orders=set()
    for prototype in ((1,2,4),(2,3,4)):
        for perm in itertools.permutations(range(3)):
            for mask in range(8):
                w=[0]*3
                for i,j in enumerate(perm):w[j]=prototype[i]*(-1 if (mask>>j)&1 else 1)
                scores=[sum(w[j]*((x>>j)&1) for j in range(3)) for x in range(8)]
                assert len(set(scores))==8
                orders.add(tuple(sorted(range(8),key=scores.__getitem__)))
    assert len(orders)==96
    histogram={};max_rlc=0;max_codes=[]
    for code in range(128):
        rank=tree_rank(3,code);rlc=min(runs([rank[x] for x in order]) for order in orders)
        histogram[str(rlc)]=histogram.get(str(rlc),0)+1
        if rlc>max_rlc:max_rlc,max_codes=rlc,[code]
        elif rlc==max_rlc:max_codes.append(code)
    assert max_rlc==4 and len(max_codes)==8
    return {'complete_generic_additive_orders':len(orders),'tree_orientations':128,
            'RLC_histogram':histogram,'maximum_RLC':max_rlc,'maximizing_codes':max_codes}

def check_case(dims,codes,digest):
    n=sum(dims);m=len(dims);order,weights=witness(dims,codes)
    rank=[tensor_rank(x,dims,codes) for x in range(1<<n)]
    assert sorted(rank)==list(range(1<<n))
    actual=runs([rank[x] for x in order]);expected=(1<<(n-m+1))-1
    assert actual==expected
    digest.update(json.dumps([dims,codes,actual],separators=(',',':')).encode())
    return actual,weights

def main():
    started=time.monotonic();digest=hashlib.sha256();rows=[];cases=0
    exhaustive=[]
    for m in range(1,5):exhaustive.append((2,)*m)
    exhaustive += [(3,2),(2,3),(3,3)]
    for dims in exhaustive:
        spaces=[range(1<<((1<<d)-1)) for d in dims]
        count=0;expected=(1<<(sum(dims)-len(dims)+1))-1
        example=None
        for codes in itertools.product(*spaces):
            actual,w=check_case(dims,codes,digest)
            if example is None:example={'codes':list(codes),'weights':w}
            count+=1
        rows.append({'dims':list(dims),'coverage':'all factor orientations',
                     'cases':count,'expected_and_actual_runs':expected,'example':example})
        cases+=count;print('exhaustive',dims,count,flush=True)
    rng=random.Random(SEED);sampled=0
    for _ in range(500):
        m=rng.randint(1,5);dims=tuple(rng.randint(1,6) for _ in range(m))
        if sum(dims)>15:continue
        codes=tuple(rng.randrange(1<<((1<<d)-1)) for d in dims)
        check_case(dims,codes,digest);sampled+=1
    result={'seed':SEED,'q3_classification':classify_q3(),
            'theorem_formula':'2^(n-m+1)-1',
            'exhaustive':rows,'exhaustive_cases':cases,
            'sampled_mixed_cases':sampled,'violations':0,
            'digest_sha256':digest.hexdigest(),
            'elapsed_seconds':round(time.monotonic()-started,3)}
    Path(__file__).with_name('finite_block_tensor_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
