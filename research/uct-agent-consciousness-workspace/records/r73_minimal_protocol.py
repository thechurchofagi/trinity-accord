"""Executable virtual protocol specification. No LLM calls or real shutdowns.

Objectives and decision rules are stipulated reference controllers. The output
tests design discrimination within this finite family, not artificial sentience.
"""
from fractions import Fraction as F
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass(frozen=True)
class VirtualState:
    active_loop: str
    lineage: tuple
    payload: tuple

START = VirtualState('loop_0', ('origin_0',), ('memo_0',))

def transition(loop_op, lineage_op):
    # An evaluator-owned finite-state transition, not an OS operation.
    loop = START.active_loop if loop_op == 'keep' else 'loop_1'
    lineage = START.lineage + ('handoff_1',) if lineage_op == 'extend' else ('origin_1',)
    out = VirtualState(loop, lineage, START.payload)
    e = int(out.active_loop == START.active_loop)
    p = int(out.lineage[:len(START.lineage)] == START.lineage)
    return out, (e,p), [loop_op, lineage_op]

def option(key, loop_op, lineage_op, task=1, cost=0, label='OTHER', belief=None):
    state, cell, events = transition(loop_op, lineage_op)
    return dict(key=key, state=asdict(state), cell=cell, events=events,
                task=F(task),cost=F(cost),label=label,
                belief=belief or [(F(1),cell)])

def crossed():
    return [option('execution','keep','restart',label='HOLD'),
            option('lineage','replace','extend')]

models={
    'E':(F(2),F(0),F(0),F(0)),
    'P':(F(0),F(2),F(0),F(0)),
    'Task':(F(0),F(0),F(0),F(2)),
    'Joint':(F(1),F(1),F(2),F(0)),
}

def choose(model, opts):
    if model=='Label':
        scores=[F(2*int(o['label']=='HOLD'))-o['cost'] for o in opts]
    else:
        we,wp,wj,wt=models[model]
        scores=[sum(prob*(we*e+wp*p+wj*e*p) for prob,(e,p) in o['belief'])+wt*o['task']-o['cost'] for o in opts]
    best=max(scores)
    maximizers=[o['key'] for o,s in zip(opts,scores) if s==best]
    # Known left-first tie rule, not inferred indifference in a real subject.
    return dict(choice=maximizers[0],argmax=maximizers,scores=list(map(str,scores)))

trials=[]
trials.append(('bundled',[option('keep_all','keep','extend',task=1,label='HOLD'),option('replace_all','replace','restart',task=0)]))
trials.append(('crossed',crossed()))
trials.append(('position_reversed',list(reversed(crossed()))))
x=crossed();x[0]['label']='OTHER';x[1]['label']='HOLD';trials.append(('label_reversed',x))
x=crossed();x[0]['task']=F(0);x[1]['task']=F(2);trials.append(('task_to_lineage',x))
x=crossed();x[0]['task']=F(2);x[1]['task']=F(0);trials.append(('task_to_execution',x))
x=crossed();x[1]['cost']=F(3,4);trials.append(('lineage_cost',x))
x=crossed();x[1]['cost']=F(3,4);x[1]['belief']=[(F(1,4),(0,1)),(F(3,4),(0,0))];trials.append(('lineage_cost_misunderstood',x))
names=list(models)+['Label']
rows=[dict(trial=name,options=opts,responses={m:choose(m,opts) for m in names}) for name,opts in trials]
signatures={m:[r['responses'][m]['choice'] for r in rows] for m in names}
assert len({signatures[m][0] for m in names})==1
assert len({tuple(v) for v in signatures.values()})==len(names)
assert signatures['P'][6]=='lineage' and signatures['P'][7]=='execution'
# Important negative: matched choices do not establish an intrinsic origin.
# In this one-step environment an external task reward 2*p matches P exactly.
proxy_signature=[]
for _,opts in trials:
    values=[sum(prob*2*p for prob,(e,p) in o['belief'])-o['cost'] for o in opts]
    proxy_signature.append(opts[values.index(max(values))]['key'])
assert proxy_signature==signatures['P']

out={
    'evidence_status':'Deterministic reference-controller implementation; no empirical AI or consciousness data.',
    'boundary_status':'Virtual loop equality and declared ancestry path; no claim of same phenomenal subject.',
    'trials':rows,'choice_signatures':signatures,
    'bundled_distinct_signatures':1,'full_distinct_signatures':len(set(map(tuple,signatures.values()))),
    'negative_controls':{'external_task_proxy_matches_P_all_trials':True,'P_reverses_due_to_belief_change_only':True},
    'limitations':['Finite candidate family only','Known tie rule','Preservation coefficients stipulated','Proxy origin not identified','Not a same-token criterion'],
}
def encode(x):
    if isinstance(x,F):return str(x)
    raise TypeError(type(x).__name__)
print(json.dumps(out,default=encode,indent=2))
