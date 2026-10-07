"""Small exact checks of R146 mathematical examples, not empirical experiments."""
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import json

def tv(p,q):
    return sum(abs(a-b) for a,b in zip(p,q))/2

out={"scope":"Finite examples only; general proofs are in the manuscript. No consciousness measurement."}
sym=[]
for n in range(2,6):
    ps=list(permutations(range(n)))
    fixed=[i for i in range(n) if all(p[i]==i for p in ps)]
    assert not fixed
    # Covariance of all local XOR updates and predictions under every permutation.
    count=0
    for z in product(range(2),repeat=n):
        for a in product(range(2),repeat=n):
            nxt=tuple(x^u for x,u in zip(z,a))
            for p in ps:
                zz=[0]*n; aa=[0]*n; nn=[0]*n
                for i in range(n): zz[p[i]]=z[i]; aa[p[i]]=a[i]; nn[p[i]]=nxt[i]
                assert tuple(x^u for x,u in zip(zz,aa))==tuple(nn)
                count+=1
    # Arbitrary deterministic guesses on three equiprobable histories independent of B.
    for guesses in product(range(n),repeat=3):
        success=sum(F(1,3*n) for h in range(3) for b in range(n) if guesses[h]==b)
        assert success==F(1,n)
    sym.append({"n":n,"permutations":len(ps),"state_action_permutation_cases":count,"fixed_candidates":fixed,"label_success":str(F(1,n))})
out['duplicate_examples']=sym

profiles=[]
for external_flip,self_flip in product(range(2),repeat=2):
    correct=0; errs=[]
    for z,a,c in product(range(2),repeat=3):
        y=c^external_flip; pred=z^a^self_flip; truth=z^a
        correct+=y==c; errs.append(int(pred!=truth))
    profile=(F(correct,8),max(errs));profiles.append(list(map(str,profile)))
assert len({tuple(x) for x in profiles})==4
out['external_accuracy_self_error']=profiles

# Exhaust every map m:{0,1,2,3}->{0,1}, every binary deterministic target table
# for two actions, and every deterministic decoder. Exact iff is independently
# tested by enumerating possible decoder tables (not only recomputing fibers).
count=0
for ms in product(range(2),repeat=4):
    for qs in product(range(2),repeat=8):
        fiber_constant=all(ms[i]!=ms[j] or all(qs[2*i+a]==qs[2*j+a] for a in range(2)) for i in range(4) for j in range(4))
        dec_exists=any(all(ds[2*ms[i]+a]==qs[2*i+a] for i in range(4) for a in range(2)) for ds in product(range(2),repeat=4))
        assert fiber_constant==dec_exists
        # Binary point-mass targets have optimal row error 0 or 1/2.
        optimal=max(F(0) if len({qs[2*i+a] for i in range(4) if ms[i]==m})<=1 else F(1,2) for m in set(ms) for a in range(2))
        assert (optimal==0)==dec_exists
        count+=1
out['fiber_iff_exhaustive_cases']=count

# Counterlimit: diameter/2 need not equal minimax radius for three point masses.
points=[tuple(F(int(i==j)) for j in range(3)) for i in range(3)]
center=(F(1,3),)*3
assert max(tv(p,q) for p in points for q in points)==1
assert max(tv(center,q) for q in points)==F(2,3)
# Every simplex point has a component <=1/3, so max_j TV(p,delta_j)>=2/3.
out['radius_counterexample']={"diameter":"1","radius":"2/3","diameter_half":"1/2","lower_bound_reason":"min coordinate <= 1/3, TV(p,delta_j)=1-p_j"}
out['all_checks_passed']=True
dest=Path(__file__).with_name('EXACT_CHECKS.json');dest.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
