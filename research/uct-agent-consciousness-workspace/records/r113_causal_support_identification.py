#!/usr/bin/env python3
"""R113 exact causal-support taxonomy by exhaustive relation subsets."""
import json

relations=("g","r1","r2","h","c")
target=(0,1,1,0)

def accuracy(out):
    return sum(int(a==b) for a,b in zip(out,target))/4

def evaluate(S):
    route_active=("r1" in S) or ("r2" in S)
    route=tuple(t if route_active else 0 for t in target)
    core=tuple(v if "g" in S else 0 for v in route)
    report=tuple(v if "h" in S else 0 for v in core)
    correlate=tuple(t if "c" in S else 0 for t in target)
    return {
        "core_accuracy":accuracy(core),
        "report_accuracy":accuracy(report),
        "correlate_accuracy":accuracy(correlate),
        "core":core,
        "report":report,
        "correlate":correlate,
    }

states=[]
for mask in range(1<<len(relations)):
    S=frozenset(relations[i] for i in range(len(relations)) if mask&(1<<i))
    states.append((S,evaluate(S)))

def minimal_sets(metric):
    good=[(S,r) for S,r in states if r[metric]==1.0]
    mins=[]
    for S,r in good:
        if not any(T < S and rr[metric]==1.0 for T,rr in good):
            mins.append(sorted(S))
    return sorted(mins)

full=frozenset(relations)
single_lesions={
    r:evaluate(full-{r})
    for r in relations
}
double_route_lesion=evaluate(full-{"r1","r2"})

result={
    "round":"R113",
    "enumerated_relation_sets":len(states),
    "minimal_core_support_sets":minimal_sets("core_accuracy"),
    "minimal_report_support_sets":minimal_sets("report_accuracy"),
    "single_lesions":{
        r:{
            "core_accuracy":x["core_accuracy"],
            "report_accuracy":x["report_accuracy"],
            "correlate_accuracy":x["correlate_accuracy"],
        }
        for r,x in single_lesions.items()
    },
    "joint_route_lesion":{
        "core_accuracy":double_route_lesion["core_accuracy"],
        "report_accuracy":double_route_lesion["report_accuracy"],
    },
    "classification":{
        "g":"shared indispensable/permissive support for core and report",
        "r1":"degenerate alternative content-bearing core route",
        "r2":"degenerate alternative content-bearing core route",
        "h":"downstream report/readout support; not core-task support",
        "c":"perfect task correlate but not causal support in tested system",
    },
    "scope":"Exact toy causal-support witness. Necessity/sufficiency are background-relative; not a consciousness measurement."
}

assert result["minimal_core_support_sets"]==[["g","r1"],["g","r2"]]
assert result["minimal_report_support_sets"]==[["g","h","r1"],["g","h","r2"]]
assert result["single_lesions"]["r1"]["core_accuracy"]==1.0
assert result["single_lesions"]["r2"]["core_accuracy"]==1.0
assert result["joint_route_lesion"]["core_accuracy"]==0.5
assert result["single_lesions"]["g"]["core_accuracy"]==0.5
assert result["single_lesions"]["h"]["core_accuracy"]==1.0
assert result["single_lesions"]["h"]["report_accuracy"]==0.5
assert result["single_lesions"]["c"]["core_accuracy"]==1.0

print(json.dumps(result,indent=2))
