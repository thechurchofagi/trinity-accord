#!/usr/bin/env python3
"""Exact finite validation of task-safe reversible transport.
Standard library only. Tests mathematical contracts, not phenomenal experience.
"""
from __future__ import annotations
import argparse, itertools as it, json, math
from collections import Counter, deque
from fractions import Fraction as F
from pathlib import Path

Perm = tuple[int, ...]
def inv(p: Perm) -> Perm:
    out=[0]*len(p)
    for i,j in enumerate(p):out[j]=i
    return tuple(out)
def compose(p: Perm,q: Perm) -> Perm:
    return tuple(p[q[i]] for i in range(len(p)))
def group(gens: tuple[Perm,...],n: int) -> tuple[Perm,...]:
    ident=tuple(range(n));seen={ident};todo=[ident]
    for h in todo:
        for g in gens:
            z=compose(g,h)
            if z not in seen:seen.add(z);todo.append(z)
    return tuple(sorted(seen))
def orbits(G: tuple[Perm,...],n: int) -> tuple[tuple[int,...],...]:
    unseen=set(range(n));out=[]
    while unseen:
        x=min(unseen);o=tuple(sorted({g[x] for g in G}));out.append(o);unseen.difference_update(o)
    return tuple(out)
def reader(f: tuple, p: Perm) -> tuple:
    pi=inv(p);return tuple(f[pi[y]] for y in range(len(p)))
def brute_decoder(f: tuple, routes: tuple[Perm,...]) -> tuple | None:
    # Independent enumeration of decoder tables, not invariance calculation.
    ys=tuple(sorted(set(f)))
    for d in it.product(ys,repeat=len(f)):
        if all(d[p[x]]==f[x] for p in routes for x in range(len(f))):return d
    return None
def partitions(n: int):
    if n==0:yield ();return
    for p in partitions(n-1):
        for j in range(max(p,default=-1)+2):yield p+(j,)
def brute_tags(f: tuple,routes: tuple[Perm,...]) -> int:
    # Try all set partitions of route identities, then enumerate decoders per cell.
    for labels in sorted(set(partitions(len(routes))), key=lambda p:max(p)+1):
        if all(brute_decoder(f,tuple(p for p,c in zip(routes,labels) if c==label)) is not None
               for label in set(labels)):return len(set(labels))
    raise AssertionError('Full route label must suffice')
def optimal(f: tuple,routes: tuple[Perm,...]) -> F:
    counts={y:Counter() for y in range(len(f))}
    for p in routes:
        for x in range(len(f)):counts[p[x]][f[x]]+=1
    return F(sum(max(v.values()) for v in counts.values()),len(f)*len(routes))
def rank_mod(A: list[list[int]],q: int) -> int:
    A=[list(r) for r in A]
    if not A:return 0
    rank=0
    for c in range(len(A[0])):
        pivot=next((r for r in range(rank,len(A)) if A[r][c]%q),None)
        if pivot is None:continue
        A[rank],A[pivot]=A[pivot],A[rank]
        v=pow(A[rank][c]%q,-1,q);A[rank]=[(v*x)%q for x in A[rank]]
        for r in range(len(A)):
            if r!=rank:
                v=A[r][c]%q;A[r]=[(x-v*y)%q for x,y in zip(A[r],A[rank])]
        rank+=1
        if rank==len(A):break
    return rank

def run() -> dict:
    n=4;I=tuple(range(n));ps=tuple(it.permutations(range(n)));fs=tuple(it.product((0,1),repeat=n))
    counts=Counter();counterexamples=[]
    for p,q in it.product(ps,repeat=2):
        routes=tuple(dict.fromkeys((I,p,q)))
        G=group((p,q),n);O=orbits(G,n)
        for f in fs:
            truth=brute_decoder(f,routes) is not None
            invariant=all(f[g[x]]==f[x] for g in G for x in range(n))
            assert truth==invariant
            counts['route_target_universal_checks']+=1
            if len(routes)<=3:
                expected=len({reader(f,g) for g in routes})
                assert brute_tags(f,routes)==expected
                counts['minimal_tag_partition_checks']+=1
            # Uniform complete group, direct joint-count Bayes optimization.
            predicted=sum(max(Counter(f[x] for x in o).values()) for o in O)
            assert optimal(f,G)==F(predicted,n)
            counts['group_orbit_bayes_checks']+=1
            # Pairwise approximate obstruction is tight under equal routes.
            delta=F(sum(a!=b for a,b in zip(reader(f,p),reader(f,q))),n)
            assert optimal(f,(p,q))==1-delta/2
            counts['pairwise_error_bound_checks']+=1
        assert sum(all(f[g[x]]==f[x] for g in G for x in range(n)) for f in fs)==2**len(O)
        counts['maximal_invariant_algebra_checks']+=1
    # Actual coordinate transport on BOTH ends, including target/reader orientation.
    for a,b,p in it.product(ps,repeat=3):
        routes=(I,p);rr=tuple(compose(b,compose(t,inv(a))) for t in routes)
        for f in ((0,0,1,1),(0,1,1,0)):
            ff=tuple(f[inv(a)[x]] for x in range(n))
            assert len({reader(f,t) for t in routes})==len({reader(ff,t) for t in rr})
            assert optimal(f,routes)==optimal(ff,rr)
            counts['coordinate_covariance_checks']+=1
    # Noncommuting coordinate swaps: three retained registers, source dimension three.
    bits=tuple(it.product((0,1),repeat=3));idx={b:i for i,b in enumerate(bits)}
    G3=tuple(tuple(idx[tuple(x[j] for j in p)] for x in bits) for p in it.permutations(range(3)))
    swap01=tuple(idx[(x[1],x[0],x[2])] for x in bits)
    swap12=tuple(idx[(x[0],x[2],x[1])] for x in bits)
    assert set(group((swap01,swap12),8))==set(G3)
    assert compose(swap01,swap12)!=compose(swap12,swap01)
    fbit=tuple(x[0] for x in bits);fpar=tuple(sum(x)%2 for x in bits)
    fweight=tuple(sum(x) for x in bits);fid=tuple(range(8))
    classes={k:len({reader(f,p) for p in G3}) for k,f in [('first_bit',fbit),('parity',fpar),('weight',fweight),('whole_state',fid)]}
    assert classes=={'first_bit':3,'parity':1,'weight':1,'whole_state':6}
    accuracy={k:optimal(f,G3) for k,f in [('first_bit',fbit),('parity',fpar),('weight',fweight),('whole_state',fid)]}
    assert accuracy=={'first_bit':F(3,4),'parity':F(1),'weight':F(1),'whole_state':F(1,2)}
    # Verify the full quotient has four classes, not only two parity classes.
    O3=orbits(G3,8);assert sorted(map(len,O3))==[1,1,3,3]
    invariant_binary=sum(all(f[g[x]]==f[x] for g in G3 for x in range(8)) for f in it.product((0,1),repeat=8))
    assert invariant_binary==16
    # Finite field fixed dual-space formula for all 2x2 invertible generators in F2/F3.
    fields={}
    for q in (2,3):
        vectors=tuple(it.product(range(q),repeat=2));ii={x:i for i,x in enumerate(vectors)}
        matrices=[]
        for a in it.product(range(q),repeat=4):
            M=[list(a[:2]),list(a[2:])]
            if rank_mod(M,q)==2:matrices.append(M)
        nc=0
        for A,B in it.product(matrices,repeat=2):
            # W=sum im(A-I)+im(B-I); concatenate matrices horizontally.
            W=[[(M[i][j]-int(i==j))%q for M in (A,B) for j in range(2)] for i in range(2)]
            dim=2-rank_mod(W,q)
            admissible=[]
            for l in vectors:
                if all(sum(l[i]*M[i][j] for i in range(2))%q==l[j] for M in (A,B) for j in range(2)):
                    admissible.append(l)
            assert len(admissible)==q**dim;nc+=1
        fields[str(q)]={'invertible_matrices':len(matrices),'generator_pair_checks':nc}
    # A source-correlated route or route-readable clock is a different information contract.
    flip=(1,0);f=(0,1);routes=(tuple(range(2)),flip)
    assert brute_decoder(f,routes) is None
    assert all((y ^ p)==x for p in (0,1) for x in (0,1) for y in [routes[p][x]])
    counterexamples.append('A route/clock bit restores exact identity, so the untagged impossibility cannot be applied when route history is accessible.')
    counterexamples.append('Nonlinear Hamming weight has four invariant classes although the invariant linear target subspace has dimension one.')
    # Full source on every route is needed for the min-tag equivalence.
    f=(0,1,1,0);T=(1,0,2,3);supports=((0,2),(0,3));d=(0,0,1,0)
    assert all(d[p[x]]==f[x] for p,S in zip((I,T),supports) for x in S)
    assert len({reader(f,p) for p in (I,T)})==2
    counterexamples.append('Restricted route-dependent source domains can need fewer labels than the full-domain formula; keep full-support/route-domain assumptions.')
    return {'status':'PASS','verification_kind':'exact_finite_models_not_experience_measurement',
            'counts':dict(counts),'finite_field_tests':fields,
            'three_register_orbits':[list(o) for o in O3],
            'route_tags_required':classes,'optimal_untagged_accuracy':{k:str(v) for k,v in accuracy.items()},
            'invariant_binary_targets':invariant_binary,'retained_counterexamples':counterexamples}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path('MODEL_RESULTS.json'));args=ap.parse_args()
    result=run();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
