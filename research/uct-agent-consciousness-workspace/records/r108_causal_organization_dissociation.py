#!/usr/bin/env python3
"""R108 executable causal-organization and report-head dissociation checks."""
from itertools import product
import json

inputs=list(product([0,1], repeat=2))

def sys_a(x1,x2,clamp=None):
    y=x1 ^ x2
    if clamp is not None:
        y=int(clamp)
    return {"y":y}

def sys_b(x1,x2,clamp=None):
    a=x1 | x2
    b=x1 & x2
    nb=1-b
    y=a & nb
    if clamp is not None:
        node,val=clamp
        val=int(val)
        if node=="a":
            a=val
            y=a & nb
        elif node=="b":
            b=val
            nb=1-b
            y=a & nb
        elif node=="nb":
            nb=val
            y=a & nb
        elif node=="y":
            y=val
        else:
            raise ValueError(node)
    return {"a":a,"b":b,"nb":nb,"y":y}

def bits(vals):
    return ''.join(str(int(v)) for v in vals)

target=[x1 ^ x2 for x1,x2 in inputs]
base_a=[sys_a(*x)["y"] for x in inputs]
base_b=[sys_b(*x)["y"] for x in inputs]
assert base_a==target==base_b

a_interventions={
    f"xor={v}":bits([sys_a(*x,clamp=v)["y"] for x in inputs])
    for v in [0,1]
}
b_interventions={}
for node in ["a","b","nb","y"]:
    for v in [0,1]:
        b_interventions[f"{node}={v}"]=bits([
            sys_b(*x,clamp=(node,v))["y"] for x in inputs
        ])

report_id=target[:]
report_inv=[1-y for y in target]
report_const=[0,0,0,0]
zero_core=[0,0,0,0]

def accuracy(outputs):
    return sum(int(a==b) for a,b in zip(outputs,target))/len(target)

result={
    "round":"R108",
    "inputs":[list(x) for x in inputs],
    "target":target,
    "baseline":{
        "system_A":base_a,
        "system_B":base_b,
        "behavior_equal":base_a==base_b,
        "task_accuracy_A":accuracy(base_a),
        "task_accuracy_B":accuracy(base_b),
    },
    "internal_intervention_signatures":{
        "system_A":a_interventions,
        "system_B":b_interventions,
        "unique_A":sorted(set(a_interventions.values())),
        "unique_B":sorted(set(b_interventions.values())),
        "B_signatures_not_in_A":sorted(set(b_interventions.values())-set(a_interventions.values())),
    },
    "report_head_surgery":{
        "core_task_output":target,
        "identity_report":report_id,
        "inverted_report":report_inv,
        "task_output_unchanged":True,
        "report_disagreement_fraction":sum(a!=b for a,b in zip(report_id,report_inv))/4,
    },
    "reverse_report_control":{
        "constant_report_XOR_core":report_const,
        "constant_report_zero_core":report_const,
        "reports_equal":True,
        "xor_core_accuracy":accuracy(target),
        "zero_core_accuracy":accuracy(zero_core),
    },
    "interpretation":"Natural task equivalence does not identify interventional causal equivalence; report and selected task capability can be dissociated in both directions. Not a consciousness measurement."
}

assert result["baseline"]["behavior_equal"]
assert result["internal_intervention_signatures"]["B_signatures_not_in_A"]==["0111","1110"]
assert result["report_head_surgery"]["report_disagreement_fraction"]==1.0
assert result["reverse_report_control"]["xor_core_accuracy"]==1.0
assert result["reverse_report_control"]["zero_core_accuracy"]==0.5

print(json.dumps(result,indent=2))
