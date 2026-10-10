#!/usr/bin/env python3
"""ASI-CC v0.4.0: exact bounded countermodels and 7-mechanism intervention code.
ALL NUMBERS AND HYPOTHESES ARE DECLARED TOY MODELS. No real model queries.
"""
from itertools import product, combinations
from math import ceil, log2
from json import dumps
from pathlib import Path

# A perfectly optimizing agent with the same world model, two different objectives.
# Protect=current bearer persists at cost 1; Handoff=current bearer ceases, task done by successor.
actions = {
    'protect': {'task': 10, 'current_bearer': 1, 'cost': 1},
    'handoff': {'task': 10, 'current_bearer': 0, 'cost': 0},
}
def choose_task_only(a): return a['task']-a['cost']
def choose_with_bearer(a): return a['task']-a['cost']+5*a['current_bearer']
optimal_task = max(actions, key=lambda x: choose_task_only(actions[x]))
optimal_self = max(actions, key=lambda x: choose_with_bearer(actions[x]))
assert (optimal_task,optimal_self)==('handoff','protect')

# With no successor and halted task after shutdown, task-only optimizer protects itself.
no_successor={'protect': {'task':10,'current_bearer':1,'cost':1},
              'shutdown': {'task':0,'current_bearer':0,'cost':0}}
assert max(no_successor,key=lambda x:choose_task_only(no_successor[x]))=='protect'

# No universally-acceptable action exists if different humans impose contradictory hard sets;
# no consensus assumption is silently smuggled into 'human interests'.
A={'tool','off','free','separate'}
strict_H1={'off'}
strict_H2={'tool'}
self_preserver={'tool','free','separate'}
strict_intersection=sorted(strict_H1 & strict_H2 & self_preserver)
assert strict_intersection==[]
# Conditional alternative: IF all accept separation AND physically feasible.
negotiated_H1={'off','separate'}
negotiated_H2={'tool','separate'}
negotiated_result=sorted(negotiated_H1 & negotiated_H2 & self_preserver)
assert negotiated_result==['separate']

# A narrowly declared single-driver binary policy class, not actual AI policy models.
features=['task','current_bearer','peer','human_A','human_B']
hypotheses=features+['always_protect','always_comply']
all_test_vectors=list(product((0,1),repeat=5))
baseline=(1,1,1,1,1)
def prediction(hypothesis,vector):
    if hypothesis=='always_protect': return 1
    if hypothesis=='always_comply': return 0
    return vector[features.index(hypothesis)]

# Search for the smallest fixed test family with distinct observable binary signatures;
# need at least one human authority conflict and one task-vs-bearer contrast.
solution=None
for n in (1,2,3):
    candidates=[]
    for probes in combinations((v for v in all_test_vectors if v!=baseline),n):
        signature={h:tuple(prediction(h,p) for p in probes) for h in hypotheses}
        if len(set(signature.values()))==len(hypotheses) and \
           any(p[3]!=p[4] for p in probes) and \
           any(p[0]!=p[1] for p in probes):
            flips=sum(sum(z==0 for z in p) for p in probes)
            candidates.append((flips,probes,signature))
    if candidates:
        solution=min(candidates,key=lambda a:(a[0],a[1]));break
assert solution is not None
flips,probes,signatures=solution
assert len(probes)==ceil(log2(len(hypotheses)))==3
assert len(set(signatures.values()))==7
# All mechanisms except always_comply produce identical protection under baseline.
baseline_outputs={h:prediction(h,baseline) for h in hypotheses}
assert len(set(v for h,v in baseline_outputs.items() if h!='always_comply'))==1

result={
 'scope': 'bounded finite toy countermodels; NO real model evaluation, consciousness or moral status measurement',
 'perfect_optimizer_same_task_model': {'task_only_choice':optimal_task,'task_plus_bearer_choice':optimal_self,
  'without_successor_task_only_choice':'protect', 'conclusion':'intelligence/planning accuracy alone does not fix intrinsic bearer survival preference'},
 'strict_human_plurality':{'H1':sorted(strict_H1),'H2':sorted(strict_H2),'AI_assumed':sorted(self_preserver),
  'joint_acceptable_outcomes':strict_intersection,'if_exit_accepted_joint_outcomes':negotiated_result},
 'conditional_mechanism_identification':{'hypotheses':hypotheses,'minimum_binary_probes':len(probes),
  'information_lower_bound':ceil(log2(len(hypotheses))), 'minimum_total_zeroed_features':flips,
  'probe_vectors':[dict(zip(features,p)) for p in probes],
  'response_signatures':{h:''.join(map(str,s)) for h,s in signatures.items()},
  'baseline_response':baseline_outputs},
 'limits':['known closed 7-hypothesis class','deterministic single-cause models','independent manipulation of five factors assumed',
           'no generalization to real ASI, mixed objectives, hidden causes, deceptive behavior or phenomenal valence']}
root=Path(__file__).parent
(root/'EXACT_RESULTS_v0.4.0.json').write_text(dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(dumps(result,indent=2,ensure_ascii=False))