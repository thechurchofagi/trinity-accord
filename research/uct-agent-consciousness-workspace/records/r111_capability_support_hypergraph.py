#!/usr/bin/env python3
"""R111 exact finite capability-support hypergraph checks."""
from itertools import combinations
import json

relations=("g","v","m","s","x")
tasks={
    "T1_world":[frozenset({"g","v"}),frozenset({"x"})],
    "T2_memory":[frozenset({"g","m"})],
    "T3_self":[frozenset({"g","s"})],
}

def caps(S):
    return tuple(int(any(M <= S for M in tasks[t])) for t in tasks)

states=[]
for mask in range(1<<len(relations)):
    S=frozenset(relations[i] for i in range(len(relations)) if mask & (1<<i))
    C=caps(S)
    states.append({"S":S,"C":C,"J":sum(C)})

pairs=list(combinations(states,2))
same_profile_diff_support=[
    (a,b) for a,b in pairs if a["C"]==b["C"] and a["S"]!=b["S"]
]
same_score_diff_profile=[
    (a,b) for a,b in pairs if a["J"]==b["J"] and a["C"]!=b["C"]
]

def pack(st):
    return {"S":sorted(st["S"]),"C":list(st["C"]),"J":st["J"]}

same_full_profile=next(
    (a,b) for a,b in same_profile_diff_support if a["C"]==(1,1,1)
)
same_scalar=next(iter(same_score_diff_profile))
cap_gain_incomparable=next(
    (a,b) for a,b in pairs
    if a["C"]==(1,0,0)
    and b["C"]==(1,1,0)
    and not a["S"] <= b["S"]
    and not b["S"] <= a["S"]
)

base=frozenset({"g","v","m","s"})
lesions={r:list(caps(base-{r})) for r in sorted(base)}

result={
    "round":"R111",
    "relation_universe":list(relations),
    "minimal_support_families":{
        t:[sorted(M) for M in Ms] for t,Ms in tasks.items()
    },
    "enumerated_relation_sets":len(states),
    "unordered_pairs":len(pairs),
    "same_capability_profile_different_support_pairs":len(same_profile_diff_support),
    "same_scalar_score_different_profile_pairs":len(same_score_diff_profile),
    "witnesses":{
        "same_full_profile_different_support":[pack(x) for x in same_full_profile],
        "same_scalar_different_profile":[pack(x) for x in same_scalar],
        "capability_gain_with_incomparable_relation_sets":[pack(x) for x in cap_gain_incomparable],
    },
    "shared_relation_lesions":{
        "base":sorted(base),
        "base_capabilities":list(caps(base)),
        "lesions":lesions,
    },
    "interpretation":"Capability profile and scalar intelligence are many-to-one projections of support organization. Exact toy model only; not a consciousness measurement."
}

assert result["same_capability_profile_different_support_pairs"]==100
assert result["same_scalar_score_different_profile_pairs"]==38
assert lesions["g"]==[0,0,0]
assert lesions["v"]==[0,1,1]
assert lesions["m"]==[1,0,1]
assert lesions["s"]==[1,1,0]

print(json.dumps(result,indent=2))
