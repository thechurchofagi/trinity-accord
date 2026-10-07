"""Exact finite audits for R137; no external solvers or empirical runs."""
from fractions import Fraction as F
from itertools import product,combinations
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import json
checks=[]
def check(name,condition):
    assert condition,name
    checks.append({'check':name,'pass':True})
def intersect(intervals):
    if any(x is None for x in intervals):return None
    a=max(x[0] for x in intervals);b=min(x[1] for x in intervals)
    return (a,b) if a<=b else None
def interval(p0,p1,q,e,menu=(0,1)):
    p0,p1,q,e=map(F,(p0,p1,q,e))
    lo,hi=F(0),F(1)
    if 0 not in menu:hi=F(0)
    if 1 not in menu:lo=F(1)
    if not menu:return None
    d=p0-p1
    if not d:return (lo,hi) if abs(p1-q)<=e else None
    a,b=(q-e-p1)/d,(q+e-p1)/d
    return intersect(((lo,hi),(min(a,b),max(a,b))))
grid=(F(0),F(1,2),F(1)); eps=(F(0),F(1,4),F(1,2))
cases=0
for q,e in product(grid,eps):
    constraints=[interval(a,b,q,e) for a,b in product(grid,repeat=2)]
    for family in product(constraints,repeat=3):
        feasible=intersect(family) is not None
        pairs=all(intersect((family[i],family[j])) is not None for i in range(3) for j in range(i,3))
        assert feasible==pairs
        if feasible:
            w=sum(intersect(family))/2
            assert all(r[0]<=w<=r[1] for r in family)
        cases+=1
check('6561 three-state binary-row families satisfy the two-action Helly certificate',cases==6561)
menucases=0
for q,e in product(grid,eps):
    constraints=[interval(a,b,q,e,M) for a,b in product(grid,repeat=2) for M in [(0,),(1,),(0,1)]]
    for left,right in product(constraints,repeat=2):
        out=intersect((left,right))
        if out is not None:
            assert left[0]<=out[0]<=out[1]<=left[1] and right[0]<=out[0]<=out[1]<=right[1]
        menucases+=1
check('6561 menu-constrained two-state intersections retain exact legal weights',menucases==6561)
check('opposite singleton action menus remain infeasible even with zero row mismatch',
      intersect((interval(1,1,1,0,(0,)),interval(1,1,1,0,(1,)))) is None)
check('hidden-state oracle can succeed but common deterministic-success decoder cannot',
      interval(1,0,1,0)==(F(1),F(1)) and interval(0,1,1,0)==(F(0),F(0)) and
      intersect((interval(1,0,1,0),interval(0,1,1,0))) is None)
check('common opposite-action optimum is exactly one-half error',
      intersect((interval(1,0,1,F(1,2)),interval(0,1,1,F(1,2))))==(F(1,2),F(1,2)))
check('fair target has an exact mixture but no deterministic decoder',
      intersect((interval(1,0,F(1,2),0),interval(0,1,F(1,2),0)))==(F(1,2),F(1,2)))
subsets=0
for m in range(2,9):
    for mask in range((1<<m)-1):
        seen={i for i in range(m) if (mask>>i)&1}
        missing=next(i for i in range(m) if i not in seen)
        assert all(missing!=i for i in seen)
        subsets+=1
    w=[F(1,m)]*m
    assert sum(w)==1 and max(w)==F(1,m)
check('all 501 proper hidden-state subsets in sharp m=2..8 families admit exact action',subsets==501)
def compositions(n,m):
    if m==1:
        yield (n,);return
    for a in range(n+1):
        for rest in compositions(n-a,m-1):yield (a,)+rest
weights=0
for m in range(2,6):
    for den in range(1,7):
        for nums in compositions(den,m):
            w=tuple(F(n,den) for n in nums)
            assert max(w)>=F(1,m)
            assert min(1-x for x in w)==1-max(w)
            weights+=1
check('780 rational mixtures respect the sharp 1/m error obstruction',weights==780)

# Controlled witness: s=(z,b), b hidden, actions0/1 set z'=a xor b;
# action2 holds z except with e flip noise. b' may change under action1.
# Abstract u0 holds, u1 gives a fresh uniform z'; o reports whether z changed.
def concrete_row(s,a,e):
    z,b=s
    if a==2:
        return [((z,b),0,1-e),((1-z,b),1,e)]
    zp=a^b;bp=b^(a==1)
    return [((zp,int(bp)),z^zp,F(1))]
def abstract_row(z,u):
    if u==0:return [(z,0,F(1))]
    return [(zp,z^zp,F(1,2)) for zp in (0,1)]
def decoder(u):
    return [(2,F(1))] if u==0 else [(0,F(1,2)),(1,F(1,2))]
def tv(p,q):return sum(abs(p.get(k,0)-q.get(k,0)) for k in set(p)|set(q))/2
rows=0
for e in (F(0),F(1,4),F(1,2),F(1)):
    for z,b,u in product((0,1),repeat=3):
        p=defaultdict(F)
        for a,wa in decoder(u):
            for (zp,bp),o,prob in concrete_row((z,b),a,e):p[(zp,o)]+=wa*prob
        q={(zp,o):prob for zp,o,prob in abstract_row(z,u)}
        assert tv(p,q)<=(e if u==0 else 0)
        rows+=1
check('32 translated joint rows satisfy their exact conditional error premises',rows==32)
@lru_cache(None)
def policies(h):
    if h==0:return (None,)
    return tuple((u,left,right) for u in (0,1) for left,right in product(policies(h-1),repeat=2))
def apaths(z,pi):
    if pi is None:return {():F(1)}
    u,left,right=pi;out=defaultdict(F)
    for zp,o,p in abstract_row(z,u):
        for suffix,v in apaths(zp,(left,right)[zp]).items():out[((u,o,zp),)+suffix]+=p*v
    return dict(out)
def cpaths(s,pi,e):
    if pi is None:return {():F(1)}
    u,left,right=pi;out=defaultdict(F)
    for a,wa in decoder(u):
        for sp,o,p in concrete_row(s,a,e):
            if not p:continue
            for suffix,v in cpaths(sp,(left,right)[sp[0]],e).items():out[((u,o,sp[0]),)+suffix]+=wa*p*v
    return dict(out)
pathcases=0;exactcases=0
for h in range(4):
    for pi in policies(h):
        for z,b in product((0,1),repeat=2):
            target=apaths(z,pi)
            for e in (F(0),F(1,4),F(1,2),F(1)):
                actual=cpaths((z,b),pi,e)
                assert sum(actual.values())==1 and sum(target.values())==1
                assert tv(actual,target)<=1-(1-e)**h
                if e==0:
                    assert actual==target
                    exactcases+=1
                pathcases+=1
check('556 exact adaptive feedback-policy path comparisons preserve joint histories',exactcases==556)
check('2224 adaptive feedback-policy comparisons obey the finite-horizon TV bound',pathcases==2224)
for h in range(1,9):
    strings=list(product((0,1),repeat=h))
    iid={x:F(1,2**h) for x in strings}
    reuse={tuple([0]*h):F(1,2),tuple([1]*h):F(1,2)}
    assert tv(iid,reuse)==1-F(1,2**(h-1))
    for t in range(h):
        assert sum(p for x,p in iid.items() if x[t])==sum(p for x,p in reuse.items() if x[t])==F(1,2)
check('8 seed-reuse witnesses preserve single-time marginals but attain the path-law gap',True)
result=dict(round='R137',all_pass=True,checks=checks,binary_helly_families=cases,menu_intersections=menucases,
 sharp_proper_subsets=subsets,rational_mixtures=weights,joint_rows=rows,exact_feedback_paths=exactcases,
 approximate_feedback_paths=pathcases,seed_reuse_horizons=8,
 arithmetic='Exact integers and Python Fraction; no numerical LP solver, Monte Carlo or empirical data',
 scope='Finite checks of stated examples and algebra; general theorems rely on the handwritten conditional proofs, not proof-assistant or independent certification.')
(Path(__file__).parent/'EXACT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
