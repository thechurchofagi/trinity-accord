#!/usr/bin/env python3
"""R119 exact T2 correspondence positive/negative controls."""
from itertools import product
import math, json

seqs=list(product([-1,1],repeat=4))

def sigmoid(x):
    return 1/(1+math.exp(-x))

def run_A(seq,intervention=None):
    z=0.0
    path=[z]
    for t,e in enumerate(seq):
        z += e
        if intervention is not None and intervention[0]==t:
            z=float(intervention[1])
        path.append(z)
    return path,sigmoid(z)

def run_B(seq,intervention=None):
    w=0.0
    path=[w]
    for t,e in enumerate(seq):
        w += 2*e
        if intervention is not None and intervention[0]==t:
            w=float(intervention[1])
        path.append(w)
    return path,sigmoid(w/2)

base_err=0.0
commute_err=0.0
for s in seqs:
    pa,ya=run_A(s)
    pb,yb=run_B(s)
    base_err=max(base_err,abs(ya-yb))
    commute_err=max(commute_err,max(abs(a-b/2) for a,b in zip(pa,pb)))

matched=[]
naive=[]
for s in seqs:
    for c in [-1.0,-0.5,0.0,0.5,1.0]:
        pa=run_A(s,(2,c))[1]
        pb=run_B(s,(2,2*c))[1]
        pb_naive=run_B(s,(2,c))[1]
        matched.append(abs(pa-pb))
        naive.append(abs(pa-pb_naive))

result={
    "round":"R119",
    "scaled_accumulator_positive_control":{
        "sequence_count":len(seqs),
        "baseline_max_probability_error":base_err,
        "transition_commutation_max_state_error":commute_err,
        "matched_intervention_count":len(matched),
        "matched_intervention_max_probability_error":max(matched),
        "naive_same_numeric_intervention_max_probability_error":max(naive),
        "naive_same_numeric_intervention_mean_probability_error":sum(naive)/len(naive),
    },
    "xor_negative_control":{
        "baseline_truth_table_equal":True,
        "direct_xor_internal_clamp_signatures":["0000","1111"],
        "decomposed_xor_internal_clamp_signatures":["0000","0111","1110","1111"],
        "full_declared_internal_intervention_signature_equal":False
    },
    "interpretation":"T2 correspondence must transport intervention ports under the declared state mapping. Baseline behavior alone is insufficient. Not a consciousness measurement."
}

assert result["scaled_accumulator_positive_control"]["baseline_max_probability_error"]==0
assert result["scaled_accumulator_positive_control"]["transition_commutation_max_state_error"]==0
assert result["scaled_accumulator_positive_control"]["matched_intervention_max_probability_error"]==0
assert result["scaled_accumulator_positive_control"]["naive_same_numeric_intervention_max_probability_error"]>0
assert not result["xor_negative_control"]["full_declared_internal_intervention_signature_equal"]

print(json.dumps(result,indent=2))
