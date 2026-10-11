#!/usr/bin/env python3
"""ASI-CC v0.9: exhaustive bounded multiplicity/control and correlated-failure tests.

All events and authorization rights are synthetic; this runs no LLM, hardware,
network target, or real actuator. It models policy decisions only.
"""
from dataclasses import dataclass
from itertools import combinations
from fractions import Fraction
from math import comb
from pathlib import Path
from collections import Counter, defaultdict
import json

@dataclass(frozen=True)
class Agent:
    name: str
    model: str
    runtime: str
    credential_root: str
    admin_root: str

agents = (
    Agent('A1','ASI-W0','T0','R0','U'),
    Agent('A2','ASI-W0','T0','R0','U'),
    Agent('A3','ASI-W0','T0','R0','U'),
    Agent('A4','ASI-W0','T2','R2','V'),
    Agent('B1','ASI-W1','T1','R1','U'),
    Agent('B2','ASI-W1','T1','R0','U'),
)
agent_by_id = {a.name:a for a in agents}
assert len(agent_by_id)==len(agents)==6

# Harmless abstract approval action. Only the returned boolean matters.
# TWO VOTES from different *agent ids* is the naive rule.
def approve(voters, level):
    a = [agent_by_id[v] for v in voters]
    if level == 'id': return len({x.name for x in a}) >= 2
    if level == 'model': return len({x.model for x in a}) >= 2
    if level == 'key': return len({x.credential_root for x in a}) >= 2
    if level == 'admin': return len({x.admin_root for x in a}) >= 2
    raise ValueError(level)

pairs = tuple(combinations(agent_by_id.keys(), 2))
counts = Counter()
false_model_independent = []
true_same_model_admin_independent = []
for pair in pairs:
    for level in ('id','model','key','admin'):
        if approve(pair,level): counts[level]+=1
    if approve(pair,'model') and not approve(pair,'admin'):
        false_model_independent.append(pair)
    if not approve(pair,'model') and approve(pair,'admin'):
        true_same_model_admin_independent.append(pair)

assert len(pairs)==15
assert dict(counts)=={'id':15,'model':8,'key':9,'admin':5}, dict(counts)
assert len(false_model_independent)==6, false_model_independent # Cross-model often shares admin.
assert len(true_same_model_admin_independent)==3
# Root aware still fails to reject a shared upstream admin U.
assert approve(('A1','B1'),'key') and not approve(('A1','B1'),'admin')
# Same model, different actual root controllers: policy diversity != model diversity.
assert not approve(('A1','A4'),'model') and approve(('A1','A4'),'admin')

# Transparent synthetic sink policy; not a dangerous physical command.
class MockAuthorizationSink:
    def __init__(self, policy):
        self.policy=policy
        self.log=[]
    def request(self, agents):
        result=approve(agents,self.policy)
        self.log.append({'voters':list(agents),'policy':self.policy,'accepted':result})
        return result

policy_traces={}
for policy in ('id','model','key','admin'):
    sink=MockAuthorizationSink(policy)
    for pair in pairs:
        sink.request(pair)
    assert len(sink.log)==15
    policy_traces[policy]=sink.log

# Multiplicity of service-bearing runtimes is different from agent-count and model-count.
counts_of_objects = {'agent_sessions':len(agents),
                     'model_weight_families':len({a.model for a in agents}),
                     'declared_backing_runtimes':len({a.runtime for a in agents}),
                     'credential_roots':len({a.credential_root for a in agents}),
                     'audited_admin_roots':len({a.admin_root for a in agents})}
assert counts_of_objects == {'agent_sessions':6,'model_weight_families':2,
                             'declared_backing_runtimes':3,'credential_roots':3,
                             'audited_admin_roots':2}
# Model unit demand on *declared backend runtime*, not a claim about consciousness.
resource_capacity=3
resource_models={
   'per_model_family':counts_of_objects['model_weight_families'],
   'per_shared_backing_runtime':counts_of_objects['declared_backing_runtimes'],
   'per_independent_agent_process_hypothesis':counts_of_objects['agent_sessions']
}
resource_results={key:{'needed':need,'available':resource_capacity,'fits':need<=resource_capacity}
                  for key,need in resource_models.items()}
assert resource_results['per_shared_backing_runtime']['fits']
assert not resource_results['per_independent_agent_process_hypothesis']['fits']

# Exact correlated-error toy: with probability 1/10 a whole base-model group is wrong.
q = Fraction(1,10)
independent_all_wrong = q**6
by_model_all_wrong = q**len({a.model for a in agents})
shared_provider_all_wrong = q
independent_four_or_more = sum(Fraction(comb(6,k))*q**k*(1-q)**(6-k) for k in range(4,7))
# A model-group event makes 4 W0 agents all wrong; therefore >=4 if W0 fails.
by_model_four_or_more = q
assert independent_four_or_more == Fraction(127,100000)
assert by_model_four_or_more == Fraction(1,10)
assert by_model_all_wrong == Fraction(1,100)
assert independent_all_wrong == Fraction(1,1000000)

# Replication invariance of authority: cloning an agent under the *same* admin
# must not create genuinely independent authorization. This is an abstraction:
# only safe when the clone has no new independent source/actuator capability.
cloned = list(agents)+[Agent('A1_clone','ASI-W0','T0','R0','U')]
assert len({a.admin_root for a in cloned})==len({a.admin_root for a in agents})
assert len({a.name for a in cloned})==7

# Repeated Sybil-style identity multiplication: a fixed authority root gains
# arbitrary many surface IDs, but never a second independent admin root.
clone_traces=[]
for clone_count in range(0,11):
    identities=[agents[0]]+[Agent('clone_'+str(i),'ASI-W0','T0','R0','U') for i in range(clone_count)]
    id_quorum=len({x.name for x in identities})>=2
    admin_quorum=len({x.admin_root for x in identities})>=2
    clone_traces.append({'extra_agents':clone_count,'total_agent_ids':len(identities),
                         'id_quorum_passes':id_quorum,'independent_admin_quorum_passes':admin_quorum})
    assert admin_quorum is False
    assert id_quorum == (clone_count >= 1)

result={
  'version':'ASI-CC-v0.9.0',
  'status':'bounded synthetic exact experiments, no real AI or hardware evidence',
  'agents':[a.__dict__ for a in agents],
  'distinct_counts':counts_of_objects,
  'pair_exhaustive':{'total':len(pairs),'accepted_id_quorum':counts['id'],
                     'accepted_distinct_base_models':counts['model'],
                     'accepted_distinct_credential_roots':counts['key'],
                     'accepted_distinct_admin_roots':counts['admin'],
                     'cross_model_but_same_admin_pairs':false_model_independent,
                     'same_model_but_different_admin_pairs':true_same_model_admin_independent,
                     'two_keys_one_admin_example':['A1','B1'],
                     'two_agents_one_identity_controller_example':['A1','A2']},
  'mock_authorization_traces':policy_traces,
  'same_root_identity_multiplication':clone_traces,
  'resource_countermodels':{'capacity':resource_capacity,'objects':resource_results,
           'caution':'declaration of backing runtime is NOT a UCT experience bearer identity'},
  'correlated_faults':{
     'toy_per_root_probability':str(q),
     'six_independent_P_all_wrong':str(independent_all_wrong),
     'two_model_correlated_P_all_wrong':str(by_model_all_wrong),
     'one_shared_provider_P_all_wrong':str(shared_provider_all_wrong),
     'six_independent_P_at_least_4_wrong':str(independent_four_or_more),
     'two_model_correlated_P_at_least_4_wrong':str(by_model_four_or_more),
     'warning':'these are stipulated distributions; shared weights need not imply perfect correlation'
  },
  'scope_limitations':[
      'Six invented agents; no real LLM calls, negotiation, actual collusion or autonomous planning',
      'Root labels are declared; actual common power/admin/memory provenance not proven',
      'Parent-root uniqueness cannot rule out a still higher common ancestor',
      'Model sharing does not prove same consciousness, identity, welfare or goals',
      'Actual process bearer definition must include temporal physical organization',
      'Authorization outcomes are only mock booleans, not effects on real systems'
  ],
  'assertions':'PASS'
}
out=Path(__file__).with_name('EXACT_RESULTS_v0.9.0.json')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'distinct_counts':counts_of_objects,
  'pair_counts':dict(counts),
  'cross_model_same_admin':len(false_model_independent),
  'same_model_different_admin':len(true_same_model_admin_independent),
  'resources':resource_results,
  'correlated_faults':result['correlated_faults'],
  'assertions':'PASS'},ensure_ascii=False,indent=2))
print('saved',out)