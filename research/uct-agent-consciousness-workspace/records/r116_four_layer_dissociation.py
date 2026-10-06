#!/usr/bin/env python3
"""R116 four-layer separation: behavior, report, content geometry, valence."""
from itertools import combinations
import json

X=("x0","x1","x2","x3")

base_code={
    "x0":(0,0),
    "x1":(0,1),
    "x2":(1,1),
    "x3":(1,0),
}
geo_code={
    "x0":(0,0),
    "x1":(1,1),
    "x2":(0,1),
    "x3":(1,0),
}

task={
    "x0":0,"x1":0,"x2":1,"x3":1
}
policy_swap={x:1-y for x,y in task.items()}

report={
    "x0":"L0","x1":"L1","x2":"L2","x3":"L3"
}
report_swap={
    "x0":"L0","x1":"L2","x2":"L1","x3":"L3"
}

valence={
    "x0":-1.0,"x1":-0.5,"x2":0.5,"x3":1.0
}
valence_flip={x:-v for x,v in valence.items()}

def hamming(a,b):
    return sum(int(u!=v) for u,v in zip(a,b))

def matrix(code):
    return [[hamming(code[a],code[b]) for b in X] for a in X]

def upper(M):
    return sorted(M[i][j] for i in range(len(X)) for j in range(i+1,len(X)))

base_geom=matrix(base_code)
geo_geom=matrix(geo_code)

pairs=list(combinations(X,2))
def preference(V,a,b):
    return a if V[a]>V[b] else b

pref_disagree=sum(
    preference(valence,a,b)!=preference(valence_flip,a,b)
    for a,b in pairs
)/len(pairs)

result={
    "round":"R116",
    "base":{
        "task":task,
        "report":report,
        "content_geometry":base_geom,
        "valence":valence,
    },
    "comparisons":{
        "base_vs_G_geometry_variant":{
            "task_equal":task==task,
            "report_equal":report==report,
            "content_geometry_equal":base_geom==geo_geom,
            "unlabeled_distance_multiset_equal":upper(base_geom)==upper(geo_geom),
            "valence_equal":valence==valence,
        },
        "base_vs_R_report_variant":{
            "task_equal":True,
            "report_equal":report==report_swap,
            "content_geometry_equal":True,
            "valence_equal":True,
        },
        "base_vs_B_policy_variant":{
            "task_equal":task==policy_swap,
            "report_equal":True,
            "content_geometry_equal":True,
            "valence_equal":True,
        },
        "base_vs_V_valence_variant":{
            "task_equal":True,
            "report_equal":True,
            "content_geometry_equal":True,
            "valence_equal":valence==valence_flip,
            "pairwise_preference_disagreement_fraction":pref_disagree,
        }
    },
    "scope":"Finite mechanistic separation witness; not an AI consciousness measurement."
}

assert not result["comparisons"]["base_vs_G_geometry_variant"]["content_geometry_equal"]
assert result["comparisons"]["base_vs_G_geometry_variant"]["unlabeled_distance_multiset_equal"]
assert not result["comparisons"]["base_vs_R_report_variant"]["report_equal"]
assert not result["comparisons"]["base_vs_B_policy_variant"]["task_equal"]
assert not result["comparisons"]["base_vs_V_valence_variant"]["valence_equal"]
assert pref_disagree==1.0

print(json.dumps(result,indent=2))
