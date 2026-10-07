"""Small exact checks of the new proof's failure modes; no empirical experiment."""
from itertools import product
from pathlib import Path
import json

def factors(target, rep):
    labels=sorted(set(rep)); codomain=sorted(set(target))
    # Enumerate candidate decoders rather than use the fiber test being checked.
    for vals in product(codomain,repeat=len(labels)):
        decoder=dict(zip(labels,vals))
        if all(decoder[r]==t for r,t in zip(rep,target)):
            return True
    return False

def reflects(rep, target):
    return all(rep[i]!=rep[j] or target[i]==target[j]
               for i in range(len(rep)) for j in range(len(rep)))

checked=0
for k in product(range(2),repeat=3):
    for r in product(range(3),repeat=3):
        for flip in (0,1):
            e=tuple(x^flip for x in k)
            assert factors(e,r)==reflects(r,k)==factors(k,r)
            checked+=1

# A descriptor with external labels can refine a single complete type.
k=(0,0);r=(0,1);e=(1,1)
assert factors(e,r) and reflects(r,k) and not reflects(k,r)
# Target sufficiency is weaker than complete-type sufficiency.
k=(0,1);r=(0,0);f=(1,1)
assert factors(f,r) and not factors(k,r)
# Failure of germ factorization need not survive a many-to-one bridge.
trajectory=(0,0);germ=(0,1);constant_bridge_output=(1,1)
assert not factors(germ,trajectory)
assert factors(constant_bridge_output,trajectory)
# TA18's two single-input profiles match, but joint perturbation distinguishes.
AND=lambda a,b:a&b
XNOR=lambda a,b:int(a==b)
same=[(1,1),(0,1),(1,0)]
assert all(AND(*x)==XNOR(*x) for x in same)
assert AND(0,0)!=XNOR(0,0)

result={'all_checks_passed':True,'compatibility_assignments':checked,
 'external_label_counterlimit':True,'partial_target_counterexample':True,
 'constant_bridge_counterexample':True,'singleton_vs_joint_profile_gap':True,
 'scope':'Finite mathematical checks only. General proofs are in the theory note. No consciousness measurement, source experiments, or novelty certification.'}
Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
