"""Exact finite witnesses; no simulations, numerical LP tolerances or new data."""
from fractions import Fraction as F
from itertools import product, combinations
from functools import lru_cache
from pathlib import Path
import json

checks=[]
def check(name, condition):
    checks.append({'check':name,'pass':bool(condition)})
    if not condition: raise AssertionError(name)

def primal(points):
    """Max min(x,y) over a finite 2D hull, via vertices/diagonal crossings."""
    candidates=list(points)
    for v,w in combinations(points,2):
        dv,dw=v[0]-v[1],w[0]-w[1]
        if dv == dw: continue
        t=-dw/(dv-dw)
        if 0<=t<=1:
            candidates.append(tuple(t*v[i]+(1-t)*w[i] for i in range(2)))
    return max(min(v) for v in candidates)

def dual(points):
    """Min upper envelope of affine weighted values, independent of hull code."""
    weights={F(0),F(1)}
    for v,w in combinations(points,2):
        slope=(v[0]-v[1])-(w[0]-w[1])
        if slope:
            q=(w[1]-v[1])/slope
            if 0<=q<=1:weights.add(q)
    return min(max(q*v[0]+(1-q)*v[1] for v in points) for q in weights)

def probe_points(a,b):
    return tuple((sum(a[i]*d[i] for i in range(len(a))),
                  sum(b[i]*(1-d[i]) for i in range(len(b))))
                 for d in product((0,1),repeat=len(a)))

def probe_dual(a,b):
    qs={F(0),F(1)}|{b[i]/(a[i]+b[i]) for i in range(len(a)) if a[i]+b[i]}
    return min(sum(max(q*x,(1-q)*y) for x,y in zip(a,b)) for q in qs)

family_count=0
blind=((F(1),F(0)),(F(0),F(1)))
for p0,p1 in product((F(i,4) for i in range(5)),repeat=2):
    for r00,r01,r10,r11 in product((F(0),F(1,2),F(1)),repeat=4):
        a=(p0*r00,(1-p0)*r01);b=(p1*r10,(1-p1)*r11)
        points=probe_points(a,b)
        vp=primal(points)
        assert vp==dual(points)==probe_dual(a,b)
        assert vp<=(sum(a)+sum(b)+sum(abs(x-y) for x,y in zip(a,b)))/4
        optional=points+blind
        assert primal(optional)==dual(optional)
        assert primal(optional)>=max(F(1,2),vp)
        family_count+=1
check('2025 weighted binary families: primal equals both probe dual computations',family_count==2025)
check('2025 weighted binary families: optional primal equals dual and never loses available baseline',family_count==2025)
check('weighted diagnostic/opportunity upper bound checked in every family',family_count==2025)

rho_grid=sorted({F(i,20) for i in range(21)}|{F(2,3),F(3,4),F(7,10)})
for rho in rho_grid:
    points=probe_points((rho,F(0)),(rho/2,rho/2))
    assert primal(points)==2*rho/3
    assert primal(points+blind)==max(F(1,2),2*rho/(2+rho))
check('asymmetric closed-form forced/optional values hold at 22 rational survival levels',len(rho_grid)==22)
rho=F(7,10);lam=F(20,27);q=F(13,27)
points=probe_points((rho,F(0)),(rho/2,rho/2))
mix=(lam*rho,lam*rho/2+1-lam)
check('strict mixing witness has exact common success 14/27',mix==(F(14,27),F(14,27)))
check('dual 13/27 proves the strict mixing witness optimal',max(q*v[0]+(1-q)*v[1] for v in points+blind)==F(14,27))
check('forced probing loses versus baseline while optional mixture strictly improves',F(7,15)<F(1,2)<F(14,27))
asym=((F(1),F(0)),(F(1,2),F(1,2)))
sym=((F(3,4),F(1,4)),(F(1,4),F(3,4)))
tv=lambda p,q:sum(abs(a-b) for a,b in zip(p,q))/2
check('same TV one half does not imply same robust accuracy',tv(*asym)==tv(*sym)==F(1,2)
      and primal(probe_points(*asym))==F(2,3) and primal(probe_points(*sym))==F(3,4))
check('perfect-value purification boundary differs from subunit mixing',max(min(x) for x in blind)==0 and primal(blind)==F(1,2))
check('coordinatewise oracle is outside blind attainable hull',max(v[0] for v in blind)==max(v[1] for v in blind)==1 and primal(blind)<1)

# Finite dynamic model: one persistent label, joint signal/opportunity transition.
ACT=('a0','a1','p');OBS=('0','1','?')
X=tuple((m,s) for m in (0,1) for s in ('start','ready','goal','dead'))
def kernel(channel,rho,x,action):
    m,s=x
    if s in ('goal','dead'):return ((x,'?',F(1)),)
    if action!='p':return (((m,'goal' if action=='a'+str(m) else 'dead'),'?',F(1)),)
    if s=='ready':return (((m,'dead'),'?',F(1)),) # a second probe consumes the remaining chance
    out=[]
    for y,prob in enumerate(channel[m]):
        for stage,p in [('ready',rho),('dead',1-rho)]:
            if prob*p:out.append(((m,stage),str(y),prob*p))
    return tuple(out)

@lru_cache(None)
def trees(h):
    if h==0:return (('stop',()),)
    return (('stop',()),)+tuple((a,bs) for a in ACT for bs in product(trees(h-1),repeat=3))

@lru_cache(None)
def direct(channel,rho,x,tree):
    a,bs=tree
    if a=='stop':return F(x[1]=='goal')
    return sum(p*direct(channel,rho,xp,bs[OBS.index(o)]) for xp,o,p in kernel(channel,rho,x,a))

@lru_cache(None)
def vectors(channel,rho,B,h):
    g=tuple(F(x[1]=='goal') for x in B)
    out={g}
    if h==0:return frozenset(out)
    for a in ACT:
        supports={o:tuple(sorted({xp for x in B for xp,z,p in kernel(channel,rho,x,a) if z==o and p})) for o in OBS}
        observed=[o for o in OBS if supports[o]]
        child=[vectors(channel,rho,supports[o],h-1) for o in observed]
        for selected in product(*child):
            ws={o:dict(zip(supports[o],v)) for o,v in zip(observed,selected)}
            out.add(tuple(sum(p*ws[o][xp] for xp,o,p in kernel(channel,rho,x,a)) for x in B))
    return frozenset(out)

supports=[tuple(((0,'start'),(1,'start'))), tuple(((0,'start'),)), tuple(((1,'start'),)),
          tuple(((0,'ready'),(1,'ready'))),tuple(((0,'goal'),(1,'start'))),X]
comparisons=0
for channel in (asym,sym):
    for rho in (F(0),F(1,2),F(7,10),F(1)):
        for B in supports:
            for h in range(3):
                brute={tuple(direct(channel,rho,x,t) for x in B) for t in trees(h)}
                assert brute==set(vectors(channel,rho,B,h))
                comparisons+=1
check('144 dynamic cases: vector recursion matches direct full policy-tree evaluation',comparisons==144)
B=supports[0]
for channel in (asym,sym):
    for rho in (F(0),F(1,2),F(7,10),F(1)):
        a=tuple(rho*p for p in channel[0]);b=tuple(rho*p for p in channel[1])
        assert primal(tuple(vectors(channel,rho,B,2)))==primal(probe_points(a,b)+blind)
check('eight dynamic optional-probe models match their independent decision-hull calculation',True)
# The symmetric transcript leaves both model identities possible after either output.
check('informative observations can leave the same model support',all({m for m in (0,1) if sym[m][y]>0}=={0,1} for y in (0,1)))
check('same-support history-dependent decisions beat a support-only terminal decision',primal(probe_points(*sym))==F(3,4) and primal(blind)==F(1,2))

result={'round':'R134','all_pass':True,'checks':checks,'weighted_binary_families':family_count,
        'dynamic_profile_comparisons':comparisons,'policy_trees_at_horizon_two':len(trees(2)),
        'rational_survival_levels':len(rho_grid),'arithmetic':'Python Fraction; no numerical LP solver or simulation',
        'strict_witness':{'forced':'7/15','blind':'1/2','optional':'14/27','probe_weight':'20/27','dual_q':'13/27'},
        'scope':'Finite exact witnesses and independent primal/dual comparisons; general proofs remain manual and conditional.'}
(Path(__file__).parent/'EXACT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
print('Named checks:',len(checks))
