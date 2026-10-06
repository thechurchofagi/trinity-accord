#!/usr/bin/env python3
"""R120 finite bridge-theorem witnesses."""
from itertools import product, combinations
import json

# K=(route, capability_bit, report_bit, valence_bit, richness_bit)
types=[]
for route,j,r,v,q in product([0,1], repeat=5):
    K=(route,j,r,v,q)
    E=K
    types.append({"K":K,"E":E,"J":j,"R":r,"V":v,"Q":q,"selected_support":"accumulator"})

pairs=list(combinations(types,2))

same_J_diff_E=sum(
    1 for a,b in pairs if a["J"]==b["J"] and a["E"]!=b["E"]
)
diff_J_same_E=sum(
    1 for a,b in pairs if a["J"]!=b["J"] and a["E"]==b["E"]
)
gain_richness_decline=sum(
    1 for a,b in pairs
    if a["J"]<b["J"] and a["Q"]>b["Q"]
)
same_selected_T2_diff_complete=sum(
    1 for a,b in pairs
    if a["selected_support"]==b["selected_support"] and a["K"]!=b["K"]
)

def witness(pred):
    for a,b in pairs:
        if pred(a,b):
            return {"K1":list(a["K"]),"K2":list(b["K"])}

result={
    "round":"R120",
    "type_count":len(types),
    "pair_count":len(pairs),
    "checks":{
        "same_capability_different_complete_experience_pairs":same_J_diff_E,
        "different_capability_same_complete_experience_pairs":diff_J_same_E,
        "capability_gain_candidate_richness_decline_pairs":gain_richness_decline,
        "same_selected_T2_mechanism_different_complete_type_pairs":same_selected_T2_diff_complete,
    },
    "witnesses":{
        "same_capability_different_complete_experience":witness(
            lambda a,b:a["J"]==b["J"] and a["E"]!=b["E"]),
        "capability_gain_richness_decline":witness(
            lambda a,b:a["J"]<b["J"] and a["Q"]>b["Q"]),
        "same_selected_mechanism_different_complete_type":witness(
            lambda a,b:a["selected_support"]==b["selected_support"] and a["K"]!=b["K"]),
    },
    "interpretation":"Finite logical witness for bridge asymmetries; not a consciousness model."
}

assert same_J_diff_E>0
assert diff_J_same_E==0
assert gain_richness_decline>0
assert same_selected_T2_diff_complete>0

print(json.dumps(result,indent=2))
