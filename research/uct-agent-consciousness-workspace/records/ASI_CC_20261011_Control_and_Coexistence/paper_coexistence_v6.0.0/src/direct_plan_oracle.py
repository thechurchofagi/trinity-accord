#!/usr/bin/env python3
"""Independent action-level oracle for small coupled-fault instances.

For each report observation and labeled bank allocation, enumerate every armed
channel set and test it against every compatible actual fault world. This avoids
using the candidate-union shortcut and avoids the reserve formula inside action
verification. Constructed finite models only, no network/model/hardware calls.
"""
from itertools import combinations, product
from pathlib import Path
import argparse, json
from coupled_budget import subsets, frontier, joint_world_oracle, safe


def labeled_compositions(t,m):
    if m==1:
        yield (t,); return
    for x in range(t+1):
        for rest in labeled_compositions(t-x,m-1): yield (x,)+rest


def worlds_by_report(n,k,f,d,b):
    states=tuple(combinations(range(n),k)); cells={}; count=0
    for si,S in enumerate(states):
        for A in subsets(d,f):
            for B in subsets(b,f-len(A)):
                for vals in product(range(len(states)), repeat=len(A)):
                    z=[si]*d
                    for a,v in zip(A,vals): z[a]=v
                    # Deduplicate worlds with the same effect; don't collapse S or B.
                    cells.setdefault(tuple(z),set()).add((frozenset(S),frozenset(B)))
                    count+=1
    return cells,count


def direct_safe(caps,cells,plans):
    witnesses={}
    for z,worlds in cells.items():
        good=None
        for P in plans:
            if all(S<=P and sum(c for i,c in enumerate(caps) if i not in B)>=len(P)
                   for S,B in worlds):
                good=P;break
        if good is None:return False, None
        witnesses[str(z)]=sorted(good)
    return True,witnesses


def run():
    configs=((2,1,1,2,2),(3,1,1,2,2),(4,2,1,2,3),(3,1,1,1,2),
             (3,2,1,3,2),(3,1,0,1,2),(3,1,1,0,2))
    out=[];checked=0
    for n,k,f,d,b in configs:
        cells,w=worlds_by_report(n,k,f,d,b)
        constraints=joint_world_oracle(n,k,f,d,b)['constraints']
        predicted=frontier(n,k,f,d,b)['minimum']
        plans=tuple(frozenset(p) for size in range(n+1) for p in combinations(range(n),size))
        got=None;nc=0;selected=None
        for total in range(predicted+2):
            for caps in labeled_compositions(total,b):
                passed,policy=direct_safe(caps,cells,plans)
                assert passed==safe(caps,constraints),(n,k,f,d,b,caps)
                if passed and got is None:got=total;selected=caps
                nc+=1;checked+=1
        assert got==predicted
        out.append({'parameters':[n,k,f,d,b],'generated_worlds':w,'observations':len(cells),
                    'labeled_allocations_checked':nc,'direct_minimum':got,'formula_minimum':predicted,
                    'one_direct_witness':selected})
    return {'version':'PR-v6.0.0','scope':'Direct finite action/world verification; no empirical systems',
            'configs':out,'labeled_allocations_checked':checked,'assertions':'PASS',
            'method':'For every observed vector enumerate all P subsets and test all actual S,B worlds; independent of candidate-union criterion.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='direct_plan_results.json');a=ap.parse_args()
    r=run();p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
