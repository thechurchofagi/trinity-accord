#!/usr/bin/env python3
"""R110 exact artificial dissociation and topology-insufficiency witnesses."""
from itertools import product
import json

def accuracy(out, target):
    return sum(int(a==b) for a,b in zip(out,target))/len(target)

inputs=list(product([0,1], repeat=2))
xor=[a^b for a,b in inputs]

# Output-gate lesion
internal=xor[:]
behavior_on=internal[:]
behavior_off=[0]*4

# Report-gate lesion
report_on=xor[:]
report_off=[0]*4

# Self-channel lesion
ws=list(product([0,1], repeat=2))  # (world,self)
world_target=[w for w,s in ws]
self_target=[s for w,s in ws]
world_after_self_lesion=world_target[:]
self_after_self_lesion=[0]*4

# Access-gate lesion: encoding unchanged, downstream read blocked.
encoding=xor[:]
decision_access_on=encoding[:]
decision_access_off=[0]*4

# Same external behavior, different internal state.
hidden1=[0,1,1,0]
hidden2=[1,0,0,1]
external1=[0,0,0,0]
external2=[0,0,0,0]

# Pairwise reachability topology insufficiency.
nodes=["A","I","B"]
g1={("A","I"),("I","B"),("A","B")}
g2={("A","I"),("I","B")}
def transitive_closure(edges):
    r=set(edges)
    changed=True
    while changed:
        changed=False
        for a,b in list(r):
            for c,d in list(r):
                if b==c and (a,d) not in r:
                    r.add((a,d)); changed=True
    return sorted([list(e) for e in r])

result={
    "round":"R110",
    "output_gate":{
        "internal_decision_accuracy":accuracy(internal,xor),
        "behavior_accuracy_gate_on":accuracy(behavior_on,xor),
        "behavior_accuracy_gate_off":accuracy(behavior_off,xor),
        "internal_decision_preserved":internal==xor,
    },
    "report_gate":{
        "task_accuracy_report_on":accuracy(xor,xor),
        "task_accuracy_report_off":accuracy(xor,xor),
        "report_accuracy_on":accuracy(report_on,xor),
        "report_accuracy_off":accuracy(report_off,xor),
    },
    "self_channel_lesion":{
        "world_accuracy_intact":accuracy(world_target,world_target),
        "self_accuracy_intact":accuracy(self_target,self_target),
        "world_accuracy_after_self_lesion":accuracy(world_after_self_lesion,world_target),
        "self_accuracy_after_self_lesion":accuracy(self_after_self_lesion,self_target),
    },
    "access_gate":{
        "encoding_accuracy_gate_on":accuracy(encoding,xor),
        "encoding_accuracy_gate_off":accuracy(encoding,xor),
        "decision_accuracy_access_on":accuracy(decision_access_on,xor),
        "decision_accuracy_access_off":accuracy(decision_access_off,xor),
    },
    "same_external_different_internal":{
        "external_equal":external1==external2,
        "internal_equal":hidden1==hidden2,
        "internal_hamming_fraction":sum(a!=b for a,b in zip(hidden1,hidden2))/4,
    },
    "topology_insufficiency":{
        "G1_edges":sorted([list(e) for e in g1]),
        "G2_edges":sorted([list(e) for e in g2]),
        "same_transitive_reachability":transitive_closure(g1)==transitive_closure(g2),
        "reachability":transitive_closure(g1),
        "graphs_equal":g1==g2,
        "distinguishing_intervention":"Set A=1 and intervene I=0: a direct A->B path can remain in G1 but not G2."
    },
    "interpretation":"Functional dissociation topology is an intermediate comparator. Matching behavior or pairwise reachability does not establish constitutive organizational identity or experience."
}

assert result["output_gate"]["internal_decision_accuracy"]==1.0
assert result["output_gate"]["behavior_accuracy_gate_off"]==0.5
assert result["report_gate"]["task_accuracy_report_off"]==1.0
assert result["report_gate"]["report_accuracy_off"]==0.5
assert result["self_channel_lesion"]["world_accuracy_after_self_lesion"]==1.0
assert result["self_channel_lesion"]["self_accuracy_after_self_lesion"]==0.5
assert result["access_gate"]["encoding_accuracy_gate_off"]==1.0
assert result["access_gate"]["decision_accuracy_access_off"]==0.5
assert result["same_external_different_internal"]["external_equal"]
assert not result["same_external_different_internal"]["internal_equal"]
assert result["topology_insufficiency"]["same_transitive_reachability"]
assert not result["topology_insufficiency"]["graphs_equal"]

print(json.dumps(result,indent=2))
