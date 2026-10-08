#!/usr/bin/env python3
"""UCT scoped exact check. This checks finite models, not subjective experience."""
import itertools
from fractions import Fraction

B=(0,1)
states=list(itertools.product(B,repeat=3))

# A: physical crosswire, forcing plant/report values; counterfactual at fixed switch
def routed(s,q):
    return {"Uo":q if s=="overt" else 1,"Hi":q if s=="imagery" else 1,"plant":1,"report":1}
assert routed("overt",1)==routed("imagery",1)
assert routed("overt",0)=={"Uo":0,"Hi":1,"plant":1,"report":1}
assert routed("imagery",0)=={"Uo":1,"Hi":0,"plant":1,"report":1}

# B: equal XY and YZ, unequal XZ. All singleton marginals uniform,
# but no joint assignment can satisfy all 3.
XY={(0,0):Fraction(1,2),(1,1):Fraction(1,2)}
YZ={(0,0):Fraction(1,2),(1,1):Fraction(1,2)}
XZ={(0,1):Fraction(1,2),(1,0):Fraction(1,2)}
for variable in range(3):
    marginals=[]
    for (i,j),dist in [((0,1),XY),((1,2),YZ),((0,2),XZ)]:
        if variable in (i,j):
            idx=(i,j).index(variable)
            marginals.append({v:sum(p for tup,p in dist.items() if tup[idx]==v) for v in B})
    assert all(dist=={0:Fraction(1,2),1:Fraction(1,2)} for dist in marginals)
extension=[s for s in states if (s[0],s[1]) in XY and (s[1],s[2]) in YZ and (s[0],s[2]) in XZ]
assert extension==[]

# C: identical every pairwise marginal, distinct global supports
uni={s:Fraction(1,8) for s in states}
even={s:(Fraction(1,4) if sum(s)%2==0 else Fraction(0)) for s in states}
for pair in ((0,1),(1,2),(0,2)):
    for x in itertools.product(B,repeat=2):
        pu=sum(p for s,p in uni.items() if tuple(s[i] for i in pair)==x)
        pe=sum(p for s,p in even.items() if tuple(s[i] for i in pair)==x)
        assert pu==pe==Fraction(1,4)
assert (sum(p>0 for p in uni.values()),sum(p>0 for p in even.values()))==(8,4)

# D: two closed, overlapping updates disagree unless a == b
valid=[(a,m,b) for a,m,b in states if a^m==m^b]
assert len(valid)==4 and all(a==b for a,m,b in valid)

# E: no choice of four nodewise flips makes one inconsistent diagram commute
natural=[(ha,hb,hc,hd) for ha,hb,hc,hd in itertools.product(B,repeat=4)
         if hb==ha and hc==ha and hd==hb and hd==(hc^1)]
assert natural==[]

print("PASS A crosswire matched baseline / route-sensitive do(q=0)")
print("PASS B locally consistent marginals / zero global support")
print("PASS C all pairwise marginals equal / 8 vs 4 joint support")
print("PASS D one shared token / 4 of 8 joint states compatible")
print("PASS E objectwise isomorphisms / no simultaneous diagram alignment")
print("SCOPE: conditional finite constructions; no human feelings measured.")
