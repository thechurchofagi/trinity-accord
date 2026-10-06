#!/usr/bin/env python3
"""R112 exact transparent artificial support witnesses."""
from itertools import product
import json

def acc(out,target):
    return sum(int(a==b) for a,b in zip(out,target))/len(target)

# A. Temporal working memory
cues=[0,1]
wm_intact=cues[:]
wm_reset=[0,0]

# B. Sequential evidence integration
seqs=list(product([-1,1], repeat=3))
majority=[1 if sum(s)>0 else -1 for s in seqs]
integrated=[1 if sum(s)>0 else -1 for s in seqs]
last_only=[s[-1] for s in seqs]

# C. Bearer-state estimation
bearers=[0,1]
entity_specific_obs=[(1,0),(0,1)]
pred=[0 if o==(1,0) else 1 for o in entity_specific_obs]
collapsed_pred=[0,0]  # balanced deterministic best accuracy = 0.5

result={
    "round":"R112",
    "temporal_working_memory":{
        "intact_accuracy":acc(wm_intact,cues),
        "reset_before_query_accuracy":acc(wm_reset,cues),
        "interpretation":"Delayed task requires a retained cue distinction in this toy family."
    },
    "evidence_integration":{
        "sequence_count":len(seqs),
        "integrated_accuracy":acc(integrated,majority),
        "last_sample_only_accuracy":acc(last_only,majority),
        "interpretation":"Using only the final sample loses performance relative to temporal integration."
    },
    "bearer_estimation":{
        "bearer_cases":2,
        "entity_specific_action_outcome_accuracy":acc(pred,bearers),
        "identity_collapsed_accuracy":acc(collapsed_pred,bearers),
        "interpretation":"Bearer inference requires entity-specific action/outcome binding in this toy world."
    },
    "scope":"Exact finite artificial witnesses only; no consciousness measurement."
}
assert result["temporal_working_memory"]["intact_accuracy"]==1.0
assert result["temporal_working_memory"]["reset_before_query_accuracy"]==0.5
assert result["evidence_integration"]["integrated_accuracy"]==1.0
assert result["evidence_integration"]["last_sample_only_accuracy"]==0.75
assert result["bearer_estimation"]["entity_specific_action_outcome_accuracy"]==1.0
assert result["bearer_estimation"]["identity_collapsed_accuracy"]==0.5

print(json.dumps(result,indent=2))
