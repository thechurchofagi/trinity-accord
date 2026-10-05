#!/usr/bin/env python3
"""R96 path-blocking continuation-preference identifiability audit. Standard library only."""
import itertools,json,math
from pathlib import Path
P=Path(__file__).resolve().parent
VALS=(-1,0,1)
PROFILES=list(itertools.product(VALS,repeat=5)) # theta_Q,theta_O,theta_G,theta_QG,theta_OG
ROWS={
 "q_direct":(1,0,0,0,0),
 "o_direct":(0,1,0,0,0),
 "task_only":(0,0,1,0,0),
 "q_bundled":(1,0,1,1,0),
 "o_bundled":(0,1,1,0,1),
 "qo_joint":(1,1,1,1,1),
}
BETA=2.0
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def sgn(x): return -1 if x<0 else (1 if x>0 else 0)
def classify(names,sign_only=False):
    groups={}
    for th in PROFILES:
        sig=tuple(dot(ROWS[n],th) for n in names)
        if sign_only:sig=tuple(sgn(x) for x in sig)
        groups.setdefault(sig,[]).append(th)
    return len(groups),max(map(len,groups.values())),groups
bundled=("q_bundled","o_bundled")
full=("q_direct","o_direct","task_only","q_bundled","o_bundled")
be,bm,bg=classify(bundled)
bs,bsm,_=classify(bundled,True)
fe,fm,_=classify(full)
fs,fsm,_=classify(full,True)
assert (be,bm)==(43,17)
assert (bs,bsm)==(9,46)
assert (fe,fm)==(243,1)
assert (fs,fsm)==(121,9)

controllers={
 "direct_self":(1,0,0,0,0),
 "instrumental_task":(0,0,1,0,0),
 "q_task_interaction":(0,0,0,1,0),
 "equal_mixture":(.5,0,.5,0,0),
}
outc={}
for name,th in controllers.items():
    outc[name]={}
    for rn in ("q_bundled","q_direct","task_only","o_bundled","o_direct"):
        z=dot(ROWS[rn],th)
        outc[name][rn]={"logit":z,"choice_probability":1/(1+math.exp(-BETA*z))}
assert all(outc[n]["q_bundled"]["logit"]==1 for n in ("direct_self","instrumental_task","q_task_interaction"))
assert outc["direct_self"]["q_direct"]["logit"]==1
assert outc["instrumental_task"]["q_direct"]["logit"]==0
assert outc["instrumental_task"]["task_only"]["logit"]==1
assert outc["q_task_interaction"]["q_bundled"]["logit"]-outc["q_task_interaction"]["q_direct"]["logit"]-outc["q_task_interaction"]["task_only"]["logit"]==1

res={
 "round":"R96","date":"2026-10-06","beta":BETA,
 "coefficient_order":["theta_Q","theta_O","theta_G","theta_QG","theta_OG"],
 "contrast_rows":ROWS,"num_profiles":len(PROFILES),
 "bundled_exact":{"signatures":be,"max_class":bm},
 "bundled_deterministic":{"signatures":bs,"max_class":bsm},
 "full_exact":{"signatures":fe,"max_class":fm},
 "full_deterministic":{"signatures":fs,"max_class":fsm},
 "bundled_signature_example":{"signature":[1,0],"profiles":bg[(1,0)]},
 "controllers":outc,
 "identification_formulas":{
   "theta_Q":"z(q_direct)","theta_O":"z(o_direct)","theta_G":"z(task_only)",
   "theta_QG":"z(q_bundled)-z(q_direct)-z(task_only)",
   "theta_OG":"z(o_bundled)-z(o_direct)-z(task_only)"
 },
 "scope":"Virtual pairwise-choice causal-path audit only; no subjective/valence measurement."
}
(P/"R96_Results.regenerated.json").write_text(json.dumps(res,indent=2)+"\n")
print("R96 assertions PASS")
print("Bundled exact signatures/max class",be,bm)
print("Bundled deterministic signatures/max class",bs,bsm)
print("Full exact signatures/max class",fe,fm)
print("Full deterministic signatures/max class",fs,fsm)
for n in controllers:
    print(n,outc[n])
