#!/usr/bin/env python3
"""R106 finite witness for projection non-equivalence.

This is an exact toy check. It is not a biological/AI consciousness model.
"""
from itertools import product, combinations
import json

types=[]
for i,q,s,r in product([0,1], repeat=4):
    k=(i,q,s,r)
    types.append({
        "K":k,
        "E":k,   # explicit C1-style identity in this toy witness
        "I":i,
        "B":i,
        "R":r,
        "S":s,
        "core":(i,q,s),
        "richness_coordinate":q,
    })

pairs=list(combinations(types,2))
def count(pred):
    return sum(1 for a,b in pairs if pred(a,b))
def witness(pred):
    for a,b in pairs:
        if pred(a,b):
            return {"K1":list(a["K"]),"K2":list(b["K"])}

result={
    "round":"R106",
    "purpose":"Finite witness for projection non-equivalence under E=K toy identity; not a biological or AI consciousness measurement.",
    "structural_types":len(types),
    "unordered_pairs":len(pairs),
    "checks":{
        "same_I_distinct_E_pairs":count(lambda a,b:a["I"]==b["I"] and a["E"]!=b["E"]),
        "same_B_distinct_E_pairs":count(lambda a,b:a["B"]==b["B"] and a["E"]!=b["E"]),
        "same_R_distinct_E_pairs":count(lambda a,b:a["R"]==b["R"] and a["E"]!=b["E"]),
        "different_I_same_E_pairs":count(lambda a,b:a["I"]!=b["I"] and a["E"]==b["E"]),
        "intelligence_gain_richness_decline_pairs":count(lambda a,b:a["I"]<b["I"] and a["richness_coordinate"]>b["richness_coordinate"]),
        "report_only_change_preserved_core_pairs":count(lambda a,b:a["core"]==b["core"] and a["R"]!=b["R"]),
    },
    "witnesses":{
        "same_I_distinct_E":witness(lambda a,b:a["I"]==b["I"] and a["E"]!=b["E"]),
        "same_B_distinct_E":witness(lambda a,b:a["B"]==b["B"] and a["E"]!=b["E"]),
        "same_R_distinct_E":witness(lambda a,b:a["R"]==b["R"] and a["E"]!=b["E"]),
        "intelligence_gain_richness_decline":witness(lambda a,b:a["I"]<b["I"] and a["richness_coordinate"]>b["richness_coordinate"]),
        "report_only_change_preserved_core":witness(lambda a,b:a["core"]==b["core"] and a["R"]!=b["R"]),
    },
}

assert result["checks"]["different_I_same_E_pairs"] == 0
assert result["checks"]["same_I_distinct_E_pairs"] > 0
assert result["checks"]["same_B_distinct_E_pairs"] > 0
assert result["checks"]["same_R_distinct_E_pairs"] > 0
assert result["checks"]["intelligence_gain_richness_decline_pairs"] > 0
assert result["checks"]["report_only_change_preserved_core_pairs"] > 0

print(json.dumps(result,indent=2))
