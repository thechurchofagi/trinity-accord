"""Exact small checks of profile geometry, coupled abstractions and hard legality."""
from fractions import Fraction as F
from itertools import product, combinations
from functools import lru_cache
from pathlib import Path
import json

checks=[]
def check(name,ok):
    checks.append({'check':name,'pass':bool(ok)})
    if not ok:raise AssertionError(name)

def h(vertices,q):
    return max(q*v[0]+(1-q)*v[1] for v in vertices)

def breaks(vertices):
    out={F(0),F(1)}
    for a,b in combinations(vertices,2):
        slope=(a[0]-a[1])-(b[0]-b[1])
        if slope:
            q=(b[1]-a[1])/slope
            if 0<=q<=1:out.add(q)
    return out

def loss_to_hull(v,D):
    # Minimize the max coordinate deficit over vertices and diagonal crossings
    # of all target segments; in 2D a Pareto boundary optimum uses <=2 vertices.
    choices=list(D)
    for a,b in combinations(D,2):
        da=a[0]-a[1];db=b[0]-b[1]
        if da!=db:
            t=(v[0]-v[1]-db)/(da-db)
            if 0<=t<=1:choices.append(tuple(t*a[i]+(1-t)*b[i] for i in (0,1)))
    return min(max(F(0),v[0]-w[0],v[1]-w[1]) for w in choices)

def directed(C,D):
    return max(loss_to_hull(v,D) for v in C)

def weighted_gap(C,D):
    return max([F(0)]+[h(C,q)-h(D,q) for q in breaks(C)|breaks(D)])

grid=((F(0),F(0)),(F(1),F(0)),(F(0),F(1)),(F(1),F(1)),(F(1,2),F(1,2)))
families=[c for k in range(1,6) for c in combinations(grid,k)]
pairs=0
for C,D in product(families,repeat=2):
    assert directed(C,D)==weighted_gap(C,D)
    pairs+=1
check('961 compact convex profile-set pairs: direct deficiency equals all-weight gap',pairs==961)
C1=(grid[0],grid[1],grid[2]);D1=(grid[0],grid[4])
C2=(grid[0],grid[3]);D2=(grid[0],grid[3],grid[1])
robust=lambda V:min(h(V,q) for q in breaks(V))
check('equal robust score does not imply equal guarantee region',robust(C1)==robust(D1)==F(1,2)
      and directed(C1,D1)==F(1,2) and directed(D1,C1)==0)
check('all nonnegative optima can agree despite different exact profile sets',
      directed(C2,D2)==directed(D2,C2)==0 and grid[1][0]!=grid[1][1])
check('without mixtures support-function domination need not transfer thresholds',
      all(h((grid[4],),q)<=h((grid[1],grid[2]),q) for q in (F(0),F(1,2),F(1)))
      and not any(all(w[i]>=grid[4][i] for i in (0,1)) for w in (grid[1],grid[2])))
# Composition and robust bounds on a declared finite family of sets.
selected=[C1,D1,C2,D2,(grid[0],),(grid[1],),(grid[2],)]
for C,D,E in product(selected,repeat=3):
    assert directed(C,E)<=directed(C,D)+directed(D,E)
for C,D in product(families,repeat=2):
    assert robust(C)<=robust(D)+directed(C,D)
check('directed errors compose on 343 triples',len(selected)**3==343)
check('robust scalar gap respects the directional guarantee bound on all 961 pairs',True)

# Nontrivial state compression alpha(m,x,b)=(m,x), with common total actions.
ACT=(0,1);OBS=(0,1)
def abstract(m,x,a):
    p=F(1) if x else (F(1,4) if a==m else F(3,4))
    return tuple(((m,xp),xp,prob) for xp,prob in ((0,1-p),(1,p)) if prob)

def concrete(eps,m,x,b,a):
    out={}
    for (mp,xp),o,p in abstract(m,x,a):
        key=((mp,xp,1-b),o);out[key]=out.get(key,F(0))+(1-eps)*p
    key=((m,max(x,a^b),1-b),a^b)
    out[key]=out.get(key,F(0))+eps
    return tuple((xp,o,p) for (xp,o),p in out.items() if p)

def tv_rows(left,right):
    return sum(abs(left.get(k,F(0))-right.get(k,F(0))) for k in left.keys()|right.keys())/2

@lru_cache(None)
def trees(H):
    if H==0:return (None,)
    return tuple((a,children) for a in ACT for children in product(trees(H-1),repeat=2))

@lru_cache(None)
def value_abs(m,x,tree):
    if tree is None:return F(x)
    a,children=tree
    return sum(p*value_abs(mp,xp,children[o]) for (mp,xp),o,p in abstract(m,x,a))

@lru_cache(None)
def value_con(eps,m,x,b,tree):
    if tree is None:return F(x)
    a,children=tree
    return sum(p*value_con(eps,mp,xp,bp,children[o])
               for (mp,xp,bp),o,p in concrete(eps,m,x,b,a))

eps_grid=(F(0),F(1,10),F(1,3),F(1))
row_count=policy_count=0
for eps in eps_grid:
    for m,x,b,a in product((0,1),repeat=4):
        raw=concrete(eps,m,x,b,a);left={}
        for (mp,xp,bp),o,p in raw:left[((mp,xp),o)]=left.get(((mp,xp),o),F(0))+p
        right={(s,o):p for s,o,p in abstract(m,x,a)}
        assert sum(left.values())==sum(right.values())==1
        assert tv_rows(left,right)<=eps
        row_count+=1
    for m,x,b in product((0,1),repeat=3):
        for H in range(4):
            bound=1-(1-eps)**H
            for tree in trees(H):
                assert abs(value_con(eps,m,x,b,tree)-value_abs(m,x,tree))<=bound
                policy_count+=1
check('64 joint compressed kernel rows satisfy their exact uniform TV premise',row_count==64)
check('4448 adaptive-policy evaluations respect the finite-horizon error bound',policy_count==4448)
check('zero-error quotient preserves every checked policy exactly',
      all(value_con(F(0),m,x,b,t)==value_abs(m,x,t)
          for m,x,b in product((0,1),repeat=3) for t in trees(3)))
sharp_count=0
for eps in (F(0),F(1,10),F(1,3),F(1,2),F(1)):
    failure=F(1)
    for H in range(9):
        success=1-failure
        assert success==1-(1-eps)**H
        assert success<=min(F(1),H*eps)
        failure*=1-eps
        sharp_count+=1
check('45 absorbing-goal witnesses attain the sharp bound, including horizon zero',sharp_count==45)

# Partial menus agree statewise, but rare hidden states alter history legality.
def legal_value(delta,totalized=False):
    menus={'start':{'p'},'good':{'a'},'bad':{'a'} if totalized else set(),'goal':set()}
    def K(s,a):
        if s=='start':return tuple((xp,p) for xp,p in [('good',1-delta),('bad',delta)] if p)
        if s=='good':return (('goal',F(1)),)
        if s=='bad' and totalized:return (('bad',F(1)),)
        raise ValueError((s,a))
    @lru_cache(None)
    def profiles(B,H):
        out={tuple(F(s=='goal') for s in B)}
        if H==0:return out
        enabled=set.intersection(*(menus[s] for s in B))
        for a in enabled:
            nextB=tuple(sorted({sp for s in B for sp,p in K(s,a) if p}))
            for child in profiles(nextB,H-1):
                scores=dict(zip(nextB,child))
                out.add(tuple(sum(p*scores[sp] for sp,p in K(s,a)) for s in B))
        return out
    return max(v[0] for v in profiles(('start',),2))
check('zero rare-state probability permits the successful two-step legal policy',legal_value(F(0))==1)
for delta in (F(1,10),F(1,1000),F(1,1000000)):
    assert legal_value(delta)==0
    assert legal_value(delta,True)==1-delta
check('arbitrarily small checked support changes destroy the hard-legal guarantee',True)
check('explicitly totalized alternative restores continuous success 1-delta',True)

result={'round':'R135','all_pass':True,'checks':checks,'profile_pairs':pairs,
        'composition_triples':343,'joint_rows':row_count,'policy_evaluations':policy_count,
        'sharp_bound_cases':sharp_count,'arithmetic':'Python Fraction; no simulations or numeric solver',
        'scope':'Finite witness and exact algebra checks; general theorems rely on stated conditional manual proofs.'}
(Path(__file__).parent/'EXACT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
print('Named checks:',len(checks))
