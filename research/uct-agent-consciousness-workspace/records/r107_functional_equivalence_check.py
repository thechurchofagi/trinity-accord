#!/usr/bin/env python3
"""R107 exact functional-equivalence / structural-non-equivalence witness."""
from itertools import product
import json

rows=[]
for x1,x2 in product([0,1], repeat=2):
    direct=x1 ^ x2
    or_node=x1 | x2
    and_node=x1 & x2
    decomposed=or_node & (1-and_node)
    rows.append({
        "x1":x1,"x2":x2,
        "direct_xor":direct,
        "or_node":or_node,
        "and_node":and_node,
        "decomposed_xor":decomposed,
        "same_output":direct==decomposed,
    })

assert all(r["same_output"] for r in rows)
result={
    "round":"R107",
    "truth_table_equal":True,
    "input_count":4,
    "system_A_graph":"x1,x2 -> XOR -> y",
    "system_B_graph":"x1,x2 -> OR/AND -> AND(NOT) -> y",
    "same_behavior_on_complete_binary_task":True,
    "same_internal_constitutive_graph":False,
    "rows":rows,
    "interpretation":"Functional/behavioral equivalence does not identify constitutive organizational equivalence. This is not a consciousness measurement."
}
print(json.dumps(result,indent=2))
